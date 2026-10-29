#!/usr/bin/env python3
"""Exact adversarial verification of the finite-list geometry boundary."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    _feature_code_minimum_distance,
    certify_two_action_plan_from_ambiguous_transcript,
)
from theorica.agents.robust_provenance import _fraction_matrix_rank

OUT = Path("results/finite_list_geometry_boundary/results.json")


def vandermonde(rank, count):
    return tuple(
        tuple(Fraction(x) ** degree for degree in range(rank)) for x in range(count)
    )


def positive(case, rank, errors):
    features = vandermonde(rank, rank + errors)
    shift = Fraction(2 * case - 31, 7)
    delta = Fraction(case + 1, 13)
    observations = tuple((shift, shift) for _ in features[:-1]) + (
        (shift, shift + delta),
    )
    result = certify_two_action_plan_from_ambiguous_transcript(
        features,
        range(len(features)),
        observations,
        payoff_in_feature_span_certified=True,
        corruption_budget=errors,
    )
    exhaustive = all(
        _fraction_matrix_rank(
            tuple(row for index, row in enumerate(features) if index not in deleted)
        ) == rank
        for deleted in combinations(range(len(features)), errors)
    )
    return {
        "case": case,
        "rank": rank,
        "errors": errors,
        "queries": len(features),
        "unique_decoding_queries": rank + 2 * errors,
        "version_space_size": result.version_space_size,
        "minimum_distance": result.finite_list_minimum_distance,
        "saved_queries": errors,
        "passed": (
            exhaustive
            and result.finite_list_minimum_distance == errors + 1
            and result.policy_identifiable
            and not result.model_identifiable
            and result.minimax_value == shift
            and result.action_probabilities == (1, 0)
        ),
    }


def degenerate(case, rank, errors):
    if rank == 2:
        features = tuple([(1, 0)] * (1 + errors) + [(0, 1)])
    else:
        features = tuple([(1, 0, 0)] * (1 + errors) + [(0, 1, 0), (0, 0, 1)])
    observations = tuple((Fraction(case), Fraction(case)) for _ in features)
    distance = _feature_code_minimum_distance(features, rank)
    rejected = False
    try:
        certify_two_action_plan_from_ambiguous_transcript(
            features,
            range(len(features)),
            observations,
            payoff_in_feature_span_certified=True,
            corruption_budget=errors,
        )
    except ValueError as exc:
        rejected = "finite completion list" in str(exc)
    witness = next(
        deleted
        for deleted in combinations(range(len(features)), errors)
        if _fraction_matrix_rank(
            tuple(row for index, row in enumerate(features) if index not in deleted)
        ) < rank
    )
    return {
        "case": case,
        "rank": rank,
        "errors": errors,
        "queries": len(features),
        "minimum_distance": distance,
        "rank_drop_witness": witness,
        "rejected_before_enumeration": rejected,
        "passed": distance < errors + 1 and rejected,
    }


def main():
    prior = [positive(case, 2, 1) for case in range(40)] + [
        positive(100 + case, 3, 1) for case in range(20)
    ]
    new = [positive(200 + case, 2, 2) for case in range(20)] + [
        positive(300 + case, 3, 2) for case in range(20)
    ]
    attacks = [degenerate(case, 2, 1) for case in range(20)]
    attacks += [degenerate(100 + case, 2, 2) for case in range(20)]
    attacks += [degenerate(200 + case, 3, 1) for case in range(20)]
    transcript = prior + new + attacks
    canonical = json.dumps(transcript, default=str, sort_keys=True, separators=(",", ":"))
    summary = {
        "prior_positive_passed": sum(row["passed"] for row in prior),
        "prior_positive_total": len(prior),
        "new_mds_positive_passed": sum(row["passed"] for row in new),
        "new_mds_positive_total": len(new),
        "degenerate_attacks_rejected": sum(row["passed"] for row in attacks),
        "degenerate_attack_total": len(attacks),
        "queries_saved_vs_unique": sum(row["saved_queries"] for row in prior + new),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in transcript),
    }
    result = {"schema": "theorica.finite-list-geometry-boundary/1",
              "summary": summary, "cases": transcript}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
