#!/usr/bin/env python3
"""Independent zero-import audit of the symmetric-slice theorem."""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_three_level_middle_first_symmetric/results.json")
OUT = Path("results/qary_three_level_middle_first_symmetric/independent_audit.json")
FACES = ((7, 1), (6, 3), (5, 4))


def pareto(points):
    points = set(points)
    return frozenset(
        point
        for point in points
        if not any(
            point != other and all(x <= y for x, y in zip(point, other))
            for other in points
        )
    )


def queries(costs=None):
    worlds = tuple((x, y, z) for x in range(2) for y in range(2) for z in range(2))
    result = []
    for depth in range(3):
        for stem in sorted({world[:depth] for world in worlds}):
            row = tuple(world[depth] if world[:depth] == stem else 0 for world in worlds)
            result.append((row, 0 if depth < 2 else 1, 4 if costs is None else costs[depth], 4))
    return tuple(result)


def projected_guarantees():
    groups = queries()
    answers = tuple(tuple(sorted(set(row))) for row, _, _, _ in groups)

    def successors(scores, erased, stock, query):
        row, _, _, _ = groups[query]
        rest = tuple(n - (index == query) for index, n in enumerate(stock))
        out = []
        for answer in answers[query]:
            child = tuple(min(2, score + (row[index] != answer)) for index, score in enumerate(scores))
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
            row, axis, _, _ = groups[query]
            if len({row[index] for index in live}) < 2:
                continue
            options = set()
            for child in successors(scores, erased, stock, query):
                options.update(
                    tuple(value + (coordinate == axis) for coordinate, value in enumerate(point))
                    for point in force(*child, False)
                )
            per_query.append(pareto(options))
        if not per_query:
            return frozenset({(0, 0)})
        current = per_query[0]
        for option in per_query[1:]:
            current = pareto(
                tuple(min(x, y) for x, y in zip(a, b))
                for a in current
                for b in option
            )
        return current

    return force((0,) * 8, 0, (4,) * 7, True)


def candidate(x, y):
    return max(a * x + b * y for a, b in FACES)


def exact_middle_first(x, y):
    groups = queries((x, x, y))
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
                child = tuple(min(2, score + (row[index] != answer)) for index, score in enumerate(scores))
                if any(score <= 1 for score in child):
                    children.append((child, erased))
            if erased == 0:
                children.append((scores, 1))
            if children and all(feasible(child, used, rest, limit - cost) for child, used in children):
                return True
        return False

    upper = candidate(x, y)
    if not feasible(initial_scores, 0, initial_stock, upper):
        return None
    lower = -1
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
    guarantees = projected_guarantees()
    replays = []
    for item in primary["holdouts"]:
        x, y = item["symmetric_costs"]
        exact = exact_middle_first(x, y)
        expected = candidate(x, y)
        replays.append({
            "symmetric_costs": [x, y],
            "independent_exact_cost": exact,
            "production_exact_cost": item["exact_cost"],
            "candidate_cost": expected,
            "matched": exact == item["exact_cost"] == expected,
        })
    cone_checks = []
    for cone in primary["upper_bound_cones"]:
        checks = []
        exposures = tuple(tuple(row) for row in cone["unique_projected_exposures"])
        face = tuple(cone["face"])
        for record in cone["extreme_ray_inequalities"]:
            ray = tuple(record["ray"])
            actual = max(sum(a * b for a, b in zip(point, ray)) for point in exposures)
            limit = sum(a * b for a, b in zip(face, ray))
            checks.append(actual == record["policy_cost"] and actual <= limit == record["face_cost"])
        cone_checks.append(all(checks))
    imports = len({name for name in sys.modules if name.startswith("theorica")} - before)
    result = {
        "schema": "theorica.middle-first-symmetric-slice-audit/1",
        "production_imports": imports,
        "maximal_projected_guarantees": [list(point) for point in sorted(guarantees)],
        "holdout_total": len(replays),
        "holdouts_reproduced": sum(item["matched"] for item in replays),
        "upper_cones_reproduced": sum(cone_checks),
        "replays": replays,
    }
    result["passed"] = (
        imports == 0
        and guarantees == frozenset(FACES)
        and result["holdouts_reproduced"] == result["holdout_total"] == 7
        and result["upper_cones_reproduced"] == 3
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "replays"}, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
