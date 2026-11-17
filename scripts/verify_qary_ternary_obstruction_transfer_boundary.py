#!/usr/bin/env python3
"""Exact obstruction-pair isomorphism and policy-transfer experiment."""

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_ternary_obstruction_transfer_boundary/results.json")
BASE = tuple(product(range(2), repeat=3))
FIBER = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
PAIRS = tuple(combinations(FIBER, 2))
COSTS = (2, 9, 3)
COPIES = 4


def rows(words):
    ids = tuple(sum(x * 3 ** (2 - i) for i, x in enumerate(w)) for w in words)
    return tuple(
        tuple(r[i] for i in ids) for r in qary_prefix_query_library(3, 3, copies=1)
    )


def level(q):
    return 0 if q < 1 else 1 if q < 4 else 2


def graph(words):
    color = {}
    adj = {}
    for i in range(10):
        color[f"c:{i}"] = "c"
        adj[f"c:{i}"] = set()
    for q, row in enumerate(rows(words)):
        qv = f"q:{q}"
        color[qv] = f"q:{level(q)}"
        adj[qv] = set()
        for a in sorted(set(row)):
            rv = f"r:{q}:{a}"
            color[rv] = f"r:{level(q)}"
            adj[rv] = {qv}
            adj[qv].add(rv)
            for i, x in enumerate(row):
                if x == a:
                    adj[rv].add(f"c:{i}")
                    adj[f"c:{i}"].add(rv)
    return color, adj


def refine(left, right):
    lc, la = left
    rc, ra = right
    lab = {
        **{("l", v): c for v, c in lc.items()},
        **{("r", v): c for v, c in rc.items()},
    }
    adj = {
        **{("l", v): {("l", n) for n in ns} for v, ns in la.items()},
        **{("r", v): {("r", n) for n in ns} for v, ns in ra.items()},
    }
    rounds = 0
    while True:
        sig = {v: (lab[v], tuple(sorted(lab[n] for n in adj[v]))) for v in lab}
        pal = {s: i for i, s in enumerate(sorted(set(sig.values()), key=repr))}
        new = {v: pal[s] for v, s in sig.items()}
        rounds += 1
        stable = all((lab[a] == lab[b]) == (new[a] == new[b]) for a in lab for b in lab)
        lab = new
        if stable:
            break
    return {v: lab["l", v] for v in lc}, {v: lab["r", v] for v in rc}, rounds


def isomorphism(left, right):
    lc, la = left
    rc, ra = right
    ll, rl, rounds = refine(left, right)
    lh = Counter(ll.values())
    rh = Counter(rl.values())
    cert = {
        "refinement_rounds": rounds,
        "left_color_sizes": sorted(lh.values()),
        "right_color_sizes": sorted(rh.values()),
    }
    if lh != rh:
        cert["WL_multiplicity_separation"] = True
        return None, cert
    classes = {}
    for v, c in rl.items():
        classes.setdefault(c, []).append(v)
    mapping = {}
    used = set()
    steps = 0

    def compatible(s, t):
        return lc[s] == rc[t] and all(
            (u in la[s]) == (mapping[u] in ra[t]) for u in mapping
        )

    def go():
        nonlocal steps
        if len(mapping) == len(lc):
            return True
        choices = []
        for s in lc:
            if s not in mapping:
                ts = [t for t in classes[ll[s]] if t not in used and compatible(s, t)]
                choices.append((len(ts), s, ts))
        _, s, ts = min(choices, key=lambda z: (z[0], z[1]))
        for t in sorted(ts):
            steps += 1
            mapping[s] = t
            used.add(t)
            if go():
                return True
            used.remove(t)
            del mapping[s]
        return False

    if not go():
        cert.update(exhaustive_nonisomorphism=True, backtracking_steps=steps)
        return None, cert
    valid = (
        len(set(mapping.values())) == len(mapping)
        and all(lc[v] == rc[mapping[v]] for v in mapping)
        and all(
            (w in la[v]) == (mapping[w] in ra[mapping[v]])
            for v in mapping
            for w in mapping
        )
    )
    if not valid:
        raise RuntimeError("invalid isomorphism")
    cert.update(mapping_edge_checked=True, backtracking_steps=steps)
    return mapping, cert


def compact(full, source, target):
    sr, tr = rows(source), rows(target)
    cm = [int(full[f"c:{i}"].split(":")[1]) for i in range(10)]
    qm = [int(full[f"q:{q}"].split(":")[1]) for q in range(13)]
    cells = {}
    for q, row in enumerate(sr):
        for a in sorted(set(row)):
            _, tq, ta = full[f"r:{q}:{a}"].split(":")
            tq = int(tq)
            ta = int(ta)
            if tq != qm[q] or any(
                (x == a) != (tr[tq][cm[i]] == ta) for i, x in enumerate(row)
            ):
                raise RuntimeError("bad cell map")
            cells[f"{q}:{a}"] = ta
    return {"completions": cm, "queries": qm, "cells": cells}


def games(n):
    return tuple(
        (((1 - (p := Fraction(i + 1, n + 1)), p - 1), (-p, p))) for i in range(n)
    )


def solve(words):
    physical = tuple(r for r in rows(words) for _ in range(COPIES))
    return plan_adaptive_decision_queries_with_weighted_faults(
        games(10),
        physical,
        query_costs=qary_prefix_query_costs(3, 3, copies=4, level_costs=COSTS),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 16),
        known_feasible_cost_upper_bound=51,
    )


def serialize(root):
    ids = {}
    nodes = []

    def visit(node):
        if id(node) in ids:
            return ids[id(node)]
        i = len(ids)
        ids[id(node)] = i
        nodes.append(None)
        nodes[i] = (
            {"query": None}
            if node.query_index is None
            else {
                "query": node.query_index,
                "children": [[a, visit(c)] for a, c in node.children],
            }
        )
        return i

    return {"root": visit(root), "nodes": nodes}


def replay(policy, target, mapping):
    physical = tuple(r for r in rows(target) for _ in range(4))
    costs = tuple(c for c, n in zip(COSTS, (4, 12, 36)) for _ in range(n))
    nodes = policy["nodes"]

    def walk(nid, counts, erased, used, spent):
        node = nodes[nid]
        live = [i for i, c in enumerate(counts) if c <= 1]
        if node["query"] is None:
            if len(live) > 1:
                raise RuntimeError("ambiguous leaf")
            return spent
        sq, copy = divmod(node["query"], 4)
        tq = mapping["queries"][sq]
        query = 4 * tq + copy
        if query in used:
            raise RuntimeError("query reuse")
        branches = []
        for a, child in node["children"]:
            branches.append(
                (None if a is None else mapping["cells"][f"{sq}:{a}"], child)
            )
        if len({a for a, _ in branches}) != len(branches):
            raise RuntimeError("collapsed branches")
        worst = spent
        for a, child in branches:
            if a is None:
                if erased:
                    raise RuntimeError("second erasure")
                cc, ee = counts, 1
            else:
                cc = tuple(
                    min(2, c + (physical[query][i] != a)) for i, c in enumerate(counts)
                )
                ee = erased
                if not any(c <= 1 for c in cc):
                    raise RuntimeError("dead branch")
            worst = max(
                worst, walk(child, cc, ee, used | {query}, spent + costs[query])
            )
        return worst

    return walk(policy["root"], (0,) * 10, 0, set(), 0)


def exposure_antichain(policy, mapping=None):
    terminal = []
    nodes = policy["nodes"]

    def walk(nid, counts):
        node = nodes[nid]
        if node["query"] is None:
            terminal.append(counts)
            return
        q = node["query"] // 4
        if mapping is not None:
            q = mapping["queries"][q]
        nxt = list(counts)
        nxt[level(q)] += 1
        for _, child in node["children"]:
            walk(child, tuple(nxt))

    walk(policy["root"], (0, 0, 0))
    unique = set(terminal)
    return sorted(
        x
        for x in unique
        if not any(y != x and all(a >= b for a, b in zip(y, x)) for y in unique)
    )


def transform(words, mask):
    return tuple(
        tuple(3 - x if x in (1, 2) and mask & (1 << i) else x for i, x in enumerate(w))
        for w in words
    )


def main():
    fam = [(*BASE, *p) for p in PAIRS]
    iso01, c01 = isomorphism(graph(fam[0]), graph(fam[1]))
    iso02, c02 = isomorphism(graph(fam[0]), graph(fam[2]))
    if iso01 is None or iso02 is not None or not c02.get("WL_multiplicity_separation"):
        raise RuntimeError("structural prediction failed")
    source_plan = solve(fam[0])
    policy = serialize(source_plan.root)
    targets = [("opened_pair_P1", fam[1], compact(iso01, fam[0], fam[1]), c01)]
    for mask in range(1, 8):
        target = transform(fam[0], mask)
        full, cert = isomorphism(graph(fam[0]), graph(target))
        if full is None:
            raise RuntimeError("transform not isomorphic")
        targets.append(
            (
                f"unseen_coordinate_swap_{mask:03b}",
                target,
                compact(full, fam[0], target),
                cert,
            )
        )
    source_exposures = exposure_antichain(policy)
    evidence = []
    for name, target, mapping, cert in targets:
        transported = replay(policy, target, mapping)
        plan = solve(target)
        target_exposures = exposure_antichain(policy, mapping)
        evidence.append(
            {
                "name": name,
                "words": target,
                "mapping": mapping,
                "isomorphism_certificate": cert,
                "transported_policy_cost": transported,
                "transported_exposure_antichain": target_exposures,
                "exact_cost": plan.worst_case_cost,
                "states_solved": plan.states_solved,
                "passed": transported == plan.worst_case_cost == 51
                and target_exposures == source_exposures,
            }
        )
    summary = {
        "source_exact_cost": source_plan.worst_case_cost,
        "source_states_solved": source_plan.states_solved,
        "serialized_policy_nodes": len(policy["nodes"]),
        "P0_P1_isomorphic": True,
        "P0_P2_isomorphic": False,
        "P0_P2_WL_separated": True,
        "targets_tested": len(evidence),
        "unseen_families_tested": 7,
        "transported_cost_51": sum(
            x["transported_policy_cost"] == 51 for x in evidence
        ),
        "exact_cost_51": sum(x["exact_cost"] == 51 for x in evidence),
        "reserved_cost_holdouts_opened": 0,
    }
    summary["passed"] = (
        all(x["passed"] for x in evidence) and source_plan.worst_case_cost == 51
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-obstruction-transfer-boundary/1",
                "source_words": fam[0],
                "source_policy": policy,
                "source_exposure_antichain": source_exposures,
                "P0_P1_certificate": c01,
                "P0_P2_nonisomorphism_certificate": c02,
                "targets": evidence,
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
