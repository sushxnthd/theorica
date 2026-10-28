#!/usr/bin/env python3
"""Independent zero-THEORICA-import audit of the rational-ratio theorem."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

from audit_qary_three_level_middle_first_ratio_two import exact_middle_first

SRC = Path("results/qary_three_level_middle_first_rational_ratio/results.json")
OUT = Path(
    "results/qary_three_level_middle_first_rational_ratio/independent_audit.json"
)


def faces(orientation, p, q):
    if orientation == "root":
        return ((4 * p + 2 * q, 1), (3 * p + 3 * q, 3), (2 * p + 3 * q, 4))
    return ((5 * p + q, 1), (4 * p + 2 * q, 3), (3 * p + 2 * q, 4))


def crossing(row):
    slope = row["left"][0] - row["right"][0]
    intercept = row["left"][1] - row["right"][1]
    return None if slope == 0 else Fraction(-intercept, slope)


def trace_valid(row):
    ratio = Fraction(*row["ratio"])
    for comparison in row["comparisons"]:
        left = ratio * comparison["left"][0] + comparison["left"][1]
        right = ratio * comparison["right"][0] + comparison["right"][1]
        result = left == right if comparison["operator"] == "eq" else left <= right
        if result != comparison["result"]:
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
            and root > lower
            and (upper is None or root < upper)
            for comparison in row["comparisons"]
        ):
            return False
    return (
        row["symbolic_sources"] == row["expected_sources"]
        and row["sources_matched"]
        and row["cell_certified"]
    )


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    report = json.loads(SRC.read_text(encoding="utf-8"))
    traces = [trace_valid(row) for row in report["decision_trace_certificate"]]
    holdouts = []
    for row in report["prospective_holdouts"]:
        p, q = row["ratio"]
        unit, leaf = row["unit_and_leaf_costs"]
        expected = max(a * unit + b * leaf for a, b in faces(row["orientation"], p, q))
        holdouts.append(
            exact_middle_first(tuple(row["level_costs"]), expected)
            == row["exact_cost"]
            == expected
        )
    policies = [
        policy["passed"]
        and all(
            margin["slope"] >= 0 and margin["value_at_k2"] >= 0
            for ray in policy["symbolic_inequalities"]
            for margin in ray["margins"]
        )
        for rows in report["universal_upper_policies"].values()
        for policy in rows
    ]
    imports = len({name for name in sys.modules if name.startswith("theorica")} - before)
    result = {
        "schema": "theorica.middle-first-rational-ratio-family-audit/1",
        "production_imports": imports,
        "trace_certificates_reproduced": sum(traces),
        "trace_certificate_total": len(traces),
        "holdouts_reproduced": sum(holdouts),
        "holdout_total": len(holdouts),
        "universal_cones_reproduced": sum(policies),
        "universal_cone_total": len(policies),
    }
    result["passed"] = (
        imports == 0
        and result["trace_certificates_reproduced"]
        == result["trace_certificate_total"]
        == 12
        and result["holdouts_reproduced"] == result["holdout_total"] == 48
        and result["universal_cones_reproduced"]
        == result["universal_cone_total"]
        == 6
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
