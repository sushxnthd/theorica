from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np

from .translation_action import CachedFiniteOracle, is_permutation, permutation_group_closure


@dataclass
class TranslationCompletenessCertificate:
    accepted: bool
    reason: str
    oracle_calls: int
    generated_group_size: int
    reconstructed_table: np.ndarray | None


@dataclass
class RackClosureCertificate:
    """Conditional exact reconstruction under a certified left-rack promise."""

    accepted: bool
    reason: str
    oracle_calls: int
    seed_rows: tuple[int, ...]
    derived_rows: int
    reconstructed_table: np.ndarray | None
    derivations: tuple[tuple[int, int, int], ...]


def reconstruct_rack_from_generating_rows(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    generator_rows: Iterable[int],
) -> RackClosureCertificate:
    """Reconstruct a promised finite left rack from operation-generating rows.

    If ``c = a * b``, left self-distributivity implies
    ``L_c = L_a L_b L_a^-1``.  Complete rows for a forward-generating seed
    set therefore determine the whole table using exactly ``|S| * n`` oracle
    cells.  This routine checks every collision among derived rows and abstains
    if the supplied seeds do not close the carrier.

    The result is conditional on an externally certified left-rack promise;
    the routine cannot certify that promise without querying the black box.
    """
    n = int(carrier_size)
    seeds = tuple(dict.fromkeys(int(row) for row in generator_rows))
    if n <= 0 or not seeds or any(not 0 <= row < n for row in seeds):
        raise ValueError("invalid carrier or generator rows")

    counted = CachedFiniteOracle(oracle, n)
    known: dict[int, np.ndarray] = {}
    for row in seeds:
        action = counted.row(row)
        if not is_permutation(action):
            return RackClosureCertificate(
                False, "non_bijective_seed_translation", counted.calls,
                seeds, 0, None, tuple(),
            )
        known[row] = action

    derivations: list[tuple[int, int, int]] = []
    changed = True
    while changed:
        changed = False
        snapshot = tuple(sorted(known))
        for a in snapshot:
            left_a = known[a]
            inverse_a = np.empty_like(left_a)
            inverse_a[left_a] = np.arange(n, dtype=np.int64)
            for b in snapshot:
                c = int(left_a[b])
                derived = left_a[known[b][inverse_a]]
                if c in known:
                    if not np.array_equal(known[c], derived):
                        return RackClosureCertificate(
                            False, "rack_identity_contradiction", counted.calls,
                            seeds, len(known) - len(seeds), None,
                            tuple(derivations + [(a, b, c)]),
                        )
                    continue
                known[c] = derived.copy()
                derivations.append((a, b, c))
                changed = True

    if len(known) != n:
        return RackClosureCertificate(
            False, "seed_rows_do_not_generate_carrier", counted.calls,
            seeds, len(known) - len(seeds), None, tuple(derivations),
        )

    table = np.stack([known[row] for row in range(n)])
    return RackClosureCertificate(
        True, "rack_reconstructed_from_operation_generators", counted.calls,
        seeds, len(known) - len(seeds), table, tuple(derivations),
    )


def certify_translation_group_completeness(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    generator_rows: Iterable[int],
    *,
    max_group_size: int = 20000,
) -> TranslationCompletenessCertificate:
    """Fail-closed exact certificate for an arbitrary permutation-row operation.

    After fully querying the trusted generator rows, this routine queries n-1
    coordinates of every other row. Bijectivity forces the remaining image,
    enabling exact membership testing in the generated group. The exact query
    count is r*n + (n-r)*(n-1); the companion theorem shows this is worst-case
    optimal without additional algebraic promises.
    """
    n = int(carrier_size)
    rows = tuple(dict.fromkeys(int(row) for row in generator_rows))
    if n < 2 or not rows or any(not 0 <= row < n for row in rows):
        raise ValueError("invalid carrier or generator rows")
    counted = CachedFiniteOracle(oracle, n)
    generators = []
    reconstructed: dict[int, np.ndarray] = {}
    for row in rows:
        action = counted.row(row)
        if not is_permutation(action):
            return TranslationCompletenessCertificate(False, "non_bijective_generator", counted.calls, 0, None)
        generators.append(action)
        reconstructed[row] = action
    group = permutation_group_closure(generators, max_size=max_group_size)
    if group is None:
        return TranslationCompletenessCertificate(False, "translation_group_exceeds_cap", counted.calls, max_group_size + 1, None)
    group_index = {tuple(map(int, permutation)) for permutation in group}
    for row in range(n):
        if row in reconstructed:
            continue
        prefix = [counted(row, column) for column in range(n - 1)]
        if len(set(prefix)) != len(prefix):
            return TranslationCompletenessCertificate(False, "non_bijective_row", counted.calls, len(group), None)
        missing = set(range(n)) - set(prefix)
        if len(missing) != 1:
            return TranslationCompletenessCertificate(False, "non_bijective_row", counted.calls, len(group), None)
        action = np.asarray(prefix + [missing.pop()], dtype=np.int64)
        if tuple(map(int, action)) not in group_index:
            return TranslationCompletenessCertificate(False, "incomplete_generator_group", counted.calls, len(group), None)
        reconstructed[row] = action
    table = np.stack([reconstructed[row] for row in range(n)])
    return TranslationCompletenessCertificate(True, "complete_translation_group_certified", counted.calls, len(group), table)
