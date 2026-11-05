#!/usr/bin/env python3
"""Exact set-valued optimal-policy quotient for the P0/P2 obstruction pair."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from functools import lru_cache
from pathlib import Path

from theorica.agents.corruption_resilient_features import certify_common_robust_plan

SPEC = importlib.util.spec_from_file_location("helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py"))
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)
OUT = Path("results/qary_ternary_optimal_policy_bisimulation/results.json")
FULL = Path("results/qary_ternary_optimal_policy_bisimulation/quotient.json.gz")
INF = 10**9


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build(label, words):
    rows = H.rows(words)
    costs = tuple(H.COSTS[H.level(i)] for i in range(len(rows)))
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)
    games = H.games(10)
    start = ((0,) * 10, 0, (H.COPIES,) * len(rows))
    compat = {}
    value_states = 0

    def live(counts):
        return tuple(i for i, count in enumerate(counts) if count <= 1)

    def terminal(counts):
        ids = live(counts)
        if ids not in compat:
            if len(ids) <= 1:
                compat[ids] = bool(ids)
            else:
                cert = certify_common_robust_plan(tuple(games[i] for i in ids))
                compat[ids] = cert.policy_identifiable and cert.certificate_valid
        return compat[ids]

    def candidates(state, allowed=None):
        counts, _, remaining = state
        ids, permitted = live(counts), None if allowed is None else frozenset(allowed)
        return tuple(g for g, n in enumerate(remaining) if n and (permitted is None or g in permitted) and len({rows[g][i] for i in ids}) >= 2)

    def transitions(state, group):
        counts, erasures, remaining = state
        nxt = tuple(n - (i == group) for i, n in enumerate(remaining))
        result = []
        for answer in alphabets[group]:
            changed = tuple(min(2, count + (rows[group][i] != answer)) for i, count in enumerate(counts))
            if live(changed):
                result.append((answer, (changed, erasures, nxt)))
        if erasures < 1:
            result.append((None, (counts, erasures + 1, nxt)))
        return tuple(result)

    @lru_cache(None)
    def value(state):
        nonlocal value_states
        value_states += 1
        if terminal(state[0]):
            return 0
        best = INF
        for group in candidates(state):
            child = [value(s) for _, s in transitions(state, group)]
            if child and max(child) < INF:
                best = min(best, costs[group] + max(child))
        return best

    def action_value(state, group):
        child = [value(s) for _, s in transitions(state, group)]
        return INF if not child or max(child) >= INF else costs[group] + max(child)

    nodes, cache, records = {}, {}, []

    def encode(state, allowed=None):
        key = (state, None if allowed is None else tuple(allowed))
        if key in cache:
            return cache[key]
        counts, erasures, _ = state
        ids = live(counts)
        if terminal(counts):
            content = {"kind": "terminal", "value": 0, "feasible_count": len(ids), "lie_histogram": sorted(counts[i] for i in ids), "erasures_used": erasures, "optimal_actions": []}
        else:
            groups = candidates(state, allowed)
            evaluated = [(g, action_value(state, g)) for g in groups]
            best = min(score for _, score in evaluated)
            records.append({"state_value": best, "actions": [{"query_cost": costs[g], "child_values": [value(s) for _, s in transitions(state, g)], "action_value": score, "optimal": score == best} for g, score in evaluated]})
            actions = []
            for group, score in evaluated:
                if score != best:
                    continue
                ordinary, erased = [], None
                for answer, child in transitions(state, group):
                    child_hash = encode(child)
                    if answer is None:
                        erased = child_hash
                    else:
                        ordinary.append(child_hash)
                cells = {}
                for i in ids:
                    cells[rows[group][i]] = cells.get(rows[group][i], 0) + 1
                actions.append({"query_level": H.level(group), "query_cost": costs[group], "cell_sizes": sorted(cells.values()), "ordinary_children": sorted(ordinary), "erasure_child": erased, "action_value": score})
            actions.sort(key=lambda item: json.dumps(item, sort_keys=True))
            content = {"kind": "state", "value": best, "feasible_count": len(ids), "lie_histogram": sorted(counts[i] for i in ids), "erasures_used": erasures, "optimal_actions": actions}
        digest = sha(content)
        if digest in nodes and nodes[digest] != content:
            raise RuntimeError("hash collision")
        nodes[digest] = content
        cache[key] = digest
        return digest

    roots = []
    for name, allowed in (("unrestricted", (1, 2, 3)), ("middle_1", (1,)), ("middle_2", (2,)), ("middle_3", (3,))):
        root = encode(start, allowed)
        roots.append({"name": name, "root_sha256": root, "exact_cost": nodes[root]["value"], "optimal_root_action_count": len(nodes[root]["optimal_actions"])})
    finite_omitted = [a["action_value"] - r["state_value"] for r in records for a in r["actions"] if not a["optimal"] and a["action_value"] < INF]
    return {"label": label, "words": words, "roots": roots, "quotient_nodes": nodes, "quotient_node_count": len(nodes), "value_states_solved": value_states, "compatibility_states_solved": len(compat), "bellman_audit": {"state_records": records, "evaluated_actions": sum(len(r["actions"]) for r in records), "omitted_finite_actions": len(finite_omitted), "minimum_omitted_gap": min(finite_omitted)}}


def difference(lh, rh, ln, rn, path="root"):
    if lh == rh:
        return None
    left, right = ln[lh], rn[rh]
    for key in ("kind", "value", "feasible_count", "lie_histogram", "erasures_used"):
        if left[key] != right[key]:
            return {"path": f"{path}.{key}", "P0": left[key], "P2": right[key]}
    la, ra = left["optimal_actions"], right["optimal_actions"]
    if len(la) != len(ra):
        return {"path": f"{path}.optimal_actions", "P0_count": len(la), "P2_count": len(ra)}
    for i, (a, b) in enumerate(zip(la, ra)):
        for key in ("query_level", "query_cost", "cell_sizes"):
            if a[key] != b[key]:
                return {"path": f"{path}.optimal_actions[{i}].{key}", "P0": a[key], "P2": b[key]}
        if a["erasure_child"] != b["erasure_child"]:
            found = difference(a["erasure_child"], b["erasure_child"], ln, rn, f"{path}.optimal_actions[{i}].erasure_child")
            if found:
                return found
        for j, (x, y) in enumerate(zip(a["ordinary_children"], b["ordinary_children"])):
            if x != y:
                found = difference(x, y, ln, rn, f"{path}.optimal_actions[{i}].ordinary_children[{j}]")
                if found:
                    return found
    return {"path": path, "P0_hash": lh, "P2_hash": rh}


def main():
    base = tuple(H.BASE)
    p0 = build("P0_isomorphic_orbit_representative", (*base, *H.PAIRS[0]))
    p2 = build("P2_WL_nonisomorphic", (*base, *H.PAIRS[2]))
    comparisons = []
    for left, right in zip(p0["roots"], p2["roots"]):
        equal = left["root_sha256"] == right["root_sha256"]
        comparisons.append({"name": left["name"], "equal": equal, "P0_root_sha256": left["root_sha256"], "P2_root_sha256": right["root_sha256"], "first_difference": None if equal else difference(left["root_sha256"], right["root_sha256"], p0["quotient_nodes"], p2["quotient_nodes"])})
    unequal = sum(not row["equal"] for row in comparisons)
    report = {"schema": "theorica.ternary-optimal-policy-bisimulation/1", "level_costs": H.COSTS, "opened_reserved_cases": 0, "remaining_reserved_cases": 18, "families": [p0, p2], "comparisons": comparisons, "summary": {"prediction_supported": bool(unequal), "classification": "set_valued_optimal_policy_separation" if unequal else "set_valued_invariant_falsified", "unequal_root_quotients": unequal, "passed": True}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    FULL.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    summary = json.loads(json.dumps(report))
    for family in summary["families"]:
        del family["quotient_nodes"]
        del family["bellman_audit"]["state_records"]
    summary["quotient_gzip_sha256"] = hashlib.sha256(FULL.read_bytes()).hexdigest()
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
