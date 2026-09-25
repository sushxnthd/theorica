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
        return z + float(
            self.rng.normal(
                0.0,
                self.noise_fraction * (self.domain[1] - self.domain[0]),
            )
        )


def make_world(seed):
    rng = np.random.default_rng(seed)
    domain = (-0.8, 0.8)
    grid = np.linspace(*domain, 5001)

    for _ in range(200):
        b = float(rng.uniform(-1.2, 1.2))
        c = float(rng.uniform(-0.7, 1.7))
        den = 1.0 + b * grid + c * grid**2
        if float(np.min(den)) > 0.20:
            break

    p0 = float(rng.uniform(0.65, 1.35))
    p1 = float(rng.uniform(-0.50, 0.50))
    p2 = float(rng.uniform(0.0, 1.3))
    num = p0 + p1 * grid + p2 * grid**2
    if float(np.min(num)) <= 0.18:
        num = p0 + p2 * grid**2

    derivative = num / den
    g = cumulative_trapezoid(derivative, grid, initial=0.0)
    g -= np.interp(0.0, grid, g)

    def additive(x, y):
        target = np.interp(x, grid, g) + np.interp(y, grid, g)
        if target < g[0] or target > g[-1]:
            return np.nan
        return float(np.interp(target, g, grid))

    def mean(x, y):
        target = 0.5 * (np.interp(x, grid, g) + np.interp(y, grid, g))
        return float(np.interp(target, g, grid))

    return {"domain": domain, "additive": additive, "mean": mean}


def _normalize_X(X, domain):
    lo, hi = domain
    return (np.asarray(X, dtype=float) - lo) / (hi - lo)


def _rbf(X, Y, lengthscale):
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    d2 = (
        np.sum(X**2, axis=1)[:, None]
        + np.sum(Y**2, axis=1)[None, :]
        - 2.0 * X @ Y.T
    )
    return np.exp(-0.5 * np.maximum(d2, 0.0) / (lengthscale**2))


def _gp_fit(samples, domain, noise_fraction):
    X = _normalize_X(samples[:, :2], domain)
    span = domain[1] - domain[0]
    y = samples[:, 2] / span
    mean = float(np.mean(y))
    yc = y - mean

    best = None
    for ell in (0.10, 0.18, 0.30, 0.50, 0.80, 1.20):
        K = _rbf(X, X, ell)
        noise = max(float(noise_fraction), 2e-4)
        K = K + (noise**2 + 1e-8) * np.eye(len(X))
        try:
            L = np.linalg.cholesky(K)
            alpha = np.linalg.solve(L.T, np.linalg.solve(L, yc))
            logdet = 2.0 * np.sum(np.log(np.diag(L)))
            nll = 0.5 * float(yc @ alpha) + 0.5 * logdet
        except np.linalg.LinAlgError:
            continue
        if best is None or nll < best[0]:
            best = (nll, ell, X, alpha, L, mean, span)

    if best is None:
        raise RuntimeError("GP fit failed")
    return best[1:]


def _gp_predict(model, Xnew, domain, return_variance=False):
    ell, Xtrain, alpha, L, mean, span = model
    Xn = _normalize_X(Xnew, domain)
    Ks = _rbf(Xn, Xtrain, ell)
    pred = (mean + Ks @ alpha) * span
    if not return_variance:
        return pred
    v = np.linalg.solve(L, Ks.T)
    var = np.maximum(1.0 - np.sum(v**2, axis=0), 1e-12)
    return pred, var


def active_gp_samples(
    oracle,
    domain,
    noise_fraction,
    *,
    budget,
    initial,
    seed,
    candidate_pool=300,
):
    rng = np.random.default_rng(seed)
    samples = random_operation_samples(
        oracle, domain, count=initial, seed=seed
    )
    lo, hi = domain

    while len(samples) < budget:
        model = _gp_fit(samples, domain, noise_fraction)
        candidates = rng.uniform(lo, hi, size=(candidate_pool, 2))
        _, variance = _gp_predict(
            model, candidates, domain, return_variance=True
        )

        chosen = None
        for index in np.argsort(variance)[::-1]:
            x, y = candidates[int(index)]
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


def route(clean, domain, noise, seed):
    miner = EquationalTheoryMiner(
        max_operations=2,
        p95_tolerance=0.02,
        min_common_fraction=0.20,
    )
    theory = miner.mine(
        NoisyOracle(clean, domain, seed + 1, noise),
        domain,
        assignments=20,
        seed=seed + 2,
    )
    evidence = verify_representation_hypotheses(
        NoisyOracle(clean, domain, seed + 3, noise),
        domain,
        theory,
        probes=60,
        seed=seed + 4,
    )
    return theory, evidence, verified_representation_coefficient(evidence)


def test_pairs(clean, domain, seed, count=600):
    rng = np.random.default_rng(seed)
    rows, truth = [], []
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


def run():
    budgets = [10, 20]
    noises = [0.001, 0.003]
    records = []
    routing_records = []
    route_success = 0
    route_total = 0

    for noise_index, noise in enumerate(noises):
        for family_index, family in enumerate(("additive", "mean")):
            for i in range(20):
                seed = 5000 + 100 * family_index + i
                world = make_world(seed)
                clean = world[family]
                domain = world["domain"]
                route_total += 1

                theory, evidence, coefficient = route(
                    clean,
                    domain,
                    noise,
                    seed + 100000 * (noise_index + 1),
                )
                routing_records.append(
                    {
                        "noise": noise,
                        "family": family,
                        "seed": seed,
                        "candidate_family": theory.family,
                        "verified_family": evidence.verified_family,
                        "monotonicity_rate": evidence.monotonicity_rate,
                        "bisymmetry_p95": evidence.bisymmetry_p95,
                        "routed": coefficient is not None,
                    }
                )
                if coefficient is None:
                    continue
                route_success += 1

                Xtest, ytest = test_pairs(
                    clean, domain, seed + 800000 + noise_index
                )

                for budget in budgets:
                    base = (
                        seed
                        + 1000000 * (noise_index + 1)
                        + 10000 * budget
                    )
                    initial = min(6, budget - 1)

                    structural_samples = active_coordinate_samples(
                        NoisyOracle(clean, domain, base + 10, noise),
                        domain,
                        coefficient,
                        budget=budget,
                        initial=initial,
                        seed=base + 11,
                        candidate_pool=180,
                    )
                    structural_model = fit_coordinate(
                        structural_samples, domain, coefficient
                    )

                    gp_samples = active_gp_samples(
                        NoisyOracle(clean, domain, base + 20, noise),
                        domain,
                        noise,
                        budget=budget,
                        initial=initial,
                        seed=base + 21,
                        candidate_pool=300,
                    )
                    gp_model = _gp_fit(gp_samples, domain, noise)

                    records.append(
                        {
                            "noise": noise,
                            "family": family,
                            "seed": seed,
                            "budget": budget,
                            "verified_family": evidence.verified_family,
                            "representation_nrmse": nrmse(
                                structural_model.predict(
                                    Xtest[:, 0], Xtest[:, 1]
                                ),
                                ytest,
                                domain,
                            ),
                            "active_gp_nrmse": nrmse(
                                _gp_predict(
                                    gp_model,
                                    Xtest,
                                    domain,
                                    return_variance=False,
                                ),
                                ytest,
                                domain,
                            ),
                        }
                    )

    summaries = []
    for noise in noises:
        for budget in budgets:
            rows = [
                r for r in records
                if r["noise"] == noise and r["budget"] == budget
            ]
            a = np.asarray([r["representation_nrmse"] for r in rows])
            g = np.asarray([r["active_gp_nrmse"] for r in rows])
            summaries.append(
                {
                    "noise": noise,
                    "budget": budget,
                    "n": len(rows),
                    "representation_median": float(np.median(a)),
                    "active_gp_median": float(np.median(g)),
                    "representation_wins": int(np.sum(a < g)),
                    "median_error_ratio": float(np.median(a / g)),
                    "wilcoxon_p": float(
                        wilcoxon(a, g, alternative="less").pvalue
                    ),
                }
            )

    payload = {
        "experiment": "THEORICA confirmatory representation-information vs active GP",
        "date": "2026-09-25",
        "untouched_seeds": {
            "additive": [5000, 5019],
            "mean": [5100, 5119],
        },
        "route_success": route_success,
        "route_total": route_total,
        "summaries": summaries,
        "routing_records": routing_records,
        "records": records,
    }
    Path("results/representation_vs_active_gp_confirmatory.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "route_success": route_success,
            "route_total": route_total,
            "summaries": summaries,
            "routing_failures": [
                r for r in routing_records if not r["routed"]
            ],
        },
        indent=2,
    ))

    # This 5000-series panel was fixed before execution after replacing the
    # brittle absolute bisymmetry cutoff with replicate-noise calibration.
    assert route_success == 80
    for noise in noises:
        s20 = next(
            s for s in summaries
            if s["noise"] == noise and s["budget"] == 20
        )
        assert s20["representation_wins"] >= 30
        assert s20["wilcoxon_p"] < 0.01


if __name__ == "__main__":
    run()
