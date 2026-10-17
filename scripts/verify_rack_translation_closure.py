#!/usr/bin/env python3
"""Exhaust the rack translation-closure theorem through order four."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

from theorica.agents.translation_certificate import reconstruct_rack_from_generating_rows


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[value] for value in right)


def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * len(permutation)
    for index, value in enumerate(permutation):
        result[value] = index
    return tuple(result)


def is_rack(table: tuple[tuple[int, ...], ...]) -> bool:
    for a, left_a in enumerate(table):
        inverse_a = inverse(left_a)
        for b, left_b in enumerate(table):
            c = left_a[b]
            if table[c] != compose(left_a, compose(left_b, inverse_a)):
                return False
    return True


def forward_closure(table: tuple[tuple[int, ...], ...], seeds: tuple[int, ...]) -> set[int]:
    known = set(seeds)
    changed = True
    while changed:
        changed = False
        for a in tuple(known):
            for b in tuple(known):
                c = table[a][b]
                if c not in known:
                    known.add(c)
                    changed = True
    return known


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    by_n = {}
    counterexamples = []
    ablations = {"identity_only_failure": None, "reversed_conjugation_failure": None,
                 "nonrack_false_reconstruction": None}
    for n in range(1, args.max_n + 1):
        permutations = tuple(itertools.permutations(range(n)))
        operations = racks = quandles = generating_subsets = reconstructions = 0
        for table in itertools.product(permutations, repeat=n):
            operations += 1
            rack = is_rack(table)
            if not rack:
                if ablations["nonrack_false_reconstruction"] is None:
                    for size in range(1, n + 1):
                        found = False
                        for seeds in itertools.combinations(range(n), size):
                            if len(forward_closure(table, seeds)) != n:
                                continue
                            result = reconstruct_rack_from_generating_rows(
                                lambda x, y, t=table: t[x][y], n, seeds
                            )
                            if result.accepted and not np.array_equal(result.reconstructed_table, table):
                                ablations["nonrack_false_reconstruction"] = {
                                    "n": n, "seeds": seeds, "table": table
                                }
                                found = True
                                break
                        if found:
                            break
                continue
            racks += 1
            if all(table[x][x] == x for x in range(n)):
                quandles += 1
            for size in range(1, n + 1):
                for seeds in itertools.combinations(range(n), size):
                    if len(forward_closure(table, seeds)) != n:
                        continue
                    generating_subsets += 1
                    result = reconstruct_rack_from_generating_rows(
                        lambda x, y, t=table: t[x][y], n, seeds
                    )
                    reconstructions += 1
                    expected_calls = size * n
                    if (not result.accepted or result.oracle_calls != expected_calls
                            or not np.array_equal(result.reconstructed_table, table)):
                        counterexamples.append({
                            "n": n, "seeds": seeds, "table": table,
                            "reason": result.reason, "calls": result.oracle_calls,
                        })
                    if ablations["identity_only_failure"] is None:
                        known = {s: table[s] for s in seeds}
                        for a in seeds:
                            for b in seeds:
                                c = table[a][b]
                                if c not in known and table[c] != table[b]:
                                    ablations["identity_only_failure"] = {
                                        "n": n, "a": a, "b": b, "c": c, "table": table
                                    }
                                    break
                            if ablations["identity_only_failure"] is not None:
                                break
                    if ablations["reversed_conjugation_failure"] is None:
                        for a in seeds:
                            ia = inverse(table[a])
                            for b in seeds:
                                c = table[a][b]
                                wrong = compose(ia, compose(table[b], table[a]))
                                if wrong != table[c]:
                                    ablations["reversed_conjugation_failure"] = {
                                        "n": n, "a": a, "b": b, "c": c, "table": table
                                    }
                                    break
                            if ablations["reversed_conjugation_failure"] is not None:
                                break
        by_n[str(n)] = {
            "permutation_row_operations": operations,
            "racks": racks,
            "quandles": quandles,
            "forward_generating_seed_subsets": generating_subsets,
            "exact_reconstructions": reconstructions,
        }

    gates = {
        "no_rack_counterexample": not counterexamples,
        "every_eligible_case_reconstructed": all(
            item["forward_generating_seed_subsets"] == item["exact_reconstructions"]
            for item in by_n.values()
        ),
        "identity_only_ablation_falsified": ablations["identity_only_failure"] is not None,
        "reversed_order_ablation_falsified": ablations["reversed_conjugation_failure"] is not None,
        "rack_promise_is_necessary": ablations["nonrack_false_reconstruction"] is not None,
    }
    payload = {
        "schema": "theorica.rack-translation-closure.v1",
        "classification": "EXACT_ENUMERATION",
        "max_n": args.max_n,
        "theorem_query_bound": "|S|*n when forward_closure(S)=X under a certified left-rack promise",
        "by_n": by_n,
        "ablations": ablations,
        "counterexamples": counterexamples[:10],
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "gates": gates,
                      "by_n": by_n, "canonical_sha256": payload["canonical_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
