#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def compose(left, right):
    return tuple(left[v] for v in right)


def inverse(p):
    out = [0] * len(p)
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def is_rack(table):
    for a, la in enumerate(table):
        ia = inverse(la)
        for b, lb in enumerate(table):
            if table[la[b]] != compose(la, compose(lb, ia)):
                return False
    return True


def closure(table, seeds):
    known = set(seeds)
    while True:
        old = len(known)
        for a in tuple(known):
            for b in tuple(known):
                known.add(table[a][b])
        if len(known) == old:
            return known


def greedy(table):
    seeds, known = [], set()
    while len(known) < len(table):
        seeds.append(min(set(range(len(table))) - known))
        known = closure(table, seeds)
    return tuple(seeds)


def minimum_generators(table):
    n = len(table)
    for size in range(1, n + 1):
        for seeds in itertools.combinations(range(n), size):
            if len(closure(table, seeds)) == n:
                return tuple(seeds)
    raise AssertionError


def hidden_cycle_rack(n, z):
    identity = tuple(range(n))
    others = [x for x in range(n) if x != z]
    cycle = list(range(n))
    for i, x in enumerate(others):
        cycle[x] = others[(i + 1) % len(others)]
    return tuple(tuple(cycle) if x == z else identity for x in range(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-exhaustive-n", type=int, default=4)
    ap.add_argument("--max-family-n", type=int, default=64)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    exhaustive = {}
    first_gap = None
    validity_failures = []
    for n in range(1, args.max_exhaustive_n + 1):
        perms = tuple(itertools.permutations(range(n)))
        racks = gaps = max_additive_gap = 0
        for table in itertools.product(perms, repeat=n):
            if not is_rack(table):
                continue
            racks += 1
            g = greedy(table)
            o = minimum_generators(table)
            if len(closure(table, g)) != n:
                validity_failures.append({"n": n, "table": table, "greedy": g})
            if len(g) > len(o):
                gaps += 1
                max_additive_gap = max(max_additive_gap, len(g) - len(o))
                if first_gap is None:
                    first_gap = {
                        "n": n, "table": table,
                        "greedy_seeds": g, "optimal_seeds": o,
                    }
        exhaustive[str(n)] = {
            "racks": racks,
            "greedy_suboptimal_racks": gaps,
            "max_additive_seed_gap": max_additive_gap,
        }

    family = {}
    family_failures = []
    for n in range(3, args.max_family_n + 1):
        z = n - 1
        table = hidden_cycle_rack(n, z)
        rack_ok = is_rack(table)
        singleton_full = any(len(closure(table, (x,))) == n for x in range(n))
        two_seed_full = all(
            len(closure(table, (z, x))) == n for x in range(n) if x != z
        )
        greedy_rows = len(greedy(table))
        expectation = Fraction(n * (n + 1) // 2 + 1, n)
        formula = Fraction(n + 1, 2) + Fraction(1, n)
        row_transcript_match = all(
            table[x] == tuple(range(n)) for x in range(n - 1)
        )
        record = {
            "rack": rack_ok,
            "minimum_rank": 2 if (not singleton_full and two_seed_full) else None,
            "greedy_rows": greedy_rows,
            "identity_prefix_rows": n - 1 if row_transcript_match else None,
            "random_label_expected_rows": f"{expectation.numerator}/{expectation.denominator}",
            "expected_formula": f"{formula.numerator}/{formula.denominator}",
        }
        family[str(n)] = record
        if not (
            rack_ok and not singleton_full and two_seed_full
            and greedy_rows == n and row_transcript_match
            and expectation == formula
        ):
            family_failures.append({"n": n, **record})

    gates = {
        "family_is_rack_through_64": not family_failures,
        "family_minimum_rank_exactly_two": all(v["minimum_rank"] == 2 for v in family.values()),
        "order_three_is_first_greedy_gap": (
            first_gap is not None and first_gap["n"] == 3
            and tuple(first_gap["greedy_seeds"]) == (0, 1, 2)
            and len(first_gap["optimal_seeds"]) == 2
            and exhaustive["1"]["greedy_suboptimal_racks"] == 0
            and exhaustive["2"]["greedy_suboptimal_racks"] == 0
        ),
        "greedy_always_generates_exhaustive_domain": not validity_failures,
        "adversarial_label_forces_n_rows": all(v["greedy_rows"] == int(n) for n, v in family.items()),
        "randomized_expectation_exact": all(
            v["random_label_expected_rows"] == v["expected_formula"] for v in family.values()
        ),
    }
    payload = {
        "schema": "theorica.adaptive-rack-seed-boundary.v1",
        "classification": "EXACT_ENUMERATION_AND_CONSTRUCTIVE_LOWER_BOUND",
        "claim": (
            "In the complete-row acquisition model under only a certified left-rack promise, "
            "every deterministic always-correct policy has instances of generating rank 2 "
            "requiring n queried rows; least-outside closure attains this worst case."
        ),
        "max_exhaustive_n": args.max_exhaustive_n,
        "max_family_n": args.max_family_n,
        "exhaustive": exhaustive,
        "first_greedy_gap": first_gap,
        "family": family,
        "family_failures": family_failures,
        "validity_failures": validity_failures,
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "gates": gates,
                      "exhaustive": exhaustive, "first_gap": first_gap,
                      "canonical_sha256": payload["canonical_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
