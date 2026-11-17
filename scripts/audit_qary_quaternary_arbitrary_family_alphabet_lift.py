#!/usr/bin/env python3
"""Independent zero-production-import audit of the q=4 alphabet lift."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "independent_suffix_audit",
    Path("scripts/audit_qary_depth4_explicit_sentinel_suffix_trie_quotient.py"),
)
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
A.Q = 4

SOURCE = Path("results/qary_quaternary_arbitrary_family_alphabet_lift/results.json")
OUT = Path("results/qary_quaternary_arbitrary_family_alphabet_lift/audit.json")
Q, D, K = 4, 4, 3
SUFFIXES = tuple(product(range(Q), repeat=D - 1))


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
    shapes = sorted({A.trie_shape(family) for family in representatives.values()}, key=repr)
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
        holdout_checks.append(
            compact == row["transport"] and digest == row["transport_sha256"]
        )

    class_sizes = {str(key): value for key, value in sorted(counts.items())}
    recursive_sizes = {
        str(index): A.embedding_count(shape, Q) for index, shape in enumerate(shapes)
    }
    q5_counts = {
        "0": 5**4 * 4**2 // 2,
        "1": 5**5 * 4**2 // 2,
        "2": 5**2 * comb(5, 3),
        "3": 5**6 * 4**2 // 2,
        "4": 5**4 * comb(5, 3),
        "5": 5**6 * comb(5, 3),
    }
    stream_checks = aggregate.hexdigest() == result["all_family_transport_stream_sha256"]
    class_stream_checks = all(
        class_aggregates[index].hexdigest()
        == classes[index]["transport_stream_sha256"]
        for index in representatives
    )
    cross = result["cross_representative_nonisomorphism"]
    passed = (
        transport_checks == comb(len(SUFFIXES), K) == 41664
        and len(shapes) == 6
        and class_sizes == result["class_sizes"] == recursive_sizes
        and stream_checks
        and class_stream_checks
        and len(holdout_checks) == 6
        and all(holdout_checks)
        and len(cross) == 15
        and all(not row["isomorphic"] for row in cross.values())
        and q5_counts == result["q5_symbolic_identity_counts"]
        and sum(q5_counts.values()) == comb(5**3, 3)
    )
    report = {
        "schema": "theorica.quaternary-arbitrary-family-alphabet-lift-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": transport_checks,
        "trie_shapes_reconstructed": len(shapes),
        "transport_digests_reproduced": transport_checks,
        "aggregate_transport_stream_reproduced": stream_checks,
        "class_transport_streams_reproduced": sum(
            class_aggregates[index].hexdigest()
            == classes[index]["transport_stream_sha256"]
            for index in representatives
        ),
        "holdout_maps_reproduced": sum(holdout_checks),
        "cross_class_nonisomorphisms_checked": len(cross),
        "q5_count_identity_passed": sum(q5_counts.values()) == comb(5**3, 3),
        "class_sizes": class_sizes,
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
