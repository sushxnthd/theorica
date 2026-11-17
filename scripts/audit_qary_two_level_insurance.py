#!/usr/bin/env python3
"""Independent standard-library replay of the two-level insurance law."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_two_level_insurance/results.json")
OUT = Path("results/qary_two_level_insurance/independent_audit.json")


def library(arity, root_cost, child_cost):
    rows, costs = [], []
    for level, cost in enumerate((root_cost, child_cost)):
        prefix_divisor = arity ** (2 - level)
        symbol_divisor = arity ** (1 - level)
        for prefix in range(arity**level):
            row = tuple(
                (item // symbol_divisor) % arity
                if item // prefix_divisor == prefix
                else 0
                for item in range(arity**2)
            )
            rows.extend((row,) * 4)
            costs.extend((cost,) * 4)
    return tuple(rows), tuple(costs)


def exact_cost(rows, costs, completion_count):
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)

    @cache
    def search(counts, erased, remaining, limit):
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return True
        seen = set()
        for query in remaining:
            if costs[query] > limit:
                continue
            row = rows[query]
            key = (row, costs[query])
            if key in seen or len({row[index] for index in feasible}) < 2:
                continue
            seen.add(key)
            next_remaining = tuple(item for item in remaining if item != query)
            children = []
            for answer in alphabets[query]:
                child = tuple(
                    min(2, count + (row[index] != answer))
                    for index, count in enumerate(counts)
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


def formula(root_cost, child_cost):
    return max(
        2 * root_cost + 4 * child_cost,
        3 * root_cost + 3 * child_cost,
        4 * root_cost + child_cost,
    )


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text())
    replays = []
    for item in primary["cases"]:
        rows, costs = library(
            item["arity"], item["root_cost"], item["child_cost"]
        )
        actual = exact_cost(rows, costs, item["arity"] ** 2)
        replays.append(
            {
                "arity": item["arity"],
                "root_cost": item["root_cost"],
                "child_cost": item["child_cost"],
                "actual": actual,
                "production_exact": item["exact_cost"],
                "formula": formula(item["root_cost"], item["child_cost"]),
                "matched": actual == item["exact_cost"] == item["formula_cost"],
            }
        )
    rows, costs = library(3, 2, 7)
    missing = exact_cost(rows[:-1], costs[:-1], 9)
    canonical = json.dumps(primary["cases"], sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-two-level-insurance-audit/1",
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
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
