#!/usr/bin/env python3
"""Independent zero-production-import audit of the suffix-trie quotient."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb, factorial
from pathlib import Path

SOURCE = Path("results/qary_depth4_explicit_sentinel_suffix_trie_quotient/results.json")
OUT = Path("results/qary_depth4_explicit_sentinel_suffix_trie_quotient/audit.json")
Q, D = 3, 4
BASE = tuple(product(range(2), repeat=D))


def trie(family, leaf_depth, depth=0):
    if depth == leaf_depth:
        return {}
    node = {}
    for word in family:
        node.setdefault(word[depth], []).append(word)
    return {
        symbol: trie(tuple(words), leaf_depth, depth + 1)
        for symbol, words in node.items()
    }


def node_shape(node):
    return tuple(sorted((node_shape(child) for child in node.values()), key=repr))


def trie_shape(family, leaf_depth=D - 1):
    return node_shape(trie(family, leaf_depth))


def shape_json(shape):
    return [shape_json(child) for child in shape]


def product_int(values):
    result = 1
    for value in values:
        result *= value
    return result


def embedding_count(shape, q=Q):
    if not shape:
        return 1
    multiplicities = Counter(map(repr, shape))
    falling = factorial(q) // factorial(q - len(shape))
    symmetry = product_int(factorial(count) for count in multiplicities.values())
    return falling // symmetry * product_int(embedding_count(child, q) for child in shape)


def leaf_bijection(source, target):
    mapping = {}

    def descend(left, right, left_prefix=(), right_prefix=()):
        if not left and not right:
            mapping[left_prefix] = right_prefix
            return
        left_groups, right_groups = defaultdict(list), defaultdict(list)
        for symbol, child in left.items():
            left_groups[repr(node_shape(child))].append((symbol, child))
        for symbol, child in right.items():
            right_groups[repr(node_shape(child))].append((symbol, child))
        assert set(left_groups) == set(right_groups)
        for key in sorted(left_groups):
            left_children = sorted(left_groups[key])
            right_children = sorted(right_groups[key])
            assert len(left_children) == len(right_children)
            for (lsymbol, lchild), (rsymbol, rchild) in zip(
                left_children, right_children
            ):
                descend(
                    lchild,
                    rchild,
                    (*left_prefix, lsymbol),
                    (*right_prefix, rsymbol),
                )

    descend(trie(source, D - 1), trie(target, D - 1))
    return mapping


def rows(words):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(D)
        for prefix in product(range(Q), repeat=level)
    )


def query_level(query):
    offset = 0
    for depth in range(D):
        next_offset = offset + Q**depth
        if query < next_offset:
            return depth
        offset = next_offset
    raise ValueError(query)


def row_partition(row, completion_map=None):
    mapped = range(len(row)) if completion_map is None else completion_map
    return tuple(
        sorted(
            tuple(sorted(mapped[index] for index, value in enumerate(row) if value == answer))
            for answer in set(row)
        )
    )


def transport(source_suffixes, target_suffixes):
    suffix_map = leaf_bijection(source_suffixes, target_suffixes)
    source_words = (*BASE, *((2, *suffix) for suffix in source_suffixes))
    target_words = (*BASE, *((2, *suffix) for suffix in target_suffixes))
    target_indices = {suffix: len(BASE) + i for i, suffix in enumerate(target_suffixes)}
    completion_map = list(range(len(BASE))) + [
        target_indices[suffix_map[suffix]] for suffix in source_suffixes
    ]
    source_rows, target_rows = rows(source_words), rows(target_words)
    buckets = defaultdict(list)
    for query, row in enumerate(target_rows):
        buckets[(query_level(query), row_partition(row))].append(query)
    query_map = []
    for query, row in enumerate(source_rows):
        signature = (query_level(query), row_partition(row, completion_map))
        query_map.append(buckets[signature].pop(0))
    assert not any(buckets.values())
    cells = {}
    for query, row in enumerate(source_rows):
        target_query = query_map[query]
        for answer in sorted(set(row)):
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
            cells[f"{query}:{answer}"] = target_answer
    compact = {
        "completions": completion_map,
        "queries": query_map,
        "cells": cells,
        "certificate": {
            "constructive_partition_bijection": True,
            "mapping_edge_checked": True,
            "query_groups_mapped": len(query_map),
        },
    }
    digest = hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return compact, digest


def formula_grid_check(q, depth, k):
    suffixes = tuple(product(range(q), repeat=depth - 1))
    grouped = Counter(
        trie_shape(family, leaf_depth=depth - 1)
        for family in combinations(suffixes, k)
    )
    return all(size == embedding_count(shape, q) for shape, size in grouped.items()) and sum(
        grouped.values()
    ) == comb(len(suffixes), k)


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)

    def parse_family(family_id):
        return tuple(
            tuple(int(symbol) for symbol in word) for word in family_id.split("|")
        )

    suffixes = tuple(product(range(Q), repeat=D - 1))
    expected = set(combinations(suffixes, 3))
    observed = {parse_family(family_id) for family_id in result["catalogue"]}
    classes = {int(key): value for key, value in result["classes"].items()}
    representatives = {
        class_id: tuple(tuple(word) for word in row["representative_suffixes"])
        for class_id, row in classes.items()
    }

    transport_checks, counts, shapes = [], Counter(), set()
    for family_id, row in result["catalogue"].items():
        family = parse_family(family_id)
        class_id, expected_digest = row
        shape = trie_shape(family)
        assert shape_json(shape) == classes[class_id]["shape"]
        _, digest = transport(representatives[class_id], family)
        transport_checks.append(digest == expected_digest)
        counts[class_id] += 1
        shapes.add(repr(shape))

    holdout_checks = []
    for key, row in result["holdouts"].items():
        class_id = int(key)
        family = tuple(tuple(word) for word in row["suffixes"])
        compact, digest = transport(representatives[class_id], family)
        holdout_checks.append(
            compact == row["transport"] and digest == row["transport_sha256"]
        )

    formula_grid = {
        f"q={q},d={depth},k={k}": formula_grid_check(q, depth, k)
        for q in (3, 4)
        for depth in (2, 3, 4)
        for k in (2, 3)
    }
    cross = result["cross_representative_nonisomorphism"]
    cross_checks = len(cross) == 15 and all(
        row["isomorphic"] is False for row in cross.values()
    ) and len({repr(trie_shape(family)) for family in representatives.values()}) == 6
    passed = (
        observed == expected
        and len(shapes) == 6
        and all(transport_checks)
        and len(transport_checks) == 2925
        and all(holdout_checks)
        and len(holdout_checks) == 6
        and cross_checks
        and all(formula_grid.values())
        and {str(key): value for key, value in sorted(counts.items())}
        == result["class_sizes"]
    )
    report = {
        "schema": "theorica.depth4-explicit-sentinel-suffix-trie-quotient-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": len(observed),
        "trie_shapes_reconstructed": len(shapes),
        "transport_digests_reproduced": sum(transport_checks),
        "holdout_maps_reproduced": sum(holdout_checks),
        "cross_class_nonisomorphisms_checked": len(cross),
        "recursive_formula_grid_checks": sum(formula_grid.values()),
        "class_sizes": result["class_sizes"],
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
