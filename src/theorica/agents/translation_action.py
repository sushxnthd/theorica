from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Callable, Iterable

import numpy as np


@dataclass
class TranslationActionResult:
    accepted: bool
    reason: str
    oracle_calls: int
    queried_rows: int
    generated_group_size: int
    base: tuple[int, ...]
    validation_queries: int
    reconstructed_table: np.ndarray | None
    translation_index: dict[int, int] | None


class CachedFiniteOracle:
    """Cache chosen queries to a deterministic finite binary-operation oracle."""

    def __init__(self, oracle: Callable[[int, int], int], size: int):
        self.oracle = oracle
        self.size = int(size)
        self.cache: dict[tuple[int, int], int] = {}
        self.calls = 0

    def __call__(self, x: int, y: int) -> int:
        key = (int(x), int(y))
        if key not in self.cache:
            value = int(self.oracle(*key))
            if not 0 <= value < self.size:
                raise ValueError("oracle output outside carrier")
            self.cache[key] = value
            self.calls += 1
        return self.cache[key]

    def row(self, x: int) -> np.ndarray:
        return np.asarray(
            [self(int(x), y) for y in range(self.size)],
            dtype=np.int64,
        )


def is_permutation(action: np.ndarray) -> bool:
    action = np.asarray(action, dtype=np.int64)
    return bool(
        len(action) > 0
        and np.array_equal(
            np.sort(action),
            np.arange(len(action), dtype=np.int64),
        )
    )


def inverse_permutation(action: np.ndarray) -> np.ndarray:
    action = np.asarray(action, dtype=np.int64)
    if not is_permutation(action):
        raise ValueError("action is not a permutation")
    inv = np.empty_like(action)
    inv[action] = np.arange(len(action), dtype=np.int64)
    return inv


def compose_permutations(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return left after right."""
    left = np.asarray(left, dtype=np.int64)
    right = np.asarray(right, dtype=np.int64)
    return left[right]


def permutation_group_closure(
    generators: Iterable[np.ndarray],
    *,
    max_size: int = 20000,
) -> list[np.ndarray] | None:
    generators = [np.asarray(g, dtype=np.int64) for g in generators]
    if not generators:
        return []
    n = len(generators[0])
    if any(len(g) != n or not is_permutation(g) for g in generators):
        return None

    moves: list[tuple[int, ...]] = []
    for generator in generators:
        moves.append(tuple(map(int, generator)))
        moves.append(tuple(map(int, inverse_permutation(generator))))

    identity = tuple(range(n))
    seen: set[tuple[int, ...]] = {identity}
    queue: deque[tuple[int, ...]] = deque([identity])

    while queue:
        current = np.asarray(queue.popleft(), dtype=np.int64)
        for move_tuple in moves:
            move = np.asarray(move_tuple, dtype=np.int64)
            candidate = tuple(
                map(int, compose_permutations(move, current))
            )
            if candidate in seen:
                continue
            seen.add(candidate)
            if len(seen) > int(max_size):
                return None
            queue.append(candidate)

    return [np.asarray(item, dtype=np.int64) for item in seen]


def greedy_permutation_base(
    group: list[np.ndarray],
    carrier_size: int,
    *,
    max_base_size: int = 12,
) -> tuple[int, ...] | None:
    """Greedily choose points whose images distinguish every group element.

    A base B of a permutation group has trivial pointwise stabilizer, so the
    image tuple (g(b))_{b in B} uniquely identifies g within the group.
    """
    if not group:
        return tuple()

    signatures = [tuple() for _ in group]
    remaining = set(range(int(carrier_size)))
    chosen: list[int] = []

    while len(set(signatures)) < len(group):
        if not remaining or len(chosen) >= int(max_base_size):
            return None

        best_point = None
        best_unique = -1
        for point in remaining:
            candidate = [
                signature + (int(g[point]),)
                for signature, g in zip(signatures, group)
            ]
            unique = len(set(candidate))
            if unique > best_unique:
                best_unique = unique
                best_point = int(point)
            if unique == len(group):
                break

        if best_point is None:
            return None

        chosen.append(best_point)
        remaining.remove(best_point)
        signatures = [
            signature + (int(g[best_point]),)
            for signature, g in zip(signatures, group)
        ]

    return tuple(chosen)


def _signature_index(
    group: list[np.ndarray],
    base: tuple[int, ...],
) -> dict[tuple[int, ...], list[int]]:
    index: dict[tuple[int, ...], list[int]] = {}
    for i, action in enumerate(group):
        signature = tuple(int(action[b]) for b in base)
        index.setdefault(signature, []).append(i)
    return index


def discover_translation_action_representation(
    oracle: Callable[[int, int], int],
    carrier_size: int,
    *,
    seed: int = 0,
    max_generator_rows: int = 8,
    max_group_size: int = 20000,
    max_base_size: int = 12,
    validation_queries: int = 64,
    acquisition_policy: str = "unresolved",
) -> TranslationActionResult:
    """Discover a faithful finite operation through its left-translation action.

    The procedure has no named group/quandle/quasigroup route. It queries a
    small number of complete left translations, generates the permutation group
    they induce, computes a base for that group, and identifies every remaining
    left translation only from its images on the base.

    Acceptance is empirical and falsifiable:
    - any queried non-bijective translation rejects the representation;
    - group closure larger than max_group_size rejects the compact model;
    - translations not uniquely identifiable on the base cause another full
      row to be acquired;
    - fresh held-out oracle pairs must match the reconstructed table.
    """
    n = int(carrier_size)
    if n <= 0:
        raise ValueError("carrier_size must be positive")
    if acquisition_policy not in {"unresolved", "random"}:
        raise ValueError("acquisition_policy must be 'unresolved' or 'random'")

    rng = np.random.default_rng(seed)
    counted = CachedFiniteOracle(oracle, n)

    generators: list[np.ndarray] = []
    queried_rows: set[int] = set()
    next_row = int(rng.integers(0, n))
    group: list[np.ndarray] = []
    base: tuple[int, ...] = tuple()

    for _ in range(int(max_generator_rows)):
        if next_row not in queried_rows:
            action = counted.row(next_row)
            queried_rows.add(next_row)
            if not is_permutation(action):
                return TranslationActionResult(
                    accepted=False,
                    reason="non_bijective_translation",
                    oracle_calls=counted.calls,
                    queried_rows=len(queried_rows),
                    generated_group_size=0,
                    base=tuple(),
                    validation_queries=0,
                    reconstructed_table=None,
                    translation_index=None,
                )
            generators.append(action)

        group = permutation_group_closure(
            generators,
            max_size=max_group_size,
        )
        if group is None:
            return TranslationActionResult(
                accepted=False,
                reason="translation_group_exceeds_cap",
                oracle_calls=counted.calls,
                queried_rows=len(queried_rows),
                generated_group_size=max_group_size + 1,
                base=tuple(),
                validation_queries=0,
                reconstructed_table=None,
                translation_index=None,
            )

        base_candidate = greedy_permutation_base(
            group,
            n,
            max_base_size=max_base_size,
        )
        if base_candidate is None:
            return TranslationActionResult(
                accepted=False,
                reason="no_small_permutation_base",
                oracle_calls=counted.calls,
                queried_rows=len(queried_rows),
                generated_group_size=len(group),
                base=tuple(),
                validation_queries=0,
                reconstructed_table=None,
                translation_index=None,
            )
        base = base_candidate
        index = _signature_index(group, base)

        preliminary: dict[int, int] = {}
        unresolved: list[int] = []

        for x in range(n):
            signature = tuple(counted(x, b) for b in base)
            matches = index.get(signature, [])
            if len(matches) == 1:
                preliminary[x] = int(matches[0])
            else:
                unresolved.append(int(x))

        # Faithfulness is part of the representation promise: distinct carrier
        # elements must correspond to distinct translations. A too-small
        # generated group can otherwise make many elements share the same base
        # signature (notably when the first acquired row is the identity).
        reverse: dict[int, list[int]] = {}
        for x, group_index in preliminary.items():
            reverse.setdefault(group_index, []).append(x)

        collided: set[int] = set()
        for xs in reverse.values():
            if len(xs) > 1:
                collided.update(xs)

        unresolved.extend(sorted(collided))
        unresolved = sorted(set(unresolved))
        translation_index = {
            x: group_index
            for x, group_index in preliminary.items()
            if x not in collided
        }

        if not unresolved:
            reconstructed = np.stack(
                [group[translation_index[x]] for x in range(n)],
                axis=0,
            )

            validation_used = 0
            attempts = 0
            while (
                validation_used < int(validation_queries)
                and attempts < 20 * max(1, int(validation_queries))
            ):
                attempts += 1
                x, y = map(int, rng.integers(0, n, size=2))
                if (x, y) in counted.cache:
                    continue
                validation_used += 1
                if counted(x, y) != int(reconstructed[x, y]):
                    return TranslationActionResult(
                        accepted=False,
                        reason="heldout_validation_failure",
                        oracle_calls=counted.calls,
                        queried_rows=len(queried_rows),
                        generated_group_size=len(group),
                        base=base,
                        validation_queries=validation_used,
                        reconstructed_table=None,
                        translation_index=None,
                    )

            return TranslationActionResult(
                accepted=True,
                reason="faithful_translation_action_recovered",
                oracle_calls=counted.calls,
                queried_rows=len(queried_rows),
                generated_group_size=len(group),
                base=base,
                validation_queries=validation_used,
                reconstructed_table=reconstructed,
                translation_index=translation_index,
            )

        # Acquire the most direct counterexample to the current representation:
        # a carrier element whose translation cannot yet be uniquely represented
        # by the generated permutation group.
        unseen_unresolved = [
            x for x in unresolved if x not in queried_rows
        ]
        if not unseen_unresolved:
            return TranslationActionResult(
                accepted=False,
                reason="nonfaithful_or_unresolved_translation_action",
                oracle_calls=counted.calls,
                queried_rows=len(queried_rows),
                generated_group_size=len(group),
                base=base,
                validation_queries=0,
                reconstructed_table=None,
                translation_index=None,
            )

        if acquisition_policy == "unresolved":
            candidates = unseen_unresolved
        else:
            candidates = [
                x for x in range(n) if x not in queried_rows
            ]
            if not candidates:
                candidates = unseen_unresolved
        next_row = int(rng.choice(candidates))

    return TranslationActionResult(
        accepted=False,
        reason="generator_budget_exhausted",
        oracle_calls=counted.calls,
        queried_rows=len(queried_rows),
        generated_group_size=len(group),
        base=base,
        validation_queries=0,
        reconstructed_table=None,
        translation_index=None,
    )



@dataclass
class TranslationLaw:
    word: str
    diagonal_constant: int | None
    exhaustive_pairs: int


def _evaluate_translation_word(
    word: str,
    left_x: np.ndarray,
    left_y: np.ndarray,
    left_c: np.ndarray | None = None,
) -> np.ndarray:
    token_map = {
        "X": np.asarray(left_x, dtype=np.int64),
        "Y": np.asarray(left_y, dtype=np.int64),
        "x": inverse_permutation(left_x),
        "y": inverse_permutation(left_y),
    }
    if left_c is not None:
        token_map["C"] = np.asarray(left_c, dtype=np.int64)
        token_map["c"] = inverse_permutation(left_c)

    actions = [token_map[token] for token in word]
    result = actions[-1].copy()
    for action in reversed(actions[:-1]):
        result = compose_permutations(action, result)
    return result


def discover_short_translation_law(
    table: np.ndarray,
    *,
    max_word_length: int = 3,
    screening_pairs: int = 16,
    seed: int = 0,
) -> TranslationLaw | None:
    """Compress a reconstructed operation into a short left-action law.

    Search is deliberately representation-level rather than family-labelled.
    X,Y denote L_x,L_y and lowercase x,y their inverses. If F(x,x) is a
    carrier-wide constant c, C/c denote L_c and its inverse.

    A candidate must first survive random screening and is then verified on
    every ordered pair (x,y) in the carrier.
    """
    table = np.asarray(table, dtype=np.int64)
    n = len(table)
    rows = [table[i].copy() for i in range(n)]
    if not all(is_permutation(row) for row in rows):
        return None
    inverses = [inverse_permutation(row) for row in rows]

    diagonal = np.diag(table)
    constant = int(diagonal[0]) if np.all(diagonal == diagonal[0]) else None
    left_c = None if constant is None else rows[constant]
    inverse_c = None if constant is None else inverses[constant]

    tokens = ["X", "Y", "x", "y"]
    if left_c is not None:
        tokens += ["C", "c"]

    rng = np.random.default_rng(seed)
    probes = [
        tuple(map(int, rng.integers(0, n, size=2)))
        for _ in range(int(screening_pairs))
    ]
    probes += [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]

    import itertools

    def evaluate(word: str, x_value: int, y_value: int) -> np.ndarray:
        token_map = {
            "X": rows[x_value],
            "Y": rows[y_value],
            "x": inverses[x_value],
            "y": inverses[y_value],
        }
        if left_c is not None:
            token_map["C"] = left_c
            token_map["c"] = inverse_c

        actions = [token_map[token] for token in word]
        result = actions[-1]
        for action in reversed(actions[:-1]):
            result = compose_permutations(action, result)
        return result

    for length in range(1, int(max_word_length) + 1):
        for word_tuple in itertools.product(tokens, repeat=length):
            word = "".join(word_tuple)

            if any(
                not np.array_equal(
                    evaluate(word, x_value, y_value),
                    rows[int(table[x_value, y_value])],
                )
                for x_value, y_value in probes
            ):
                continue

            passed = True
            for x_value in range(n):
                for y_value in range(n):
                    if not np.array_equal(
                        evaluate(word, x_value, y_value),
                        rows[int(table[x_value, y_value])],
                    ):
                        passed = False
                        break
                if not passed:
                    break

            if passed:
                return TranslationLaw(
                    word=word,
                    diagonal_constant=constant,
                    exhaustive_pairs=n * n,
                )

    return None
