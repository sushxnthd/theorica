#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def make_operation(n, special):
    def op(x, y):
        if x != special or y == special:
            return y
        ordinary = [v for v in range(n) if v != special]
        return ordinary[(ordinary.index(y) + 1) % len(ordinary)]
    return op


def generated(n, op, seeds):
    reached = set(seeds)
    frontier = True
    while frontier:
        frontier = False
        before = tuple(reached)
        for x in before:
            for y in before:
                value = op(x, y)
                if value not in reached:
                    reached.add(value)
                    frontier = True
    return reached


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("primary", type=Path)
    ap.add_argument("--max-n", type=int, default=64)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    primary = json.loads(args.primary.read_text())

    checks = []
    failures = []
    for n in range(3, args.max_n + 1):
        special = n - 1
        op = make_operation(n, special)
        rack = all(
            op(x, op(y, z)) == op(op(x, y), op(x, z))
            for x in range(n) for y in range(n) for z in range(n)
        )
        no_singleton = all(len(generated(n, op, [x])) < n for x in range(n))
        all_pairs = all(
            len(generated(n, op, [special, x])) == n
            for x in range(n) if x != special
        )
        indistinguishable = all(
            all(op(x, y) == y for y in range(n))
            for x in range(n - 1)
        )
        average = sum(Fraction(2 if position == 1 else position, n)
                      for position in range(1, n + 1))
        expected = Fraction(n + 1, 2) + Fraction(1, n)
        primary_row = primary["family"][str(n)]
        ok = (
            rack and no_singleton and all_pairs and indistinguishable
            and average == expected
            and primary_row["minimum_rank"] == 2
            and primary_row["greedy_rows"] == n
            and primary_row["random_label_expected_rows"]
                == f"{expected.numerator}/{expected.denominator}"
        )
        checks.append({"n": n, "ok": ok})
        if not ok:
            failures.append({"n": n, "rack": rack, "no_singleton": no_singleton,
                             "all_pairs": all_pairs, "indistinguishable": indistinguishable,
                             "average": str(average), "expected": str(expected)})
    payload = {
        "schema": "theorica.adaptive-rack-seed-boundary.audit.v1",
        "independent_method": "direct operation oracle and cubic rack identity check",
        "checks": len(checks),
        "failures": failures,
        "status": "PASS" if not failures and primary["status"] == "PASS" else "FAIL",
        "primary_canonical_sha256": primary["canonical_sha256"],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
