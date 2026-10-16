from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Callable

import numpy as np

from .translation_action import CachedFiniteOracle
from .translation_certificate import RackClosureCertificate, reconstruct_rack_from_generating_rows


@dataclass
class RackSeedAcquisitionResult:
    """Budgeted deterministic seed acquisition under a certified rack promise."""

    accepted: bool
    reason: str
    oracle_calls: int
    seed_rows: tuple[int, ...]
    certified_rows: int
    reconstruction: RackClosureCertificate | None


@dataclass(frozen=True)
class HiddenGeneratorLocalizationResult:
    """Cell-query localization result for the certified hidden-cycle family."""

    accepted: bool
    reason: str
    oracle_calls: int
    distinguished_row: int | None
    seed_rows: tuple[int, ...]
    observations: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class RandomizedHiddenGeneratorResult:
    """Explicit bounded-error localization receipt for a certified family."""

    accepted: bool
    reason: str
    oracle_calls: int
    distinguished_row: int | None
    seed_rows: tuple[int, ...]
    observations: tuple[tuple[int, int, int], ...]
    query_budget: int
    guaranteed_success_numerator: int
    guaranteed_success_denominator: int


def locate_hidden_generator_randomized(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    *,
    family_certified: bool,
    allow_bounded_error: bool,
    minimum_success_numerator: int,
    minimum_success_denominator: int,
    rng_seed: int,
) -> RandomizedHiddenGeneratorResult:
    """Use the exact randomized query frontier under an explicit contract.

    For alpha < 1 this API is deliberately opt-in.  A random permutation is
    generated from ``rng_seed``; its first q rows are probed and the next row is
    the guess after an all-identity transcript.  The exact worst-case success
    receipt is (q+1)/n, where q=max(0,ceil(n*alpha-1)).
    """
    n = int(carrier_size)
    if n < 3:
        raise ValueError("carrier_size must be at least 3")
    if minimum_success_denominator <= 0:
        raise ValueError("minimum_success_denominator must be positive")
    alpha = Fraction(minimum_success_numerator, minimum_success_denominator)
    if not 0 <= alpha <= 1:
        raise ValueError("minimum success probability must lie in [0,1]")
    if not family_certified:
        return RandomizedHiddenGeneratorResult(False, "family_certificate_required", 0, None, (), (), 0, 0, 1)
    if alpha < 1 and not allow_bounded_error:
        return RandomizedHiddenGeneratorResult(False, "bounded_error_authorization_required", 0, None, (), (), 0, 0, 1)
    if alpha == 1:
        exact = locate_hidden_generator_by_cells(oracle, n, family_certified=True)
        return RandomizedHiddenGeneratorResult(
            exact.accepted, exact.reason, exact.oracle_calls,
            exact.distinguished_row, exact.seed_rows, exact.observations,
            n - 1, 1, 1,
        )
    q = max(0, math.ceil(n * alpha - 1))
    order = [int(x) for x in np.random.default_rng(int(rng_seed)).permutation(n)]
    observations: list[tuple[int, int, int]] = []
    for row in order[:q]:
        column = (row + 1) % n
        value = int(oracle(row, column))
        observations.append((row, column, value))
        if not 0 <= value < n:
            return RandomizedHiddenGeneratorResult(
                False, "oracle_value_out_of_range", len(observations), None,
                (), tuple(observations), q, q + 1, n,
            )
        if value != column:
            companion = column
            return RandomizedHiddenGeneratorResult(
                True, "hidden_generator_localized", len(observations), row,
                (row, companion), tuple(observations), q, q + 1, n,
            )
    guess = order[q]
    companion = (guess + 1) % n
    return RandomizedHiddenGeneratorResult(
        True, "hidden_generator_guessed_with_bounded_error", q, guess,
        (guess, companion), tuple(observations), q, q + 1, n,
    )


def locate_hidden_generator_by_cells(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    *,
    family_certified: bool,
) -> HiddenGeneratorLocalizationResult:
    """Locate the unique nonidentity row using at most n - 1 cell queries.

    The external certificate must promise the family R(n, z, sigma): every row
    except z is the identity and row z fixes z while acting as a full cycle on
    the other elements.  The function deliberately refuses to extrapolate this
    theorem to an uncertified rack.

    Rows 0 through n - 2 receive one deterministic off-diagonal probe.  A
    nonidentity answer identifies z immediately; after n - 1 identity answers,
    z is the omitted final row.  Any other element paired with z is then a
    generating seed for this promised family.
    """
    n = int(carrier_size)
    if n < 3:
        raise ValueError("carrier_size must be at least 3")
    if not family_certified:
        return HiddenGeneratorLocalizationResult(
            False,
            "family_certificate_required",
            0,
            None,
            (),
            (),
        )

    observations: list[tuple[int, int, int]] = []
    for row in range(n - 1):
        column = (row + 1) % n
        value = int(oracle(row, column))
        observations.append((row, column, value))
        if not 0 <= value < n:
            return HiddenGeneratorLocalizationResult(
                False,
                "oracle_value_out_of_range",
                len(observations),
                None,
                (),
                tuple(observations),
            )
        if value != column:
            return HiddenGeneratorLocalizationResult(
                True,
                "hidden_generator_localized",
                len(observations),
                row,
                (row, column),
                tuple(observations),
            )

    distinguished = n - 1
    companion = 0
    return HiddenGeneratorLocalizationResult(
        True,
        "hidden_generator_inferred",
        n - 1,
        distinguished,
        (distinguished, companion),
        tuple(observations),
    )


def acquire_rack_generating_rows(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    *,
    max_seed_rows: int,
) -> RackSeedAcquisitionResult:
    """Acquire least unseen full rows until rack closure covers the carrier.

    This is fail-closed and deterministic.  It shares an oracle cache across
    attempts, so each chosen seed costs exactly one new complete row.  The
    companion boundary theorem shows that this policy can require all n rows
    even when a two-row generating set exists; callers must therefore supply an
    explicit budget and treat exhaustion as abstention.
    """
    n = int(carrier_size)
    budget = int(max_seed_rows)
    if n <= 0 or budget <= 0:
        raise ValueError("carrier_size and max_seed_rows must be positive")

    cached = CachedFiniteOracle(oracle, n)
    seeds: list[int] = []
    known: set[int] = set()
    last: RackClosureCertificate | None = None

    while len(known) < n:
        unseen = sorted(set(range(n)) - known)
        if len(seeds) >= budget:
            return RackSeedAcquisitionResult(
                False, "seed_budget_exhausted", cached.calls,
                tuple(seeds), len(known), last,
            )
        seeds.append(unseen[0])
        last = reconstruct_rack_from_generating_rows(cached, n, seeds)
        if last.reason in {
            "non_bijective_seed_translation",
            "rack_identity_contradiction",
        }:
            return RackSeedAcquisitionResult(
                False, last.reason, cached.calls, tuple(seeds),
                len(known), last,
            )
        known = set(seeds)
        known.update(c for _, _, c in last.derivations)
        if last.accepted:
            return RackSeedAcquisitionResult(
                True, "rack_seed_certificate_acquired", cached.calls,
                tuple(seeds), n, last,
            )

    raise AssertionError("unreachable")
