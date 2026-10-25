#!/usr/bin/env python3
"""Exact adversarial verification of the pre-query finite-list selector."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    _feature_code_minimum_distance,
    certify_two_action_plan_from_ambiguous_transcript,
    select_finite_list_feature_queries,
)
from theorica.agents.robust_provenance import _fraction_matrix_rank

OUT = Path("results/finite_list_error_erasure_selector/results.json")


def vandermonde(rank, count, offset):
    return tuple(
        tuple(Fraction(offset + row) ** degree for degree in range(rank))
        for row in range(count)
    )


def cauchy(rank, count, offset):
    return tuple(
        tuple(Fraction(1, offset + row + 3 * column + 1) for column in range(rank))
        for row in range(count)
    )


def positive(case, family, rank, errors, erasures):
    count = rank + errors + erasures
    rows = (vandermonde if family == "vandermonde" else cauchy)(
        rank, count, 5 + 11 * case
    )
    plan = select_finite_list_feature_queries(
        rows,
        payoff_in_feature_span_certified=True,
        corruption_budget=errors,
        erasure_budget=erasures,
    )
    selected_rows = tuple(rows[index] for index in plan.query_indices)
    punctures = 0
    transcript_checks = 0
    for erased_count in range(erasures + 1):
        for erased in combinations(range(count), erased_count):
            punctures += 1
            available_rows = tuple(
                row for position, row in enumerate(selected_rows)
                if position not in erased
            )
            assert _feature_code_minimum_distance(available_rows, rank) >= errors + 1
            observed = tuple(None if position in erased else (0, 0)
                             for position in range(count))
            result = certify_two_action_plan_from_ambiguous_transcript(
                rows,
                plan.query_indices,
                observed,
                payoff_in_feature_span_certified=True,
                corruption_budget=errors,
                erasure_budget=erasures,
            )
            transcript_checks += int(result.certificate_valid)
    deletion_safe = all(
        _fraction_matrix_rank(
            tuple(row for position, row in enumerate(selected_rows)
                  if position not in deleted)
        ) == rank
        for deleted in combinations(range(count), errors + erasures)
    )
    passed = (
        plan.query_count == count
        and plan.minimum_distance == errors + erasures + 1
        and deletion_safe
        and transcript_checks == punctures
    )
    return {
        "case": case,
        "family": family,
        "rank": rank,
        "errors": errors,
        "erasures": erasures,
        "queries": count,
        "minimum_distance": plan.minimum_distance,
        "erasure_patterns": punctures,
        "transcript_checks": transcript_checks,
        "saved_vs_unique": errors,
        "passed": passed,
    }


def degenerate(case, rank, errors, erasures):
    repeated = [(1,) + (0,) * (rank - 1)] * (1 + errors + erasures)
    rows = tuple(repeated + [tuple(int(i == column) for i in range(rank))
                             for column in range(1, rank)])
    rejected = False
    try:
        select_finite_list_feature_queries(
            rows,
            payoff_in_feature_span_certified=True,
            corruption_budget=errors,
            erasure_budget=erasures,
            max_query_count=len(rows),
        )
    except ValueError as exc:
        rejected = "no query subset" in str(exc)
    witness = next(
        deleted
        for deleted in combinations(range(len(rows)), errors + erasures)
        if _fraction_matrix_rank(
            tuple(row for position, row in enumerate(rows) if position not in deleted)
        ) < rank
    )
    return {
        "case": case,
        "rank": rank,
        "errors": errors,
        "erasures": erasures,
        "queries": len(rows),
        "rank_drop_witness": witness,
        "rejected_before_transcript": rejected,
        "passed": rejected,
    }


def main():
    positives = []
    case = 0
    for family in ("vandermonde", "cauchy"):
        for rank in (2, 3):
            for errors in (1, 2):
                for erasures in (1, 2):
                    for _ in range(5):
                        positives.append(positive(case, family, rank, errors, erasures))
                        case += 1
    attacks = []
    for case in range(60):
        rank = 2 + (case % 2)
        errors = 1 + ((case // 2) % 2)
        erasures = 1 + ((case // 4) % 2)
        attacks.append(degenerate(case, rank, errors, erasures))
    transcript = positives + attacks
    canonical = json.dumps(transcript, sort_keys=True, separators=(",", ":"))
    summary = {
        "positive_cases_passed": sum(row["passed"] for row in positives),
        "positive_case_total": len(positives),
        "cauchy_holdouts_passed": sum(
            row["passed"] for row in positives if row["family"] == "cauchy"
        ),
        "cauchy_holdout_total": sum(
            row["family"] == "cauchy" for row in positives
        ),
        "erasure_patterns_exhausted": sum(row["erasure_patterns"] for row in positives),
        "transcript_checks_passed": sum(row["transcript_checks"] for row in positives),
        "degenerate_attacks_rejected": sum(row["passed"] for row in attacks),
        "degenerate_attack_total": len(attacks),
        "queries_saved_vs_unique": sum(row["saved_vs_unique"] for row in positives),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in transcript),
    }
    result = {
        "schema": "theorica.finite-list-error-erasure-selector/1",
        "summary": summary,
        "cases": transcript,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
