#!/usr/bin/env python3
"""Prove and prospectively test the frozen rational-ratio extension."""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
from typing import ClassVar

import verify_qary_three_level_middle_first_integer_ratio as integer_ratio
from verify_qary_three_level_middle_first_symmetric import games

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_rational_ratio/results.json")
TRACE_POINTS = (
    (Fraction(2), "boundary_2", None),
    (Fraction(5, 2), "cell_2_3", (Fraction(2), Fraction(3))),
    (Fraction(3), "boundary_3", None),
    (Fraction(7, 2), "cell_3_4", (Fraction(3), Fraction(4))),
    (Fraction(4), "boundary_4", None),
    (Fraction(5), "tail_above_4", (Fraction(4), None)),
)
FROZEN_RATIOS = ((13, 6), (7, 3), (5, 2), (7, 2), (9, 2), (17, 3))
EXPECTED_SOURCES = {
    "root": ((2, 3, 4), (3, 3, 3), (4, 2, 1)),
    "middle": ((1, 5, 1), (2, 3, 4), (2, 4, 3)),
}


class AffineCoordinate:
    records: ClassVar[set[tuple]] = set()

    def __init__(self, slope, intercept, ratio):
        self.slope, self.intercept, self.ratio = slope, intercept, ratio

    @property
    def value(self):
        return self.ratio * self.slope + self.intercept

    def __hash__(self):
        return hash(self.value)

    def _record(self, other, operator, result):
        slope = self.slope - other.slope
        intercept = self.intercept - other.intercept
        crossing = None if slope == 0 else Fraction(-intercept, slope)
        self.records.add(
            (
                self.slope,
                self.intercept,
                other.slope,
                other.intercept,
                operator,
                result,
                crossing,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, AffineCoordinate):
            return NotImplemented
        result = self.value == other.value
        self._record(other, "eq", result)
        return result

    def __le__(self, other):
        if not isinstance(other, AffineCoordinate):
            return NotImplemented
        result = self.value <= other.value
        self._record(other, "le", result)
        return result


def fraction_json(value):
    return [value.numerator, value.denominator]


def traced_guarantees(orientation, ratio):
    original = integer_ratio.projected
    AffineCoordinate.records = set()

    def projected(vector, selected_orientation, _ratio):
        root, middle, leaf = vector
        return (
            AffineCoordinate(
                root if selected_orientation == "root" else middle,
                middle if selected_orientation == "root" else root,
                ratio,
            ),
            leaf,
        )

    integer_ratio.projected = projected
    try:
        sources, states = integer_ratio.symbolic_projected_guarantees(
            orientation, ratio
        )
    finally:
        integer_ratio.projected = original
    unique = sorted(
        AffineCoordinate.records,
        key=lambda row: (
            row[6] is None,
            row[6] or Fraction(0),
            row[:6],
        ),
    )
    comparisons = [
        {
            "left": [row[0], row[1]],
            "right": [row[2], row[3]],
            "operator": row[4],
            "result": row[5],
            "crossing": None if row[6] is None else fraction_json(row[6]),
        }
        for row in unique
    ]
    return sources, states, comparisons


def trace_record(args):
    orientation, ratio, label, cell = args
    sources, states, comparisons = traced_guarantees(orientation, ratio)
    interior = []
    if cell is not None:
        lower, upper = cell
        interior = [
            row
            for row in comparisons
            if row["crossing"] is not None
            and (crossing := Fraction(*row["crossing"])) > lower
            and (upper is None or crossing < upper)
        ]
    return {
        "orientation": orientation,
        "ratio": fraction_json(ratio),
        "label": label,
        "cell": None
        if cell is None
        else [
            fraction_json(cell[0]),
            None if cell[1] is None else fraction_json(cell[1]),
        ],
        "states_checked": states,
        "symbolic_sources": [list(item) for item in sorted(sources)],
        "expected_sources": [list(item) for item in EXPECTED_SOURCES[orientation]],
        "sources_matched": tuple(sorted(sources)) == EXPECTED_SOURCES[orientation],
        "comparisons": comparisons,
        "interior_crossings": interior,
        "cell_certified": not interior,
    }


def faces(orientation, p, q):
    if orientation == "root":
        return ((4 * p + 2 * q, 1), (3 * p + 3 * q, 3), (2 * p + 3 * q, 4))
    return ((5 * p + q, 1), (4 * p + 2 * q, 3), (3 * p + 2 * q, 4))


def exact_holdout(orientation, p, q, unit, leaf):
    expected = max(a * unit + b * leaf for a, b in faces(orientation, p, q))
    level_costs = (
        (p * unit, q * unit, leaf)
        if orientation == "root"
        else (q * unit, p * unit, leaf)
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            2, 3, copies=4, level_costs=level_costs
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=expected,
    )
    return {
        "orientation": orientation,
        "ratio": [p, q],
        "unit_and_leaf_costs": [unit, leaf],
        "level_costs": list(level_costs),
        "predicted_cost": expected,
        "exact_cost": plan.worst_case_cost,
        "matched": plan.worst_case_cost == expected,
    }


def main():
    jobs = [
        (orientation, ratio, label, cell)
        for orientation in ("root", "middle")
        for ratio, label, cell in TRACE_POINTS
    ]
    with ProcessPoolExecutor(max_workers=2) as pool:
        traces = list(pool.map(trace_record, jobs))
    holdouts = []
    for p, q in FROZEN_RATIOS:
        regimes = ((79, 1), (2, p - q), (1, p), (1, 79 * p))
        for orientation in ("root", "middle"):
            holdouts.extend(
                exact_holdout(orientation, p, q, unit, leaf)
                for unit, leaf in regimes
            )
    integer_evidence = json.loads(
        Path(
            "results/qary_three_level_middle_first_integer_ratio/results.json"
        ).read_text(encoding="utf-8")
    )
    upper = integer_evidence["universal_upper_policies"]
    universal_cones = sum(
        item["passed"] for rows in upper.values() for item in rows
    )
    summary = {
        "trace_sources_matched": sum(row["sources_matched"] for row in traces),
        "trace_total": len(traces),
        "cells_certified": sum(row["cell_certified"] for row in traces),
        "universal_upper_cones_reused": universal_cones,
        "holdouts_matched": sum(row["matched"] for row in holdouts),
        "holdout_total": len(holdouts),
    }
    summary["passed"] = (
        summary["trace_sources_matched"] == summary["trace_total"] == 12
        and summary["cells_certified"] == 12
        and summary["universal_upper_cones_reused"] == 6
        and summary["holdouts_matched"] == summary["holdout_total"] == 48
    )
    result = {
        "schema": "theorica.middle-first-rational-ratio-family/1",
        "decision_trace_certificate": traces,
        "universal_upper_policies": upper,
        "prospective_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
