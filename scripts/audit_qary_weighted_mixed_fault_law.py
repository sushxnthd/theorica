#!/usr/bin/env python3
"""Independent stdlib-only replay of the weighted q-ary mixed-fault law."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_weighted_mixed_fault_law/results.json")
OUT = Path("results/qary_weighted_mixed_fault_law/independent_audit.json")


def library(arity, depth, copies, level_costs):
    rows, costs = [], []
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
            rows.extend((row,) * copies)
            costs.extend((level_costs[level],) * copies)
    return tuple(rows), tuple(costs)


def exact_cost(query_rows, query_costs, completion_count, corruptions, erasures):
    alphabets = tuple(tuple(sorted(set(row))) for row in query_rows)

    @cache
    def search(counts, erased, remaining, limit):
        feasible = tuple(i for i, count in enumerate(counts) if count <= corruptions)
        if len(feasible) <= 1:
            return True
        if not remaining:
            return False
        seen = set()
        for query in remaining:
            cost = query_costs[query]
            if cost > limit:
                continue
            row = query_rows[query]
            key = (row, cost)
            if key in seen or len({row[i] for i in feasible}) < 2:
                continue
            seen.add(key)
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
                search(child, child_erased, next_remaining, limit - cost)
                for child, child_erased in children
            ):
                return True
        return False

    initial = (0,) * completion_count
    remaining = tuple(range(len(query_rows)))
    lower, upper = -1, sum(query_costs)
    if not search(initial, 0, remaining, upper):
        return None
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if search(initial, 0, remaining, middle):
            upper = middle
        else:
            lower = middle
    return upper


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    replays = []
    for item in primary["cases"]:
        copies = 2 * item["corruption_budget"] + item["erasure_budget"] + 1
        rows, costs = library(
            item["arity"], item["depth"], copies, item["level_costs"]
        )
        actual = exact_cost(
            rows,
            costs,
            item["arity"] ** item["depth"],
            item["corruption_budget"],
            item["erasure_budget"],
        )
        replays.append(
            {
                "arity": item["arity"],
                "depth": item["depth"],
                "level_costs": item["level_costs"],
                "actual": actual,
                "production_exact": item["exact_adaptive_cost"],
                "formula_prediction": item["predicted_cost"],
                "formula_matched": actual == item["predicted_cost"],
                "replay_matched": actual == item["exact_adaptive_cost"],
            }
        )
    rows, costs = library(3, 2, 4, (1, 5))
    missing_cost = exact_cost(rows[:-1], costs[:-1], 9, 1, 1)
    canonical = json.dumps(primary["cases"], sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-weighted-mixed-fault-law-audit/1",
        "cases_replayed": sum(item["replay_matched"] for item in replays),
        "case_total": len(replays),
        "missing_copy_cost": missing_cost,
        "missing_copy_abstained": missing_cost is None,
        "case_digest_reproduced": hashlib.sha256(canonical.encode()).hexdigest()
        == primary["summary"]["case_digest"],
        "production_imports": len(
            {name for name in sys.modules if name.startswith("theorica")} - before
        ),
        "replays": replays,
    }
    result["passed"] = (
        result["cases_replayed"] == result["case_total"]
        and any(not item["formula_matched"] for item in replays)
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
