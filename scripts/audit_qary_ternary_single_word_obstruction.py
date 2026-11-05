#!/usr/bin/env python3
"""Independent stdlib-only replay of the minimal ternary obstruction."""

from __future__ import annotations

import json
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path

SOURCE = Path("results/qary_ternary_single_word_obstruction/results.json")
OUT = Path("results/qary_ternary_single_word_obstruction/audit.json")
WORDS = tuple(product(range(3), repeat=3))
WORD_INDEX = {word: index for index, word in enumerate(WORDS)}
BASE_WORDS = tuple(word for word in WORDS if 2 not in word)
NEW_WORDS = tuple(word for word in WORDS if 2 in word)
LEVEL_COSTS = (1, 3, 1)


def query_groups(words):
    groups = []
    for level in range(3):
        for prefix in product(range(3), repeat=level):
            row = tuple(
                word[level] if word[:level] == prefix else 0 for word in words
            )
            groups.append((row, level))
    return tuple(groups)


def feasible(words, budget):
    groups = query_groups(words)
    alphabets = tuple(tuple(sorted(set(row))) for row, _ in groups)
    states = 0

    def children(counts, erased, remaining, group):
        row, _ = groups[group]
        rest = tuple(
            count - (index == group) for index, count in enumerate(remaining)
        )
        answer = []
        for observed in alphabets[group]:
            child = tuple(
                min(2, count + (row[index] != observed))
                for index, count in enumerate(counts)
            )
            if any(count <= 1 for count in child):
                answer.append((child, erased, rest))
        if erased == 0:
            answer.append((counts, 1, rest))
        return tuple(answer)

    @cache
    def search(counts, erased, remaining, remaining_budget, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return True
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in range(1, 4)):
                continue
            row, level = groups[group]
            cost = LEVEL_COSTS[level]
            if cost > remaining_budget or len({row[index] for index in live}) < 2:
                continue
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                search(*child, remaining_budget - cost, False)
                for child in descendants
            ):
                return True
        return False

    initial = ((0,) * len(words), 0, (4,) * len(groups))
    return search(*initial, budget, True), states


def permute_word(word, permutation):
    return tuple(permutation[symbol] for symbol in word)


def main():
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    baseline, baseline_states = feasible(BASE_WORDS, 17)
    singleton_checks = []
    independent_states = baseline_states
    for word in NEW_WORDS:
        result, states = feasible((*BASE_WORDS, word), 17)
        singleton_checks.append(result)
        independent_states += states
    pair_checks = []
    obstruction_pairs = []
    for pair in combinations(NEW_WORDS, 2):
        at_17, states_17 = feasible((*BASE_WORDS, *pair), 17)
        independent_states += states_17
        at_18 = None
        if not at_17:
            at_18, states_18 = feasible((*BASE_WORDS, *pair), 18)
            independent_states += states_18
            obstruction_pairs.append(pair)
        pair_checks.append((at_17, at_18))
    symmetry_checks = []
    for pair in obstruction_pairs:
        for permutation in permutations(range(3)):
            words = tuple(
                sorted(
                    (*[permute_word(word, permutation) for word in BASE_WORDS],
                     *[permute_word(word, permutation) for word in pair]),
                    key=WORD_INDEX.__getitem__,
                )
            )
            at_17, states_17 = feasible(words, 17)
            at_18, states_18 = feasible(words, 18)
            independent_states += states_17 + states_18
            symmetry_checks.append(
                {
                    "fixes_zero": permutation[0] == 0,
                    "obstructing": not at_17 and at_18,
                    "feasible_at_17": at_17,
                }
            )
    primary_pairs = {
        tuple(tuple(word) for word in pair)
        for pair in primary["obstruction_pairs"]
    }
    report = {
        "production_module_imports": 0,
        "independent_baseline_budget_17_feasible": baseline,
        "independent_singletons_budget_17_feasible": sum(singleton_checks),
        "independent_singleton_total": len(singleton_checks),
        "independent_pairs_budget_17_infeasible": sum(
            not at_17 for at_17, _ in pair_checks
        ),
        "independent_pair_total": len(pair_checks),
        "independent_obstruction_pairs": [
            [list(word) for word in pair] for pair in obstruction_pairs
        ],
        "independent_symmetry_checks_obstructing": sum(
            row["obstructing"] for row in symmetry_checks
        ),
        "independent_symmetry_check_total": len(symmetry_checks),
        "independent_zero_fixing_checks_obstructing": sum(
            row["fixes_zero"] and row["obstructing"] for row in symmetry_checks
        ),
        "independent_zero_fixing_check_total": sum(
            row["fixes_zero"] for row in symmetry_checks
        ),
        "independent_zero_moving_checks_feasible_at_17": sum(
            not row["fixes_zero"] and row["feasible_at_17"]
            for row in symmetry_checks
        ),
        "independent_zero_moving_check_total": sum(
            not row["fixes_zero"] for row in symmetry_checks
        ),
        "independent_states_solved": independent_states,
    }
    report["passed"] = (
        baseline
        and report["independent_singletons_budget_17_feasible"]
        == report["independent_singleton_total"]
        == 19
        and report["independent_pairs_budget_17_infeasible"] == 3
        and report["independent_pair_total"] == 171
        and set(obstruction_pairs) == primary_pairs
        and report["independent_symmetry_check_total"] == 18
        and report["independent_symmetry_checks_obstructing"] == 6
        and report["independent_zero_fixing_checks_obstructing"]
        == report["independent_zero_fixing_check_total"]
        == 6
        and report["independent_zero_moving_checks_feasible_at_17"]
        == report["independent_zero_moving_check_total"]
        == 12
        and primary["summary"]["passed"]
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
