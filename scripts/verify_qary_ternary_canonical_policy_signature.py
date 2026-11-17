#!/usr/bin/env python3
"""Compare relabeling-invariant signatures of the exact P0/P2 policy trees."""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
)

HELPER_PATH = Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
SPEC = importlib.util.spec_from_file_location("transfer_helper", HELPER_PATH)
assert SPEC is not None and SPEC.loader is not None
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)

OUT = Path("results/qary_ternary_canonical_policy_signature/results.json")
FULL = Path("results/qary_ternary_canonical_policy_signature/canonical_policies.json.gz")


def solve(words, forced_middle=None):
    physical = tuple(row for row in HELPER.rows(words) for _ in range(HELPER.COPIES))
    allowed = (
        range(4, 16)
        if forced_middle is None
        else range(4 * forced_middle, 4 * forced_middle + 4)
    )
    return plan_adaptive_decision_queries_with_weighted_faults(
        HELPER.games(10),
        physical,
        query_costs=qary_prefix_query_costs(
            3, 3, copies=HELPER.COPIES, level_costs=HELPER.COSTS
        ),
        corruption_budget=1,
        erasure_budget=1,
        known_feasible_cost_upper_bound=52,
        allowed_initial_query_indices=allowed,
    )


def canonical_policy(root, words):
    physical = tuple(row for row in HELPER.rows(words) for _ in range(HELPER.COPIES))
    costs = qary_prefix_query_costs(
        3, 3, copies=HELPER.COPIES, level_costs=HELPER.COSTS
    )

    def visit(node):
        feasible = tuple(i for i, count in enumerate(node.lie_counts) if count <= 1)
        common = {
            "erasures_used": node.erasures_used,
            "feasible_count": len(feasible),
            "lie_histogram": sorted(node.lie_counts[i] for i in feasible),
        }
        if node.query_index is None:
            return {"kind": "terminal", **common}
        row = physical[node.query_index]
        cells = {}
        for i in feasible:
            cells[row[i]] = cells.get(row[i], 0) + 1
        ordinary = []
        erasure = None
        for answer, child in node.children:
            encoded = visit(child)
            if answer is None:
                erasure = encoded
            else:
                ordinary.append(encoded)
        ordinary.sort(key=lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")))
        return {
            "kind": "query",
            **common,
            "query_level": HELPER.level(node.query_index // HELPER.COPIES),
            "query_cost": costs[node.query_index],
            "cell_sizes": sorted(cells.values()),
            "ordinary_children": ordinary,
            "erasure_child": erasure,
        }

    return visit(root)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def replay(value):
    if value["kind"] == "terminal":
        return 0, 1, 0
    children = list(value["ordinary_children"])
    if value["erasure_child"] is not None:
        children.append(value["erasure_child"])
    child = [replay(item) for item in children]
    return (
        value["query_cost"] + max(row[0] for row in child),
        1 + sum(row[1] for row in child),
        1 + max(row[2] for row in child),
    )


def first_difference(left, right, path="root"):
    if type(left) is not type(right):
        return {"path": path, "left": type(left).__name__, "right": type(right).__name__}
    if isinstance(left, dict):
        if set(left) != set(right):
            return {"path": path, "left_keys": sorted(left), "right_keys": sorted(right)}
        for key in sorted(left):
            found = first_difference(left[key], right[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(left, list):
        if len(left) != len(right):
            return {"path": path, "left_length": len(left), "right_length": len(right)}
        for index, (a, b) in enumerate(zip(left, right)):
            found = first_difference(a, b, f"{path}[{index}]")
            if found:
                return found
        return None
    return None if left == right else {"path": path, "left": left, "right": right}


def family(pair):
    return (*HELPER.BASE, *pair)


def profile(label, words):
    entries = []
    for name, forced in (("unrestricted", None), ("middle_1", 1), ("middle_2", 2), ("middle_3", 3)):
        plan = solve(words, forced)
        canonical = canonical_policy(plan.root, words)
        replayed_cost, nodes, depth = replay(canonical)
        if replayed_cost != plan.worst_case_cost:
            raise RuntimeError("canonical replay changed policy cost")
        entries.append(
            {
                "name": name,
                "exact_cost": plan.worst_case_cost,
                "states_solved": plan.states_solved,
                "canonical_sha256": digest(canonical),
                "canonical_node_count": nodes,
                "canonical_depth": depth,
                "canonical_policy": canonical,
            }
        )
    return {"label": label, "words": words, "entries": entries}


def main():
    p0 = profile("P0_isomorphic_orbit_representative", family(HELPER.PAIRS[0]))
    p2 = profile("P2_WL_nonisomorphic", family(HELPER.PAIRS[2]))
    comparisons = []
    for left, right in zip(p0["entries"], p2["entries"]):
        equal = left["canonical_sha256"] == right["canonical_sha256"]
        comparisons.append(
            {
                "name": left["name"],
                "equal": equal,
                "P0_sha256": left["canonical_sha256"],
                "P2_sha256": right["canonical_sha256"],
                "first_difference": None
                if equal
                else first_difference(left["canonical_policy"], right["canonical_policy"]),
            }
        )
    separated = any(not row["equal"] for row in comparisons)
    result = {
        "schema": "theorica.ternary-canonical-policy-signature/1",
        "level_costs": HELPER.COSTS,
        "opened_reserved_cases": 0,
        "remaining_reserved_cases": 18,
        "families": [p0, p2],
        "comparisons": comparisons,
        "summary": {
            "prediction_supported": separated,
            "classification": "canonical_policy_tree_separation" if separated else "invariant_falsified",
            "unequal_signatures": sum(not row["equal"] for row in comparisons),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    FULL.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    summary = json.loads(json.dumps(result))
    for family_row in summary["families"]:
        for entry in family_row["entries"]:
            del entry["canonical_policy"]
    summary["canonical_policies_gzip_sha256"] = hashlib.sha256(FULL.read_bytes()).hexdigest()
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
