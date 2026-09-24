from __future__ import annotations

import json
import math

import numpy as np
from scipy.special import dawsn, erf

from theorica.agents.anytime_falsification import AnytimeRepresentationFalsifier
from theorica.agents.representation_closure import normalized_rmse


def task(family, seed):
    rng = np.random.default_rng(seed)

    if family == "gaussian":
        x0 = np.linspace(-1.5, 1.5, 41)
        test = np.linspace(-3.0, 3.0, 401)
        probe = np.concatenate([
            np.linspace(-2.5, -1.6, 45),
            np.linspace(1.6, 2.5, 45),
        ])
        a = rng.uniform(0.45, 1.10)
        b = rng.uniform(-0.25, 0.25)
        A = rng.uniform(0.6, 1.4) * rng.choice([-1, 1])
        law = lambda z: A * np.exp(-a * (np.asarray(z) - b) ** 2)

    elif family == "erf":
        x0 = np.linspace(-1.5, 1.5, 41)
        test = np.linspace(-3.0, 3.0, 401)
        probe = np.concatenate([
            np.linspace(-2.5, -1.6, 45),
            np.linspace(1.6, 2.5, 45),
        ])
        k = rng.uniform(0.60, 1.30)
        s = rng.uniform(-0.30, 0.30)
        A = rng.uniform(0.6, 1.4) * rng.choice([-1, 1])
        law = lambda z: A * erf(k * np.asarray(z) + s)

    elif family == "dawson":
        x0 = np.linspace(-1.5, 1.5, 41)
        test = np.linspace(-3.0, 3.0, 401)
        probe = np.concatenate([
            np.linspace(-2.5, -1.6, 45),
            np.linspace(1.6, 2.5, 45),
        ])
        k = rng.uniform(0.60, 1.20)
        s = rng.uniform(-0.25, 0.25)
        A = rng.uniform(0.6, 1.4) * rng.choice([-1, 1])
        law = lambda z: A * dawsn(k * np.asarray(z) + s)

    elif family == "sinc":
        x0 = np.linspace(0.50, 3.00, 41)
        test = np.linspace(0.30, 6.00, 401)
        probe = np.linspace(3.1, 5.2, 90)
        k = rng.uniform(0.80, 1.40)
        A = rng.uniform(0.6, 1.4) * rng.choice([-1, 1])
        law = lambda z: A * np.sin(k * np.asarray(z)) / (k * np.asarray(z))

    elif family == "polynomial":
        x0 = np.linspace(-1.5, 1.5, 41)
        test = np.linspace(-3.0, 3.0, 401)
        probe = np.concatenate([
            np.linspace(-2.5, -1.6, 45),
            np.linspace(1.6, 2.5, 45),
        ])
        degree = int(rng.integers(2, 6))
        coeff = rng.uniform(-1.2, 1.2, degree + 1)
        coeff[-1] += np.sign(coeff[-1] or 1.0) * 0.6
        law = lambda z: sum(c * np.asarray(z) ** p for p, c in enumerate(coeff))

    elif family == "trig":
        x0 = np.linspace(-2.0, 2.0, 41)
        test = np.linspace(-4.0, 4.0, 401)
        probe = np.concatenate([
            np.linspace(-3.3, -2.1, 45),
            np.linspace(2.1, 3.3, 45),
        ])
        a, b = rng.uniform(0.5, 1.5, 2) * rng.choice([-1, 1], 2)
        slope = rng.uniform(-0.35, 0.35)
        offset = rng.uniform(-0.3, 0.3)
        law = lambda z: (
            a * np.sin(np.asarray(z))
            + b * np.cos(np.asarray(z))
            + slope * np.asarray(z)
            + offset
        )
    else:
        raise ValueError(family)

    clean0 = np.asarray(law(x0), dtype=float)
    sigma = 0.003 * max(float(np.std(clean0)), 1e-6)
    y0 = clean0 + rng.normal(0.0, sigma, len(x0))

    probe_clean = np.asarray(law(probe), dtype=float)
    probe_noise = rng.normal(0.0, sigma, len(probe))
    observations = {
        round(float(x), 12): float(y)
        for x, y in zip(probe, probe_clean + probe_noise)
    }

    def observe(x):
        return observations[round(float(x), 12)]

    return x0, y0, probe, test, np.asarray(law(test), dtype=float), sigma, observe


def run():
    rows = []
    policies = ("disagreement", "uniform", "random")
    for family_index, family in enumerate(
        ("gaussian", "erf", "dawson", "sinc", "polynomial", "trig")
    ):
        for offset in range(6):
            seed = 3000 + 100 * family_index + offset
            x0, y0, probe, xt, truth, sigma, observe = task(family, seed)
            for policy in policies:
                scientist = AnytimeRepresentationFalsifier(
                    alpha=0.01,
                    adequacy_tolerance_sigma=3.0,
                    adequacy_tolerance_fraction=0.003,
                )
                result = scientist.run(
                    x0,
                    y0,
                    bounds=(float(xt.min()), float(xt.max())),
                    probe_pool=probe,
                    observe=observe,
                    noise_sigma=sigma,
                    budget=8,
                    policy=policy,
                    random_seed=seed + 991,
                )
                rows.append({
                    "family": family,
                    "seed": seed,
                    "policy": policy,
                    "mode": result.mode,
                    "rejected_at": result.rejected_at,
                    "log_e_value": result.log_e_value,
                    "nrmse": normalized_rmse(result.predict(xt), truth),
                })

    summary = {}
    for family in sorted(set(r["family"] for r in rows)):
        summary[family] = {}
        for policy in policies:
            q = [r for r in rows if r["family"] == family and r["policy"] == policy]
            summary[family][policy] = {
                "switches": sum(r["mode"] == "operator" for r in q),
                "median_nrmse": float(np.median([r["nrmse"] for r in q])),
                "median_reject_step": (
                    None
                    if not [r["rejected_at"] for r in q if r["rejected_at"] is not None]
                    else float(np.median([
                        r["rejected_at"] for r in q if r["rejected_at"] is not None
                    ]))
                ),
            }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
