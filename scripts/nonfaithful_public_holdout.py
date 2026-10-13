#!/usr/bin/env python3
"""Frozen prospective public-catalogue test for certified nonfaithful recovery."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np

from theorica.agents.translation_action import (
    discover_translation_action_representation,
    greedy_permutation_base,
    is_permutation,
    permutation_group_closure,
    reconstruct_from_translation_generators,
)

CORPUS = Path("results/nonfaithful_public_holdout.tsv")
OUTPUT = Path("results/nonfaithful_public_holdout.json")
MAX_GROUP_SIZE = 20_000
MAX_BASE_SIZE = 12


def old_ids(count: int, offset: int) -> set[int]:
    ids: list[int] = []
    x = offset % count + 1
    while len(ids) < 25:
        if x not in ids:
            ids.append(x)
        x = (x - 1 + 37) % count + 1
    return set(ids)


def closure(rows):
    group = permutation_group_closure(rows, max_size=MAX_GROUP_SIZE)
    if group is None:
        raise RuntimeError("translation group exceeds frozen cap")
    return group


def certificate_indices(rows):
    n = len(rows[0])
    identity = np.arange(n, dtype=np.int64)
    current = closure([identity])
    indices = []
    for index, row in enumerate(rows):
        if not any(np.array_equal(row, g) for g in current):
            indices.append(index)
            current = closure([*current, row])
    target = closure(rows)
    if {tuple(g) for g in current} != {tuple(g) for g in target}:
        raise AssertionError("certificate did not generate the full group")
    if not indices:
        indices = [0]
    return indices, target


def independent_reconstruct(rows, group, base):
    index = {tuple(int(g[p]) for p in base): np.asarray(g) for g in group}
    return np.stack([index[tuple(int(row[p]) for p in base)] for row in rows])


def main():
    records = []
    overlap = []
    opened = {8: old_ids(1581, 23), 9: old_ids(11079, 29)}
    for line in CORPUS.read_text().splitlines():
        n_text, id_text, table_text = line.split("\t", 2)
        n, library_id = int(n_text), int(id_text)
        if library_id in opened[n]:
            overlap.append([n, library_id])
        table = np.asarray(ast.literal_eval(table_text), dtype=np.int64) - 1
        rows = [table[x].copy() for x in range(n)]
        bijective = all(is_permutation(row) for row in rows)
        nonfaithful = len({tuple(row) for row in rows}) < n
        if not (bijective and nonfaithful):
            continue
        generators, group = certificate_indices(rows)
        base = greedy_permutation_base(group, n, max_base_size=MAX_BASE_SIZE)
        if base is None:
            raise RuntimeError("no base within frozen cap")
        oracle = lambda x, y, t=table: int(t[int(x), int(y)])
        result = reconstruct_from_translation_generators(
            oracle, n, generators,
            max_group_size=MAX_GROUP_SIZE, max_base_size=MAX_BASE_SIZE,
        )
        independent = independent_reconstruct(rows, group, base)
        old = discover_translation_action_representation(
            oracle, n, seed=20261013 + library_id,
            max_generator_rows=n, validation_queries=n * n,
        )
        exact = bool(result.accepted and np.array_equal(result.reconstructed_table, table))
        independent_exact = bool(np.array_equal(independent, table))
        records.append({
            "order": n, "library_id": library_id,
            "distinct_translations": len({tuple(row) for row in rows}),
            "group_size": len(group), "generator_rows": generators,
            "base": list(base), "calls": int(result.oracle_calls),
            "full_table_calls": n * n,
            "query_reduction": 1.0 - result.oracle_calls / (n * n),
            "production_exact": exact,
            "independent_exact": independent_exact,
            "implementations_agree": bool(
                exact and independent_exact and
                np.array_equal(result.reconstructed_table, independent)
            ),
            "old_learner_accepted": bool(old.accepted),
            "old_learner_reason": old.reason,
        })

    reductions = [row["query_reduction"] for row in records]
    below_full = sum(row["calls"] < row["full_table_calls"] for row in records)
    gates = {
        "at_least_50_eligible": len(records) >= 50,
        "production_all_exact": all(row["production_exact"] for row in records),
        "independent_all_exact_and_agree": all(
            row["independent_exact"] and row["implementations_agree"] for row in records
        ),
        "at_least_90_percent_below_full_table": bool(records) and below_full / len(records) >= 0.90,
        "median_reduction_at_least_25_percent": bool(records) and float(np.median(reductions)) >= 0.25,
        "old_learner_accepts_none": not any(row["old_learner_accepted"] for row in records),
        "zero_opened_id_overlap": not overlap,
    }
    payload = {
        "schema": "theorica.nonfaithful-public-holdout.v1",
        "source": "GAP RightQuasigroups v0.9.12 SmallQuandle",
        "selected": 160, "eligible": len(records),
        "opened_id_overlap": overlap,
        "median_query_reduction": float(np.median(reductions)) if records else None,
        "below_full_table": below_full,
        "records": records, "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in ["status", "eligible", "median_query_reduction", "below_full_table", "gates", "canonical_sha256"]}, indent=2))


if __name__ == "__main__":
    main()

