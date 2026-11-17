#!/usr/bin/env python3
"""Independent stdlib-only replay of adaptive decision queries with lies."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import cache
from math import comb
from pathlib import Path

PRIMARY = Path("results/adaptive_decision_lies/results.json")
OUT = Path("results/adaptive_decision_lies/independent_audit.json")


def repeated(row, copies):
    return tuple(tuple(row) for _ in range(copies))


def prefix_tree_queries(depth, copies=3):
    count = 1 << depth
    rows = []
    for level in range(depth):
        for prefix in range(1 << level):
            row = []
            for completion in range(count):
                if completion >> (depth - level) == prefix:
                    row.append((completion >> (depth - level - 1)) & 1)
                else:
                    row.append(0)
            rows.extend((tuple(row),) * copies)
    return tuple(rows)


def exact_depth(rows, completion_count, budget, compatibility):
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)
    eliminated = budget + 1

    def feasible(counts):
        return tuple(index for index, count in enumerate(counts) if count <= budget)

    def terminal(indices):
        if compatibility == "unique":
            return len(indices) <= 1
        if compatibility == "proper-subset":
            return len(indices) < completion_count
        raise AssertionError("unknown compatibility predicate")

    def sphere_fails(counts, indices, limit):
        if compatibility != "unique":
            return False
        weight = sum(
            sum(comb(limit, extra) for extra in range(budget - counts[index] + 1))
            for index in indices
        )
        return weight > 2**limit

    def update(counts, query, answer):
        return tuple(
            min(eliminated, count + (rows[query][index] != answer))
            for index, count in enumerate(counts)
        )

    @cache
    def search(counts, remaining, limit):
        indices = feasible(counts)
        if terminal(indices):
            return True
        if limit == 0 or not remaining or sphere_fails(counts, indices, limit):
            return False
        seen = set()
        for query in remaining:
            row = rows[query]
            if row in seen:
                continue
            seen.add(row)
            if len({row[index] for index in indices}) < 2:
                continue
            next_remaining = tuple(item for item in remaining if item != query)
            possible = []
            for answer in alphabets[query]:
                child = update(counts, query, answer)
                if feasible(child):
                    possible.append(child)
            if possible and all(
                search(child, next_remaining, limit - 1) for child in possible
            ):
                return True
        return False

    initial = (0,) * completion_count
    remaining = tuple(range(len(rows)))
    for limit in range(len(rows) + 1):
        if search(initial, remaining, limit):
            return limit
    return None


def replay_tree(tree, rows, completion_count, budget, compatibility):
    def terminal(indices):
        return (
            len(indices) <= 1
            if compatibility == "unique"
            else len(indices) < completion_count
        )

    def visit(node, remaining, depth):
        counts = tuple(node["lie_counts"])
        feasible = tuple(
            index for index, count in enumerate(counts) if count <= budget
        )
        if tuple(node["feasible_completions"]) != feasible:
            return False, depth
        query = node["query_index"]
        if query is None:
            return (
                terminal(feasible)
                and node["action_probabilities"] is not None
                and node["minimax_value"] is not None
            ), depth
        if query not in remaining:
            return False, depth
        next_remaining = tuple(item for item in remaining if item != query)
        children = {item["answer"]: item["node"] for item in node["children"]}
        expected = {}
        for answer in sorted(set(rows[query])):
            child_counts = tuple(
                min(budget + 1, count + (rows[query][index] != answer))
                for index, count in enumerate(counts)
            )
            if any(count <= budget for count in child_counts):
                expected[answer] = child_counts
        if set(children) != set(expected):
            return False, depth
        checks = []
        for answer, child in children.items():
            if tuple(child["lie_counts"]) != expected[answer]:
                return False, depth
            checks.append(visit(child, next_remaining, depth + 1))
        return all(valid for valid, _ in checks), max(level for _, level in checks)

    return visit(tree, tuple(range(len(rows))), 0)


def sibling_lower_bound(depth, rows):
    required = set()
    valid = True
    for left in range(0, 1 << depth, 2):
        right = left + 1
        differing = {
            query
            for query, row in enumerate(rows)
            if row[left] != row[right]
        }
        valid = valid and len(differing) == 3 and not (required & differing)
        required.update(differing)
    return len(required), valid


def main():
    production_before = {name for name in sys.modules if name.startswith("theorica")}
    report = json.loads(PRIMARY.read_text(encoding="utf-8"))
    cases = report["cases"]
    replayed = []
    for case in cases:
        family = case["family"]
        if family == "two-class-repetition":
            budget = case["budget"]
            rows = repeated((0, 1), 2 * budget + 1)
            depth = exact_depth(rows, 2, budget, "unique")
            tree_valid, tree_depth = replay_tree(
                case["tree"], rows, 2, budget, "unique"
            )
            passed = depth == case["adaptive_depth"] == tree_depth and tree_valid
        elif family == "missing-copy-attack":
            budget = case["budget"]
            rows = repeated((0, 1), 2 * budget)
            depth = exact_depth(rows, 2, budget, "unique")
            passed = depth is None and case["adaptive_depth"] is None
        elif family in {"opened-prefix-tree", "prospective-prefix-tree"}:
            source_depth = case["depth"]
            rows = prefix_tree_queries(source_depth)
            count = 1 << source_depth
            depth = exact_depth(rows, count, 1, "unique")
            tree_valid, tree_depth = replay_tree(
                case["tree"], rows, count, 1, "unique"
            )
            fixed_lower, sibling_valid = sibling_lower_bound(source_depth, rows)
            passed = (
                depth == case["adaptive_depth"] == tree_depth
                and tree_valid
                and sibling_valid
                and fixed_lower == case["fixed_schedule_lower_bound"]
                and depth < fixed_lower
            )
        elif family == "higher-order-policy-conflict":
            count = case["actions"]
            row = tuple(0 if index == 0 else 1 for index in range(count))
            rows = repeated(row, 3)
            depth = exact_depth(rows, count, 1, "proper-subset")
            tree_valid, tree_depth = replay_tree(
                case["tree"], rows, count, 1, "proper-subset"
            )
            passed = (
                depth == case["adaptive_depth"] == tree_depth == 3
                and tree_valid
                and case["pairwise_conflict_edges"] == 0
            )
        else:
            raise AssertionError(f"unknown case family: {family}")
        replayed.append({"family": family, "passed": passed})

    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.adaptive-decision-lies-audit/1",
        "cases_replayed": sum(item["passed"] for item in replayed),
        "case_total": len(replayed),
        "case_digest_reproduced": (
            hashlib.sha256(canonical.encode()).hexdigest()
            == report["summary"]["case_digest"]
        ),
        "production_imports": len(
            {name for name in sys.modules if name.startswith("theorica")}
            - production_before
        ),
        "replays": replayed,
    }
    result["passed"] = (
        result["cases_replayed"] == result["case_total"]
        and result["case_digest_reproduced"]
        and result["production_imports"] == 0
    )
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
