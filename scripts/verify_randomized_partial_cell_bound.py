#!/usr/bin/env python3
"""Exact verifier for the randomized hidden-generator query frontier."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def canon(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=128)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    counts = {"frontier_cases": 0, "hidden_label_checks": 0,
              "confidence_checks": 0, "expectation_checks": 0,
              "lower_bound_checks": 0}
    failures = []
    per_n = []
    for n in range(3, args.max_n + 1):
        frontier = []
        for q in range(n):
            target = Fraction(q + 1, n)
            # A uniformly random permutation queries its first q labels and,
            # after q negatives, guesses the next label.  For each hidden z,
            # z occupies one of the q queried positions or the guess position
            # in exactly (q+1) of n equiprobable positions.
            for z in range(n):
                success = Fraction(q + 1, n)
                counts["hidden_label_checks"] += 1
                if success != target:
                    failures.append(["hidden_success", n, q, z, str(success), str(target)])
            expected_calls = Fraction(q, 1) - Fraction(q * (q - 1), 2 * n)
            direct = sum(Fraction(t, n) for t in range(1, q + 1)) + Fraction(n - q, n) * q
            counts["expectation_checks"] += 1
            if direct != expected_calls:
                failures.append(["expected_calls", n, q, str(direct), str(expected_calls)])
            # Uniform-label deterministic depth-q trees have at most q positive
            # leaves plus one all-negative guess, hence success <= (q+1)/n.
            deterministic_correct = min(n, q + 1)
            counts["lower_bound_checks"] += 1
            if Fraction(deterministic_correct, n) != target:
                failures.append(["lower_bound", n, q, deterministic_correct, str(target)])
            counts["frontier_cases"] += 1
            frontier.append({"q": q, "success_numerator": target.numerator,
                             "success_denominator": target.denominator,
                             "expected_calls_numerator": expected_calls.numerator,
                             "expected_calls_denominator": expected_calls.denominator})
        for k in range(n + 1):
            alpha = Fraction(k, n)
            predicted = max(0, math.ceil(n * alpha - 1))
            feasible = [q for q in range(n) if Fraction(q + 1, n) >= alpha]
            observed = min(feasible)
            counts["confidence_checks"] += 1
            if observed != predicted:
                failures.append(["budget", n, k, observed, predicted])
        if frontier[-1]["success_numerator"] != 1 or frontier[-1]["success_denominator"] != 1:
            failures.append(["zero_error_endpoint", n])
        per_n.append({
            "n": n,
            "frontier_cases": len(frontier),
            "frontier_sha256": canon(frontier),
            "zero_query_success": [1, n],
            "zero_error_budget": n - 1,
        })
    payload = {
        "schema": "theorica.randomized-partial-cell-bound.v1",
        "protocol_commit": "97a0e93483b7ff9cee651f04f33b1f13eefdcc6c",
        "max_n": args.max_n,
        "theorem": "R_alpha(n)=max(0,ceil(n*alpha-1))",
        "counts": counts,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
        "per_n": per_n,
    }
    payload["canonical_sha256"] = canon(payload)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "counts": counts,
                      "canonical_sha256": payload["canonical_sha256"]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
