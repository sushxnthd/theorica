#!/usr/bin/env python3
"""Independent no-search verifier for ternary obstruction refutation DAGs."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
from itertools import product
from pathlib import Path

SOURCE = Path("results/qary_ternary_obstruction_certificate/certificates.json.gz")
SUMMARY = Path("results/qary_ternary_obstruction_certificate/results.json")
OUT = Path("results/qary_ternary_obstruction_certificate/audit.json")
LEVEL_COSTS = (1, 3, 1)
INITIAL_GROUPS = frozenset(range(1, 4))


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def query_groups(words):
    groups = []
    for level in range(3):
        for prefix in product(range(3), repeat=level):
            row = tuple(
                word[level] if word[:level] == prefix else 0 for word in words
            )
            groups.append((row, level))
    return tuple(groups)


def descendants(node, group, groups):
    counts = tuple(node["counts"])
    remaining = tuple(node["remaining"])
    row, _ = groups[group]
    rest = tuple(
        count - (index == group) for index, count in enumerate(remaining)
    )
    answer = []
    for observed in sorted(set(row)):
        child_counts = tuple(
            min(2, count + (row[index] != observed))
            for index, count in enumerate(counts)
        )
        if any(count <= 1 for count in child_counts):
            answer.append(("observed", observed, child_counts, node["erased"], rest))
    if node["erased"] == 0:
        answer.append(("erasure", None, counts, 1, rest))
    return tuple(answer)


def admissible(node, groups):
    counts = tuple(node["counts"])
    remaining = tuple(node["remaining"])
    live = tuple(index for index, count in enumerate(counts) if count <= 1)
    answer = []
    for group, multiplicity in enumerate(remaining):
        if multiplicity == 0 or (node["initial"] and group not in INITIAL_GROUPS):
            continue
        row, level = groups[group]
        if LEVEL_COSTS[level] > node["budget"]:
            continue
        if len({row[index] for index in live}) < 2:
            continue
        answer.append(group)
    return tuple(answer)


def unpack_nodes(packed_nodes):
    nodes = []
    hashes = []
    for index, packed in enumerate(packed_nodes):
        if len(packed) != 6:
            raise ValueError("packed node width mismatch")
        counts, erased, remaining, budget, initial, packed_edges = packed
        edges = []
        for group, kind, observed, child_index in packed_edges:
            if child_index < 0 or child_index >= index:
                raise ValueError("child index is not topological")
            if kind not in {"o", "e"}:
                raise ValueError("unknown response code")
            edges.append(
                {
                    "group": group,
                    "response_kind": "observed" if kind == "o" else "erasure",
                    "observed": observed if kind == "o" else None,
                    "child": hashes[child_index],
                }
            )
        node = {
            "counts": [int(value) for value in counts],
            "erased": erased,
            "remaining": [int(value) for value in remaining],
            "budget": budget,
            "initial": bool(initial),
            "edges": edges,
        }
        nodes.append(node)
        hashes.append(digest(node))
    return nodes, hashes


def verify_certificate(certificate, packed_nodes, nodes, hashes):
    words = tuple(tuple(word) for word in certificate["words"])
    groups = query_groups(words)
    seen = set()
    edge_count = 0
    max_depth = 0

    def visit(node_index, depth):
        nonlocal edge_count, max_depth
        if node_index in seen:
            return
        if node_index < 0 or node_index >= len(nodes):
            raise ValueError("missing child node")
        node = nodes[node_index]
        if len(node["counts"]) != len(words) or len(node["remaining"]) != len(groups):
            raise ValueError("state dimension mismatch")
        if sum(count <= 1 for count in node["counts"]) <= 1:
            raise ValueError("terminal state cannot be refuted")
        expected_groups = admissible(node, groups)
        edges = node["edges"]
        if tuple(edge["group"] for edge in edges) != expected_groups:
            raise ValueError("planner-query coverage mismatch")
        seen.add(node_index)
        edge_count += len(edges)
        max_depth = max(max_depth, depth)
        for edge, packed_edge in zip(edges, packed_nodes[node_index][5], strict=True):
            group = edge["group"]
            matches = [
                row
                for row in descendants(node, group, groups)
                if row[0] == edge["response_kind"] and row[1] == edge["observed"]
            ]
            if len(matches) != 1:
                raise ValueError("illegal adversarial response")
            _, _, counts, erased, remaining = matches[0]
            child_index = packed_edge[3]
            child = nodes[child_index]
            expected_budget = node["budget"] - LEVEL_COSTS[groups[group][1]]
            if (
                tuple(child["counts"]) != counts
                or child["erased"] != erased
                or tuple(child["remaining"]) != remaining
                or child["budget"] != expected_budget
                or child["initial"]
            ):
                raise ValueError("invalid state transition")
            visit(child_index, depth + 1)

    root = certificate["root_index"]
    if hashes[root] != certificate["root"]:
        raise ValueError("root content hash mismatch")
    visit(root, 0)
    root_node = nodes[root]
    if root_node["counts"] != [0] * len(words):
        raise ValueError("invalid root counts")
    if root_node["erased"] != 0 or root_node["remaining"] != [4] * len(groups):
        raise ValueError("invalid root resources")
    if root_node["budget"] != 17 or not root_node["initial"]:
        raise ValueError("invalid root budget/action constraint")
    return {
        "nodes": len(seen),
        "edges": edge_count,
        "max_depth": max_depth,
        "reachable": seen,
    }


def verify_payload(payload):
    if payload["schema"] != "theorica.ternary-obstruction-refutation-dag/2":
        raise ValueError("schema mismatch")
    if payload["level_costs"] != [1, 3, 1] or payload["query_copies"] != 4:
        raise ValueError("model mismatch")
    packed_nodes = payload["nodes"]
    nodes, hashes = unpack_nodes(packed_nodes)
    audits = [
        verify_certificate(certificate, packed_nodes, nodes, hashes)
        for certificate in payload["certificates"]
    ]
    reachable = set().union(*(audit.pop("reachable") for audit in audits))
    if reachable != set(range(len(nodes))):
        raise ValueError("uncommitted or unreachable certificate nodes")
    return audits


def mutation_rejections(payload):
    mutations = []
    child = copy.deepcopy(payload)
    root = child["certificates"][0]["root_index"]
    child["nodes"][root][5][0][3] = len(child["nodes"]) + 1
    mutations.append(child)
    budget = copy.deepcopy(payload)
    root = budget["certificates"][0]["root_index"]
    budget["nodes"][root][3] -= 1
    mutations.append(budget)
    state = copy.deepcopy(payload)
    root = state["certificates"][0]["root_index"]
    state["nodes"][root][0] = "1" + state["nodes"][root][0][1:]
    mutations.append(state)
    rejected = 0
    for mutation in mutations:
        try:
            verify_payload(mutation)
        except ValueError:
            rejected += 1
    return rejected, len(mutations)


def main():
    payload = json.loads(gzip.decompress(SOURCE.read_bytes()))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    audits = verify_payload(payload)
    rejected, total = mutation_rejections(payload)
    report = {
        "production_module_imports": 0,
        "optimizer_calls": 0,
        "certificate_file_sha256": digest(payload),
        "summary_file_sha256_matches": digest(payload)
        == summary["certificate_file_sha256"],
        "certificates_verified": len(audits),
        "certificate_audits": audits,
        "mutation_rejections": rejected,
        "mutation_total": total,
        "shared_nodes_hash_checked": len(payload["nodes"]),
    }
    report["passed"] = (
        summary["passed"]
        and report["summary_file_sha256_matches"]
        and report["certificates_verified"] == 3
        and rejected == total == 3
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
