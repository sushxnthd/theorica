from __future__ import annotations

"""Translation-Action Challenge v1.1: public cross-family holdout.

Extends v1 with public faithful connected quandles and nonassociative loops
without changing THEORICA's learner or thresholds.
"""

import ast
import json
from pathlib import Path

import numpy as np

from theorica.agents.translation_action import (
    discover_translation_action_representation,
    greedy_permutation_base,
    is_permutation,
    permutation_group_closure,
)


CORPUS = Path("results/translation_action_challenge_v1_1.tsv")
OUTPUT = Path("results/translation_action_challenge_v1_1.json")

MAX_GROUP_SIZE = 20_000
MAX_BASE_SIZE = 12
MAX_GENERATOR_ROWS = 8
VALIDATION_QUERIES = 64
REPEATS = 3


class DirectOracle:
    def __init__(self, table):
        self.table = np.asarray(table, dtype=np.int64)

    def __call__(self, x, y):
        return int(self.table[int(x), int(y)])


def parse_corpus(path):
    cases = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        parts = line.split("\t", 4)
        if len(parts) != 5:
            raise ValueError(
                f"malformed corpus line {line_number}: {line[:500]!r}"
            )
        name, source, order_text, library_id_text, table_text = parts
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


def eligibility(table):
    table = np.asarray(table, dtype=np.int64)
    n = len(table)
    rows = [table[i].copy() for i in range(n)]

    if not all(is_permutation(row) for row in rows):
        return False, "non_bijective_translation", None, None

    if len({tuple(map(int, row)) for row in rows}) != n:
        return False, "nonfaithful_translations", None, None

    group = permutation_group_closure(rows, max_size=MAX_GROUP_SIZE)
    if group is None:
        return False, "translation_group_exceeds_cap", None, None

    base = greedy_permutation_base(
        group, n, max_base_size=MAX_BASE_SIZE
    )
    if base is None:
        return False, "no_small_base", len(group), None

    return True, "compact_faithful_translation_action", len(group), len(base)


def run_policy(table, *, seed, policy):
    result = discover_translation_action_representation(
        DirectOracle(table),
        len(table),
        seed=seed,
        max_generator_rows=MAX_GENERATOR_ROWS,
        max_group_size=MAX_GROUP_SIZE,
        max_base_size=MAX_BASE_SIZE,
        validation_queries=VALIDATION_QUERIES,
        acquisition_policy=policy,
    )
    exact = bool(
        result.accepted
        and np.array_equal(result.reconstructed_table, table)
    )
    return {
        "accepted": bool(result.accepted),
        "exact": exact,
        "calls": int(result.oracle_calls),
        "fraction": float(result.oracle_calls / table.size),
        "queried_rows": int(result.queried_rows),
        "base_size": int(len(result.base)),
        "reason": result.reason,
    }


def group_summary(records, source=None):
    rows = [
        r
        for r in records
        if r["split"] == "holdout"
        and (source is None or r["source"] == source)
    ]
    eligible_rows = [r for r in rows if r["eligible"]]
    ineligible_rows = [r for r in rows if not r["eligible"]]
    paired = [
        r
        for r in eligible_rows
        if r["adaptive"]["exact"] and r["random"]["exact"]
    ]

    return {
        "cases": len(rows),
        "eligible": len(eligible_rows),
        "ineligible": len(ineligible_rows),
        "adaptive_exact": int(
            sum(r["adaptive"]["exact"] for r in eligible_rows)
        ),
        "random_exact": int(
            sum(r["random"]["exact"] for r in eligible_rows)
        ),
        "adaptive_false_accepts": int(
            sum(r["adaptive"]["accepted"] for r in ineligible_rows)
        ),
        "adaptive_median_fraction": (
            float(np.median([r["adaptive"]["fraction"] for r in eligible_rows]))
            if eligible_rows
            else None
        ),
        "random_median_fraction": (
            float(np.median([r["random"]["fraction"] for r in eligible_rows]))
            if eligible_rows
            else None
        ),
        "adaptive_call_wins": int(
            sum(r["adaptive"]["calls"] < r["random"]["calls"] for r in paired)
        ),
        "adaptive_call_ties": int(
            sum(r["adaptive"]["calls"] == r["random"]["calls"] for r in paired)
        ),
        "adaptive_call_losses": int(
            sum(r["adaptive"]["calls"] > r["random"]["calls"] for r in paired)
        ),
    }


def run():
    cases = parse_corpus(CORPUS)
    labels = {}
    for case in cases:
        ok, reason, group_size, base_size = eligibility(case["table"])
        labels[case["name"]] = {
            "eligible": ok,
            "reason": reason,
            "group_size": group_size,
            "base_size": base_size,
        }

    records = []
    for case_index, case in enumerate(cases):
        label = labels[case["name"]]
        for repeat in range(REPEATS):
            seed = 990_000 + 10_000 * repeat + case_index
            records.append(
                {
                    "name": case["name"],
                    "source": case["source"],
                    "order": case["order"],
                    "library_id": case["library_id"],
                    "split": case["split"],
                    "repeat": repeat,
                    "eligible": label["eligible"],
                    "eligibility_reason": label["reason"],
                    "full_translation_group_size": label["group_size"],
                    "full_base_size": label["base_size"],
                    "adaptive": run_policy(
                        case["table"], seed=seed, policy="unresolved"
                    ),
                    "random": run_policy(
                        case["table"], seed=seed, policy="random"
                    ),
                }
            )

    sources = sorted({case["source"] for case in cases})
    per_source = {source: group_summary(records, source) for source in sources}
    overall = group_summary(records)

    unique_holdout = [case for case in cases if case["split"] == "holdout"]
    eligible_unique = [
        case for case in unique_holdout if labels[case["name"]]["eligible"]
    ]
    non_group_eligible_unique = [
        case for case in eligible_unique if case["source"] != "SmallGrp"
    ]

    overall.update(
        {
            "unique_holdout_algebras": len(unique_holdout),
            "unique_eligible_holdout_algebras": len(eligible_unique),
            "unique_cross_family_eligible_holdout_algebras": len(
                non_group_eligible_unique
            ),
        }
    )

    payload = {
        "experiment": "Translation-Action Challenge v1.1",
        "date": "2026-09-25",
        "corpus": {
            "total_public_algebras": len(cases),
            "sources": {
                source: sum(case["source"] == source for case in cases)
                for source in sources
            },
            "extension_from_v1": (
                "retains v1 corpus; adds faithful connected quandles and "
                "public nonassociative small loops; learner unchanged"
            ),
        },
        "parameters": {
            "max_generator_rows": MAX_GENERATOR_ROWS,
            "max_group_size": MAX_GROUP_SIZE,
            "max_base_size": MAX_BASE_SIZE,
            "validation_queries": VALIDATION_QUERIES,
            "repeats": REPEATS,
        },
        "summary": overall,
        "per_source": per_source,
        "records": records,
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(
        {
            "corpus": payload["corpus"],
            "summary": overall,
            "per_source": per_source,
        },
        indent=2,
    ))

    # Frozen v1.1 gates.
    assert overall["adaptive_false_accepts"] == 0
    assert overall["adaptive_exact"] == overall["eligible"]
    assert overall["unique_cross_family_eligible_holdout_algebras"] >= 10
    assert overall["adaptive_median_fraction"] < 0.25


if __name__ == "__main__":
    run()
