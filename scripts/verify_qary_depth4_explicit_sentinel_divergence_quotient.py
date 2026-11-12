#!/usr/bin/env python3
"""Complete q=3, d=4 test of the frozen divergence quotient theorem."""
from __future__ import annotations

import importlib.util
import json
from itertools import combinations, product
from math import comb
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "iso_helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)

OUT = Path("results/qary_depth4_explicit_sentinel_divergence_quotient/results.json")
Q = 3
D = 4
BASE = tuple(product(range(2), repeat=D))
FIBRE = tuple((2, *suffix) for suffix in product(range(Q), repeat=D - 1))
PAIRS = tuple(combinations(FIBRE, 2))
SPECS = {
    0: {
        "representative": ((2, 0, 0, 0), (2, 1, 0, 0)),
        "holdout": ((2, 1, 2, 1), (2, 2, 0, 2)),
        "predicted_size": 243,
    },
    1: {
        "representative": ((2, 0, 0, 0), (2, 0, 1, 0)),
        "holdout": ((2, 2, 0, 1), (2, 2, 2, 2)),
        "predicted_size": 81,
    },
    2: {
        "representative": ((2, 0, 0, 0), (2, 0, 0, 1)),
        "holdout": ((2, 1, 2, 0), (2, 1, 2, 2)),
        "predicted_size": 27,
    },
}


def rows(words):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(D)
        for prefix in product(range(Q), repeat=level)
    )


def level(query):
    offset = 0
    for depth in range(D):
        next_offset = offset + Q**depth
        if query < next_offset:
            return depth
        offset = next_offset
    raise ValueError(query)


def graph(words):
    color, adjacent = {}, {}
    for index in range(len(words)):
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


def row_partition(row, completion_map=None):
    mapped = range(len(row)) if completion_map is None else completion_map
    return tuple(
        sorted(
            tuple(sorted(mapped[index] for index, value in enumerate(row) if value == answer))
            for answer in set(row)
        )
    )


def constructive_transport(source, target):
    source_rows, target_rows = rows(source), rows(target)
    completion_map = list(range(len(source)))
    target_buckets = {}
    for query, row in enumerate(target_rows):
        target_buckets.setdefault((level(query), row_partition(row)), []).append(query)
    query_map = []
    for query, row in enumerate(source_rows):
        signature = (level(query), row_partition(row, completion_map))
        candidates = target_buckets.get(signature, [])
        if not candidates:
            raise RuntimeError(f"missing target query for source query {query}")
        query_map.append(candidates.pop(0))
    if any(candidates for candidates in target_buckets.values()):
        raise RuntimeError("target query mapping is not surjective")
    cell_map = {}
    for query, row in enumerate(source_rows):
        for answer in sorted(set(row)):
            target_query = query_map[query]
            source_cell = {
                completion_map[index] for index, value in enumerate(row) if value == answer
            }
            target_answer = next(
                value
                for value in set(target_rows[target_query])
                if {
                    index
                    for index, candidate in enumerate(target_rows[target_query])
                    if candidate == value
                }
                == source_cell
            )
            if any(
                (value == answer)
                != (target_rows[target_query][completion_map[index]] == target_answer)
                for index, value in enumerate(row)
            ):
                raise RuntimeError("invalid response-cell transport")
            cell_map[f"{query}:{answer}"] = target_answer
    return {
        "completions": completion_map,
        "queries": query_map,
        "cells": cell_map,
        "certificate": {
            "constructive_partition_bijection": True,
            "mapping_edge_checked": True,
            "query_groups_mapped": len(query_map),
        },
    }


def divergence_class(pair):
    for index, (left, right) in enumerate(zip(pair[0][1:], pair[1][1:])):
        if left != right:
            return index
    raise ValueError("pair is not distinct")


def pair_json(pair):
    return [list(word) for word in pair]


def main():
    representatives = {
        r: (*BASE, *spec["representative"]) for r, spec in SPECS.items()
    }
    representative_graphs = {r: graph(words) for r, words in representatives.items()}
    catalogue = []
    class_sizes = {str(r): 0 for r in SPECS}
    for pair in PAIRS:
        family = (*BASE, *pair)
        r = divergence_class(pair)
        transport = constructive_transport(representatives[r], family)
        class_sizes[str(r)] += 1
        catalogue.append(
            {
                "pair": pair_json(pair),
                "computed_common_suffix_prefix": divergence_class(pair),
                "class": r,
                "isomorphism": transport,
                "isomorphism_certificate": transport["certificate"],
            }
        )

    holdouts = {}
    for r, spec in SPECS.items():
        source = representatives[r]
        target = (*BASE, *spec["holdout"])
        transport = constructive_transport(source, target)
        holdouts[str(r)] = {
            "pair": pair_json(spec["holdout"]),
            "computed_common_suffix_prefix": divergence_class(spec["holdout"]),
            "isomorphism": transport,
            "certificate": transport["certificate"],
        }

    cross_representative_nonisomorphism = {}
    for left, right in combinations(SPECS, 2):
        mapping, certificate = H.isomorphism(
            representative_graphs[left], representative_graphs[right]
        )
        cross_representative_nonisomorphism[f"{left}:{right}"] = {
            "isomorphic": mapping is not None,
            "certificate": certificate,
        }

    predicted_sizes = {
        str(r): comb(Q, 2) * Q**r * Q ** (2 * (D - r - 2)) for r in SPECS
    }
    expected_total = comb(Q ** (D - 1), 2)
    structural_pass = (
        len(catalogue) == expected_total
        and class_sizes == predicted_sizes
        and all(row["class"] == row["computed_common_suffix_prefix"] for row in catalogue)
        and all(
            row["isomorphism_certificate"].get("mapping_edge_checked") is True
            for row in catalogue
        )
        and all(not row["isomorphic"] for row in cross_representative_nonisomorphism.values())
        and all(
            row["computed_common_suffix_prefix"] == int(r)
            and row["certificate"].get("mapping_edge_checked") is True
            for r, row in holdouts.items()
        )
        and sum(predicted_sizes.values()) == expected_total
    )
    report = {
        "schema": "theorica.depth4-explicit-sentinel-divergence-quotient/1",
        "alphabet_size": Q,
        "depth": D,
        "base_size": len(BASE),
        "fibre_size": len(FIBRE),
        "family_count": len(catalogue),
        "class_count": len(class_sizes),
        "class_sizes": class_sizes,
        "predicted_class_sizes": predicted_sizes,
        "representative_solve_reduction": expected_total // len(SPECS),
        "catalogue": catalogue,
        "holdouts": holdouts,
        "cross_representative_nonisomorphism": cross_representative_nonisomorphism,
        "summary": {
            "divergence_invariant_complete": structural_pass,
            "all_351_families_classified": len(catalogue) == 351,
            "all_frozen_holdouts_passed": all(
                row["computed_common_suffix_prefix"] == int(r)
                for r, row in holdouts.items()
            ),
            "closed_form_counts_passed": class_sizes == predicted_sizes,
            "overall_passed": structural_pass,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if structural_pass else 1)


if __name__ == "__main__":
    main()
