#!/usr/bin/env python3
"""Zero-production-import audit of canonical policy-signature evidence."""

import gzip
import hashlib
import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_canonical_policy_signature/results.json")
FULL = Path("results/qary_ternary_canonical_policy_signature/canonical_policies.json.gz")
OUT = Path("results/qary_ternary_canonical_policy_signature/audit.json")


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def replay(value):
    assert value["kind"] in {"terminal", "query"}
    assert value["feasible_count"] == len(value["lie_histogram"])
    assert all(item in {0, 1} for item in value["lie_histogram"])
    assert value["erasures_used"] in {0, 1}
    if value["kind"] == "terminal":
        return 0, 1, 0
    assert value["query_level"] in {0, 1, 2}
    assert value["query_cost"] == (2, 9, 3)[value["query_level"]]
    assert sum(value["cell_sizes"]) == value["feasible_count"]
    children = list(value["ordinary_children"])
    # Responses absent from the currently feasible set can still be reachable
    # after the one allowed substitution, so ordinary branches may outnumber
    # the nonempty truthful cells recorded by the invariant.
    assert len(children) >= len(value["cell_sizes"])
    if value["erasure_child"] is not None:
        children.append(value["erasure_child"])
    checked = [replay(child) for child in children]
    return value["query_cost"] + max(x[0] for x in checked), 1 + sum(x[1] for x in checked), 1 + max(x[2] for x in checked)


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


def main():
    summary = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert hashlib.sha256(FULL.read_bytes()).hexdigest() == summary["canonical_policies_gzip_sha256"]
    report = json.loads(gzip.decompress(FULL.read_bytes()))
    checks = []
    for family in report["families"]:
        for entry in family["entries"]:
            cost, nodes, depth = replay(entry["canonical_policy"])
            checks.append(
                cost == entry["exact_cost"]
                and nodes == entry["canonical_node_count"]
                and depth == entry["canonical_depth"]
                and digest(entry["canonical_policy"]) == entry["canonical_sha256"]
            )
    comparison_checks = []
    left_entries, right_entries = (family["entries"] for family in report["families"])
    for claim, left, right in zip(report["comparisons"], left_entries, right_entries):
        equal = digest(left["canonical_policy"]) == digest(right["canonical_policy"])
        witness = None if equal else first_difference(left["canonical_policy"], right["canonical_policy"])
        comparison_checks.append(equal == claim["equal"] and witness == claim["first_difference"])
    audit = {
        "schema": "theorica.ternary-canonical-policy-signature-audit/1",
        "production_imports": 0,
        "compressed_evidence_sha256_checked": True,
        "policy_trees_checked": len(checks),
        "comparisons_checked": len(comparison_checks),
        "all_tree_hash_cost_shape_checks_passed": all(checks),
        "all_comparison_witness_checks_passed": all(comparison_checks),
        "passed": all(checks) and all(comparison_checks),
    }
    OUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
