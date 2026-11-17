#!/usr/bin/env python3
"""Independent stdlib audit of identical-copy quotient combinatorics."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("results/qary_multiset_quotient/independent_audit.json")


def prefix_rows(arity: int, depth: int):
    words = []
    for index in range(arity**depth):
        digits = []
        value = index
        for _ in range(depth):
            digits.append(value % arity)
            value //= arity
        words.append(tuple(reversed(digits)))
    rows = []
    for level in range(depth):
        for prefix_index in range(arity**level):
            prefix = []
            value = prefix_index
            for _ in range(level):
                prefix.append(value % arity)
                value //= arity
            prefix = tuple(reversed(prefix))
            rows.append(tuple(word[level] + 1 if word[:level] == prefix else 0 for word in words))
    return tuple(rows)


def main() -> None:
    arity, depth, copies = 2, 4, 4
    rows = prefix_rows(arity, depth)
    physical_queries = len(rows) * copies
    indexed_remaining_states = 2**physical_queries
    quotient_remaining_states = (copies + 1) ** len(rows)
    result = {
        "schema": "theorica.qary-multiset-quotient-audit/1",
        "imports_theorica": False,
        "arity": arity,
        "depth": depth,
        "copies_per_group": copies,
        "completion_count": arity**depth,
        "query_groups": len(rows),
        "distinct_rows": len(set(rows)),
        "physical_queries": physical_queries,
        "indexed_remaining_states": indexed_remaining_states,
        "quotient_remaining_states": quotient_remaining_states,
        "raw_state_reduction_factor": indexed_remaining_states / quotient_remaining_states,
        "passed": len(rows) == len(set(rows)) == 15
        and physical_queries == 60
        and indexed_remaining_states == 2**60
        and quotient_remaining_states == 5**15,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
