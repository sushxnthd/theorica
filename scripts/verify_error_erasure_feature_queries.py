#!/usr/bin/env python3
"""Frozen exact experiment for joint error-erasure feature queries."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    reconstruct_corruption_resilient_feature_payoffs,
)
from theorica.agents.robust_provenance import solve_two_action_robust_game

SEED = 202610250453
HOLDOUT_SEEDS = tuple(3_100_019 + 10_007 * index for index in range(30))
HOLDOUT_COUNTS = (17, 29, 47, 71, 97)
OUT = Path("results/error_erasure_feature_queries/primary.json")


def rows_for(family, rank, count, offset):
    xs = tuple(Fraction(3 * index - count + offset, count + 11)
               for index in range(count))
    if family == "vandermonde":
        return tuple(tuple(x ** power for power in range(rank)) for x in xs)
    if family == "cauchy":
        return tuple(tuple(Fraction(1, x - (column + count + 3))
                                    for column in range(rank)) for x in xs)
    raise ValueError(f"unknown family: {family}")


def make_table(rows, seed):
    rng = random.Random(seed)
    actions = []
    for _ in range(2):
        coefficients = tuple(Fraction(rng.randint(-9, 9))
                             for _ in range(len(rows[0])))
        actions.append(tuple(sum(
            (coefficient * feature for coefficient, feature
             in zip(coefficients, row)), Fraction(0)
        ) for row in rows))
    return (tuple(actions),)


def evaluate(family, rank, errors, erasures, count, seed):
    rows = rows_for(family, rank, count, seed % 13)
    table = make_table(rows, seed)
    erased = set(range(erasures))
    corrupted = set(range(erasures, erasures + errors))
    calls = []

    def oracle(index):
        calls.append(index)
        if index in erased:
            return None
        return tuple(tuple(
            action[index] + (
                Fraction((component + 2) * (action_index + 3) * (index + 5), 11)
                if index in corrupted else Fraction(0)
            )
            for action_index, action in enumerate(component_actions)
        ) for component, component_actions in enumerate(table))

    result = reconstruct_corruption_resilient_feature_payoffs(
        rows, oracle, payoff_in_feature_span_certified=True,
        corruption_budget=errors, erasure_budget=erasures,
    )
    expected = solve_two_action_robust_game(table[0])
    observed = solve_two_action_robust_game(result.component_payoff_vectors[0])
    query_target = rank + 2 * errors + erasures
    passed = (
        result.certificate_valid
        and result.query_count == query_target
        and result.minimum_distance == 2 * errors + erasures + 1
        and result.erased_query_indices == tuple(sorted(erased))
        and result.corrected_query_indices == tuple(sorted(corrupted))
        and result.component_payoff_vectors == table
        and calls == list(result.query_indices)
        and expected.minimax_value == observed.minimax_value
        and expected.action_probabilities == observed.action_probabilities
    )
    return {
        "family": family, "rank": rank, "error_budget": errors,
        "erasure_budget": erasures, "scenario_count": count, "seed": seed,
        "query_indices": list(result.query_indices),
        "query_count": result.query_count,
        "minimum_distance": result.minimum_distance,
        "corrected_query_indices": list(result.corrected_query_indices),
        "erased_query_indices": list(result.erased_query_indices),
        "treat_erasures_as_errors_queries": rank + 2 * (errors + erasures),
        "repeated_basis_queries": rank * (2 * errors + erasures + 1),
        "minimax_value": str(observed.minimax_value),
        "passed": passed,
    }


def product(values):
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def lower_bound(rank, errors, erasures, offset):
    count = rank + 2 * errors + erasures - 1
    xs = tuple(Fraction(index + offset + 1, count + 5) for index in range(count))
    roots = xs[:rank - 1]
    alternative = tuple(-product(tuple(x - root for root in roots)) for x in xs)
    support = tuple(index for index, value in enumerate(alternative) if value)
    erased = set(support[:erasures])
    remaining = tuple(index for index in support if index not in erased)
    left_errors = set(remaining[:errors])
    right_errors = set(remaining[errors:])
    visible = tuple(index for index in range(count) if index not in erased)
    from_zero = tuple(
        alternative[index] if index in left_errors else Fraction(0)
        for index in visible
    )
    from_alternative = tuple(
        Fraction(0) if index in right_errors else alternative[index]
        for index in visible
    )
    passed = (
        len(support) == 2 * errors + erasures
        and len(erased) == erasures
        and len(left_errors) == len(right_errors) == errors
        and from_zero == from_alternative
        and min(alternative) != 0
    )
    return {
        "rank": rank, "error_budget": errors, "erasure_budget": erasures,
        "offset": offset,
        "query_count": count, "codeword_weight": len(support),
        "transcripts_equal_after_erasures": from_zero == from_alternative,
        "left_errors": len(left_errors), "right_errors": len(right_errors),
        "erasures": len(erased), "robust_values_differ": min(alternative) != 0,
        "passed": passed,
    }


def error_only_baseline_attack(rank, errors, erasures, offset):
    count = rank + 2 * errors
    xs = tuple(Fraction(index + offset + 2, count + 7) for index in range(count))
    roots = xs[:rank - 1]
    word = tuple(-product(tuple(x - root for root in roots)) for x in xs)
    support = tuple(index for index, value in enumerate(word) if value)
    erased = set(support[:erasures])
    remaining = tuple(index for index in support if index not in erased)
    left = set(remaining[:errors])
    right = set(remaining[errors:])
    visible = tuple(index for index in range(count) if index not in erased)
    a = tuple(word[index] if index in left else Fraction(0) for index in visible)
    b = tuple(Fraction(0) if index in right else word[index] for index in visible)
    false_accept = a == b and len(left) <= errors and len(right) <= errors
    return {"rank": rank, "error_budget": errors, "erasure_budget": erasures,
            "offset": offset,
            "error_only_queries": count, "false_accept": false_accept,
            "passed": false_accept}


def degenerate_geometry():
    rows = ((1, 0),) * 4 + ((0, 1),) * 4
    values = (Fraction(2),) * 4 + (Fraction(-1),) * 4

    def oracle(index):
        if index == 0:
            return None
        return ((values[index] + (9 if index == 1 else 0),),)

    result = reconstruct_corruption_resilient_feature_payoffs(
        rows, oracle, payoff_in_feature_span_certified=True,
        corruption_budget=1, erasure_budget=1, max_query_count=8,
    )
    calls = []
    rejected = False
    try:
        reconstruct_corruption_resilient_feature_payoffs(
            rows[:-1], lambda index: calls.append(index),
            payoff_in_feature_span_certified=True,
            corruption_budget=1, erasure_budget=1, max_query_count=7,
        )
    except ValueError as exc:
        rejected = "no query subset" in str(exc)
    return {
        "singleton_lower_bound": 5, "optimal_query_count": result.query_count,
        "minimum_distance": result.minimum_distance,
        "reconstructed": result.component_payoff_vectors == ((values,),),
        "insufficient_geometry_rejected": rejected,
        "oracle_calls_before_rejection": len(calls),
        "passed": result.query_count == 8 and result.minimum_distance == 4
        and result.component_payoff_vectors == ((values,),)
        and rejected and not calls,
    }


def main():
    opened = []
    case = 0
    for rank in (2, 3, 4):
        for errors, erasures in ((0, 1), (1, 1), (1, 2), (2, 1)):
            for index in range(10):
                opened.append(evaluate(
                    "vandermonde", rank, errors, erasures, 11 + index,
                    SEED + 10_000 * rank + 1_000 * case + index,
                ))
            case += 1
    holdout = []
    for index, seed in enumerate(HOLDOUT_SEEDS):
        rank = 2 + index % 3
        errors, erasures = ((0, 1), (1, 1), (1, 2), (2, 1))[index % 4]
        holdout.append(evaluate(
            "cauchy", rank, errors, erasures,
            HOLDOUT_COUNTS[index % len(HOLDOUT_COUNTS)], seed,
        ))
    lower_bounds = [lower_bound(2 + i % 3, 1 + (i // 3) % 2, 1 + i % 2, i)
                    for i in range(60)]
    baselines = [error_only_baseline_attack(2 + i % 3, 1, 1, i)
                 for i in range(60)]
    degenerate = degenerate_geometry()
    payload = {
        "schema": "theorica.error-erasure-feature-queries/1",
        "seed": SEED, "holdout_seeds": list(HOLDOUT_SEEDS),
        "opened": opened, "holdout": holdout,
        "lower_bounds": lower_bounds,
        "error_only_baseline": baselines,
        "degenerate_geometry": degenerate,
    }
    payload["summary"] = {
        "opened_passed": sum(item["passed"] for item in opened),
        "opened_total": len(opened),
        "holdout_passed": sum(item["passed"] for item in holdout),
        "holdout_total": len(holdout),
        "lower_bounds_passed": sum(item["passed"] for item in lower_bounds),
        "error_only_false_accepts": sum(item["passed"] for item in baselines),
        "erasure_aware_savings": sum(
            item["treat_erasures_as_errors_queries"] - item["query_count"]
            for item in opened + holdout
        ),
        "degenerate_boundary_passed": degenerate["passed"],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    payload["passed"] = all(
        item["passed"] for item in opened + holdout + lower_bounds + baselines
    ) and degenerate["passed"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**payload["summary"], "digest": payload["digest"],
                      "passed": payload["passed"]}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
