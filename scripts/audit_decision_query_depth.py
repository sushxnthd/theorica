#!/usr/bin/env python3
"""Independent stdlib-only replay of decision-query-depth predictions."""

from __future__ import annotations

import hashlib
import json
from functools import cache
from math import ceil, log2
from pathlib import Path

PRIMARY = Path("results/decision_query_depth/results.json")
OUT = Path("results/decision_query_depth/independent_audit.json")


def coordinate_outcomes(dimension):
    return tuple(
        tuple((completion >> (dimension - query - 1)) & 1
              for completion in range(1 << dimension))
        for query in range(dimension)
    )


def indexed_outcomes(completion_count):
    dimension = ceil(log2(completion_count))
    return tuple(
        tuple((completion >> (dimension - query - 1)) & 1
              for completion in range(completion_count))
        for query in range(dimension)
    )


def independent_depth(completion_count, outcomes, compatible):
    @cache
    def solve(state, remaining):
        if compatible(state):
            return 0
        best = None
        for query in remaining:
            cells = {}
            for completion in state:
                cells.setdefault(outcomes[query][completion], []).append(completion)
            if len(cells) < 2:
                continue
            tail = tuple(index for index in remaining if index != query)
            depths = [solve(tuple(members), tail) for members in cells.values()]
            if any(depth is None for depth in depths):
                continue
            candidate = 1 + max(depths)
            best = candidate if best is None else min(best, candidate)
        return best

    return solve(tuple(range(completion_count)), tuple(range(len(outcomes))))


def audit_cases():
    cases = []
    for count in range(2, 9):
        depth = independent_depth(count, indexed_outcomes(count), lambda state: len(state) == 1)
        expected = ceil(log2(count))
        cases.append({"family": "opened-binary-feature-code", "completions": count,
                      "depth": depth, "passed": depth == expected})
    for dimension in range(1, 7):
        count = 1 << dimension
        outcomes = coordinate_outcomes(dimension)
        depth = independent_depth(count, outcomes, lambda state: len(state) == 1)
        cases.append({"family": "coordinate", "dimension": dimension,
                      "depth": depth, "passed": depth == dimension})
    for dimension in range(2, 7):
        count = 1 << dimension
        outcomes = coordinate_outcomes(dimension)
        depth = independent_depth(
            count, outcomes,
            lambda state, half=count // 2: all(index < half for index in state)
            or all(index >= half for index in state),
        )
        cases.append({"family": "decision-quotient-saving", "dimension": dimension,
                      "depth": depth, "passed": depth == 1})
        missing = independent_depth(
            count, outcomes[:-1], lambda state: len(state) == 1
        )
        cases.append({"family": "missing-coordinate", "dimension": dimension,
                      "depth": missing, "passed": missing is None})
    for actions in range(3, 7):
        outcomes = (tuple(0 if index == 0 else 1 for index in range(actions)),)
        depth = independent_depth(
            actions, outcomes, lambda state, total=actions: len(state) < total
        )
        cases.append({"family": "higher-order", "actions": actions,
                      "depth": depth, "passed": depth == 1})
    return cases


def main():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    cases = audit_cases()
    digest = hashlib.sha256(
        json.dumps(cases, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    summary = {
        "cases_passed": sum(case["passed"] for case in cases),
        "cases_total": len(cases),
        "production_imports": 0,
        "primary_passed": primary["summary"]["passed"],
        "audit_digest": digest,
        "passed": all(case["passed"] for case in cases)
        and primary["summary"]["passed"],
    }
    OUT.write_text(json.dumps(
        {"schema": "theorica.decision-query-depth-audit/1", "summary": summary,
         "cases": cases},
        indent=2,
        sort_keys=True,
    ) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
