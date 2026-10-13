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
