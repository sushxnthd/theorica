#!/usr/bin/env python3
"""Prospective q=4 orbit classification and exact symbol-3 holdouts."""
from __future__ import annotations

import importlib.util
import json
from itertools import combinations, product
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = load("q4_helper", "scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
S = load("q4_solver", "scripts/verify_qary_ternary_clean_separator.py")
OUT = Path("results/qary_quaternary_explicit_sentinel_orbit_transfer/results.json")
BASE = tuple(product(range(2), repeat=3))
FIBRE = tuple((2, x, y) for x, y in product(range(4), repeat=2))
PAIRS = tuple(combinations(FIBRE, 2))
LEVEL_COSTS = (4, 11)
LEAF_COSTS = (1, 23)
CLASSES = {
    "same_middle": {
        "representative": ((2, 0, 0), (2, 0, 1)),
        "holdout": ((2, 3, 1), (2, 3, 3)),
        "values": {1: 6, 23: 69},
    },
    "different_middle": {
        "representative": ((2, 0, 0), (2, 1, 0)),
        "holdout": ((2, 0, 3), (2, 3, 0)),
        "values": {1: 7, 23: 38},
    },
}


def rows(words, q=4):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(3)
        for prefix in product(range(q), repeat=level)
    )


def level(query, q=4):
    return 0 if query < 1 else 1 if query < 1 + q else 2


def graph(words):
    color, adjacent = {}, {}
    for index in range(10):
        color[f"c:{index}"] = "c"
        adjacent[f"c:{index}"] = set()
    for query, row in enumerate(rows(words)):
        query_vertex = f"q:{query}"
        color[query_vertex] = f"q:{level(query)}"
        adjacent[query_vertex] = set()
        for answer in sorted(set(row)):
            response_vertex = f"r:{query}:{answer}"
            color[response_vertex] = f"r:{level(query)}"
            adjacent[response_vertex] = {query_vertex}
            adjacent[query_vertex].add(response_vertex)
            for index, value in enumerate(row):
                if value == answer:
                    adjacent[response_vertex].add(f"c:{index}")
                    adjacent[f"c:{index}"].add(response_vertex)
    return color, adjacent


def compact(mapping, source, target):
    source_rows, target_rows = rows(source), rows(target)
    completion_map = [int(mapping[f"c:{i}"].split(":")[1]) for i in range(10)]
    query_map = [int(mapping[f"q:{q}"].split(":")[1]) for q in range(21)]
    cell_map = {}
    for query, row in enumerate(source_rows):
        for answer in sorted(set(row)):
            _, target_query, target_answer = mapping[f"r:{query}:{answer}"].split(":")
            target_query, target_answer = int(target_query), int(target_answer)
            if target_query != query_map[query] or any(
                (value == answer)
                != (target_rows[target_query][completion_map[index]] == target_answer)
                for index, value in enumerate(row)
            ):
                raise RuntimeError("invalid response-cell map")
            cell_map[f"{query}:{answer}"] = target_answer
    return {"completions": completion_map, "queries": query_map, "cells": cell_map}


def partition(row):
    return tuple(sorted(tuple(i for i, value in enumerate(row) if value == answer) for answer in set(row)))


def active_signature(words, q):
    return tuple(
        sorted(
            (level(query, q), partition(row))
            for query, row in enumerate(rows(words, q))
            if len(set(row)) > 1
        )
    )


def state():
    return ((1,) * 8 + (0, 0), 1, (3, 3) + (4,) * 19)


def endpoint(pair, leaf_cost):
    exact = S.exact_value((*BASE, *pair), (*LEVEL_COSTS, leaf_cost), state())
    return {
        "leaf_cost": leaf_cost,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            row["query_group"] for row in exact["root_actions"] if row["optimal"]
        ),
        "exact": exact,
    }


def main():
    H.rows, H.level = rows, level
    S.H.rows, S.H.level = rows, level
    representatives = {
        name: (*BASE, *spec["representative"]) for name, spec in CLASSES.items()
    }
    catalogue, class_sizes = [], {name: 0 for name in CLASSES}
    for pair in PAIRS:
        family = (*BASE, *pair)
        matches = []
        for name, representative in representatives.items():
            mapping, certificate = H.isomorphism(graph(representative), graph(family))
            if mapping is not None:
                matches.append((name, mapping, certificate))
        if len(matches) != 1:
            raise RuntimeError(f"family {pair} matched {len(matches)} classes")
        name, mapping, certificate = matches[0]
        class_sizes[name] += 1
        catalogue.append(
            {
                "pair": [list(word) for word in pair],
                "class": name,
                "middle_relation": "same" if pair[0][1] == pair[1][1] else "different",
                "isomorphism": compact(mapping, representatives[name], family),
                "certificate": certificate,
            }
        )

    class_results, holdout_checks = {}, {}
    for name, spec in CLASSES.items():
        representative = spec["representative"]
        holdout = spec["holdout"]
        source = (*BASE, *representative)
        target = (*BASE, *holdout)
        mapping, certificate = H.isomorphism(graph(source), graph(target))
        assert mapping is not None
        transport = compact(mapping, source, target)
        representative_endpoints = [endpoint(representative, c) for c in LEAF_COSTS]
        holdout_endpoints = [endpoint(holdout, c) for c in LEAF_COSTS]
        checks = {}
        for source_row, target_row in zip(representative_endpoints, holdout_endpoints):
            c = source_row["leaf_cost"]
            checks[str(c)] = {
                "frozen_value": target_row["exact_value"] == spec["values"][c],
                "bounds_closed": target_row["exact"]["exact_lower_bound"]
                == target_row["exact"]["constructive_upper_bound"],
                "transported_optima": sorted(
                    transport["queries"][query]
                    for query in source_row["optimal_groups"]
                )
                == target_row["optimal_groups"],
                "search_counts_equal": all(
                    source_row["exact"][key] == target_row["exact"][key]
                    for key in ("states_solved", "actions_evaluated", "compatibility_states")
                ),
            }
        class_results[name] = {
            "representative": [list(word) for word in representative],
            "holdout": [list(word) for word in holdout],
            "q3_active_rows": len(active_signature(source, 3)),
            "q4_active_rows": len(active_signature(source, 4)),
            "active_row_reduction_equal": active_signature(source, 3)
            == active_signature(source, 4),
            "representative_endpoints": representative_endpoints,
            "holdout_endpoints": holdout_endpoints,
            "holdout_transport": transport,
            "holdout_certificate": certificate,
        }
        holdout_checks[name] = checks

    structural_pass = (
        len(catalogue) == 120
        and class_sizes == {"same_middle": 24, "different_middle": 96}
        and all(
            (row["middle_relation"] == "same") == (row["class"] == "same_middle")
            and row["certificate"].get("mapping_edge_checked") is True
            for row in catalogue
        )
    )
    reduction_pass = all(row["active_row_reduction_equal"] for row in class_results.values())
    holdouts_pass = all(
        all(all(check.values()) for check in rows_by_cost.values())
        for rows_by_cost in holdout_checks.values()
    )
    report = {
        "schema": "theorica.quaternary-explicit-sentinel-orbit-transfer/1",
        "alphabet_size": 4,
        "family_count": len(catalogue),
        "class_sizes": class_sizes,
        "representative_solve_reduction": 60,
        "catalogue": catalogue,
        "class_results": class_results,
        "holdout_checks": holdout_checks,
        "summary": {
            "two_class_generalization_passed": structural_pass,
            "active_row_reduction_passed": reduction_pass,
            "all_frozen_symbol3_holdouts_passed": holdouts_pass,
            "overall_passed": structural_pass and reduction_pass and holdouts_pass,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if report["summary"]["overall_passed"] else 1)


if __name__ == "__main__":
    main()
