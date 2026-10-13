#!/usr/bin/env python3
"""Independent exhaustive audit of nonfaithful translation reconstruction.

This checker intentionally does not import the production learner or the primary
enumerator.  It rebuilds permutation closure, minimal generator sets, bases, and
row recovery from the mathematical specification.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path


def multiply(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[x]] for x in range(len(p)))


def generated_group(seeds: tuple[tuple[int, ...], ...]) -> frozenset[tuple[int, ...]]:
    identity = tuple(range(len(seeds[0])))
    known = {identity}
    changed = True
    while changed:
        changed = False
        for left in tuple(known) + seeds:
            for right in tuple(known) + seeds:
                product = multiply(left, right)
                if product not in known:
                    known.add(product)
                    changed = True
    return frozenset(known)


def smallest_generators(rows: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    distinct = tuple(dict.fromkeys(rows))
    target = generated_group(distinct)
    for width in range(1, len(distinct) + 1):
        for choice in itertools.combinations(distinct, width):
            if generated_group(choice) == target:
                return choice
    raise AssertionError("finite generator search failed")


def smallest_base(group: frozenset[tuple[int, ...]]) -> tuple[int, ...]:
    n = len(next(iter(group)))
    for width in range(n + 1):
        for points in itertools.combinations(range(n), width):
            images = {tuple(g[p] for p in points) for g in group}
            if len(images) == len(group):
                return points
    raise AssertionError("finite base search failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary: dict[str, dict[str, int]] = {}
    failures: list[dict[str, object]] = []
    first_nonfaithful: dict[str, object] | None = None

    for n in range(1, args.max_n + 1):
        permutations = tuple(itertools.permutations(range(n)))
        counts = {"operations": 0, "faithful": 0, "nonfaithful": 0, "failures": 0}
        cache: dict[tuple[tuple[int, ...], ...], tuple[frozenset[tuple[int, ...]], tuple[tuple[int, ...], ...], tuple[int, ...]]] = {}
        for rows in itertools.product(permutations, repeat=n):
            counts["operations"] += 1
            faithful = len(set(rows)) == n
            counts["faithful" if faithful else "nonfaithful"] += 1
            key = tuple(sorted(set(rows)))
            if key not in cache:
                generators = smallest_generators(key)
                group = generated_group(generators)
                cache[key] = (group, generators, smallest_base(group))
            group, generators, base = cache[key]
            lookup = {tuple(g[p] for p in base): g for g in group}
            recovered = tuple(lookup[tuple(row[p] for p in base)] for row in rows)
            if recovered != rows:
                counts["failures"] += 1
                if len(failures) < 10:
                    failures.append({"n": n, "rows": rows, "base": base})
            if not faithful and first_nonfaithful is None:
                generator_rows = []
                remaining = list(generators)
                for index, row in enumerate(rows):
                    if row in remaining:
                        generator_rows.append(index)
                        remaining.remove(row)
                first_nonfaithful = {
                    "n": n,
                    "table": rows,
                    "group_size": len(group),
                    "base": base,
                    "generator_rows": generator_rows,
                    "queries": len(generator_rows) * n + (n - len(generator_rows)) * len(base),
                }
        summary[str(n)] = counts

    expected = sum(math.factorial(n) ** n for n in range(1, args.max_n + 1))
    total = sum(row["operations"] for row in summary.values())
    payload = {
        "schema": "theorica.nonfaithful-translation-boundary.independent-audit.v1",
        "implementation": "independent_no_production_or_primary_checker_imports",
        "max_n": args.max_n,
        "expected_operations": expected,
        "observed_operations": total,
        "by_n": summary,
        "first_nonfaithful": first_nonfaithful,
        "failures": failures,
        "status": "PASS" if total == expected and not failures else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
