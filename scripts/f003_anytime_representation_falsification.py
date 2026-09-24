from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial
from scipy.stats import wilcoxon

from theorica.agents.anytime_falsification import AnytimeRepresentationFalsifier
from theorica.agents.representation_closure import normalized_rmse
from theorica.agents.symbolic_synthesis import CompositionalTheorySynthesizer


def _sample_noninteger_power(rng):
    while True:
        p = float(rng.uniform(0.7, 3.4))
        if abs(p - round(p)) >= 0.18 and abs(p - 0.5) >= 0.18:
            return p


def make_task(family, seed):
    rng = np.random.default_rng(seed)

    if family == "arctan":
        x0 = np.linspace(-1.2, 1.2, 41)
        probe = np.concatenate([
            np.linspace(-2.5, -1.3, 55),
            np.linspace(1.3, 2.5, 55),
        ])
        xt = np.linspace(-4.0, 4.0, 401)
        k = float(rng.uniform(0.7, 1.4))
        A = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))
        law = lambda z: A * np.arctan(k * np.asarray(z, dtype=float))
        params = {"k": k, "A": A}

    elif family == "asinh":
        x0 = np.linspace(-1.2, 1.2, 41)
        probe = np.concatenate([
            np.linspace(-2.5, -1.3, 55),
            np.linspace(1.3, 2.5, 55),
        ])
        xt = np.linspace(-4.0, 4.0, 401)
        k = float(rng.uniform(0.7, 1.4))
        A = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))
        law = lambda z: A * np.arcsinh(k * np.asarray(z, dtype=float))
        params = {"k": k, "A": A}

    elif family == "power":
        x0 = np.linspace(0.7, 2.0, 41)
        probe = np.linspace(2.1, 3.3, 110)
        xt = np.linspace(0.55, 4.5, 401)
        p = _sample_noninteger_power(rng)
        A = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))
        law = lambda z: A * np.asarray(z, dtype=float) ** p
        params = {"p": p, "A": A}

    elif family == "lorentzian":
        x0 = np.linspace(-1.2, 1.2, 41)
        probe = np.concatenate([
            np.linspace(-2.5, -1.3, 55),
            np.linspace(1.3, 2.5, 55),
        ])
        xt = np.linspace(-4.0, 4.0, 401)
        k = float(rng.uniform(0.7, 1.4))
        A = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))
        law = lambda z: A / (1.0 + (k * np.asarray(z, dtype=float)) ** 2)
        params = {"k": k, "A": A}

    elif family == "polynomial":
        x0 = np.linspace(-1.2, 1.2, 41)
        probe = np.concatenate([
            np.linspace(-2.5, -1.3, 55),
            np.linspace(1.3, 2.5, 55),
        ])
        xt = np.linspace(-4.0, 4.0, 401)
        degree = int(rng.integers(2, 5))
        coeff = rng.uniform(-1.2, 1.2, degree + 1)
        coeff[-1] += np.sign(coeff[-1] or 1.0) * 0.7
        law = lambda z: sum(
            c * np.asarray(z, dtype=float) ** q
            for q, c in enumerate(coeff)
        )
        params = {"degree": degree}

    elif family == "trig":
        x0 = np.linspace(-2.0, 2.0, 41)
        probe = np.concatenate([
            np.linspace(-3.4, -2.1, 55),
            np.linspace(2.1, 3.4, 55),
        ])
        xt = np.linspace(-5.0, 5.0, 401)
        a, b = rng.uniform(0.6, 1.4, 2) * rng.choice([-1, 1], 2)
        law = lambda z: (
            a * np.sin(np.asarray(z, dtype=float))
            + b * np.cos(np.asarray(z, dtype=float))
        )
        params = {"a": float(a), "b": float(b)}

    else:
        raise ValueError(family)

    clean0 = np.asarray(law(x0), dtype=float)
    sigma = 0.003 * max(float(np.std(clean0)), 1e-6)
    y0 = clean0 + rng.normal(0.0, sigma, size=len(x0))

    clean_probe = np.asarray(law(probe), dtype=float)
    y_probe = clean_probe + rng.normal(0.0, sigma, size=len(probe))
    obs = {
        round(float(x), 12): float(y)
        for x, y in zip(probe, y_probe)
    }

    def observe(x):
        return obs[round(float(x), 12)]

    truth = np.asarray(law(xt), dtype=float)
    return x0, y0, probe, xt, truth, sigma, observe, params


def polynomial_baseline(x, y, xt):
    qlo, qhi = np.quantile(x, [0.18, 0.82])
    inner = (x >= qlo) & (x <= qhi)
    best = None
    for degree in range(1, 13):
        model = Polynomial.fit(x[inner], y[inner], degree)
        err = normalized_rmse(model(x[~inner]), y[~inner])
        if best is None or err < best[0]:
            best = (err, degree)
    model = Polynomial.fit(x, y, best[1])
    return np.asarray(model(xt), dtype=float), int(best[1])


def evaluate_one(family, seed):
    x0, y0, probe, xt, truth, sigma, observe, params = make_task(family, seed)

    explicit, _ = CompositionalTheorySynthesizer(trial_width=200).fit(x0, y0)
    explicit_nrmse = normalized_rmse(explicit.predict(xt), truth)

    poly_pred, poly_degree = polynomial_baseline(x0, y0, xt)
    poly_nrmse = normalized_rmse(poly_pred, truth)

    scientist = AnytimeRepresentationFalsifier(
        alpha=0.01,
        adequacy_tolerance_sigma=3.0,
        adequacy_tolerance_fraction=0.003,
        symbolic_trial_width=200,
        operator_top_k=40,
    )
    result = scientist.run(
        x0,
        y0,
        bounds=(float(xt.min()), float(xt.max())),
        probe_pool=probe,
        observe=observe,
        noise_sigma=sigma,
        budget=6,
        policy="disagreement",
        random_seed=seed + 777,
    )
    closure_nrmse = normalized_rmse(result.predict(xt), truth)

    return {
        "family": family,
        "seed": seed,
        "params": params,
        "noise_sigma": sigma,
        "explicit_nrmse": explicit_nrmse,
        "poly12_nrmse": poly_nrmse,
        "poly12_degree": poly_degree,
        "f003_nrmse": closure_nrmse,
        "mode": result.mode,
        "rejected_at": result.rejected_at,
        "final_log_e": result.log_e_value,
        "adequacy_tolerance": result.adequacy_tolerance,
        "n_probes": len(result.probes),
        "theory_expression": result.theory.expression,
    }


def summarize(records):
    ood_names = {"arctan", "asinh", "power", "lorentzian"}
    ood = [r for r in records if r["family"] in ood_names]
    controls = [r for r in records if r["family"] not in ood_names]

    explicit = np.array([r["explicit_nrmse"] for r in ood], dtype=float)
    f003 = np.array([r["f003_nrmse"] for r in ood], dtype=float)
    poly = np.array([r["poly12_nrmse"] for r in ood], dtype=float)
    paired = explicit - f003

    rng = np.random.default_rng(20260924)
    boots = np.array([
        np.mean(rng.choice(paired, size=len(paired), replace=True))
        for _ in range(10000)
    ])
    ci = np.quantile(boots, [0.025, 0.975])

    family_summary = {}
    for family in sorted(set(r["family"] for r in records)):
        rows = [r for r in records if r["family"] == family]
        reject_steps = [
            r["rejected_at"] for r in rows if r["rejected_at"] is not None
        ]
        family_summary[family] = {
            "n": len(rows),
            "explicit_median_nrmse": float(
                np.median([r["explicit_nrmse"] for r in rows])
            ),
            "f003_median_nrmse": float(
                np.median([r["f003_nrmse"] for r in rows])
            ),
            "poly12_median_nrmse": float(
                np.median([r["poly12_nrmse"] for r in rows])
            ),
            "switches": int(sum(r["mode"] == "operator" for r in rows)),
            "wins_vs_explicit": int(
                sum(r["f003_nrmse"] < r["explicit_nrmse"] for r in rows)
            ),
            "median_reject_step": (
                None if not reject_steps else float(np.median(reject_steps))
            ),
        }

    ratio = explicit / np.maximum(f003, 1e-15)
    return {
        "ood_n": len(ood),
        "control_n": len(controls),
        "ood_explicit_median_nrmse": float(np.median(explicit)),
        "ood_f003_median_nrmse": float(np.median(f003)),
        "ood_poly12_median_nrmse": float(np.median(poly)),
        "ood_median_error_ratio_explicit_over_f003": float(np.median(ratio)),
        "ood_wins_vs_explicit": int(np.sum(f003 < explicit)),
        "ood_wins_vs_poly12": int(np.sum(f003 < poly)),
        "ood_rejections": int(sum(r["mode"] == "operator" for r in ood)),
        "ood_median_reject_step": (
            None
            if not [r["rejected_at"] for r in ood if r["rejected_at"] is not None]
            else float(np.median([
                r["rejected_at"] for r in ood if r["rejected_at"] is not None
            ]))
        ),
        "paired_mean_improvement": float(np.mean(paired)),
        "paired_bootstrap_95ci": [float(ci[0]), float(ci[1])],
        "paired_wilcoxon_one_sided_p": float(
            wilcoxon(explicit, f003, alternative="greater").pvalue
        ),
        "control_switches": int(
            sum(r["mode"] == "operator" for r in controls)
        ),
        "control_explicit_median_nrmse": float(
            np.median([r["explicit_nrmse"] for r in controls])
        ),
        "control_f003_median_nrmse": float(
            np.median([r["f003_nrmse"] for r in controls])
        ),
        "family_summary": family_summary,
    }


def run():
    records = []
    for family, base in (
        ("arctan", 40000),
        ("asinh", 40100),
        ("power", 40200),
        ("lorentzian", 40300),
    ):
        for offset in range(20):
            records.append(evaluate_one(family, base + offset))

    for family, base in (("polynomial", 41000), ("trig", 41100)):
        for offset in range(20):
            records.append(evaluate_one(family, base + offset))

    summary = summarize(records)
    payload = {
        "campaign": "F003",
        "date": "2026-09-24",
        "method_freeze_commit": "4a25a15868a3b78f4f0fe5312ca2aaa9b4d04bf4",
        "preregistration": "docs/F003_ANYTIME_REPRESENTATION_FALSIFICATION_PREREG.md",
        "summary": summary,
        "records": records,
    }
    out = Path("results/f003_anytime_representation_falsification.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    assert summary["ood_wins_vs_explicit"] >= 60
    assert summary["ood_f003_median_nrmse"] <= 0.03
    assert summary["ood_median_error_ratio_explicit_over_f003"] >= 5.0
    assert summary["ood_rejections"] >= 60
    assert summary["control_switches"] <= 4
    lo, hi = summary["paired_bootstrap_95ci"]
    assert lo > 0.0
    assert summary["paired_wilcoxon_one_sided_p"] < 1e-6


if __name__ == "__main__":
    run()
