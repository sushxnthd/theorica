#!/usr/bin/env python3
"""Complete q=4,d=4,k=3 alphabet-lift experiment."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from itertools import combinations, product
from math import comb
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "suffix_trie",
    Path("scripts/verify_qary_depth4_explicit_sentinel_suffix_trie_quotient.py"),
)
assert SPEC and SPEC.loader
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)
S.Q = 4

OUT = Path("results/qary_quaternary_arbitrary_family_alphabet_lift/results.json")
Q, D, K = 4, 4, 3
SUFFIXES = tuple(product(range(Q), repeat=D - 1))
FROZEN_COUNTS = {"0": 1152, "1": 4608, "2": 64, "3": 18432, "4": 1024, "5": 16384}
FROZEN_HOLDOUTS = (
    ((3, 2, 3), (3, 3, 2), (3, 3, 3)),
    ((2, 3, 3), (3, 3, 2), (3, 3, 3)),
    ((3, 3, 1), (3, 3, 2), (3, 3, 3)),
    ((2, 3, 3), (3, 2, 3), (3, 3, 3)),
    ((3, 1, 3), (3, 2, 3), (3, 3, 3)),
    ((1, 3, 3), (2, 3, 3), (3, 3, 3)),
)


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def predicted_counts(q):
    choose_three = comb(q, 3)
    return {
        "0": q**4 * (q - 1) ** 2 // 2,
        "1": q**5 * (q - 1) ** 2 // 2,
        "2": q**2 * choose_three,
        "3": q**6 * (q - 1) ** 2 // 2,
        "4": q**4 * choose_three,
        "5": q**6 * choose_three,
    }


def main():
    grouped = defaultdict(list)
    for family in combinations(SUFFIXES, K):
        grouped[S.trie_shape(family)].append(family)
    shapes = sorted(grouped, key=repr)
    if len(shapes) != 6:
        raise RuntimeError(f"expected six shapes, found {len(shapes)}")
    representatives = {index: grouped[shape][0] for index, shape in enumerate(shapes)}
    holdouts = {index: grouped[shape][-1] for index, shape in enumerate(shapes)}
    if tuple(holdouts.values()) != FROZEN_HOLDOUTS:
        raise RuntimeError("symbol-3 holdouts differ from frozen protocol")
    shape_class = {shape: index for index, shape in enumerate(shapes)}

    aggregate = hashlib.sha256()
    class_aggregates = {index: hashlib.sha256() for index in representatives}
    transport_checks = 0
    for family in combinations(SUFFIXES, K):
        class_id = shape_class[S.trie_shape(family)]
        _, digest = S.constructive_transport(representatives[class_id], family)
        row = f"{family_id(family)}|{class_id}|{digest}\n".encode()
        aggregate.update(row)
        class_aggregates[class_id].update(row)
        transport_checks += 1

    holdout_rows = {}
    for class_id, family in holdouts.items():
        compact, digest = S.constructive_transport(representatives[class_id], family)
        holdout_rows[str(class_id)] = {
            "suffixes": [list(word) for word in family],
            "shape": S.shape_json(shapes[class_id]),
            "transport": compact,
            "transport_sha256": digest,
        }

    graphs = {
        class_id: S.graph((*S.BASE, *((2, *suffix) for suffix in family)))
        for class_id, family in representatives.items()
    }
    cross = {}
    for left, right in combinations(representatives, 2):
        mapping, certificate = S.H.isomorphism(graphs[left], graphs[right])
        cross[f"{left}:{right}"] = {
            "isomorphic": mapping is not None,
            "certificate": certificate,
        }

    class_sizes = {str(i): len(grouped[shape]) for i, shape in enumerate(shapes)}
    recursive_sizes = {str(i): S.embedding_count(shape, Q) for i, shape in enumerate(shapes)}
    q5_counts = predicted_counts(5)
    passed = (
        sum(class_sizes.values()) == comb(len(SUFFIXES), K) == 41664
        and class_sizes == FROZEN_COUNTS == recursive_sizes == predicted_counts(Q)
        and sum(q5_counts.values()) == comb(5**3, 3)
        and transport_checks == 41664
        and len(holdout_rows) == 6
        and all(not row["isomorphic"] for row in cross.values())
    )
    report = {
        "schema": "theorica.quaternary-arbitrary-family-alphabet-lift/1",
        "alphabet_size": Q,
        "depth": D,
        "added_words": K,
        "family_count": transport_checks,
        "class_count": len(shapes),
        "class_sizes": class_sizes,
        "frozen_counts": FROZEN_COUNTS,
        "recursive_formula_counts": recursive_sizes,
        "q5_symbolic_identity_counts": q5_counts,
        "representative_solve_reduction": {"from": 41664, "to": 6, "factor": 6944},
        "classes": {
            str(i): {
                "shape": S.shape_json(shape),
                "representative_suffixes": [list(word) for word in representatives[i]],
                "holdout_suffixes": [list(word) for word in holdouts[i]],
                "transport_stream_sha256": class_aggregates[i].hexdigest(),
            }
            for i, shape in enumerate(shapes)
        },
        "all_family_transport_stream_sha256": aggregate.hexdigest(),
        "holdouts": holdout_rows,
        "cross_representative_nonisomorphism": cross,
        "summary": {
            "alphabet_lift_passed": passed,
            "all_41664_families_classified": transport_checks == 41664,
            "all_41664_transports_edge_checked": transport_checks == 41664,
            "all_six_symbol3_holdouts_passed": len(holdout_rows) == 6,
            "recursive_count_law_passed": class_sizes == recursive_sizes,
            "all_15_cross_classes_separated": len(cross) == 15
            and all(not row["isomorphic"] for row in cross.values()),
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
