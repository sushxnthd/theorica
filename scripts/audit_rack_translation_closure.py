#!/usr/bin/env python3
"""Independent audit on modular Alexander quandles; no production imports."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path


def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def inv(p):
    out = [None] * len(p)
    for i, value in enumerate(p):
        out[value] = i
    return tuple(out)


def closure_reconstruct(table, seeds):
    n = len(table)
    rows = {i: table[i] for i in seeds}
    conflicts = 0
    witnesses = []
    again = True
    while again:
        again = False
        for a, b in itertools.product(tuple(rows), repeat=2):
            c = rows[a][b]
            candidate = compose(rows[a], compose(rows[b], inv(rows[a])))
            if c in rows:
                conflicts += candidate != rows[c]
            else:
                rows[c] = candidate
                witnesses.append((a, b, c))
                again = True
    rebuilt = tuple(rows[i] for i in range(n)) if len(rows) == n else None
    return rebuilt, conflicts, witnesses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-modulus", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    families = eligible = exact = collisions = derived_rows = 0
    failures = []
    for modulus in range(2, args.max_modulus + 1):
        for multiplier in range(1, modulus):
            if math.gcd(multiplier, modulus) != 1:
                continue
            table = tuple(
                tuple(((1 - multiplier) * x + multiplier * y) % modulus for y in range(modulus))
                for x in range(modulus)
            )
            families += 1
            seed_sets = {
                tuple(range(seed_count))
                for seed_count in range(1, min(modulus, 6) + 1)
            }
            seed_sets.update(
                tuple(sorted({0, offset % modulus, (offset * multiplier + 1) % modulus}))
                for offset in range(1, min(modulus, 12))
            )
            for seeds in sorted(seed_sets, key=lambda item: (len(item), item)):
                rebuilt, conflict_count, witnesses = closure_reconstruct(table, seeds)
                if rebuilt is None:
                    continue
                eligible += 1
                collisions += conflict_count
                derived_rows += len(witnesses)
                if rebuilt == table and conflict_count == 0:
                    exact += 1
                elif len(failures) < 10:
                    failures.append({
                        "modulus": modulus, "multiplier": multiplier,
                        "seeds": seeds, "conflicts": conflict_count,
                    })

    gates = {
        "nonempty_family_corpus": families > 0,
        "nonempty_generating_cases": eligible > 0,
        "all_reconstructions_exact": exact == eligible,
        "all_derivation_collisions_agree": collisions == 0,
        "no_failures": not failures,
    }
    payload = {
        "schema": "theorica.rack-translation-closure-independent-audit.v1",
        "classification": "INDEPENDENT_CONSTRUCTIVE_AUDIT",
        "max_modulus": args.max_modulus,
        "alexander_quandle_families": families,
        "forward_generating_seed_subsets": eligible,
        "exact_reconstructions": exact,
        "derived_rows": derived_rows,
        "derivation_conflicts": collisions,
        "failures": failures,
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
