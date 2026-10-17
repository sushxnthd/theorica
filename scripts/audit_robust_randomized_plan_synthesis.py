#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


def independent_tv_payoff(weights: list[int], delta: float, inclusion: list[float]) -> float:
    n = len(weights)
    p = np.asarray(weights, dtype=float) / sum(weights)
    objective = np.zeros(2 * n); objective[:n] = inclusion
    aub, bub = [], []
    for index in range(n):
        row = np.zeros(2 * n); row[index] = 1; row[n + index] = -1
        aub.append(row); bub.append(p[index])
        row = np.zeros(2 * n); row[index] = -1; row[n + index] = -1
        aub.append(row); bub.append(-p[index])
    row = np.zeros(2 * n); row[n:] = 1
    aub.append(row); bub.append(2 * delta)
    equality = np.zeros((1, 2 * n)); equality[0, :n] = 1
    solved = linprog(objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub), A_eq=equality, b_eq=[1.0], bounds=[(0, None)] * (2 * n), method="highs")
    if not solved.success:
        raise RuntimeError(solved.message)
    return float(solved.fun)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("primary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    primary = json.loads(args.primary.read_text())
    failures = []
    checks = 0
    max_residual = 0.0
    for case in primary["certificates"]:
        reconstructed = [0.0] * case["n"]
        total_probability = 0.0
        for component in case["mixture"]:
            total_probability += component["probability"]
            if len(component["labels"]) != case["q"] + 1 or len(set(component["labels"])) != len(component["labels"]):
                failures.append({"case": case, "kind": "support"})
            for label in component["labels"]:
                reconstructed[label] += component["probability"]
        checks += 1
        inclusion_error = max(abs(a - b) for a, b in zip(reconstructed, case["inclusion"], strict=True))
        payoff = independent_tv_payoff(case["weights"], float(eval_fraction(case["delta"])), reconstructed)
        residual = abs(payoff - case["frontier"])
        max_residual = max(max_residual, residual, inclusion_error, abs(total_probability - 1.0))
        if max(inclusion_error, residual, abs(total_probability - 1.0)) > 2e-8:
            failures.append({"n": case["n"], "q": case["q"], "delta": case["delta"], "kind": "payoff", "residual": residual})
    result = {"schema": "theorica.robust-randomized-plan-synthesis-audit.v1", "certificate_checks": checks, "max_independent_residual": max_residual, "failures": failures, "status": "PASS" if not failures else "FAIL"}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


def eval_fraction(value: str) -> float:
    numerator, separator, denominator = value.partition("/")
    return int(numerator) / int(denominator) if separator else float(numerator)


if __name__ == "__main__":
    main()
