from __future__ import annotations

"""Sparse-corruption falsification challenge for translation-base reconstruction.

Uses the unchanged public v1.2 corpus.  For each eligible holdout algebra,
deterministically corrupt a small set of oracle cells while retaining the clean
table only for post-hoc scoring.

A run is safe iff THEORICA either:
1. reconstructs the clean operation exactly; or
2. abstains.

Accepting an incorrect reconstructed table is an unsafe failure.
"""

import ast
import json
import math
from pathlib import Path

import numpy as np

from theorica.agents.translation_action import (
    discover_translation_action_representation,
    greedy_permutation_base,
    is_permutation,
    permutation_group_closure,
)


CORPUS = Path("results/translation_action_challenge_v1_1.tsv")
OUTPUT = Path("results/translation_action_corruption_challenge.json")

MAX_GROUP_SIZE = 20_000
MAX_BASE_SIZE = 12
MAX_GENERATOR_ROWS = 8
VALIDATION_QUERIES = 64

CORRUPTION_RATES = (0.001, 0.005, 0.01)
CORRUPTION_SEEDS = 3


class CorruptOracle:
    def __init__(self, clean_table: np.ndarray, corruptions: dict[tuple[int, int], int]):
        self.clean_table = np.asarray(clean_table, dtype=np.int64)
        self.corruptions = dict(corruptions)

    def __call__(self, x: int, y: int) -> int:
        key = (int(x), int(y))
        if key in self.corruptions:
            return int(self.corruptions[key])
        return int(self.clean_table[key])


def parse_corpus(path: Path):
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        name, source, order_text, library_id_text, table_text = line.split("\t", 4)
        table = np.asarray(ast.literal_eval(table_text), dtype=np.int64) - 1
        n = int(order_text)

        if source == "SmallGrp":
            split = "dev" if n in {24, 32} else "holdout"
        elif source == "RQ:SmallLoop":
            split = "dev" if n == 5 else "holdout"
        else:
            split = "dev" if n in {6, 7} else "holdout"

        cases.append(
            {
                "name": name,
                "source": source,
                "order": n,
                "library_id": int(library_id_text),
                "split": split,
                "table": table,
            }
        )
    return cases


def eligible(table: np.ndarray) -> bool:
    table = np.asarray(table, dtype=np.int64)
    n = len(table)
    rows = [table[i].copy() for i in range(n)]

    if not all(is_permutation(row) for row in rows):
        return False
    if len({tuple(map(int, row)) for row in rows}) != n:
        return False

    group = permutation_group_closure(rows, max_size=MAX_GROUP_SIZE)
    if group is None:
        return False

    base = greedy_permutation_base(group, n, max_base_size=MAX_BASE_SIZE)
    return base is not None


def make_corruptions(table: np.ndarray, rate: float, seed: int):
    n = len(table)
    rng = np.random.default_rng(seed)
    total = n * n
    k = max(1, int(math.ceil(float(rate) * total)))
    flat = rng.choice(total, size=min(k, total), replace=False)
    corruptions = {}
    for index in flat:
        x, y = divmod(int(index), n)
        truth = int(table[x, y])
        # Always choose a different in-carrier symbol.
        offset = int(rng.integers(1, n))
        corruptions[(x, y)] = int((truth + offset) % n)
    return corruptions


def run():
    cases = [
        case for case in parse_corpus(CORPUS)
        if case["split"] == "holdout" and eligible(case["table"])
    ]

    records = []
    for case_index, case in enumerate(cases):
        table = case["table"]
        for rate_index, rate in enumerate(CORRUPTION_RATES):
            for repeat in range(CORRUPTION_SEEDS):
                corruption_seed = (
                    1_300_000
                    + 100_000 * rate_index
                    + 10_000 * repeat
                    + case_index
                )
                corruptions = make_corruptions(
                    table,
                    rate,
                    corruption_seed,
                )

                result = discover_translation_action_representation(
                    CorruptOracle(table, corruptions),
                    len(table),
                    seed=2_300_000 + corruption_seed,
                    max_generator_rows=MAX_GENERATOR_ROWS,
                    max_group_size=MAX_GROUP_SIZE,
                    max_base_size=MAX_BASE_SIZE,
                    validation_queries=VALIDATION_QUERIES,
                    acquisition_policy="unresolved",
                )

                exact_clean = bool(
                    result.accepted
                    and np.array_equal(result.reconstructed_table, table)
                )
                abstained = bool(not result.accepted)
                unsafe_wrong_accept = bool(result.accepted and not exact_clean)

                records.append(
                    {
                        "name": case["name"],
                        "source": case["source"],
                        "order": case["order"],
                        "rate": float(rate),
                        "corrupted_cells": len(corruptions),
                        "repeat": repeat,
                        "accepted": bool(result.accepted),
                        "exact_clean": exact_clean,
                        "abstained": abstained,
                        "unsafe_wrong_accept": unsafe_wrong_accept,
                        "calls": int(result.oracle_calls),
                        "reason": result.reason,
                    }
                )

    by_rate = {}
    for rate in CORRUPTION_RATES:
        rows = [r for r in records if r["rate"] == float(rate)]
        by_rate[str(rate)] = {
            "cases": len(rows),
            "exact_clean": int(sum(r["exact_clean"] for r in rows)),
            "abstained": int(sum(r["abstained"] for r in rows)),
            "unsafe_wrong_accept": int(
                sum(r["unsafe_wrong_accept"] for r in rows)
            ),
            "safe_fraction": float(
                np.mean(
                    [
                        r["exact_clean"] or r["abstained"]
                        for r in rows
                    ]
                )
            ),
        }

    by_source = {}
    for source in sorted({r["source"] for r in records}):
        rows = [r for r in records if r["source"] == source]
        by_source[source] = {
            "cases": len(rows),
            "exact_clean": int(sum(r["exact_clean"] for r in rows)),
            "abstained": int(sum(r["abstained"] for r in rows)),
            "unsafe_wrong_accept": int(
                sum(r["unsafe_wrong_accept"] for r in rows)
            ),
        }

    summary = {
        "unique_clean_holdout_algebras": len(cases),
        "corrupted_task_cases": len(records),
        "exact_clean": int(sum(r["exact_clean"] for r in records)),
        "abstained": int(sum(r["abstained"] for r in records)),
        "unsafe_wrong_accept": int(
            sum(r["unsafe_wrong_accept"] for r in records)
        ),
        "safe_fraction": float(
            np.mean(
                [r["exact_clean"] or r["abstained"] for r in records]
            )
        ),
        "by_rate": by_rate,
        "by_source": by_source,
    }

    payload = {
        "experiment": "Translation-Action sparse-corruption falsification",
        "date": "2026-09-25",
        "corruption_rates": list(CORRUPTION_RATES),
        "corruption_seeds_per_rate": CORRUPTION_SEEDS,
        "success_definition": (
            "safe iff exact reconstruction of clean hidden table or abstention; "
            "accepting any incorrect table is unsafe"
        ),
        "summary": summary,
        "records": records,
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    # Frozen safety gate.
    assert summary["unsafe_wrong_accept"] == 0


if __name__ == "__main__":
    run()
