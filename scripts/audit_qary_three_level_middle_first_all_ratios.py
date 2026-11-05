#!/usr/bin/env python3
"""Independent zero-THEORICA-import audit of the all-ratio boundary."""

from __future__ import annotations

import gzip
import json
import sys
from fractions import Fraction
from pathlib import Path

from audit_qary_three_level_middle_first_ratio_two import exact_middle_first

SRC = Path("results/qary_three_level_middle_first_all_ratios/raw_results.json.gz")
OUT = Path("results/qary_three_level_middle_first_all_ratios/independent_audit.json")
FACES = ((1, 5, 1), (2, 3, 4), (2, 4, 3), (3, 3, 3), (3, 4, 1), (4, 2, 1))


def crossing(row):
    slope = row["left"][0] - row["right"][0]
    intercept = row["left"][1] - row["right"][1]
    return None if slope == 0 else Fraction(-intercept, slope)


def trace_valid(row):
    ratio = Fraction(*row["ratio"])
    for comparison in row["comparisons"]:
        left = ratio * comparison["left"][0] + comparison["left"][1]
        right = ratio * comparison["right"][0] + comparison["right"][1]
        actual = left == right if comparison["operator"] == "eq" else left <= right
        if actual != comparison["result"]:
            return False
        root = crossing(comparison)
        stored = comparison["crossing"]
        if root is None and stored is not None:
            return False
        if root is not None and stored != [root.numerator, root.denominator]:
            return False
    if row["cell"] is not None:
        lower = Fraction(*row["cell"][0])
        upper = None if row["cell"][1] is None else Fraction(*row["cell"][1])
        if any(
            (root := crossing(comparison)) is not None
            and root > lower and (upper is None or root < upper)
            for comparison in row["comparisons"]
        ):
            return False
    actual_projection = sorted({
        (ratio * root + middle, leaf)
        for root, middle, leaf in row["symbolic_sources"]
    })
    stored_projection = [
        (Fraction(*first), leaf) for first, leaf in row["projected_antichain"]
    ]
    expected_projection = [
        (Fraction(*first), leaf)
        for first, leaf in row["expected_projected_antichain"]
    ]
    return (
        actual_projection == stored_projection == expected_projection
        and row["projected_antichain_matched"]
        and row["cell_certified"]
    )


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    with gzip.open(SRC, "rt", encoding="utf-8") as source:
        report = json.load(source)
    traces = [trace_valid(row) for row in report["decision_trace_partition"]]
    holdouts = []
    for row in report["prospective_exact_holdouts"]:
        p, q = row["ratio"]
        unit, leaf = row["unit_and_leaf_costs"]
        expected = max(
            (root * p + middle * q) * unit + leaves * leaf
            for root, middle, leaves in FACES
        )
        holdouts.append(
            exact_middle_first(tuple(row["level_costs"]), expected)
            == row["exact_cost"] == expected
        )
    source_union = sorted({
        tuple(source)
        for row in report["decision_trace_partition"]
        for source in row["symbolic_sources"]
    })
    imports = len({name for name in sys.modules if name.startswith("theorica")} - before)
    result = {
        "schema": "theorica.middle-first-all-positive-ratios-audit/1",
        "production_imports": imports,
        "trace_certificates_reproduced": sum(traces),
        "trace_certificate_total": len(traces),
        "holdouts_reproduced": sum(holdouts),
        "holdout_total": len(holdouts),
        "all_six_faces_recovered": source_union == list(FACES),
    }
    result["passed"] = (
        imports == 0
        and result["trace_certificates_reproduced"]
        == result["trace_certificate_total"] == 19
        and result["holdouts_reproduced"] == result["holdout_total"] == 30
        and result["all_six_faces_recovered"]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
