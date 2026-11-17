#!/usr/bin/env python3
"""Complete two-word obstruction quotient with prospective exact holdouts."""
from __future__ import annotations

import importlib.util
import json
from itertools import combinations, product
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sentinel", Path("scripts/verify_qary_ternary_explicit_outside_sentinel.py")
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

OUT = Path("results/qary_ternary_explicit_sentinel_orbit_quotient/results.json")
COSTS = (1, 23)
CLASS_SPECS = {
    "same_middle": {
        "representative": ((2, 0, 0), (2, 0, 1)),
        "holdout": ((2, 2, 1), (2, 2, 2)),
        "predictions": {
            1: {"value": 6, "groups": [4, 5, 7, 8, 12], "counts": [5600, 3532, 49]},
            23: {"value": 69, "groups": [12], "counts": [5600, 3532, 49]},
        },
    },
    "different_middle": {
        "representative": ((2, 0, 0), (2, 1, 0)),
        "holdout": ((2, 1, 2), (2, 2, 1)),
        "predictions": {
            1: {
                "value": 7,
                "groups": [0, 4, 5, 7, 8, 11, 12],
                "counts": [20085, 15794, 95],
            },
            23: {"value": 38, "groups": [0], "counts": [20085, 15794, 95]},
        },
    },
}


def words(pair):
    return (*V.H.BASE, *pair)


def endpoint(pair, c):
    exact = V.S.exact_value(words(pair), (4, 11, c), V.S.witness_state())
    actions = {row["query_group"]: row for row in exact["root_actions"]}
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            group for group, row in actions.items() if row["optimal"]
        ),
        "root_actions": actions,
        "exact": exact,
    }


def pair_json(pair):
    return [list(word) for word in pair]


def family_id(pair):
    return "|".join("".join(map(str, word)) for word in pair)


def main():
    V.H.rows = V.sentinel_rows
    V.S.H.rows = V.sentinel_rows
    fibre = tuple((2, x, y) for x, y in product(range(3), repeat=2))
    pairs = tuple(combinations(fibre, 2))
    representatives = {
        name: words(spec["representative"]) for name, spec in CLASS_SPECS.items()
    }

    catalogue = []
    class_sizes = {name: 0 for name in CLASS_SPECS}
    for pair in pairs:
        family = words(pair)
        matched = []
        certificates = {}
        mappings = {}
        for name, representative in representatives.items():
            mapping, certificate = V.H.isomorphism(
                V.H.graph(representative), V.H.graph(family)
            )
            certificates[name] = certificate
            if mapping is not None:
                matched.append(name)
                mappings[name] = V.H.compact(mapping, representative, family)
        if len(matched) != 1:
            raise RuntimeError(f"family {pair} matched classes {matched}")
        class_name = matched[0]
        class_sizes[class_name] += 1
        catalogue.append(
            {
                "family_id": family_id(pair),
                "pair": pair_json(pair),
                "middle_relation": "same" if pair[0][1] == pair[1][1] else "different",
                "class": class_name,
                "isomorphism": mappings[class_name],
                "isomorphism_certificate": certificates[class_name],
                "other_class_certificate": certificates[
                    next(name for name in CLASS_SPECS if name != class_name)
                ],
            }
        )

    class_results = {}
    holdout_checks = {}
    for name, spec in CLASS_SPECS.items():
        representative_pair = spec["representative"]
        holdout_pair = spec["holdout"]
        representative_sweep = [
            endpoint(representative_pair, c) for c in range(1, 24)
        ]
        representative_rows = [representative_sweep[c - 1] for c in COSTS]
        holdout_rows = [endpoint(holdout_pair, c) for c in COSTS]
        mapping, certificate = V.H.isomorphism(
            V.H.graph(words(representative_pair)), V.H.graph(words(holdout_pair))
        )
        if mapping is None:
            raise RuntimeError(f"holdout {name} lost structural transport")
        compact = V.H.compact(
            mapping, words(representative_pair), words(holdout_pair)
        )
        checks = {}
        for representative, holdout in zip(representative_rows, holdout_rows):
            c = representative["leaf_cost"]
            predicted = spec["predictions"][c]
            transported_groups = sorted(
                compact["queries"][group]
                for group in representative["optimal_groups"]
            )
            child_transport = all(
                sorted(representative["root_actions"][group]["child_values"])
                == sorted(
                    holdout["root_actions"][compact["queries"][group]][
                        "child_values"
                    ]
                )
                for group in representative["optimal_groups"]
            )
            counts = [
                holdout["exact"][key]
                for key in (
                    "states_solved",
                    "actions_evaluated",
                    "compatibility_states",
                )
            ]
            checks[str(c)] = {
                "representative_bounds_equal": representative["exact"][
                    "exact_lower_bound"
                ]
                == representative["exact"]["constructive_upper_bound"],
                "holdout_bounds_equal": holdout["exact"]["exact_lower_bound"]
                == holdout["exact"]["constructive_upper_bound"],
                "value": holdout["exact_value"] == predicted["value"],
                "transported_groups": transported_groups == predicted["groups"]
                == holdout["optimal_groups"],
                "child_multisets": child_transport,
                "search_counts": counts == predicted["counts"],
                "source_target_counts_equal": all(
                    representative["exact"][key] == holdout["exact"][key]
                    for key in (
                        "states_solved",
                        "actions_evaluated",
                        "compatibility_states",
                    )
                ),
            }
        class_results[name] = {
            "representative_pair": pair_json(representative_pair),
            "holdout_pair": pair_json(holdout_pair),
            "representative_integer_sweep": representative_sweep,
            "representative_endpoints": representative_rows,
            "holdout_endpoints": holdout_rows,
            "holdout_isomorphism": compact,
            "holdout_isomorphism_certificate": certificate,
        }
        holdout_checks[name] = checks

    structural_pass = (
        len(catalogue) == 36
        and class_sizes == {"same_middle": 9, "different_middle": 27}
        and all(
            (row["middle_relation"] == "same")
            == (row["class"] == "same_middle")
            for row in catalogue
        )
        and all(
            row["isomorphism_certificate"].get("mapping_edge_checked") is True
            for row in catalogue
        )
    )
    holdouts_pass = all(
        all(all(values.values()) for values in checks.values())
        for checks in holdout_checks.values()
    )
    same_values = [
        row["exact_value"]
        for row in class_results["same_middle"]["representative_integer_sweep"]
    ]
    different_values = [
        row["exact_value"]
        for row in class_results["different_middle"]["representative_integer_sweep"]
    ]
    chamber_laws_pass = (
        same_values[0] == 6
        and all(same_values[c - 1] == 4 + 3 * c for c in range(2, 12))
        and all(same_values[c - 1] == 15 + 2 * c for c in range(12, 16))
        and all(same_values[c - 1] == 3 * c for c in range(16, 24))
        and all(different_values[c - 1] == 4 + 3 * c for c in range(1, 11))
        and all(different_values[c - 1] == 37 for c in range(11, 23))
        and different_values[22] == 38
        and same_values[0] < different_values[0]
        and all(same_values[c - 1] == different_values[c - 1] for c in range(2, 12))
        and all(same_values[c - 1] > different_values[c - 1] for c in range(12, 24))
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-orbit-quotient/1",
        "outside_response": -1,
        "fixed_root_middle_costs": [4, 11],
        "leaf_costs": list(COSTS),
        "family_count": len(catalogue),
        "class_sizes": class_sizes,
        "representative_solve_reduction": 18,
        "catalogue": catalogue,
        "class_results": class_results,
        "holdout_checks": holdout_checks,
        "post_holdout_exact_integer_laws": {
            "same_middle": {
                "c=1": "V=6",
                "2<=c<=11": "V=4+3c",
                "12<=c<=15": "V=15+2c",
                "16<=c<=23": "V=3c",
            },
            "different_middle": {
                "1<=c<=10": "V=4+3c",
                "11<=c<=22": "V=37",
                "c=23": "V=38",
            },
            "class_order": {
                "c=1": "same_middle<different_middle",
                "2<=c<=11": "same_middle=different_middle",
                "12<=c<=23": "same_middle>different_middle",
            },
        },
        "summary": {
            "two_class_structural_theorem_passed": structural_pass,
            "same_middle_values_c1_c23": [
                row["exact_value"]
                for row in class_results["same_middle"]["representative_endpoints"]
            ],
            "different_middle_values_c1_c23": [
                row["exact_value"]
                for row in class_results["different_middle"][
                    "representative_endpoints"
                ]
            ],
            "all_frozen_holdouts_passed": holdouts_pass,
            "post_holdout_chamber_laws_passed": chamber_laws_pass,
            "overall_passed": structural_pass and holdouts_pass and chamber_laws_pass,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if report["summary"]["overall_passed"] else 1)


if __name__ == "__main__":
    main()
