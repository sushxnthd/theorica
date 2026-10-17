#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.robust_provenance import (
    deterministic_tv_frontier,
    randomized_tv_frontier_lp,
    sample_robust_randomized_plan,
    synthesize_robust_randomized_plan,
)


def patterns(n: int) -> tuple[tuple[int, ...], ...]:
    candidates = (
        (1,) * n,
        (3,) + (1,) * (n - 1),
        tuple(range(n, 0, -1)),
        tuple(1 + ((7 * index + 3 * n) % 5) for index in range(n)),
    )
    return tuple(dict.fromkeys(candidates))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    radii = (Fraction(0), Fraction(1, 20), Fraction(1, 10), Fraction(1, 4))
    counts = {
        "cases": 0, "mixture_components": 0, "seed_checks": 0,
        "strict_randomization_gains": 0, "full_coverage_corrections": 0,
    }
    failures: list[dict] = []
    certificates: list[dict] = []
    max_residual = 0.0
    for n in range(3, 9):
        for prior_index, weights in enumerate(patterns(n)):
            for q in range(n):
                for delta in radii:
                    plan = synthesize_robust_randomized_plan(weights, q, delta)
                    frontier = randomized_tv_frontier_lp(weights, q, delta)
                    deterministic = deterministic_tv_frontier(weights, q, delta)
                    counts["cases"] += 1
                    counts["mixture_components"] += len(plan.mixture)
                    max_residual = max(max_residual, plan.certificate_residual)
                    if not plan.certificate_valid or abs(plan.frontier_value - frontier) > 1e-8:
                        failures.append({"n": n, "weights": weights, "q": q, "delta": str(delta), "kind": "certificate"})
                    if q == n - 1:
                        if deterministic != 1 or abs(frontier - 1.0) > 1e-8:
                            failures.append({"n": n, "weights": weights, "q": q, "delta": str(delta), "kind": "full_coverage"})
                        if delta > 0:
                            counts["full_coverage_corrections"] += 1
                    elif frontier > float(deterministic) + 1e-8:
                        counts["strict_randomization_gains"] += 1
                    for seed in (0, "receipt-17"):
                        first = sample_robust_randomized_plan(plan, seed)
                        second = sample_robust_randomized_plan(plan, seed)
                        counts["seed_checks"] += 1
                        if first != second or first.covered_labels not in {c.covered_labels for c in plan.mixture} or len(first.query_order) != q or first.terminal_guess in first.query_order:
                            failures.append({"n": n, "weights": weights, "q": q, "delta": str(delta), "kind": "execution"})
                    if prior_index < 2 and q in {0, n // 2, n - 1} and delta in {Fraction(1, 10), Fraction(1, 4)}:
                        certificates.append({
                            "n": n, "weights": list(weights), "q": q, "delta": str(delta),
                            "frontier": round(plan.frontier_value, 12),
                            "certified_payoff": round(plan.certified_worst_case_payoff, 12),
                            "residual": round(plan.certificate_residual, 15),
                            "inclusion": [round(value, 12) for value in plan.inclusion_probabilities],
                            "mixture": [
                                {"labels": list(component.covered_labels), "probability": round(component.probability, 12)}
                                for component in plan.mixture
                            ],
                        })
    payload = {
        "schema": "theorica.robust-randomized-plan-synthesis.v1",
        "parent_commit": "6c0fc90b22af5ead1247ce92382c881b5f3120e6",
        "corrected_deterministic_law": "D*=1 for q=n-1; otherwise max(0,sum_top_(q+1)(p)-delta)",
        "constructive_law": "negative dual multipliers of subset epigraph constraints form an optimal mixture over covered-label sets",
        "counts": counts,
        "max_certificate_residual": max_residual,
        "certificates": certificates,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["canonical_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("status", "counts", "max_certificate_residual", "canonical_sha256")}, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
