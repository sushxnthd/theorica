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
    representation_coefficient,
)


class NoisyOracle:
    def __init__(self, clean, domain, seed, noise_fraction=0.001):
        self.clean = clean
        self.domain = tuple(map(float, domain))
        self.rng = np.random.default_rng(seed)
        self.noise_fraction = float(noise_fraction)

    def __call__(self, x, y):
        value = float(self.clean(float(x), float(y)))
        if not np.isfinite(value):
            return value
        span = self.domain[1] - self.domain[0]
        return value + float(self.rng.normal(0.0, self.noise_fraction * span))


def make_coordinate_world(seed):
    rng = np.random.default_rng(seed)
    domain = (-0.8, 0.8)
    grid = np.linspace(domain[0], domain[1], 4001)

    for _ in range(100):
        b = float(rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0]))
        c = float(rng.choice([-0.5, 0.5, 1.0, 1.5]))
        denominator = 1.0 + b * grid + c * grid**2
        if float(np.min(denominator)) > 0.25:
            break

    kind = int(rng.integers(0, 3))
    if kind == 0:
        numerator = np.ones_like(grid)
    elif kind == 1:
        p = float(rng.choice([-0.5, 0.5]))
        numerator = 1.0 + p * grid
        if float(np.min(numerator)) <= 0.2:
            numerator = np.ones_like(grid)
    else:
        q = float(rng.choice([0.5, 1.0, 1.5]))
        numerator = 1.0 + q * grid**2

    derivative = numerator / denominator
    generator = cumulative_trapezoid(derivative, grid, initial=0.0)
    generator = generator - np.interp(0.0, grid, generator)

    def additive(x, y):
        target = np.interp(x, grid, generator) + np.interp(y, grid, generator)
        if target < generator[0] or target > generator[-1]:
            return np.nan
        return float(np.interp(target, generator, grid))

    def mean(x, y):
        target = 0.5 * np.interp(x, grid, generator) + 0.5 * np.interp(
            y, grid, generator
        )
        return float(np.interp(target, generator, grid))

    return {
        "domain": domain,
        "grid": grid,
        "derivative": derivative,
        "additive": additive,
        "mean": mean,
    }


def make_control(seed):
    domain = (-0.8, 0.8)
    mode = seed % 3
    if mode == 0:
        return lambda x, y: 0.35 * (x + y) + 0.15 * x * y, domain
    if mode == 1:
        return lambda x, y: 0.45 * x + 0.15 * y + 0.10 * x * y, domain
    return lambda x, y: 0.45 * np.sin(x + y), domain


def poly_features(X, degree):
    X = np.asarray(X, dtype=float)
    x = X[:, 0]
    y = X[:, 1]
    columns = []
    for total in range(degree + 1):
        for px in range(total + 1):
            py = total - px
            columns.append((x**px) * (y**py))
    return np.column_stack(columns)


def fit_polynomial(samples, degree=6, ridge=1e-8):
    D = poly_features(samples[:, :2], degree)
    lhs = D.T @ D + ridge * np.eye(D.shape[1])
    return np.linalg.solve(lhs, D.T @ samples[:, 2])


def predict_polynomial(beta, X, degree=6):
    return poly_features(np.asarray(X, dtype=float), degree) @ beta


def active_polynomial_samples(
    oracle,
    domain,
    *,
    budget=20,
    initial=8,
    seed=0,
    candidate_pool=180,
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
                committee.append((degree, fit_polynomial(samples, degree)))
            except np.linalg.LinAlgError:
                continue

        candidates = rng.uniform(lo, hi, size=(candidate_pool, 2))
        predictions = np.column_stack(
            [
                predict_polynomial(beta, candidates, degree)
                for degree, beta in committee
            ]
        )
        scores = np.var(predictions, axis=1)
        observation = None

        for index in np.argsort(scores)[::-1]:
            x, y = candidates[int(index)]
            try:
                z = float(oracle(float(x), float(y)))
            except Exception:
                continue
            if np.isfinite(z) and lo <= z <= hi:
                observation = (float(x), float(y), float(z))
                break

        if observation is None:
            observation = tuple(
                random_operation_samples(
                    oracle,
                    domain,
                    count=1,
                    seed=int(rng.integers(0, 2**31 - 1)),
                )[0]
            )

        samples = np.vstack([samples, np.asarray(observation, dtype=float)])
    return samples


def evaluation_pairs(clean, domain, *, seed, count=400):
    rng = np.random.default_rng(seed)
    lo, hi = domain
    X = []
    y = []
    while len(y) < count:
        x1, x2 = rng.uniform(lo, hi, size=2)
        value = float(clean(float(x1), float(x2)))
        if np.isfinite(value) and lo <= value <= hi:
            X.append((float(x1), float(x2)))
            y.append(value)
    return np.asarray(X), np.asarray(y)


def normalized_rmse(pred, truth, domain):
    pred = np.asarray(pred, dtype=float)
    truth = np.asarray(truth, dtype=float)
    return float(
        np.sqrt(np.mean((pred - truth) ** 2))
        / max(domain[1] - domain[0], 1e-12)
    )


def derivative_shape_error(model, grid, true_derivative):
    target = np.interp(model.knots, grid, true_derivative)
    estimated = np.gradient(model.generator, model.knots)
    scale = float(np.dot(estimated, target) / max(np.dot(estimated, estimated), 1e-20))
    residual = scale * estimated - target
    return float(
        np.sqrt(np.mean(residual**2))
        / max(np.mean(np.abs(target)), 1e-12)
    )


def bootstrap_ci(values, *, seed=20260925, draws=10000):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.asarray(
        [
            np.mean(rng.choice(values, size=len(values), replace=True))
            for _ in range(draws)
        ]
    )
    return [float(v) for v in np.quantile(means, [0.025, 0.975])]


def structural_panel():
    miner = EquationalTheoryMiner(
        max_operations=2,
        p95_tolerance=0.02,
        min_common_fraction=0.20,
    )
    records = []

    for i in range(25):
        world = make_coordinate_world(1000 + i)
        cases = [
            (
                "additive_generator_candidate",
                world["additive"],
                world["domain"],
                11000 + i,
            ),
            (
                "quasi_arithmetic_mean_candidate",
                make_coordinate_world(1100 + i)["mean"],
                world["domain"],
                12000 + i,
            ),
            (
                "commutative_semilattice",
                max if i % 2 == 0 else min,
                world["domain"],
                13000 + i,
            ),
        ]
        control, domain = make_control(1200 + i)
        cases.append(("unresolved", control, domain, 14000 + i))

        for expected, clean, domain, noise_seed in cases:
            theory = miner.mine(
                NoisyOracle(clean, domain, noise_seed, noise_fraction=0.001),
                domain,
                assignments=20,
                seed=noise_seed + 1000,
            )
            records.append(
                {
                    "expected": expected,
                    "predicted": theory.family,
                    "commutative": theory.commutative,
                    "associative": theory.associative,
                    "idempotent": theory.idempotent,
                    "identity_count": len(theory.identities),
                }
            )
    return records


def active_representation_panel():
    miner = EquationalTheoryMiner(
        max_operations=2,
        p95_tolerance=0.02,
        min_common_fraction=0.20,
    )

    records = []
    for family_index, family in enumerate(("additive", "mean")):
        for i in range(25):
            seed = 2000 + 100 * family_index + i
            world = make_coordinate_world(seed)
            clean = world[family]
            domain = world["domain"]

            theory = miner.mine(
                NoisyOracle(clean, domain, seed + 10000, 0.001),
                domain,
                assignments=20,
                seed=seed + 11000,
            )
            coefficient = representation_coefficient(theory)
            if coefficient is None:
                raise AssertionError(
                    f"structure routing failed for seed {seed}: {theory.family}"
                )

            active_obs = NoisyOracle(clean, domain, seed + 12000, 0.001)
            random_obs = NoisyOracle(clean, domain, seed + 13000, 0.001)
            polynomial_obs = NoisyOracle(clean, domain, seed + 14000, 0.001)

            active_samples = active_coordinate_samples(
                active_obs,
                domain,
                coefficient,
                budget=20,
                initial=8,
                seed=seed + 15000,
                candidate_pool=180,
            )
            random_samples = random_operation_samples(
                random_obs,
                domain,
                count=20,
                seed=seed + 16000,
            )
            polynomial_samples = active_polynomial_samples(
                polynomial_obs,
                domain,
                budget=20,
                initial=8,
                seed=seed + 17000,
                candidate_pool=180,
            )

            active_model = fit_coordinate(active_samples, domain, coefficient)
            random_model = fit_coordinate(random_samples, domain, coefficient)
            poly_beta = fit_polynomial(polynomial_samples, degree=6)

            Xtest, ytest = evaluation_pairs(
                clean,
                domain,
                seed=seed + 18000,
                count=400,
            )
            active_error = normalized_rmse(
                active_model.predict(Xtest[:, 0], Xtest[:, 1]),
                ytest,
                domain,
            )
            random_error = normalized_rmse(
                random_model.predict(Xtest[:, 0], Xtest[:, 1]),
                ytest,
                domain,
            )
            polynomial_error = normalized_rmse(
                predict_polynomial(poly_beta, Xtest, degree=6),
                ytest,
                domain,
            )

            records.append(
                {
                    "family": family,
                    "seed": seed,
                    "mined_family": theory.family,
                    "coefficient": coefficient,
                    "active_coordinate_error": active_error,
                    "random_coordinate_error": random_error,
                    "active_polynomial_error": polynomial_error,
                    "active_derivative_shape_error": derivative_shape_error(
                        active_model,
                        world["grid"],
                        world["derivative"],
                    ),
                }
            )
    return records


def run():
    structure = structural_panel()
    active = active_representation_panel()

    structural_correct = sum(
        row["expected"] == row["predicted"] for row in structure
    )

    ae = np.asarray([r["active_coordinate_error"] for r in active])
    re = np.asarray([r["random_coordinate_error"] for r in active])
    pe = np.asarray([r["active_polynomial_error"] for r in active])
    de = np.asarray([r["active_derivative_shape_error"] for r in active])

    paired_random = re - ae
    paired_poly = pe - ae

    summary = {
        "structural_worlds": len(structure),
        "structural_classification_correct": int(structural_correct),
        "coordinate_worlds": len(active),
        "active_coordinate_median_nrmse": float(np.median(ae)),
        "random_coordinate_median_nrmse": float(np.median(re)),
        "active_polynomial_median_nrmse": float(np.median(pe)),
        "active_coordinate_p90_nrmse": float(np.quantile(ae, 0.90)),
        "active_derivative_shape_median_error": float(np.median(de)),
        "active_wins_vs_random_coordinate": int(np.sum(ae < re)),
        "active_wins_vs_active_polynomial": int(np.sum(ae < pe)),
        "median_active_to_random_error_ratio": float(np.median(ae / re)),
        "median_active_to_active_polynomial_error_ratio": float(np.median(ae / pe)),
        "mean_gain_vs_random": float(np.mean(paired_random)),
        "mean_gain_vs_random_bootstrap_95ci": bootstrap_ci(paired_random),
        "wilcoxon_p_vs_random": float(
            wilcoxon(ae, re, alternative="less").pvalue
        ),
        "wilcoxon_p_vs_active_polynomial": float(
            wilcoxon(ae, pe, alternative="less").pvalue
        ),
    }

    payload = {
        "experiment": "THEORICA empirical equational theory + representation-information design",
        "date": "2026-09-25",
        "structural_design": {
            "term_language_operation_depth": 2,
            "enumerated_terms": 66,
            "assignments_per_world": 20,
            "measurement_noise_fraction_of_domain": 0.001,
            "families": [
                "additive-generator",
                "quasi-arithmetic mean",
                "commutative semilattice",
                "unresolved controls",
            ],
        },
        "active_design": {
            "worlds": 50,
            "measurements_per_world": 20,
            "initial_random_measurements": 8,
            "measurement_noise_fraction_of_domain": 0.001,
            "structural_acquisition": "maximize a^T C a for latent-coordinate constraints",
            "active_baseline": "degree-2..6 polynomial query-by-committee; final degree-6 fit",
        },
        "summary": summary,
        "structural_records": structure,
        "active_records": active,
    }

    Path("results/equational_discovery_holdout.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    # Frozen gates are deliberately weaker than the development observations.
    assert summary["structural_classification_correct"] >= 96
    assert summary["active_coordinate_median_nrmse"] < 0.0015
    assert summary["active_wins_vs_random_coordinate"] >= 42
    assert summary["active_wins_vs_active_polynomial"] >= 48
    assert summary["wilcoxon_p_vs_random"] < 0.001
    assert summary["wilcoxon_p_vs_active_polynomial"] < 0.001


if __name__ == "__main__":
    run()
