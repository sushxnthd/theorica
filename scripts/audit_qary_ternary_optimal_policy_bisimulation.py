#!/usr/bin/env python3
"""Zero-production-import replay of optimal-policy quotient evidence."""
import gzip
import hashlib
import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_optimal_policy_bisimulation/results.json")
FULL = Path("results/qary_ternary_optimal_policy_bisimulation/quotient.json.gz")
OUT = Path("results/qary_ternary_optimal_policy_bisimulation/audit.json")


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    summary = json.loads(SOURCE.read_text())
    assert hashlib.sha256(FULL.read_bytes()).hexdigest() == summary["quotient_gzip_sha256"]
    report = json.loads(gzip.decompress(FULL.read_bytes()))
    hashes = edges = bellman = actions = 0
    ok = True
    for family in report["families"]:
        nodes = family["quotient_nodes"]
        for digest, node in nodes.items():
            hashes += 1
            ok &= sha(node) == digest
            for action in node["optimal_actions"]:
                children = list(action["ordinary_children"]) + ([action["erasure_child"]] if action["erasure_child"] else [])
                edges += 2
                ok &= all(child in nodes for child in children)
                ok &= action["action_value"] == action["query_cost"] + max(nodes[child]["value"] for child in children) == node["value"]
        for record in family["bellman_audit"]["state_records"]:
            bellman += 1
            actions += len(record["actions"])
            finite = [a for a in record["actions"] if a["action_value"] < 10**9]
            best = min(a["action_value"] for a in finite)
            ok &= best == record["state_value"]
            for action in record["actions"]:
                expected = 10**9 if max(action["child_values"]) >= 10**9 else action["query_cost"] + max(action["child_values"])
                ok &= action["action_value"] == expected
                ok &= action["optimal"] == (action["action_value"] == best)
    audit = {"schema": "theorica.ternary-optimal-policy-bisimulation-audit/1", "production_imports": 0, "content_hashes_checked": hashes, "edge_and_optimality_checks": edges, "bellman_state_records_checked": bellman, "evaluated_actions_checked": actions, "root_witnesses_checked": len(report["comparisons"]), "passed": bool(ok)}
    OUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
