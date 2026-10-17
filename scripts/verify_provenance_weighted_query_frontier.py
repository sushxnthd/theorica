#!/usr/bin/env python3
"""Primary exact certificate for the provenance-weighted query frontier."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from theorica.agents.rack_seed_acquisition import (
    locate_hidden_generator_with_provenance,
    provenance_weighted_query_budget,
)


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def hidden_cycle(n: int, z: int) -> np.ndarray:
    table = np.tile(np.arange(n), (n, 1))
    others = [label for label in range(n) if label != z]
    for index, label in enumerate(others):
        table[z, label] = others[(index + 1) % len(others)]
    return table


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=8)
    parser.add_argument("--max-weight", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    failures = []
    counts = {"prior_vectors": 0, "frontier_cases": 0, "hidden_label_runs": 0,
              "policy_subsets": 0, "budget_inversions": 0}
    summaries = []
    for n in range(3, args.max_n + 1):
        n_counts = {key: 0 for key in counts}
        for weights in itertools.product(range(1, args.max_weight + 1), repeat=n):
            counts["prior_vectors"] += 1
            n_counts["prior_vectors"] += 1
            total = sum(weights)
            ranked = sorted(weights, reverse=True)
            for q in range(n):
                target = Fraction(sum(ranked[: q + 1]), total)
                best = Fraction(0, 1)
                for subset in itertools.combinations(range(n), q + 1):
                    best = max(best, Fraction(sum(weights[label] for label in subset), total))
                    counts["policy_subsets"] += 1
                    n_counts["policy_subsets"] += 1
                if best != target:
                    failures.append(["exhaustive_policy", n, list(weights), q, str(best), str(target)])
                achieved = 0
                for hidden in range(n):
                    table = hidden_cycle(n, hidden)
                    result = locate_hidden_generator_with_provenance(
                        lambda x, y, table=table: int(table[x, y]), n,
                        family_certified=True, provenance_certified=True,
                        prior_weights=weights, query_budget=q,
                        allow_bounded_error=q < n - 1,
                    )
                    achieved += weights[hidden] * int(result.distinguished_row == hidden)
                    counts["hidden_label_runs"] += 1
                    n_counts["hidden_label_runs"] += 1
                    if (result.success_numerator, result.success_denominator) != (target.numerator, target.denominator):
                        failures.append(["receipt", n, list(weights), q, hidden])
                if Fraction(achieved, total) != target:
                    failures.append(["production_attainment", n, list(weights), q, achieved, str(target)])
                counts["frontier_cases"] += 1
                n_counts["frontier_cases"] += 1
            cumulative = 0
            for count, weight in enumerate(ranked, start=1):
                cumulative += weight
                target = Fraction(cumulative, total)
                observed = provenance_weighted_query_budget(
                    weights, minimum_success_numerator=target.numerator,
                    minimum_success_denominator=target.denominator,
                )
                if observed > count - 1 or Fraction(sum(ranked[: observed + 1]), total) < target:
                    failures.append(["budget", n, list(weights), count, observed])
                counts["budget_inversions"] += 1
                n_counts["budget_inversions"] += 1
        summaries.append({"n": n, **n_counts})
    payload = {
        "schema": "theorica.provenance-weighted-query-frontier.v1",
        "protocol_commit": "567255ce8cfcad6adecebffe15b9a36a633fefa5",
        "max_n": args.max_n,
        "max_weight": args.max_weight,
        "theorem": "P*(pi,q)=sum_of_largest_(q+1)_prior_masses",
        "counts": counts,
        "per_n": summaries,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    payload["canonical_sha256"] = canonical(payload)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "counts": counts,
                      "canonical_sha256": payload["canonical_sha256"]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
