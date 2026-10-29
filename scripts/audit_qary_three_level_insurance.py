#!/usr/bin/env python3
"""Independent stdlib-only replay of the three-level insurance law."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_three_level_insurance/results.json")
OUT = Path("results/qary_three_level_insurance/independent_audit.json")


def library(arity, level_costs):
    rows, costs = [], []
    for level, cost in enumerate(level_costs):
        prefix_divisor = arity ** (3 - level)
        symbol_divisor = arity ** (2 - level)
        for prefix in range(arity**level):
            row = tuple(
                (item // symbol_divisor) % arity
                if item // prefix_divisor == prefix else 0
                for item in range(arity**3)
            )
            rows.extend((row,) * 4)
            costs.extend((cost,) * 4)
    return tuple(rows), tuple(costs)


def exact_cost(rows, costs, completion_count):
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)

    @cache
    def search(counts, erased, remaining, limit):
        feasible = tuple(i for i, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return True
        seen = set()
        for query in remaining:
            if costs[query] > limit:
                continue
            row = rows[query]
            key = (row, costs[query])
            if key in seen or len({row[i] for i in feasible}) < 2:
                continue
            seen.add(key)
            next_remaining = tuple(i for i in remaining if i != query)
            children = []
            for answer in alphabets[query]:
                child = tuple(
                    min(2, count + (row[i] != answer))
                    for i, count in enumerate(counts)
                )
                if any(count <= 1 for count in child):
                    children.append((child, erased))
            if erased < 1:
                children.append((counts, erased + 1))
            if children and all(
                search(child, child_erased, next_remaining, limit - costs[query])
                for child, child_erased in children
            ):
                return True
        return False

    initial = (0,) * completion_count
    remaining = tuple(range(len(rows)))
    lower, upper = -1, sum(costs)
    if not search(initial, 0, remaining, upper):
        return None
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if search(initial, 0, remaining, middle):
            upper = middle
        else:
            lower = middle
    return upper


def formula(a, b, c):
    return max(
        4 * b + 2 * c,
        2 * a + 2 * b + 4 * c,
        2 * a + 3 * b + 3 * c,
        2 * a + 4 * b + c,
        3 * a + 2 * b + 3 * c,
        3 * a + 3 * b + c,
        4 * a + b + c,
    )


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text())
    replays = []
    for item in primary["cases"]:
        rows, costs = library(item["arity"], item["level_costs"])
        actual = exact_cost(rows, costs, item["arity"] ** 3)
        expected = formula(*item["level_costs"])
        replays.append({
            "arity": item["arity"],
            "level_costs": item["level_costs"],
            "actual": actual,
            "production_exact": item["exact_cost"],
            "formula": expected,
            "matched": actual == item["exact_cost"] == expected,
        })
    rows, costs = library(2, (2, 1, 7))
    missing = exact_cost(rows[:-1], costs[:-1], 8)
    canonical = json.dumps(primary["cases"], sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-three-level-insurance-audit/1",
        "cases_replayed": sum(item["matched"] for item in replays),
        "case_total": len(replays),
        "missing_copy_cost": missing,
        "missing_copy_abstained": missing is None,
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
