#!/usr/bin/env python3
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from theorica.agents.rack_seed_acquisition import (
    spot_check_hidden_cycle_witness,
    verify_hidden_cycle_family_by_cells,
)


def hidden_cycle_table(n: int, z: int, reverse: bool) -> np.ndarray:
    table = np.tile(np.arange(n), (n, 1))
    others = [x for x in range(n) if x != z]
    if reverse:
        others = [others[0], *reversed(others[1:])]
    for index, value in enumerate(others):
        table[z, value] = others[(index + 1) % len(others)]
    return table


def canonical_digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_n < 3:
        raise SystemExit("max-n must be at least 3")

    failures: list[dict] = []
    family_instances = 0
    runtime_acceptance_checks = 0
    corruption_witnesses = 0
    active_row_duplicate_checks = 0
    frontier_checks = 0
    hypergeometric_checks = 0
    spot_runtime_checks = 0

    for n in range(3, args.max_n + 1):
        orientations = (False,) if n == 3 else (False, True)
        population = n * n
        for z in range(n):
            for reverse in orientations:
                family_instances += 1
                table = hidden_cycle_table(n, z, reverse)
                result = verify_hidden_cycle_family_by_cells(
                    lambda x, y, table=table: int(table[x, y]), n
                )
                runtime_acceptance_checks += 1
                if not (result.accepted and result.distinguished_row == z
                        and result.oracle_calls == population):
                    failures.append({"kind": "valid_runtime", "n": n, "z": z,
                                     "reverse": reverse, "reason": result.reason})

                active = tuple(int(x) for x in table[z])
                for row in range(n):
                    for column in range(n):
                        expected = int(table[row, column])
                        for replacement in range(n):
                            if replacement == expected:
                                continue
                            corruption_witnesses += 1
                            if row == z:
                                changed = list(active)
                                changed[column] = replacement
                                active_row_duplicate_checks += 1
                                if len(set(changed)) == n:
                                    failures.append({"kind": "active_corruption_still_permutation",
                                                     "n": n, "z": z, "column": column,
                                                     "replacement": replacement})
                            # If row != z, the corruption creates a second
                            # nonidentity row.  If row == z, the replacement
                            # duplicates an existing permutation image.  These
                            # two exhaustive cases prove every one-cell change
                            # leaves the witnessed family table.

                for numerator, denominator in ((0, 1), (1, 4), (1, 2), (3, 4), (1, 1)):
                    beta = Fraction(numerator, denominator)
                    expected_budget = math.ceil(population * beta)
                    checked = spot_check_hidden_cycle_witness(
                        lambda x, y, table=table: int(table[x, y]), n,
                        distinguished_row=z, active_translation=active,
                        allow_bounded_error=beta < 1,
                        minimum_rejection_numerator=numerator,
                        minimum_rejection_denominator=denominator,
                        rng_seed=10_000 * n + 100 * z + int(reverse),
                    )
                    spot_runtime_checks += 1
                    if not (checked.accepted
                            and checked.query_budget == expected_budget
                            and checked.oracle_calls == expected_budget
                            and Fraction(checked.guaranteed_rejection_numerator,
                                         checked.guaranteed_rejection_denominator)
                                == Fraction(expected_budget, population)):
                        failures.append({"kind": "spot_runtime", "n": n, "z": z,
                                         "reverse": reverse,
                                         "beta": [numerator, denominator]})

        for q in range(population + 1):
            frontier_checks += 1
            achieved = Fraction(q, population)
            if math.ceil(population * achieved) != q:
                failures.append({"kind": "frontier_inversion", "n": n, "q": q})
        distances = sorted({1, 2, n, population // 2, population})
        budgets = sorted({0, 1, population // 4, population // 2, population})
        for distance in distances:
            for q in budgets:
                hypergeometric_checks += 1
                miss = Fraction(math.comb(population - distance, q),
                                math.comb(population, q)) if q <= population - distance else Fraction(0, 1)
                detection = 1 - miss
                if distance == 1 and detection != Fraction(q, population):
                    failures.append({"kind": "single_corruption_frontier",
                                     "n": n, "q": q})
                if detection < Fraction(q, population):
                    failures.append({"kind": "multi_corruption_below_worst_case",
                                     "n": n, "q": q, "distance": distance})

    payload = {
        "status": "PASS" if not failures else "FAIL",
        "theorem": {
            "zero_error_queries": "n^2",
            "one_sided_rejection_frontier": "q/n^2",
            "confidence_inversion": "ceil(beta*n^2)",
            "distance_d_detection": "1-C(n^2-d,q)/C(n^2,q)",
        },
        "max_n": args.max_n,
        "family_instances": family_instances,
        "runtime_acceptance_checks": runtime_acceptance_checks,
        "single_cell_corruption_witnesses": corruption_witnesses,
        "active_row_duplicate_checks": active_row_duplicate_checks,
        "frontier_checks": frontier_checks,
        "hypergeometric_checks": hypergeometric_checks,
        "spot_runtime_checks": spot_runtime_checks,
        "failures": failures[:100],
    }
    payload["canonical_sha256"] = canonical_digest(payload)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items()
                      if key != "failures"}, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
