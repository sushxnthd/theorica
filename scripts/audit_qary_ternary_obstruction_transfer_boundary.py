#!/usr/bin/env python3
"""Independent stdlib-only replay of obstruction transfer evidence."""

import hashlib
import json
from collections import Counter
from functools import cache
from itertools import product
from pathlib import Path

SRC = Path("results/qary_ternary_obstruction_transfer_boundary/results.json")
OUT = SRC.with_name("audit.json")
COSTS = (2, 9, 3)


def rows(words):
    return tuple(
        tuple(w[l] if w[:l] == p else 0 for w in words)
        for l in range(3)
        for p in product(range(3), repeat=l)
    )


def level(q):
    return 0 if q < 1 else 1 if q < 4 else 2


def valid_map(source, target, m):
    sr, tr = rows(source), rows(target)
    cm = m["completions"]
    qm = m["queries"]
    if (
        sorted(cm) != list(range(10))
        or sorted(qm) != list(range(13))
        or any(level(q) != level(qm[q]) for q in range(13))
    ):
        return False
    return all(
        f"{q}:{a}" in m["cells"]
        and all(
            (x == a) == (tr[qm[q]][cm[i]] == m["cells"][f"{q}:{a}"])
            for i, x in enumerate(row)
        )
        for q, row in enumerate(sr)
        for a in set(row)
    )


def replay(policy, source, target, m):
    rr = rows(target)
    physical = tuple(r for r in rr for _ in range(4))
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
        query = 4 * m["queries"][sq] + copy
        if query in used:
            raise RuntimeError("query reuse")
        branches = [
            (None if a is None else m["cells"][f"{sq}:{a}"], child)
            for a, child in node["children"]
        ]
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


def exact(words, bound):
    groups = tuple((r, COSTS[level(q)]) for q, r in enumerate(rows(words)))
    alph = tuple(tuple(sorted(set(r))) for r, _ in groups)
    states = 0

    @cache
    def feasible(counts, erased, remaining, budget, initial):
        nonlocal states
        states += 1
        live = tuple(i for i, c in enumerate(counts) if c <= 1)
        if len(live) <= 1:
            return True
        for q, n in enumerate(remaining):
            row, cost = groups[q]
            if (
                not n
                or cost > budget
                or (initial and q not in range(1, 4))
                or len({row[i] for i in live}) < 2
            ):
                continue
            rest = tuple(x - (i == q) for i, x in enumerate(remaining))
            children = []
            for a in alph[q]:
                child = tuple(min(2, c + (row[i] != a)) for i, c in enumerate(counts))
                if any(x <= 1 for x in child):
                    children.append((child, erased))
            if not erased:
                children.append((counts, 1))
            if children and all(
                feasible(c, e, rest, budget - cost, False) for c, e in children
            ):
                return True
        return False

    at = feasible((0,) * 10, 0, (4,) * 13, bound, True)
    below = feasible((0,) * 10, 0, (4,) * 13, bound - 1, True)
    return at, below, states


def wl(left, right):
    def g(words, side):
        col = {}
        adj = {}
        for i in range(10):
            col[(side, "c", i)] = "c"
            adj[(side, "c", i)] = set()
        for q, row in enumerate(rows(words)):
            qv = (side, "q", q)
            col[qv] = f"q{level(q)}"
            adj[qv] = set()
            for a in set(row):
                rv = (side, "r", q, a)
                col[rv] = f"r{level(q)}"
                adj[rv] = {qv}
                adj[qv].add(rv)
                for i, x in enumerate(row):
                    if x == a:
                        adj[rv].add((side, "c", i))
                        adj[(side, "c", i)].add(rv)
        return col, adj

    lc, la = g(left, "l")
    rc, ra = g(right, "r")
    lab = {**lc, **rc}
    adj = {**la, **ra}
    while True:
        sig = {v: (lab[v], tuple(sorted(lab[n] for n in adj[v]))) for v in lab}
        pal = {s: i for i, s in enumerate(sorted(set(sig.values()), key=repr))}
        new = {v: pal[s] for v, s in sig.items()}
        stable = all((lab[a] == lab[b]) == (new[a] == new[b]) for a in lab for b in lab)
        lab = new
        if stable:
            break
    return Counter(lab[v] for v in lc) != Counter(lab[v] for v in rc)


def main():
    raw = SRC.read_bytes()
    data = json.loads(raw)
    source = tuple(map(tuple, data["source_words"]))
    checks = []
    for target in data["targets"]:
        words = tuple(map(tuple, target["words"]))
        mapping = valid_map(source, words, target["mapping"])
        cost = replay(data["source_policy"], source, words, target["mapping"])
        at, below, states = exact(words, 51)
        checks.append(
            {
                "name": target["name"],
                "mapping_valid": mapping,
                "transported_policy_cost": cost,
                "feasible_at_51": at,
                "infeasible_at_50": not below,
                "states": states,
                "passed": mapping and cost == 51 and at and not below,
            }
        )
    p2 = (*tuple(product(range(2), repeat=3)), (2, 1, 0), (2, 2, 0))
    summary = {
        "zero_theorica_imports": True,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "targets_checked": len(checks),
        "target_checks_passed": sum(x["passed"] for x in checks),
        "unseen_families_checked": sum(x["name"].startswith("unseen") for x in checks),
        "P0_P2_independently_WL_separated": wl(source, p2),
        "independent_states": sum(x["states"] for x in checks),
    }
    summary["passed"] = (
        len(checks) == 8
        and all(x["passed"] for x in checks)
        and summary["P0_P2_independently_WL_separated"]
    )
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-obstruction-transfer-boundary-audit/1",
                "targets": checks,
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
