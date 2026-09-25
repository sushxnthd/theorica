from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.stats import wilcoxon

from theorica.agents.equational_discovery import (
    EquationalTheoryMiner,
    active_coordinate_samples,
    fit_coordinate,
    random_operation_samples,
    verify_representation_hypotheses,
    verified_representation_coefficient,
)


class NoisyOracle:
    def __init__(self, clean, domain, seed, noise_fraction):
        self.clean = clean
        self.domain = tuple(map(float, domain))
        self.rng = np.random.default_rng(seed)
        self.noise_fraction = float(noise_fraction)

    def __call__(self, x, y):
        z = float(self.clean(float(x), float(y)))
        if not np.isfinite(z):
            return z
        span = self.domain[1] - self.domain[0]
        return z + float(self.rng.normal(0.0, self.noise_fraction * span))


def make_world(seed):
    rng = np.random.default_rng(seed)
    domain = (-0.8, 0.8)
    grid = np.linspace(domain[0], domain[1], 4001)

    for _ in range(200):
        b = float(rng.uniform(-1.1, 1.1))
        c = float(rng.uniform(-0.6, 1.6))
        den = 1.0 + b * grid + c * grid**2
        if float(np.min(den)) > 0.22:
            break

    p0 = float(rng.uniform(0.7, 1.3))
    p1 = float(rng.uniform(-0.45, 0.45))
    p2 = float(rng.uniform(0.0, 1.2))
    num = p0 + p1 * grid + p2 * grid**2
    if float(np.min(num)) <= 0.2:
        num = p0 + p2 * grid**2

    derivative = num / den
    generator = cumulative_trapezoid(derivative, grid, initial=0.0)
    generator = generator - np.interp(0.0, grid, generator)

    def add(x, y):
        gx = np.interp(x, grid, generator)
        gy = np.interp(y, grid, generator)
        target = gx + gy
        if target < generator[0] or target > generator[-1]:
            return np.nan
        return float(np.interp(target, generator, grid))

    def mean(x, y):
        target = 0.5 * (
            np.interp(x, grid, generator) + np.interp(y, grid, generator)
        )
        return float(np.interp(target, generator, grid))

    return {
        "domain": domain,
        "additive": add,
        "mean": mean,
    }


def poly_features(X, degree):
    X = np.asarray(X, dtype=float)
    x, y = X[:, 0], X[:, 1]
    cols = []
    for total in range(degree + 1):
        for px in range(total + 1):
            py = total - px
            cols.append((x**px) * (y**py))
    return np.column_stack(cols)


def fit_poly(samples, degree=6, ridge=1e-8):
    D = poly_features(samples[:, :2], degree)
    return np.linalg.solve(
        D.T @ D + ridge * np.eye(D.shape[1]),
        D.T @ samples[:, 2],
    )


def predict_poly(beta, X, degree=6):
    return poly_features(X, degree) @ beta


def active_poly_samples(
    oracle,
    domain,
    *,
    budget,
    initial,
    seed,
    candidate_pool=120,
):
    rng = np.random.default_rng(seed)
    samples = random_operation_samples(
        oracle, domain, count=initial, seed=seed
    )
    lo, hi = domain

    while len(samples) < budget:
        committee = []
        for degree in range(2, 7):
            try:
                committee.append((degree, fit_poly(samples, degree)))
            except np.linalg.LinAlgError:
                pass

        candidates = rng.uniform(lo, hi, size=(candidate_pool, 2))
        predictions = np.column_stack(
            [predict_poly(beta, candidates, d) for d, beta in committee]
        )
        order = np.argsort(np.var(predictions, axis=1))[::-1]

        chosen = None
        for idx in order:
            x, y = candidates[int(idx)]
            try:
                z = float(oracle(float(x), float(y)))
            except Exception:
                continue
            if np.isfinite(z) and lo <= z <= hi:
                chosen = (float(x), float(y), z)
                break

        if chosen is None:
            chosen = tuple(
                random_operation_samples(
                    oracle,
                    domain,
                    count=1,
                    seed=int(rng.integers(0, 2**31 - 1)),
                )[0]
            )
        samples = np.vstack([samples, np.asarray(chosen, dtype=float)])
    return samples


def test_pairs(clean, domain, seed, count=500):
    rng = np.random.default_rng(seed)
    rows = []
    truth = []
    lo, hi = domain
    while len(truth) < count:
        x, y = rng.uniform(lo, hi, size=2)
        z = float(clean(float(x), float(y)))
        if np.isfinite(z) and lo <= z <= hi:
            rows.append((x, y))
            truth.append(z)
    return np.asarray(rows), np.asarray(truth)


def nrmse(pred, truth, domain):
    return float(
        np.sqrt(np.mean((np.asarray(pred) - np.asarray(truth)) ** 2))
        / (domain[1] - domain[0])
    )


def route(clean, domain, noise_fraction, seed):
    miner = EquationalTheoryMiner(
        max_operations=2,
        p95_tolerance=0.02,
        min_common_fraction=0.20,
    )
    theory = miner.mine(
        NoisyOracle(clean, domain, seed + 1, noise_fraction),
        domain,
        assignments=20,
        seed=seed + 2,
    )
    evidence = verify_representation_hypotheses(
        NoisyOracle(clean, domain, seed + 3, noise_fraction),
        domain,
        theory,
        probes=60,
        seed=seed + 4,
    )
    return theory, evidence, verified_representation_coefficient(evidence)


def run():
    budgets = [10, 12, 16, 20]
    noise_levels = [0.001, 0.003]
    initial = 6
    records = []
    routing_records = []

    worlds = []
    for family_index, family in enumerate(("additive", "mean")):
        for i in range(20):
            seed = 3000 + 100 * family_index + i
            world = make_world(seed)
            worlds.append((family, seed, world))

    for noise_index, noise in enumerate(noise_levels):
        for family, seed, world in worlds:
            clean = world[family]
            domain = world["domain"]
            theory, evidence, coefficient = route(
                clean, domain, noise, seed + 10000 * (noise_index + 1)
            )
            routing_records.append(
                {
                    "noise": noise,
                    "family": family,
                    "seed": seed,
                    "candidate": theory.family,
                    "verified": evidence.verified_family,
                    "coefficient": coefficient,
                }
            )
            if coefficient is None:
                continue

            Xtest, ytest = test_pairs(
                clean, domain, seed + 90000 + noise_index, count=500
            )

            for budget in budgets:
                base = seed + 1000000 * (noise_index + 1) + 1000 * budget

                active_samples = active_coordinate_samples(
                    NoisyOracle(clean, domain, base + 10, noise),
                    domain,
                    coefficient,
                    budget=budget,
                    initial=min(initial, budget - 1),
                    seed=base + 11,
                    candidate_pool=120,
                )
                random_samples = random_operation_samples(
                    NoisyOracle(clean, domain, base + 20, noise),
                    domain,
                    count=budget,
                    seed=base + 21,
                )
                poly_samples = active_poly_samples(
                    NoisyOracle(clean, domain, base + 30, noise),
                    domain,
                    budget=budget,
                    initial=min(initial, budget - 1),
                    seed=base + 31,
                    candidate_pool=120,
                )

                active_model = fit_coordinate(
                    active_samples, domain, coefficient
                )
                random_model = fit_coordinate(
                    random_samples, domain, coefficient
                )
                beta = fit_poly(poly_samples, degree=6)

                records.append(
                    {
                        "noise": noise,
                        "family": family,
                        "seed": seed,
                        "budget": budget,
                        "active_coordinate_nrmse": nrmse(
                            active_model.predict(Xtest[:, 0], Xtest[:, 1]),
                            ytest,
                            domain,
                        ),
                        "random_coordinate_nrmse": nrmse(
                            random_model.predict(Xtest[:, 0], Xtest[:, 1]),
                            ytest,
                            domain,
                        ),
                        "active_polynomial_nrmse": nrmse(
                            predict_poly(beta, Xtest, degree=6),
                            ytest,
                            domain,
                        ),
                    }
                )

    summaries = []
    for noise in noise_levels:
        for budget in budgets:
            rows = [
                r for r in records
                if r["noise"] == noise and r["budget"] == budget
            ]
            ae = np.asarray([r["active_coordinate_nrmse"] for r in rows])
            re = np.asarray([r["random_coordinate_nrmse"] for r in rows])
            pe = np.asarray([r["active_polynomial_nrmse"] for r in rows])
            summaries.append(
                {
                    "noise": noise,
                    "budget": budget,
                    "n": len(rows),
                    "active_median": float(np.median(ae)),
                    "random_coordinate_median": float(np.median(re)),
                    "active_polynomial_median": float(np.median(pe)),
                    "active_wins_vs_random": int(np.sum(ae < re)),
                    "active_wins_vs_polynomial": int(np.sum(ae < pe)),
                    "median_active_random_ratio": float(np.median(ae / re)),
                    "median_active_polynomial_ratio": float(np.median(ae / pe)),
                    "wilcoxon_p_vs_random": float(
                        wilcoxon(ae, re, alternative="less").pvalue
                    ),
                    "wilcoxon_p_vs_polynomial": float(
                        wilcoxon(ae, pe, alternative="less").pvalue
                    ),
                }
            )

    routing_success = sum(r["coefficient"] is not None for r in routing_records)

    def lookup(noise, budget):
        return next(
            s for s in summaries
            if s["noise"] == noise and s["budget"] == budget
        )

    sample_efficiency = []
    for noise in noise_levels:
        random20 = lookup(noise, 20)["random_coordinate_median"]
        smallest = None
        for budget in budgets:
            if lookup(noise, budget)["active_median"] <= random20:
                smallest = budget
                break
        sample_efficiency.append(
            {
                "noise": noise,
                "random_20_median": random20,
                "smallest_tested_active_budget_matching_random_20": smallest,
            }
        )

    payload = {
        "experiment": "THEORICA untouched confirmatory representation-information budget curve",
        "date": "2026-09-25",
        "world_seeds": {
            "additive": [3000, 3019],
            "quasi_arithmetic_mean": [3100, 3119],
        },
        "budgets": budgets,
        "noise_levels": noise_levels,
        "routing_successes": routing_success,
        "routing_total": len(routing_records),
        "summaries": summaries,
        "sample_efficiency": sample_efficiency,
        "routing_records": routing_records,
        "records": records,
    }
    Path("results/representation_information_curve.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "routing_successes": routing_success,
            "routing_total": len(routing_records),
            "summaries": summaries,
            "sample_efficiency": sample_efficiency,
        },
        indent=2,
    ))

    assert routing_success >= 78
    for noise in noise_levels:
        s20 = lookup(noise, 20)
        assert s20["active_median"] < s20["random_coordinate_median"]
        assert s20["active_wins_vs_polynomial"] >= 35
        assert s20["wilcoxon_p_vs_random"] < 0.01
        assert s20["wilcoxon_p_vs_polynomial"] < 0.01


if __name__ == "__main__":
    run()
