"""Independent zero-THEORICA-import audit of the integer-ratio theorem."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from audit_qary_three_level_middle_first_ratio_two import (
    exact_middle_first,
    guarantees,
)

SRC = Path("results/qary_three_level_middle_first_integer_ratio/results.json")
OUT = Path("results/qary_three_level_middle_first_integer_ratio/independent_audit.json")
FROZEN_RATIOS = (3, 4, 7, 11)


def faces(orientation, k):
    if orientation == "root":
        return ((4 * k + 2, 1), (3 * k + 3, 3), (2 * k + 3, 4))
    return ((5 * k + 1, 1), (4 * k + 2, 3), (3 * k + 2, 4))


def weights(orientation, k):
    return (k, 1) if orientation == "root" else (1, k)


def projected(exposure, orientation, k):
    root, middle, leaf = exposure
    first = k * root + middle if orientation == "root" else root + k * middle
    return first, leaf


def rays(cone, k):
    return (
        ((1, 0), (2, k - 1)),
        ((2, k - 1), (1, k)),
        ((0, 1), (1, k)),
    )[cone]


def replay_symbolic_policy(orientation, record):
    checks = []
    cone = record["cone"]
    for ray_index, stored in enumerate(record["symbolic_inequalities"]):
        reconstructed = []
        for exposure in record["original_exposures"]:
            values = []
            for k in (2, 3):
                ray = rays(cone, k)[ray_index]
                face = faces(orientation, k)[cone]
                point = projected(exposure, orientation, k)
                values.append(
                    sum(a * b for a, b in zip(face, ray))
                    - sum(a * b for a, b in zip(point, ray))
                )
            slope = values[1] - values[0]
            reconstructed.append((tuple(exposure), slope, values[0] - 2 * slope, values[0]))
        stored_rows = {
            (
                tuple(item["exposure"]),
                item["slope"],
                item["intercept"],
                item["value_at_k2"],
            )
            for item in stored["margins"]
        }
        checks.append(
            set(reconstructed) == stored_rows
            and min(row[1] for row in reconstructed) == stored["minimum_slope"]
            and min(row[3] for row in reconstructed) == stored["minimum_value_at_k2"]
            and all(row[1] >= 0 and row[3] >= 0 for row in reconstructed)
        )
    return all(checks)


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    report = json.loads(SRC.read_text(encoding="utf-8"))
    antichains = []
    for orientation in ("root", "middle"):
        for k in FROZEN_RATIOS:
            actual = guarantees(weights(orientation, k))
            antichains.append(
                {
                    "orientation": orientation,
                    "k": k,
                    "actual": [list(item) for item in sorted(actual)],
                    "expected": [list(item) for item in sorted(faces(orientation, k))],
                    "matched": actual == frozenset(faces(orientation, k)),
                }
            )
    holdouts = []
    for item in report["prospective_holdouts"]:
        k = item["k"]
        x, y = item["base_and_leaf_costs"]
        expected = max(a * x + b * y for a, b in faces(item["orientation"], k))
        exact = exact_middle_first(tuple(item["level_costs"]), expected)
        holdouts.append(
            {
                "orientation": item["orientation"],
                "k": k,
                "base_and_leaf_costs": [x, y],
                "exact": exact,
                "expected": expected,
                "matched": exact == item["exact_cost"] == expected,
            }
        )
    policy_checks = [
        replay_symbolic_policy(orientation, item)
        for orientation, records in report["universal_upper_policies"].items()
        for item in records
    ]
    imports = len({name for name in sys.modules if name.startswith("theorica")} - before)
    result = {
        "schema": "theorica.middle-first-integer-ratio-family-audit/1",
        "production_imports": imports,
        "frozen_antichains_reproduced": sum(item["matched"] for item in antichains),
        "frozen_antichain_total": len(antichains),
        "holdouts_reproduced": sum(item["matched"] for item in holdouts),
        "holdout_total": len(holdouts),
        "symbolic_cones_reproduced": sum(policy_checks),
        "symbolic_cone_total": len(policy_checks),
        "antichains": antichains,
        "holdouts": holdouts,
    }
    result["passed"] = (
        imports == 0
        and result["frozen_antichains_reproduced"]
        == result["frozen_antichain_total"]
        == 8
        and result["holdouts_reproduced"] == result["holdout_total"] == 40
        and result["symbolic_cones_reproduced"]
        == result["symbolic_cone_total"]
        == 6
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in {"antichains", "holdouts"}},
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
