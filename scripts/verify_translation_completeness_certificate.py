#!/usr/bin/env python3
"""Exhaust the sharp zero-error completeness-certificate boundary."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    by_n = {}
    counterexamples = []
    for n in range(2, args.max_n + 1):
        identity = tuple(range(n))
        permutations = tuple(itertools.permutations(range(n)))
        ambiguous_subsets = 0
        ambiguity_failures = 0
        uniqueness_failures = 0
        agreeing_outside_total = 0
        for size in range(n - 1):
            for queried in itertools.combinations(range(n), size):
                matches = [
                    permutation for permutation in permutations
                    if permutation != identity
                    and all(permutation[index] == index for index in queried)
                ]
                ambiguous_subsets += 1
                agreeing_outside_total += len(matches)
                if not matches:
                    ambiguity_failures += 1
                    if len(counterexamples) < 10:
                        counterexamples.append({"n": n, "queried": queried, "kind": "no_outside_match"})
        for queried in itertools.combinations(range(n), n - 1):
            matches = [
                permutation for permutation in permutations
                if all(permutation[index] == index for index in queried)
            ]
            if matches != [identity]:
                uniqueness_failures += 1
                if len(counterexamples) < 10:
                    counterexamples.append({"n": n, "queried": queried, "matches": matches[:3], "kind": "not_unique"})
        by_n[str(n)] = {
            "permutations": math.factorial(n),
            "ambiguous_coordinate_subsets": ambiguous_subsets,
            "agreeing_outside_permutations_total": agreeing_outside_total,
            "ambiguity_failures": ambiguity_failures,
            "n_minus_1_subsets": n,
            "uniqueness_failures": uniqueness_failures,
            "worst_case_untrusted_row_queries": n - 1,
        }

    gates = {
        "all_subsets_at_most_n_minus_2_ambiguous": all(v["ambiguity_failures"] == 0 for v in by_n.values()),
        "all_n_minus_1_subsets_unique": all(v["uniqueness_failures"] == 0 for v in by_n.values()),
        "no_counterexamples": not counterexamples,
    }
    payload = {
        "schema": "theorica.translation-completeness-certificate-boundary.v1",
        "classification": "EXACT_ENUMERATION",
        "max_n": args.max_n,
        "theorem_query_bound": "r*n + (n-r)*(n-1)",
        "by_n": by_n,
        "counterexamples": counterexamples,
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "gates": gates, "by_n": by_n,
                      "canonical_sha256": payload["canonical_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
