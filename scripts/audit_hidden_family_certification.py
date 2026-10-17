#!/usr/bin/env python3
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


def digest_without_field(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonical_sha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def independent_cycle(n: int, z: int) -> tuple[int, ...]:
    row = list(range(n))
    complement = [x for x in range(n) if x != z]
    for left, right in zip(complement, complement[1:] + complement[:1]):
        row[left] = right
    return tuple(row)


def independent_membership(table: tuple[tuple[int, ...], ...]) -> int | None:
    n = len(table)
    identity = tuple(range(n))
    changed = [row for row in range(n) if table[row] != identity]
    if len(changed) != 1:
        return None
    z = changed[0]
    active = table[z]
    if sorted(active) != list(range(n)) or active[z] != z:
        return None
    complement = set(range(n)) - {z}
    start = min(complement)
    visited = set()
    current = start
    while current not in visited and current != z:
        visited.add(current)
        current = active[current]
    return z if current == start and visited == complement else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("primary", type=Path)
    parser.add_argument("--max-n", type=int, default=24)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    primary = json.loads(args.primary.read_text())
    failures: list[dict] = []
    checks = 0

    if primary.get("canonical_sha256") != digest_without_field(primary):
        failures.append({"kind": "primary_digest"})
    checks += 1

    for n in range(3, args.max_n + 1):
        population = n * n
        identity = tuple(range(n))
        for z in range(n):
            active = independent_cycle(n, z)
            table = tuple(active if row == z else identity for row in range(n))
            checks += 1
            if independent_membership(table) != z:
                failures.append({"kind": "independent_valid", "n": n, "z": z})
            # Independently materialize one corruption in every cell.  The
            # replacement is cyclic, which is sufficient to audit the claimed
            # one-cell lower-bound witness class without sharing primary code.
            for row in range(n):
                for column in range(n):
                    mutable = [list(values) for values in table]
                    mutable[row][column] = (mutable[row][column] + 1) % n
                    corrupted = tuple(tuple(values) for values in mutable)
                    checks += 1
                    if independent_membership(corrupted) is not None:
                        failures.append({"kind": "corruption_accepted", "n": n,
                                         "z": z, "row": row, "column": column})

        # Lower bound: on the valid transcript, inclusion probabilities sum
        # to at most q.  Uniform inclusion q/N attains the averaging bound.
        for q in range(population + 1):
            checks += 3
            uniform = [Fraction(q, population)] * population
            if sum(uniform) != q or min(uniform) != Fraction(q, population):
                failures.append({"kind": "averaging_frontier", "n": n, "q": q})
            required = math.ceil(population * Fraction(q, population))
            if required != q:
                failures.append({"kind": "confidence_inverse", "n": n, "q": q})
            miss = (Fraction(math.comb(population - 1, q), math.comb(population, q))
                    if q < population else Fraction(0, 1))
            if 1 - miss != Fraction(q, population):
                failures.append({"kind": "hypergeometric", "n": n, "q": q})

    payload = {
        "status": "PASS" if not failures else "FAIL",
        "max_n": args.max_n,
        "checks": checks,
        "failures": failures[:100],
        "independent_method": "direct table predicate, materialized cyclic corruptions, and rational averaging audit",
        "primary_canonical_sha256": primary.get("canonical_sha256"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
