#!/usr/bin/env python3
"""Independent zero-production-import audit of the k=4 trie recurrence."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from functools import cache
from itertools import combinations, combinations_with_replacement, product
from math import comb, factorial
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "independent_suffix_audit",
    Path("scripts/audit_qary_depth4_explicit_sentinel_suffix_trie_quotient.py"),
)
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

SOURCE = Path("results/qary_ternary_four_word_suffix_trie_recurrence/results.json")
OUT = Path("results/qary_ternary_four_word_suffix_trie_recurrence/audit.json")
Q, D, K = 3, 4, 4
SUFFIXES = tuple(product(range(Q), repeat=D - 1))


@cache
def leaves(shape):
    return 1 if not shape else sum(leaves(child) for child in shape)


@cache
def generated_shapes(height, count, q):
    if height == 0:
        return ((),) if count == 1 else ()
    candidates = sorted(
        {shape for size in range(1, count + 1) for shape in generated_shapes(height - 1, size, q)},
        key=repr,
    )
    found = set()
    for arity in range(1, min(q, count) + 1):
        for children in combinations_with_replacement(candidates, arity):
            if sum(leaves(child) for child in children) == count:
                found.add(tuple(sorted(children, key=repr)))
    return tuple(sorted(found, key=repr))


@cache
def embeddings(shape, q):
    if not shape:
        return 1
    symmetry = 1
    for child in set(shape):
        symmetry *= factorial(shape.count(child))
    result = factorial(q) // factorial(q - len(shape)) // symmetry
    for child in shape:
        result *= embeddings(child, q)
    return result


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    classes = {int(key): value for key, value in result["classes"].items()}
    representatives = {
        class_id: tuple(tuple(word) for word in row["representative_suffixes"])
        for class_id, row in classes.items()
    }
    shapes = generated_shapes(D - 1, K, Q)
    shape_class = {shape: index for index, shape in enumerate(shapes)}
    aggregate = hashlib.sha256()
    class_aggregates = {index: hashlib.sha256() for index in representatives}
    counts = Counter()
    transport_checks = 0
    for family in combinations(SUFFIXES, K):
        class_id = shape_class[A.trie_shape(family)]
        _, digest = A.transport(representatives[class_id], family)
        row = f"{family_id(family)}|{class_id}|{digest}\n".encode()
        aggregate.update(row)
        class_aggregates[class_id].update(row)
        counts[class_id] += 1
        transport_checks += 1

    holdout_checks = []
    for key, row in result["holdouts"].items():
        class_id = int(key)
        family = tuple(tuple(word) for word in row["suffixes"])
        compact, digest = A.transport(representatives[class_id], family)
        holdout_checks.append(compact == row["transport"] and digest == row["transport_sha256"])

    class_sizes = {str(index): counts[index] for index in range(len(shapes))}
    recurrence_sizes = {str(index): embeddings(shape, Q) for index, shape in enumerate(shapes)}
    q4_shapes = generated_shapes(D - 1, K, 4)
    q4_sum = sum(embeddings(shape, 4) for shape in q4_shapes)
    stream_ok = aggregate.hexdigest() == result["all_family_transport_stream_sha256"]
    class_streams = sum(
        class_aggregates[index].hexdigest() == classes[index]["transport_stream_sha256"]
        for index in representatives
    )
    cross = result["cross_representative_nonisomorphism"]
    passed = (
        transport_checks == comb(len(SUFFIXES), K) == 17550
        and len(shapes) == 11
        and class_sizes == result["class_sizes"] == recurrence_sizes
        and stream_ok
        and class_streams == 11
        and len(holdout_checks) == 11
        and all(holdout_checks)
        and len(cross) == 55
        and all(not row["isomorphic"] for row in cross.values())
        and len(q4_shapes) == 14
        and q4_sum == comb(64, 4) == 635376
    )
    report = {
        "schema": "theorica.ternary-four-word-suffix-trie-recurrence-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": transport_checks,
        "trie_shapes_reconstructed": len(shapes),
        "transport_digests_reproduced": transport_checks,
        "aggregate_transport_stream_reproduced": stream_ok,
        "class_transport_streams_reproduced": class_streams,
        "holdout_maps_reproduced": sum(holdout_checks),
        "cross_class_nonisomorphisms_checked": len(cross),
        "q4_shapes_reconstructed": len(q4_shapes),
        "q4_count_identity_sum": q4_sum,
        "class_sizes": class_sizes,
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
