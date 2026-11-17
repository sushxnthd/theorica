#!/usr/bin/env python3
"""Frozen exact experiment for corruption-resilient feature queries."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    reconstruct_corruption_resilient_feature_payoffs,
)
from theorica.agents.robust_provenance import (
    reconstruct_feature_span_scenario_payoffs,
    solve_two_action_robust_game,
)

SEED = 202610250234
HOLDOUT_SEEDS = tuple(2_500_019 + 7_919 * index for index in range(30))
HOLDOUT_COUNTS = (17, 29, 47, 71, 97)
OUT = Path("results/corruption_resilient_feature_queries/primary.json")


def vandermonde_rows(rank, count, offset):
    xs = tuple(Fraction(3 * index - count + offset, count + 7)
               for index in range(count))
    return tuple(tuple(x ** power for power in range(rank)) for x in xs)


def make_table(rank, rows, seed):
    rng = random.Random(seed)
    actions = []
    for _ in range(2):
        coefficients = tuple(Fraction(rng.randint(-7, 7))
                             for _ in range(rank))
        actions.append(tuple(sum(
            (coefficient * feature for coefficient, feature
             in zip(coefficients, row)), Fraction(0)
        ) for row in rows))
    return (tuple(actions),)


def route(rank, table):
    del rank
    return solve_two_action_robust_game(table[0])


def evaluate(rank, corruption_budget, count, seed):
    rows = vandermonde_rows(rank, count, seed % 11)
    table = make_table(rank, rows, seed)
    corrupt = set(range(corruption_budget))
    calls = []

    def oracle(index):
        calls.append(index)
        return tuple(tuple(
            action[index] + (
                Fraction((component + 2) * (action_index + 3) * (index + 5), 7)
                if index in corrupt else Fraction(0)
            )
            for action_index, action in enumerate(component_actions)
        ) for component, component_actions in enumerate(table))

    result = reconstruct_corruption_resilient_feature_payoffs(
        rows,
        oracle,
        payoff_in_feature_span_certified=True,
        corruption_budget=corruption_budget,
    )
    expected = route(rank, table)
    observed = route(rank, result.component_payoff_vectors)
    passed = (
        result.certificate_valid
        and result.query_count == rank + 2 * corruption_budget
        and result.minimum_distance == 2 * corruption_budget + 1
        and calls == list(result.query_indices)
        and set(result.corrected_query_indices) == corrupt
        and result.component_payoff_vectors == table
        and expected.certificate_valid
        and observed.certificate_valid
        and expected.minimax_value == observed.minimax_value
        and expected.action_probabilities == observed.action_probabilities
    )
    return {
        "rank": rank,
        "corruption_budget": corruption_budget,
        "scenario_count": count,
        "seed": seed,
        "query_indices": list(result.query_indices),
        "query_count": result.query_count,
        "minimum_distance": result.minimum_distance,
        "corrected_query_indices": list(result.corrected_query_indices),
        "repetition_baseline_queries": rank * (2 * corruption_budget + 1),
        "query_saving": rank * (2 * corruption_budget + 1) - result.query_count,
        "minimax_value": str(observed.minimax_value),
        "passed": passed,
    }


def rank_only_false_accept(rank, offset):
    rows = vandermonde_rows(rank, rank, offset)
    values = tuple(sum(row, Fraction(0)) for row in rows)
    calls = []

    def oracle(index):
        calls.append(index)
        return ((values[index] + (17 if index == 0 else 0),),)

    result = reconstruct_feature_span_scenario_payoffs(
        rows, oracle, payoff_in_feature_span_certified=True)
    return {
        "rank": rank,
        "query_count": result.query_count,
        "certificate_valid": result.certificate_valid,
        "wrong_table_accepted": result.component_payoff_vectors != ((values,),),
        "passed": (
            result.certificate_valid
            and result.component_payoff_vectors != ((values,),)
            and len(calls) == rank
        ),
    }


def degenerate_geometry():
    rows = ((1, 0),) * 3 + ((0, 1),) * 3
    values = (Fraction(2),) * 3 + (Fraction(-1),) * 3
    calls = []

    def oracle(index):
        calls.append(index)
        return ((values[index] + (9 if index == 0 else 0),),)

    result = reconstruct_corruption_resilient_feature_payoffs(
        rows,
        oracle,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
        max_query_count=6,
    )
    impossible_calls = []
    impossible_rejected = False
    try:
        reconstruct_corruption_resilient_feature_payoffs(
            rows[:-1],
            lambda index: impossible_calls.append(index),
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
            max_query_count=5,
        )
    except ValueError as exc:
        impossible_rejected = "no query subset" in str(exc)
    return {
        "rank": result.feature_rank,
        "corruption_budget": 1,
        "singleton_lower_bound": 4,
        "optimal_query_count": result.query_count,
        "minimum_distance": result.minimum_distance,
        "reconstructed": result.component_payoff_vectors == ((values,),),
        "impossible_smaller_geometry_rejected": impossible_rejected,
        "impossible_oracle_calls": len(impossible_calls),
        "passed": (
            result.query_count == 6
            and result.minimum_distance == 3
            and result.component_payoff_vectors == ((values,),)
            and impossible_rejected
            and not impossible_calls
            and calls == list(result.query_indices)
        ),
    }


def lower_bound(rank, corruption_budget, offset):
    count = rank + 2 * corruption_budget - 1
    xs = tuple(Fraction(index + offset, count + 3) for index in range(count))
    roots = xs[:rank - 1]
    alternative = tuple(-prod(tuple(x - root for root in roots)) for x in xs)
    support = tuple(index for index, value in enumerate(alternative) if value)
    left_corrupt = set(support[:corruption_budget])
    right_corrupt = set(support[corruption_budget:])
    received_from_zero = tuple(
        alternative[index] if index in left_corrupt else Fraction(0)
        for index in range(count)
    )
    received_from_alternative = tuple(
        Fraction(0) if index in right_corrupt else alternative[index]
        for index in range(count)
    )
    return {
        "rank": rank,
        "corruption_budget": corruption_budget,
        "query_count": count,
        "codeword_weight": len(support),
        "transcripts_equal": received_from_zero == received_from_alternative,
        "zero_corruptions": len(left_corrupt),
        "alternative_corruptions": len(right_corrupt),
        "tables_differ": any(alternative),
        "robust_values_differ": min(alternative) != 0,
        "passed": (
            len(support) == 2 * corruption_budget
            and received_from_zero == received_from_alternative
            and len(left_corrupt) == len(right_corrupt) == corruption_budget
            and min(alternative) != 0
        ),
    }


def prod(values):
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def main():
    opened = []
    for rank in (2, 3, 4):
        for corruption_budget in (1, 2):
            for index in range(20):
                opened.append(evaluate(
                    rank,
                    corruption_budget,
                    11 + index,
                    SEED + 10_000 * rank + 1_000 * corruption_budget + index,
                ))
    holdout = []
    for index, seed in enumerate(HOLDOUT_SEEDS):
        rank = 2 + index % 3
        corruption_budget = 1 + (index // 3) % 2
        holdout.append(evaluate(
            rank, corruption_budget, HOLDOUT_COUNTS[index % 5], seed))
    rank_baseline = [rank_only_false_accept(2 + index % 3, index)
                     for index in range(60)]
    lower_bounds = [lower_bound(2 + index % 3, 1 + (index // 3) % 2, index)
                    for index in range(60)]
    degenerate = degenerate_geometry()
    payload = {
        "schema": "theorica.corruption-resilient-feature-queries/1",
        "seed": SEED,
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "opened": opened,
        "holdout": holdout,
        "rank_only_baseline": rank_baseline,
        "lower_bounds": lower_bounds,
        "degenerate_geometry": degenerate,
    }
    payload["summary"] = {
        "opened_passed": sum(item["passed"] for item in opened),
        "opened_total": len(opened),
        "holdout_passed": sum(item["passed"] for item in holdout),
        "holdout_total": len(holdout),
        "rank_only_false_accepts": sum(item["passed"] for item in rank_baseline),
        "lower_bounds_passed": sum(item["passed"] for item in lower_bounds),
        "strict_query_savings": sum(item["query_saving"] > 0
                                    for item in opened + holdout),
        "degenerate_boundary_passed": degenerate["passed"],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    payload["passed"] = (
        all(item["passed"] for item in opened + holdout + rank_baseline + lower_bounds)
        and degenerate["passed"]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**payload["summary"], "digest": payload["digest"],
                      "passed": payload["passed"]}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
