#!/usr/bin/env python3
"""Generate content-addressed lower-bound DAGs for the ternary obstruction."""

from __future__ import annotations

import gzip
import hashlib
import json
from functools import cache
from itertools import combinations, product
from pathlib import Path

OUT = Path("results/qary_ternary_obstruction_certificate/certificates.json.gz")
SUMMARY = Path("results/qary_ternary_obstruction_certificate/results.json")
BASE = tuple(product(range(2), repeat=3))
FIBER = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
PAIRS = tuple(combinations(FIBER, 2))
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
            groups.append((row, level, prefix))
    return tuple(groups)


class Refuter:
    def __init__(self, words):
        self.words = tuple(words)
        self.groups = query_groups(self.words)
        self.alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in self.groups)
        self.states = 0
        self.nodes = {}
        self._feasible_cache = {}
        self._refute_cache = {}

    def children(self, counts, erased, remaining, group):
        row, _, _ = self.groups[group]
        rest = tuple(
            count - (index == group) for index, count in enumerate(remaining)
        )
        answer = []
        for observed in self.alphabets[group]:
            child_counts = tuple(
                min(2, count + (row[index] != observed))
                for index, count in enumerate(counts)
            )
            if any(count <= 1 for count in child_counts):
                answer.append(("observed", observed, child_counts, erased, rest))
        if erased == 0:
            answer.append(("erasure", None, counts, 1, rest))
        return tuple(answer)

    def admissible(self, counts, remaining, budget, initial):
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        answer = []
        for group, multiplicity in enumerate(remaining):
            if multiplicity == 0 or (initial and group not in INITIAL_GROUPS):
                continue
            row, level, _ = self.groups[group]
            if LEVEL_COSTS[level] > budget:
                continue
            if len({row[index] for index in live}) < 2:
                continue
            answer.append(group)
        return tuple(answer)

    def feasible(self, counts, erased, remaining, budget, initial):
        key = (counts, erased, remaining, budget, initial)
        if key not in self._feasible_cache:
            self._feasible_cache[key] = self._feasible_uncached(*key)
        return self._feasible_cache[key]

    def _feasible_uncached(self, counts, erased, remaining, budget, initial):
        self.states += 1
        if sum(count <= 1 for count in counts) <= 1:
            return True
        for group in self.admissible(counts, remaining, budget, initial):
            cost = LEVEL_COSTS[self.groups[group][1]]
            descendants = self.children(counts, erased, remaining, group)
            if descendants and all(
                self.feasible(child_counts, child_erased, child_remaining,
                              budget - cost, False)
                for _, _, child_counts, child_erased, child_remaining in descendants
            ):
                return True
        return False

    def refute(self, state):
        if state not in self._refute_cache:
            self._refute_cache[state] = self._refute_uncached(state)
        return self._refute_cache[state]

    def _refute_uncached(self, state):
        counts, erased, remaining, budget, initial = state
        if self.feasible(*state):
            raise ValueError("cannot refute a feasible state")
        edges = []
        for group in self.admissible(counts, remaining, budget, initial):
            cost = LEVEL_COSTS[self.groups[group][1]]
            losing = None
            for kind, observed, child_counts, child_erased, child_remaining in self.children(
                counts, erased, remaining, group
            ):
                child = (
                    child_counts,
                    child_erased,
                    child_remaining,
                    budget - cost,
                    False,
                )
                if not self.feasible(*child):
                    losing = (kind, observed, child)
                    break
            if losing is None:
                raise AssertionError("infeasible state has a winning query")
            kind, observed, child = losing
            child_hash = self.refute(child)
            edges.append(
                {
                    "group": group,
                    "response_kind": kind,
                    "observed": observed,
                    "child": child_hash,
                }
            )
        node = {
            "counts": list(counts),
            "erased": erased,
            "remaining": list(remaining),
            "budget": budget,
            "initial": initial,
            "edges": edges,
        }
        node_hash = digest(node)
        self.nodes.setdefault(node_hash, node)
        return node_hash

    def root(self, budget):
        state = (
            (0,) * len(self.words),
            0,
            (4,) * len(self.groups),
            budget,
            True,
        )
        return state, self.refute(state)


def max_depth(root, nodes):
    @cache
    def visit(node_hash):
        edges = nodes[node_hash]["edges"]
        return 0 if not edges else 1 + max(visit(edge["child"]) for edge in edges)

    return visit(root)


def main():
    certificates = []
    controls = []
    node_store = {}
    for pair in PAIRS:
        words = (*BASE, *pair)
        refuter = Refuter(words)
        root_state, root_hash = refuter.root(17)
        at_18 = refuter.feasible(
            root_state[0], root_state[1], root_state[2], 18, root_state[4]
        )
        singleton_controls = []
        for deleted in range(2):
            singleton_words = (*BASE, pair[1 - deleted])
            singleton = Refuter(singleton_words)
            singleton_state = (
                (0,) * len(singleton_words),
                0,
                (4,) * len(singleton.groups),
                17,
                True,
            )
            singleton_controls.append(singleton.feasible(*singleton_state))
        edge_count = sum(len(node["edges"]) for node in refuter.nodes.values())
        initial_responses = [
            {
                "group": edge["group"],
                "prefix": list(refuter.groups[edge["group"]][2]),
                "response_kind": edge["response_kind"],
                "observed": edge["observed"],
            }
            for edge in refuter.nodes[root_hash]["edges"]
        ]
        for node_hash, node in refuter.nodes.items():
            if node_hash in node_store and node_store[node_hash] != node:
                raise AssertionError("content-address collision")
            node_store[node_hash] = node
        certificates.append(
            {
                "words": [list(word) for word in words],
                "pair": [list(word) for word in pair],
                "root": root_hash,
            }
        )
        controls.append(
            {
                "pair": [list(word) for word in pair],
                "budget_17_infeasible": not refuter.feasible(*root_state),
                "budget_18_feasible": at_18,
                "singleton_deletions_budget_17_feasible": singleton_controls,
                "search_states": refuter.states,
                "certificate_nodes": len(refuter.nodes),
                "certificate_edges": edge_count,
                "certificate_max_depth": max_depth(root_hash, refuter.nodes),
                "root_hash": root_hash,
                "initial_adversarial_responses": initial_responses,
            }
        )
    index_by_hash = {
        node_hash: index for index, node_hash in enumerate(node_store)
    }
    packed_nodes = []
    for node in node_store.values():
        packed_nodes.append(
            [
                "".join(str(value) for value in node["counts"]),
                node["erased"],
                "".join(str(value) for value in node["remaining"]),
                node["budget"],
                int(node["initial"]),
                [
                    [
                        edge["group"],
                        "o" if edge["response_kind"] == "observed" else "e",
                        -1 if edge["observed"] is None else edge["observed"],
                        index_by_hash[edge["child"]],
                    ]
                    for edge in node["edges"]
                ],
            ]
        )
    for certificate in certificates:
        certificate["root_index"] = index_by_hash[certificate["root"]]
    payload = {
        "schema": "theorica.ternary-obstruction-refutation-dag/2",
        "level_costs": list(LEVEL_COSTS),
        "query_copies": 4,
        "corruption_budget": 1,
        "erasure_budget": 1,
        "nodes": packed_nodes,
        "certificates": certificates,
    }
    summary = {
        "schema": "theorica.ternary-obstruction-certificate-result/1",
        "controls": controls,
        "certificate_file_sha256": digest(payload),
        "shared_certificate_nodes": len(node_store),
    }
    summary["passed"] = all(
        row["budget_17_infeasible"]
        and row["budget_18_feasible"]
        and all(row["singleton_deletions_budget_17_feasible"])
        for row in controls
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(gzip.compress(canonical(payload) + b"\n", mtime=0))
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
