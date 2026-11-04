#!/usr/bin/env python3
"""Locate the minimal ternary augmentation causing the (1,3,1) gap."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_ternary_single_word_obstruction/results.json")
WORDS = tuple(product(range(3), repeat=3))
WORD_INDEX = {word: index for index, word in enumerate(WORDS)}
BASE = tuple(index for index, word in enumerate(WORDS) if 2 not in word)
NEW = tuple(index for index, word in enumerate(WORDS) if 2 in word)
QUERY_ROWS = qary_prefix_query_library(3, 3, copies=4)
QUERY_COSTS = qary_prefix_query_costs(3, 3, copies=4, level_costs=(1, 3, 1))
EXPECTED_OBSTRUCTION_WORDS = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
EXPECTED_PAIRS = set(combinations(EXPECTED_OBSTRUCTION_WORDS, 2))


def all_games():
    count = len(WORDS)
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


GAMES = all_games()


def solve(indices, budget):
    games = tuple(GAMES[index] for index in indices)
    rows = tuple(tuple(row[index] for index in indices) for row in QUERY_ROWS)
    try:
        plan = plan_adaptive_decision_queries_with_weighted_faults(
            games,
            rows,
            query_costs=QUERY_COSTS,
            corruption_budget=1,
            erasure_budget=1,
            allowed_initial_query_indices=range(4, 16),
            known_feasible_cost_upper_bound=budget,
        )
    except ValueError:
        return {"feasible": False, "exact_cost": None, "states_solved": None}
    return {
        "feasible": True,
        "exact_cost": plan.worst_case_cost,
        "states_solved": plan.states_solved,
    }


def permute_word(word, permutation):
    return tuple(permutation[symbol] for symbol in word)


def main():
    baseline = solve(BASE, 17)
    singletons = []
    for index in NEW:
        result = solve((*BASE, index), 17)
        singletons.append({"word": list(WORDS[index]), "budget_17": result})

    pairs = []
    obstruction_pairs = []
    for left, right in combinations(NEW, 2):
        at_17 = solve((*BASE, left, right), 17)
        at_18 = None
        if not at_17["feasible"]:
            at_18 = solve((*BASE, left, right), 18)
            obstruction_pairs.append((WORDS[left], WORDS[right]))
        pairs.append(
            {
                "words": [list(WORDS[left]), list(WORDS[right])],
                "budget_17": at_17,
                "budget_18": at_18,
            }
        )

    symmetry_checks = []
    for pair in obstruction_pairs:
        for permutation in permutations(range(3)):
            base_words = tuple(permute_word(WORDS[index], permutation) for index in BASE)
            pair_words = tuple(permute_word(word, permutation) for word in pair)
            indices = tuple(
                sorted(WORD_INDEX[word] for word in (*base_words, *pair_words))
            )
            symmetry_checks.append(
                {
                    "source_pair": [list(word) for word in pair],
                    "permutation": list(permutation),
                    "fixes_distinguished_zero": permutation[0] == 0,
                    "permuted_pair": [list(word) for word in pair_words],
                    "budget_17": solve(indices, 17),
                    "budget_18": solve(indices, 18),
                }
            )

    found = set(obstruction_pairs)
    summary = {
        "baseline_exact_cost": baseline["exact_cost"],
        "singleton_total": len(singletons),
        "singleton_budget_17_feasible": sum(
            row["budget_17"]["feasible"] for row in singletons
        ),
        "pair_total": len(pairs),
        "pair_budget_17_infeasible": len(obstruction_pairs),
        "pair_budget_18_feasible": sum(
            row["budget_18"] is not None and row["budget_18"]["feasible"]
            for row in pairs
        ),
        "symmetry_check_total": len(symmetry_checks),
        "symmetry_checks_obstructing": sum(
            not row["budget_17"]["feasible"]
            and row["budget_18"]["feasible"]
            and row["budget_18"]["exact_cost"] == 18
            for row in symmetry_checks
        ),
        "zero_fixing_check_total": sum(
            row["fixes_distinguished_zero"] for row in symmetry_checks
        ),
        "zero_fixing_checks_obstructing": sum(
            row["fixes_distinguished_zero"]
            and not row["budget_17"]["feasible"]
            and row["budget_18"]["exact_cost"] == 18
            for row in symmetry_checks
        ),
        "zero_moving_check_total": sum(
            not row["fixes_distinguished_zero"] for row in symmetry_checks
        ),
        "zero_moving_checks_budget_17_feasible": sum(
            not row["fixes_distinguished_zero"]
            and row["budget_17"]["feasible"]
            for row in symmetry_checks
        ),
    }
    summary["passed"] = (
        baseline["feasible"]
        and baseline["exact_cost"] == 17
        and summary["singleton_budget_17_feasible"]
        == summary["singleton_total"]
        == 19
        and summary["pair_total"] == 171
        and summary["pair_budget_17_infeasible"]
        == summary["pair_budget_18_feasible"]
        == 3
        and found == EXPECTED_PAIRS
        and summary["symmetry_check_total"] == 18
        and summary["symmetry_checks_obstructing"] == 6
        and summary["zero_fixing_checks_obstructing"]
        == summary["zero_fixing_check_total"]
        == 6
        and summary["zero_moving_checks_budget_17_feasible"]
        == summary["zero_moving_check_total"]
        == 12
    )
    result = {
        "schema": "theorica.ternary-single-word-obstruction/1",
        "level_costs": [1, 3, 1],
        "binary_baseline_words": [list(WORDS[index]) for index in BASE],
        "baseline_budget_17": baseline,
        "singletons": singletons,
        "pairs": pairs,
        "obstruction_pairs": [[list(word) for word in pair] for pair in obstruction_pairs],
        "symmetry_checks": symmetry_checks,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
