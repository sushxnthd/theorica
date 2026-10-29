#!/usr/bin/env python3
"""Independent zero-THEORICA-import audit of both ratio-two theorems."""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

from audit_qary_three_level_middle_first_symmetric import pareto, queries

PRIMARY = Path("results/qary_three_level_middle_first_ratio_two/results.json")
OUT = Path("results/qary_three_level_middle_first_ratio_two/independent_audit.json")
SLICES = {
    "root_double": {"weights": (2, 1), "faces": ((10, 1), (9, 3), (7, 4))},
    "middle_double": {"weights": (1, 2), "faces": ((11, 1), (10, 3), (8, 4))},
}


def guarantees(weights):
    groups = queries()
    answers = tuple(tuple(sorted(set(row))) for row, _, _, _ in groups)

    def successors(scores, erased, stock, query):
        row, _, _, _ = groups[query]
        rest = tuple(n - (index == query) for index, n in enumerate(stock))
        out = []
        for answer in answers[query]:
            child = tuple(
                min(2, score + (row[index] != answer))
                for index, score in enumerate(scores)
            )
            if any(score <= 1 for score in child):
                out.append((child, erased, rest))
        if erased == 0:
            out.append((scores, 1, rest))
        return tuple(out)

    @cache
    def force(scores, erased, stock, first):
        live = tuple(index for index, score in enumerate(scores) if score <= 1)
        if len(live) <= 1:
            return frozenset({(0, 0)})
        per_query = []
        for query, count in enumerate(stock):
            if count == 0 or (first and query not in (1, 2)):
                continue
            row, _, _, _ = groups[query]
            if len({row[index] for index in live}) < 2:
                continue
            inc = (
                (weights[0], 0)
                if query == 0
                else ((weights[1], 0) if query < 3 else (0, 1))
            )
            options = set()
            for child in successors(scores, erased, stock, query):
                options.update(
                    (point[0] + inc[0], point[1] + inc[1])
                    for point in force(*child, False)
                )
            per_query.append(pareto(options))
        if not per_query:
            return frozenset({(0, 0)})
        current = per_query[0]
        for option in per_query[1:]:
            current = pareto(
                tuple(min(x, y) for x, y in zip(a, b)) for a in current for b in option
            )
        return current

    return force((0,) * 8, 0, (4,) * 7, True)


def candidate(faces, x, y):
    return max(a * x + b * y for a, b in faces)


def exact_middle_first(level_costs, expected):
    groups = queries(level_costs)
    answers = tuple(tuple(sorted(set(row))) for row, _, _, _ in groups)
    initial_stock = (4,) * len(groups)
    initial_scores = (0,) * 8

    @cache
    def feasible(scores, erased, stock, limit):
        live = tuple(index for index, score in enumerate(scores) if score <= 1)
        if len(live) <= 1:
            return True
        first = scores == initial_scores and erased == 0 and stock == initial_stock
        choices = []
        for query, count in enumerate(stock):
            row, _, cost, _ = groups[query]
            if count == 0 or cost > limit or (first and query not in (1, 2)):
                continue
            cells = {row[index] for index in live}
            if len(cells) > 1:
                choices.append((cost, query))
        for cost, query in sorted(choices):
            row, _, _, _ = groups[query]
            rest = tuple(n - (index == query) for index, n in enumerate(stock))
            children = []
            for answer in answers[query]:
                child = tuple(
                    min(2, score + (row[index] != answer))
                    for index, score in enumerate(scores)
                )
                if any(score <= 1 for score in child):
                    children.append((child, erased))
            if erased == 0:
                children.append((scores, 1))
            if children and all(
                feasible(child, used, rest, limit - cost) for child, used in children
            ):
                return True
        return False

    if not feasible(initial_scores, 0, initial_stock, expected):
        return None
    lower, upper = -1, expected
    while upper - lower > 1:
        middle = (upper + lower) // 2
        if feasible(initial_scores, 0, initial_stock, middle):
            upper = middle
        else:
            lower = middle
    return upper


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    records = {}
    for name, specification in SLICES.items():
        faces = specification["faces"]
        antichain = guarantees(specification["weights"])
        replays = []
        for item in primary["slices"][name]["holdouts"]:
            x, y = item["base_and_leaf_costs"]
            expected = candidate(faces, x, y)
            exact = exact_middle_first(tuple(item["level_costs"]), expected)
            replays.append(
                {
                    "base_and_leaf_costs": [x, y],
                    "independent_exact_cost": exact,
                    "production_exact_cost": item["exact_cost"],
                    "candidate_cost": expected,
                    "matched": exact == item["exact_cost"] == expected,
                }
            )
        cone_checks = []
        for cone in primary["slices"][name]["upper_bound_cones"]:
            exposures = tuple(tuple(point) for point in cone["projected_exposures"])
            face = tuple(cone["face"])
            checks = []
            for record in cone["extreme_ray_inequalities"]:
                ray = tuple(record["ray"])
                actual = max(
                    sum(a * b for a, b in zip(point, ray)) for point in exposures
                )
                limit = sum(a * b for a, b in zip(face, ray))
                checks.append(
                    actual == record["policy_cost"]
                    and limit == record["face_cost"]
                    and actual <= limit
                )
            cone_checks.append(all(checks) and cone["passed"])
        records[name] = {
            "maximal_projected_guarantees": [
                list(point) for point in sorted(antichain)
            ],
            "antichain_exact": antichain == frozenset(faces),
            "holdouts_reproduced": sum(item["matched"] for item in replays),
            "holdout_total": len(replays),
            "cones_reproduced": sum(cone_checks),
            "replays": replays,
        }
    imports = len(
        {name for name in sys.modules if name.startswith("theorica")} - before
    )
    result = {
        "schema": "theorica.middle-first-ratio-two-slices-audit/1",
        "production_imports": imports,
        "slices": records,
        "summary": {
            "antichains_reproduced": sum(
                item["antichain_exact"] for item in records.values()
            ),
            "holdouts_reproduced": sum(
                item["holdouts_reproduced"] for item in records.values()
            ),
            "holdout_total": 16,
            "cones_reproduced": sum(
                item["cones_reproduced"] for item in records.values()
            ),
            "production_imports": imports,
        },
    }
    result["summary"]["passed"] = result["summary"] == {
        "antichains_reproduced": 2,
        "holdouts_reproduced": 16,
        "holdout_total": 16,
        "cones_reproduced": 6,
        "production_imports": 0,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if result["summary"]["passed"] else 1)


if __name__ == "__main__":
    main()
