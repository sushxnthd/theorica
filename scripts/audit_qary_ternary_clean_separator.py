#!/usr/bin/env python3
"""Independent artifact audit for the clean-separator experiment."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_clean_separator/results.json")
OUT = Path("results/qary_ternary_clean_separator/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    witnesses = source["clean_separator"]["witnesses"]
    cells_valid = bool(witnesses) and all(
        len([cell for cell in witness["cells"] if cell["zero_lie"]]) == 2
        and all(
            len(cell["zero_lie"]) == 1 and not cell["one_lie"]
            for cell in witness["cells"]
            if cell["zero_lie"]
        )
        for witness in witnesses
    )
    prospective = source["prospective"]
    expected = 3 * prospective["level_costs"][1]
    bounds_agree = (
        prospective["predicted_value"]
        == prospective["exact_lower_bound"]
        == prospective["constructive_upper_bound"]
        == expected
    )
    sealed_count_valid = (
        source["opened_reserved_cases"] == 1
        and source["remaining_reserved_cases"] == 17
    )
    passed = cells_valid and bounds_agree and sealed_count_valid
    report = {
        "schema": "theorica.ternary-clean-separator-audit/1",
        "clean_separator_cells_valid": cells_valid,
        "independent_formula_value": expected,
        "exact_bounds_agree": bounds_agree,
        "sealed_count_valid": sealed_count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
