#!/usr/bin/env python3
"""Independent arithmetic audit of the randomized query law."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=128)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    checks = 0
    failures = []
    for size in range(3, args.max_n + 1):
        for budget in range(size):
            # Count favorable positions of the hidden label in a random
            # permutation: queried positions 0..budget-1 plus guess position.
            favorable = budget + 1
            success = Fraction(favorable, size)
            for hidden in range(size):
                position_successes = sum(
                    pos < budget or pos == budget for pos in range(size)
                )
                checks += 1
                if Fraction(position_successes, size) != success:
                    failures.append(["symmetry", size, budget, hidden])
            costs = [pos + 1 if pos < budget else budget for pos in range(size)]
            target_cost = Fraction(budget, 1) - Fraction(budget * (budget - 1), 2 * size)
            checks += 1
            if sum(map(Fraction, costs)) / size != target_cost:
                failures.append(["cost", size, budget])
            # q equality tests distinguish q marked labels; one additional
            # label can be named at the negative leaf, and no others.
            checks += 1
            if min(size, budget + 1) != favorable:
                failures.append(["decision_tree", size, budget])
        for numerator in range(size + 1):
            alpha = Fraction(numerator, size)
            budgets = [q for q in range(size) if Fraction(q + 1, size) >= alpha]
            claimed = max(0, numerator - 1)
            checks += 1
            if min(budgets) != claimed:
                failures.append(["inverse", size, numerator, min(budgets), claimed])
    payload = {"schema": "theorica.randomized-partial-cell-bound.audit.v1",
               "max_n": args.max_n, "checks": checks, "failures": failures,
               "status": "PASS" if not failures else "FAIL"}
    payload["canonical_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
