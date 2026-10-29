#!/usr/bin/env python3
"""Certify the frozen all-positive-ratio adversary boundary."""

from __future__ import annotations

import gzip
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from verify_qary_three_level_middle_first_rational_ratio import traced_guarantees
from verify_qary_three_level_middle_first_symmetric import games

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_all_ratios/raw_results.json.gz")
SUMMARY = Path("results/qary_three_level_middle_first_all_ratios/summary.json")
FACES = ((1, 5, 1), (2, 3, 4), (2, 4, 3), (3, 3, 3), (3, 4, 1), (4, 2, 1))
BOUNDARIES = tuple(
    Fraction(*value)
    for value in ((1, 4), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1), (4, 1))
)
CELL_SAMPLES = (
    Fraction(1, 5), Fraction(2, 7), Fraction(2, 5), Fraction(4, 7),
    Fraction(5, 6), Fraction(7, 6), Fraction(7, 4), Fraction(5, 2),
    Fraction(7, 2), Fraction(9, 2),
)
PROSPECTIVE_RATIOS = (
    (1, 5), (2, 7), (2, 5), (4, 7), (5, 6),
    (7, 6), (7, 5), (7, 4), (5, 2), (9, 2),
)


def fraction_json(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def cell_for(sample: Fraction) -> tuple[Fraction, Fraction | None]:
    lower = Fraction(0)
    for boundary in BOUNDARIES:
        if sample < boundary:
            return lower, boundary
        lower = boundary
    return lower, None


def maximal_candidate_sources(ratio: Fraction) -> tuple[tuple[int, int, int], ...]:
    def projected(face):
        root, middle, leaf = face
        return ratio * root + middle, leaf

    return tuple(sorted(
        face for face in FACES
        if not any(
            projected(face) != projected(other)
            and projected(face)[0] <= projected(other)[0]
            and projected(face)[1] <= projected(other)[1]
            for other in FACES
        )
    ))


def projected_antichain(sources, ratio: Fraction):
    return tuple(sorted({(ratio * root + middle, leaf) for root, middle, leaf in sources}))


def trace_record(args):
    ratio, label, cell = args
    sources, states, comparisons = traced_guarantees("root", ratio)
    interior = []
    if cell is not None:
        lower, upper = cell
        interior = [
            row for row in comparisons
            if row["crossing"] is not None
            and (crossing := Fraction(*row["crossing"])) > lower
            and (upper is None or crossing < upper)
        ]
    expected = maximal_candidate_sources(ratio)
    actual_projection = projected_antichain(sources, ratio)
    expected_projection = projected_antichain(expected, ratio)
    return {
        "ratio": fraction_json(ratio),
        "label": label,
        "cell": None if cell is None else [
            fraction_json(cell[0]),
            None if cell[1] is None else fraction_json(cell[1]),
        ],
        "states_checked": states,
        "symbolic_sources": [list(item) for item in sorted(sources)],
        "expected_sources": [list(item) for item in expected],
        "projected_antichain": [[fraction_json(first), leaf] for first, leaf in actual_projection],
        "expected_projected_antichain": [[fraction_json(first), leaf] for first, leaf in expected_projection],
        "projected_antichain_matched": actual_projection == expected_projection,
        "boundary_representative_collapsed": (
            cell is None and tuple(sorted(sources)) != expected
            and actual_projection == expected_projection
        ),
        "comparisons": comparisons,
        "interior_crossings": interior,
        "cell_certified": not interior,
    }


def candidate_cost(p: int, q: int, unit: int, leaf: int) -> int:
    return max((r * p + m * q) * unit + ell * leaf for r, m, ell in FACES)


def exact_case(args):
    p, q, unit, leaf, regime = args
    expected = candidate_cost(p, q, unit, leaf)
    costs = (p * unit, q * unit, leaf)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(2, 3, copies=4, level_costs=costs),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=expected,
    )
    return {
        "ratio": [p, q],
        "regime": regime,
        "unit_and_leaf_costs": [unit, leaf],
        "level_costs": list(costs),
        "predicted_cost": expected,
        "exact_cost": plan.worst_case_cost,
        "matched": plan.worst_case_cost == expected,
    }


def main():
    trace_jobs = []
    for sample in CELL_SAMPLES:
        trace_jobs.append((sample, f"cell_{sample.numerator}_{sample.denominator}", cell_for(sample)))
    for boundary in BOUNDARIES:
        trace_jobs.append((boundary, f"boundary_{boundary.numerator}_{boundary.denominator}", None))
    trace_jobs.sort(key=lambda row: row[0])
    with ProcessPoolExecutor(max_workers=4) as pool:
        traces = list(pool.map(trace_record, trace_jobs))

    holdout_jobs = []
    for p, q in PROSPECTIVE_RATIOS:
        holdout_jobs.extend((
            (p, q, 79, 1, "leaf_cheap"),
            (p, q, 2, p + q, "interior"),
            (p, q, 1, 79 * (p + q), "leaf_expensive"),
        ))
    with ProcessPoolExecutor(max_workers=4) as pool:
        holdouts = list(pool.map(exact_case, holdout_jobs))

    source_union = sorted({tuple(source) for row in traces for source in row["symbolic_sources"]})
    summary = {
        "trace_projected_antichains_matched": sum(row["projected_antichain_matched"] for row in traces),
        "trace_total": len(traces),
        "equivalent_boundary_representative_collapses": sum(
            row["boundary_representative_collapsed"] for row in traces
        ),
        "open_cells_certified": sum(row["cell_certified"] for row in traces if row["cell"] is not None),
        "open_cell_total": len(CELL_SAMPLES),
        "states_per_trace": sorted({row["states_checked"] for row in traces}),
        "source_union": [list(item) for item in source_union],
        "all_six_faces_recovered": source_union == list(FACES),
        "holdouts_matched": sum(row["matched"] for row in holdouts),
        "holdout_total": len(holdouts),
    }
    summary["passed"] = (
        summary["trace_projected_antichains_matched"] == summary["trace_total"] == 19
        and summary["open_cells_certified"] == summary["open_cell_total"] == 10
        and summary["states_per_trace"] == [178964]
        and summary["all_six_faces_recovered"]
        and summary["holdouts_matched"] == summary["holdout_total"] == 30
    )
    result = {
        "schema": "theorica.middle-first-all-positive-ratios/1",
        "candidate_faces": [list(item) for item in FACES],
        "decision_trace_partition": traces,
        "prospective_exact_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    with (
        OUT.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed,
    ):
        compressed.write(encoded)
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit("all-ratio protocol failed")


if __name__ == "__main__":
    main()
