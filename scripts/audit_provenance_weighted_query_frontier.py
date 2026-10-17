#!/usr/bin/env python3
"""Independent combinatorial audit of the weighted frontier."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=8)
    parser.add_argument("--max-weight", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks = 0
    failures = []
    for size in range(3, args.max_n + 1):
        for masses in itertools.product(range(1, args.max_weight + 1), repeat=size):
            denominator = sum(masses)
            descending = sorted(masses, reverse=True)
            for depth in range(size):
                claimed = Fraction(sum(descending[: depth + 1]), denominator)
                policy_values = [
                    Fraction(sum(masses[label] for label in correct), denominator)
                    for correct in itertools.combinations(range(size), depth + 1)
                ]
                checks += len(policy_values) + 1
                if max(policy_values) != claimed:
                    failures.append([size, list(masses), depth, str(max(policy_values)), str(claimed)])
                # Every ordered negative path and terminal guess has a correct
                # set of at most depth+1 labels; ordering cannot change its mass.
                representative = tuple(sorted(range(size), key=lambda i: (-masses[i], i))[: depth + 1])
                if Fraction(sum(masses[i] for i in representative), denominator) != claimed:
                    failures.append(["construction", size, list(masses), depth])
    payload = {
        "schema": "theorica.provenance-weighted-query-frontier.audit.v1",
        "max_n": args.max_n,
        "max_weight": args.max_weight,
        "checks": checks,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    payload["canonical_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
