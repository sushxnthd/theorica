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


@dataclass(frozen=True)
class HiddenFamilyVerificationResult:
    """Receipt for full verification of the hidden-cycle rack family."""

    accepted: bool
    reason: str
    oracle_calls: int
    distinguished_row: int | None
    seed_rows: tuple[int, ...]
    observations: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class HiddenFamilySpotCheckResult:
    """One-sided bounded-error receipt for an explicit family witness."""

    accepted: bool
    reason: str
    oracle_calls: int
    distinguished_row: int | None
    query_budget: int
    population_size: int
    guaranteed_rejection_numerator: int
    guaranteed_rejection_denominator: int
    mismatch: tuple[int, int, int, int] | None


def _valid_hidden_cycle_witness(
    carrier_size: int,
    distinguished_row: int,
    active_translation: tuple[int, ...],
) -> bool:
    """Check the public witness without consulting the private oracle."""
    n = int(carrier_size)
    z = int(distinguished_row)
    row = tuple(int(value) for value in active_translation)
    if n < 3 or not 0 <= z < n or len(row) != n:
        return False
    if tuple(sorted(row)) != tuple(range(n)) or row[z] != z:
        return False
    start = next(index for index in range(n) if index != z)
    seen: list[int] = []
    current = start
    while current not in seen:
        if current == z:
            return False
        seen.append(current)
        current = row[current]
    return current == start and set(seen) == set(range(n)) - {z}


def verify_hidden_cycle_family_by_cells(
    oracle: Callable[[int, int], int],
    carrier_size: int,
) -> HiddenFamilyVerificationResult:
    """Verify family membership and locate the generator using exactly n^2 cells.

    Unlike the query-efficient locators, this path does not trust a Boolean
    family assertion.  It reads the complete operation and accepts exactly the
    tables with one nonidentity row whose translation fixes its own label and
    is a full cycle on the complement.
    """
    n = int(carrier_size)
    if n < 3:
        raise ValueError("carrier_size must be at least 3")
    rows: list[list[int]] = []
    observations: list[tuple[int, int, int]] = []
    for row in range(n):
        values: list[int] = []
        for column in range(n):
            value = int(oracle(row, column))
            observations.append((row, column, value))
            if not 0 <= value < n:
                return HiddenFamilyVerificationResult(
                    False, "oracle_value_out_of_range", len(observations),
                    None, (), tuple(observations),
                )
            values.append(value)
        rows.append(values)

    identity = tuple(range(n))
    nonidentity = [index for index, row in enumerate(rows) if tuple(row) != identity]
    if len(nonidentity) != 1:
        return HiddenFamilyVerificationResult(
            False, "not_exactly_one_nonidentity_row", n * n,
            None, (), tuple(observations),
        )
    distinguished = nonidentity[0]
    active = tuple(rows[distinguished])
    if not _valid_hidden_cycle_witness(n, distinguished, active):
        return HiddenFamilyVerificationResult(
            False, "active_translation_not_full_complement_cycle", n * n,
            None, (), tuple(observations),
        )
    companion = next(index for index in range(n) if index != distinguished)
    return HiddenFamilyVerificationResult(
        True, "hidden_cycle_family_verified", n * n, distinguished,
        (distinguished, companion), tuple(observations),
    )


def spot_check_hidden_cycle_witness(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    *,
    distinguished_row: int,
    active_translation: tuple[int, ...],
    allow_bounded_error: bool,
    minimum_rejection_numerator: int,
    minimum_rejection_denominator: int,
    rng_seed: int,
) -> HiddenFamilySpotCheckResult:
    """Spot-check an explicit witness with the exact one-sided frontier.

    If the oracle differs from the witnessed table in at least one cell,
    uniform sampling without replacement of q cells rejects with probability
    at least q/n^2.  The guarantee is over an ideal uniform permutation; the
    seed records the concrete pseudorandom execution for reproducibility.
    """
    n = int(carrier_size)
    if n < 3:
        raise ValueError("carrier_size must be at least 3")
    if minimum_rejection_denominator <= 0:
        raise ValueError("minimum_rejection_denominator must be positive")
    beta = Fraction(minimum_rejection_numerator, minimum_rejection_denominator)
    if not 0 <= beta <= 1:
        raise ValueError("minimum rejection probability must lie in [0,1]")
    population = n * n
    if not _valid_hidden_cycle_witness(n, distinguished_row, active_translation):
        return HiddenFamilySpotCheckResult(
            False, "invalid_family_witness", 0, None, 0, population,
            0, 1, None,
        )
    if beta < 1 and not allow_bounded_error:
        return HiddenFamilySpotCheckResult(
            False, "bounded_error_authorization_required", 0, None, 0,
            population, 0, 1, None,
        )

    budget = math.ceil(population * beta)
    order = np.random.default_rng(int(rng_seed)).permutation(population)
    active = tuple(int(value) for value in active_translation)
    z = int(distinguished_row)
    for call_count, flat in enumerate(order[:budget], start=1):
        row, column = divmod(int(flat), n)
        expected = active[column] if row == z else column
        observed = int(oracle(row, column))
        if not 0 <= observed < n:
            return HiddenFamilySpotCheckResult(
                False, "oracle_value_out_of_range", call_count, None, budget,
                population, budget, population,
                (row, column, expected, observed),
            )
        if observed != expected:
            return HiddenFamilySpotCheckResult(
                False, "certificate_mismatch", call_count, None, budget,
                population, budget, population,
                (row, column, expected, observed),
            )
    return HiddenFamilySpotCheckResult(
        True, "certificate_spot_check_passed", budget, z, budget,
        population, budget, population, None,
    )


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
