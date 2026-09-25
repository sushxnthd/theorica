from __future__ import annotations

"""External translation-action discovery benchmark on published BOC operations.

This benchmark evaluates THEORICA's family-agnostic finite-operation learner on
the Binary Operation Completion operations printed in Huh (ICLR 2025),
following Power et al. (2022).

The learner is not given labels such as group, quandle, quasigroup,
subtraction, or sandwich operation. It:

1. queries a small number of full left translations L_x(y)=F(x,y);
2. treats them as permutations only when the data justify doing so;
3. generates their permutation group;
4. computes a small base B for that group;
5. identifies every remaining left translation only from its images on B;
6. reconstructs the entire operation table;
7. validates on fresh unqueried pairs and otherwise abstains;
8. if accepted, searches for a short action identity over X=L_x,
   Y=L_y and their inverses.

This is a selected-query oracle benchmark, not directly the same observation
model as passive table-completion methods such as HyperCube-SE.
"""

import itertools
import json
from pathlib import Path

import numpy as np

from theorica.agents.translation_action import (
    discover_short_translation_law,
    discover_translation_action_representation,
)


def _mod_inverse(x: int, p: int = 97) -> int:
    return pow(int(x), p - 2, p)


def _mod_table(fn, p: int = 97) -> np.ndarray:
    table = np.empty((p, p), dtype=np.int64)
    for a in range(p):
        for b in range(p):
            table[a, b] = int(fn(a, b)) % p
    return table


def _permutation_table(fn, size: int = 5) -> np.ndarray:
    permutations = list(itertools.permutations(range(size)))
    index = {perm: i for i, perm in enumerate(permutations)}

    def compose(a, b):
        return tuple(a[b[i]] for i in range(size))

    def inverse(a):
        out = [0] * size
        for i, value in enumerate(a):
            out[value] = i
        return tuple(out)

    table = np.empty((len(permutations), len(permutations)), dtype=np.int64)
    for i, a in enumerate(permutations):
        for j, b in enumerate(permutations):
            table[i, j] = index[fn(a, b, compose, inverse)]
    return table


def published_boc_tables() -> dict[str, np.ndarray]:
    p = 97
    tables = {
        "add": _mod_table(lambda a, b: a + b, p),
        "sub": _mod_table(lambda a, b: a - b, p),
        "cond": _mod_table(
            lambda a, b: (
                a * _mod_inverse(b, p) if b % 2 == 1 else a - b
            ),
            p,
        ),
        "quad1": _mod_table(lambda a, b: a**2 + b**2, p),
        "quad2": _mod_table(lambda a, b: a**2 + a * b + b**2, p),
        "quad3": _mod_table(lambda a, b: a**2 + a * b + b**2 + a, p),
        "cube1": _mod_table(lambda a, b: a**3 + a * b, p),
        "cube2": _mod_table(lambda a, b: a**3 + a * b**2 + b, p),
    }

    tables["S5_comp"] = _permutation_table(
        lambda a, b, compose, inverse: compose(a, b)
    )
    tables["S5_conj"] = _permutation_table(
        lambda a, b, compose, inverse: compose(compose(a, b), inverse(a))
    )
    tables["S5_aba"] = _permutation_table(
        lambda a, b, compose, inverse: compose(compose(a, b), a)
    )
    return tables


class DirectOracle:
    def __init__(self, table):
        self.table = np.asarray(table, dtype=np.int64)

    def __call__(self, x, y):
        return int(self.table[int(x), int(y)])


def run():
    tables = published_boc_tables()
    # These are the operations for which the finite left-translation action is
    # both bijective/faithful and compact enough for the frozen compiler cap.
    expected_accept = {
        "add",
        "sub",
        "S5_comp",
        "S5_conj",
        "S5_aba",
    }

    repeats = 100
    records = []

    for repeat in range(repeats):
        for task_index, (task, table) in enumerate(tables.items()):
            result = discover_translation_action_representation(
                DirectOracle(table),
                len(table),
                seed=710000 + 10000 * repeat + task_index,
                max_generator_rows=8,
                max_group_size=20000,
                max_base_size=12,
                validation_queries=64,
            )

            exact = bool(
                result.accepted
                and np.array_equal(result.reconstructed_table, table)
            )

            records.append(
                {
                    "repeat": repeat,
                    "task": task,
                    "carrier_size": int(len(table)),
                    "expected_accept": task in expected_accept,
                    "accepted": bool(result.accepted),
                    "decision_correct": bool(
                        result.accepted == (task in expected_accept)
                    ),
                    "exact_reconstruction": exact,
                    "oracle_calls": int(result.oracle_calls),
                    "full_table_entries": int(len(table) ** 2),
                    "fraction_of_table": float(
                        result.oracle_calls / (len(table) ** 2)
                    ),
                    "queried_rows": int(result.queried_rows),
                    "generated_group_size": int(
                        result.generated_group_size
                    ),
                    "base_size": int(len(result.base)),
                    "reason": result.reason,
                }
            )

    accepted_tasks = {}
    for task in expected_accept:
        table = tables[task]
        law = discover_short_translation_law(
            table,
            max_word_length=3,
            screening_pairs=20,
            seed=20260925,
        )
        rows = [row for row in records if row["task"] == task]
        accepted_tasks[task] = {
            "runs": len(rows),
            "acceptance_rate": float(
                np.mean([row["accepted"] for row in rows])
            ),
            "exact_reconstruction_rate": float(
                np.mean([row["exact_reconstruction"] for row in rows])
            ),
            "mean_oracle_calls": float(
                np.mean([row["oracle_calls"] for row in rows])
            ),
            "median_oracle_calls": float(
                np.median([row["oracle_calls"] for row in rows])
            ),
            "p90_oracle_calls": float(
                np.quantile([row["oracle_calls"] for row in rows], 0.90)
            ),
            "mean_fraction_of_table": float(
                np.mean([row["fraction_of_table"] for row in rows])
            ),
            "mean_queried_rows": float(
                np.mean([row["queried_rows"] for row in rows])
            ),
            "mean_base_size": float(
                np.mean([row["base_size"] for row in rows])
            ),
            "translation_law": None if law is None else law.word,
            "translation_law_diagonal_constant": (
                None if law is None else law.diagonal_constant
            ),
        }

    rejected_tasks = {}
    for task in set(tables) - expected_accept:
        rows = [row for row in records if row["task"] == task]
        rejected_tasks[task] = {
            "runs": len(rows),
            "rejection_rate": float(
                np.mean([not row["accepted"] for row in rows])
            ),
            "mean_oracle_calls": float(
                np.mean([row["oracle_calls"] for row in rows])
            ),
            "reasons": sorted(set(row["reason"] for row in rows)),
        }

    summary = {
        "external_tasks": len(tables),
        "repeats": repeats,
        "task_repeat_cases": len(records),
        "decision_correct": int(
            sum(row["decision_correct"] for row in records)
        ),
        "accepted_expected_cases": int(
            sum(
                row["accepted"] and row["expected_accept"]
                for row in records
            )
        ),
        "exact_reconstructions": int(
            sum(
                row["exact_reconstruction"]
                for row in records
                if row["expected_accept"]
            )
        ),
        "unexpected_acceptances": int(
            sum(
                row["accepted"] and not row["expected_accept"]
                for row in records
            )
        ),
        "accepted_tasks": accepted_tasks,
        "rejected_tasks": rejected_tasks,
        "claim_boundary": (
            "Family-agnostic selected-query reconstruction through finite "
            "left-translation permutation actions. This benchmark does not "
            "establish priority, universal coverage, or passive-data sample "
            "efficiency superiority."
        ),
    }

    payload = {
        "experiment": "External BOC translation-action discovery",
        "date": "2026-09-25",
        "source_benchmark": (
            "Binary Operation Completion operations in Huh, ICLR 2025 "
            "Appendix B, following Power et al. 2022"
        ),
        "summary": summary,
        "records": records,
    }
    Path("results/external_translation_action.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    assert summary["decision_correct"] == len(records)
    assert summary["unexpected_acceptances"] == 0
    assert summary["accepted_expected_cases"] == repeats * len(expected_accept)
    assert summary["exact_reconstructions"] == repeats * len(expected_accept)

    # External headline gates.
    assert accepted_tasks["S5_comp"]["mean_fraction_of_table"] < 0.04
    assert accepted_tasks["S5_conj"]["mean_fraction_of_table"] < 0.05
    assert accepted_tasks["add"]["mean_fraction_of_table"] < 0.04

    # Representation-level identities must be discovered without labels.
    assert accepted_tasks["add"]["translation_law"] in {"XY", "YX"}
    assert accepted_tasks["S5_comp"]["translation_law"] == "XY"
    assert accepted_tasks["S5_conj"]["translation_law"] == "XYx"
    assert accepted_tasks["S5_aba"]["translation_law"] in {"XYX", "xYx"}


if __name__ == "__main__":
    run()
