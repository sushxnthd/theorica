from __future__ import annotations

from dataclasses import dataclass
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
