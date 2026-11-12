#!/usr/bin/env python3
"""Independent stdlib-only replay of the q-ary mixed-fault law."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_mixed_fault_law/results.json")
OUT = Path("results/qary_mixed_fault_law/independent_audit.json")


def rows(arity, depth, corruptions, erasures):
    result = []
    count = arity**depth
    for level in range(depth):
        prefix_divisor = arity ** (depth - level)
        symbol_divisor = arity ** (depth - level - 1)
        for prefix in range(arity**level):
            row = tuple(
                (item // symbol_divisor) % arity
                if item // prefix_divisor == prefix
                else 0
                for item in range(count)
            )
            result.extend((row,) * (2 * corruptions + erasures + 1))
    return tuple(result)


def exact_depth(query_rows, completion_count, corruptions, erasures):
    alphabets = tuple(tuple(sorted(set(row))) for row in query_rows)

    @cache
    def search(counts, erased, remaining, limit):
        feasible = tuple(i for i, count in enumerate(counts) if count <= corruptions)
        if len(feasible) <= 1:
            return True
        if limit == 0 or not remaining:
            return False
        seen = set()
        for query in remaining:
            row = query_rows[query]
            if row in seen or len({row[i] for i in feasible}) < 2:
                continue
            seen.add(row)
            next_remaining = tuple(i for i in remaining if i != query)
            children = []
            for answer in alphabets[query]:
                child = tuple(
                    min(corruptions + 1, count + (row[i] != answer))
                    for i, count in enumerate(counts)
                )
                if any(count <= corruptions for count in child):
                    children.append((child, erased))
            if erased < erasures:
                children.append((counts, erased + 1))
            if children and all(
                search(child, child_erased, next_remaining, limit - 1)
                for child, child_erased in children
            ):
                return True
        return False

    initial = (0,) * completion_count
    remaining = tuple(range(len(query_rows)))
    for limit in range(len(query_rows) + 1):
        if search(initial, 0, remaining, limit):
            return limit
    return None


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    replays = []
    for case in primary["cases"]:
        arity = case["arity"]
        depth = case["depth"]
        corruptions = case["corruption_budget"]
        erasures = case["erasure_budget"]
        actual = exact_depth(
            rows(arity, depth, corruptions, erasures),
            arity**depth,
            corruptions,
            erasures,
        )
        predicted = (corruptions + 1) * depth + corruptions + erasures
        replays.append(
            {
                "arity": arity,
                "depth": depth,
                "corruption_budget": corruptions,
                "erasure_budget": erasures,
                "actual": actual,
                "expected": predicted,
                "passed": actual == case["exact_adaptive_depth"] == predicted,
            }
        )
    attacked = rows(3, 2, 1, 1)[:-1]
    missing_depth = exact_depth(attacked, 9, 1, 1)
    canonical = json.dumps(primary["cases"], sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-mixed-fault-law-audit/1",
        "cases_replayed": sum(item["passed"] for item in replays),
        "case_total": len(replays),
        "missing_copy_depth": missing_depth,
        "missing_copy_abstained": missing_depth is None,
        "case_digest_reproduced": hashlib.sha256(canonical.encode()).hexdigest()
        == primary["summary"]["case_digest"],
        "production_imports": len(
            {name for name in sys.modules if name.startswith("theorica")} - before
        ),
        "replays": replays,
    }
    result["passed"] = (
        result["cases_replayed"] == result["case_total"]
        and result["missing_copy_abstained"]
        and result["case_digest_reproduced"]
        and result["production_imports"] == 0
    )
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
