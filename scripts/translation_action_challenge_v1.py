from __future__ import annotations

"""Translation-Action Challenge v1 on public GAP algebra catalogues.

The corpus is exported directly from:
- GAP SmallGrp;
- GAP RightQuasigroups SmallQuandle.

The learner receives only a table-backed oracle and carrier size. Source labels,
library identifiers, and full-table eligibility calculations are scoring-only.

Frozen split:
- development metadata: SmallGrp orders 24/32; quandles orders 6/7
- holdout metadata: SmallGrp orders 36/40/48; quandles orders 8/9

The algorithm was fixed before the public corpus was executed.
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


CORPUS = Path("results/translation_action_challenge_v1.tsv")
OUTPUT = Path("results/translation_action_challenge_v1.json")

MAX_GROUP_SIZE = 20_000
MAX_BASE_SIZE = 12
MAX_GENERATOR_ROWS = 8
VALIDATION_QUERIES = 64
REPEATS = 3


class DirectOracle:
    def __init__(self, table: np.ndarray):
        self.table = np.asarray(table, dtype=np.int64)

    def __call__(self, x: int, y: int) -> int:
        return int(self.table[int(x), int(y)])


def parse_corpus(path: Path):
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        name, source, order_text, library_id_text, table_text = line.split(
            "\t", 4
        )
        table = np.asarray(ast.literal_eval(table_text), dtype=np.int64) - 1
        n = int(order_text)
        assert table.shape == (n, n)

        if source == "SmallGrp":
            split = "dev" if n in {24, 32} else "holdout"
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


def compact_action_eligibility(table: np.ndarray):
    """Full-table scoring oracle; never exposed to the learner."""
    table = np.asarray(table, dtype=np.int64)
    n = len(table)
    rows = [table[i].copy() for i in range(n)]

    if not all(is_permutation(row) for row in rows):
        return {
            "eligible": False,
            "reason": "non_bijective_translation",
            "full_translation_group_size": None,
            "full_base_size": None,
        }

    if len({tuple(map(int, row)) for row in rows}) != n:
        return {
            "eligible": False,
            "reason": "nonfaithful_translations",
            "full_translation_group_size": None,
            "full_base_size": None,
        }

    group = permutation_group_closure(rows, max_size=MAX_GROUP_SIZE)
    if group is None:
        return {
            "eligible": False,
            "reason": "translation_group_exceeds_cap",
            "full_translation_group_size": f">{MAX_GROUP_SIZE}",
            "full_base_size": None,
        }

    base = greedy_permutation_base(
        group,
        n,
        max_base_size=MAX_BASE_SIZE,
    )
    if base is None:
        return {
            "eligible": False,
            "reason": "no_small_base",
            "full_translation_group_size": len(group),
            "full_base_size": f">{MAX_BASE_SIZE}",
        }

    return {
        "eligible": True,
        "reason": "compact_faithful_translation_action",
        "full_translation_group_size": len(group),
        "full_base_size": len(base),
    }


def run_policy(
    table: np.ndarray,
    *,
    seed: int,
    policy: str,
):
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
        "generated_group_size": int(result.generated_group_size),
        "base_size": int(len(result.base)),
        "reason": result.reason,
    }


def summarize(rows, cases_by_name):
    holdout = [r for r in rows if cases_by_name[r["name"]]["split"] == "holdout"]
    eligible = [r for r in holdout if r["eligible"]]
    ineligible = [r for r in holdout if not r["eligible"]]

    adaptive_exact = sum(r["adaptive"]["exact"] for r in eligible)
    random_exact = sum(r["random"]["exact"] for r in eligible)
    false_accepts = sum(r["adaptive"]["accepted"] for r in ineligible)

    paired = [
        r
        for r in eligible
        if r["adaptive"]["exact"] and r["random"]["exact"]
    ]
    call_ratio = [
        r["adaptive"]["calls"] / max(r["random"]["calls"], 1)
        for r in paired
    ]

    return {
        "holdout_task_repeat_cases": len(holdout),
        "holdout_eligible_cases": len(eligible),
        "holdout_ineligible_cases": len(ineligible),
        "adaptive_exact_on_eligible": int(adaptive_exact),
        "random_exact_on_eligible": int(random_exact),
        "adaptive_false_accepts_on_ineligible": int(false_accepts),
        "adaptive_median_table_fraction_eligible": float(
            np.median([r["adaptive"]["fraction"] for r in eligible])
        )
        if eligible
        else None,
        "random_median_table_fraction_eligible": float(
            np.median([r["random"]["fraction"] for r in eligible])
        )
        if eligible
        else None,
        "paired_exact_cases": len(paired),
        "adaptive_median_call_ratio_vs_random": float(np.median(call_ratio))
        if call_ratio
        else None,
        "adaptive_wins_calls_vs_random": int(
            sum(r["adaptive"]["calls"] < r["random"]["calls"] for r in paired)
        ),
        "adaptive_ties_calls_vs_random": int(
            sum(r["adaptive"]["calls"] == r["random"]["calls"] for r in paired)
        ),
        "adaptive_losses_calls_vs_random": int(
            sum(r["adaptive"]["calls"] > r["random"]["calls"] for r in paired)
        ),
    }


def run():
    cases = parse_corpus(CORPUS)
    cases_by_name = {case["name"]: case for case in cases}

    eligibility = {
        case["name"]: compact_action_eligibility(case["table"])
        for case in cases
    }

    records = []
    for case_index, case in enumerate(cases):
        label = eligibility[case["name"]]
        for repeat in range(REPEATS):
            seed = 880_000 + 10_000 * repeat + case_index
            adaptive = run_policy(
                case["table"],
                seed=seed,
                policy="unresolved",
            )
            random_baseline = run_policy(
                case["table"],
                seed=seed,
                policy="random",
            )
            records.append(
                {
                    "name": case["name"],
                    "source": case["source"],
                    "order": case["order"],
                    "library_id": case["library_id"],
                    "split": case["split"],
                    "repeat": repeat,
                    "eligible": bool(label["eligible"]),
                    "eligibility_reason": label["reason"],
                    "full_translation_group_size": label[
                        "full_translation_group_size"
                    ],
                    "full_base_size": label["full_base_size"],
                    "adaptive": adaptive,
                    "random": random_baseline,
                }
            )

    summary = summarize(records, cases_by_name)
    source_counts = {}
    for case in cases:
        key = f'{case["split"]}:{case["source"]}'
        source_counts[key] = source_counts.get(key, 0) + 1

    payload = {
        "experiment": "Translation-Action Challenge v1",
        "date": "2026-09-25",
        "corpus": {
            "total_public_algebras": len(cases),
            "source_counts": source_counts,
            "smallgrp_orders": [24, 32, 36, 40, 48],
            "smallquandle_orders": [6, 7, 8, 9],
            "smallquandle_orientation": (
                "multiplication table transposed so GAP right translations "
                "become learner left translations"
            ),
            "frozen_split": {
                "dev": "SmallGrp 24/32; SmallQuandle 6/7",
                "holdout": "SmallGrp 36/40/48; SmallQuandle 8/9",
            },
        },
        "learner": {
            "max_generator_rows": MAX_GENERATOR_ROWS,
            "max_group_size": MAX_GROUP_SIZE,
            "max_base_size": MAX_BASE_SIZE,
            "validation_queries": VALIDATION_QUERIES,
            "repeats": REPEATS,
        },
        "baseline": (
            "same translation-action learner, but when the representation is "
            "unresolved it acquires a uniformly random unqueried full row "
            "instead of a row implicated by the unresolved signatures"
        ),
        "summary": summary,
        "records": records,
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(
        {
            "corpus": payload["corpus"],
            "summary": summary,
        },
        indent=2,
    ))

    # Frozen challenge gates. They are intentionally strict on correctness and
    # modest on efficiency; a failed gate remains a result rather than being
    # silently retuned.
    assert summary["adaptive_false_accepts_on_ineligible"] == 0
    assert summary["adaptive_exact_on_eligible"] == summary["holdout_eligible_cases"]
    assert summary["adaptive_median_table_fraction_eligible"] < 0.25


if __name__ == "__main__":
    run()
