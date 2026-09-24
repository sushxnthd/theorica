from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial
from scipy.special import dawsn, erf
from scipy.stats import wilcoxon

from theorica.agents.representation_closure import (
    RepresentationClosureScientist,
    normalized_rmse,
)
from theorica.agents.symbolic_synthesis import CompositionalTheorySynthesizer


def _noise(rng, clean, fraction=0.003):
    scale = fraction * max(float(np.std(clean)), 1e-6)
    return clean + rng.normal(0.0, scale, size=len(clean))


def make_task(family, seed):
    rng = np.random.default_rng(seed)

    if family == "gaussian":
        x = np.linspace(-1.5, 1.5, 81)
        xt = np.linspace(-3.0, 3.0, 401)
        a = float(rng.uniform(0.45, 1.10))
        b = float(rng.uniform(-0.25, 0.25))
        amplitude = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))

        def law(z):
            z = np.asarray(z, dtype=float)
            return amplitude * np.exp(-a * (z - b) ** 2)

        params = {"a": a, "b": b}

    elif family == "erf":
        x = np.linspace(-1.5, 1.5, 81)
        xt = np.linspace(-3.0, 3.0, 401)
        k = float(rng.uniform(0.60, 1.30))
        shift = float(rng.uniform(-0.30, 0.30))
        amplitude = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))

        def law(z):
            z = np.asarray(z, dtype=float)
            return amplitude * erf(k * z + shift)

        params = {"k": k, "shift": shift}

    elif family == "dawson":
        x = np.linspace(-1.5, 1.5, 81)
        xt = np.linspace(-3.0, 3.0, 401)
        k = float(rng.uniform(0.60, 1.20))
        shift = float(rng.uniform(-0.25, 0.25))
        amplitude = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))

        def law(z):
            z = np.asarray(z, dtype=float)
            return amplitude * dawsn(k * z + shift)

        params = {"k": k, "shift": shift}

    elif family == "sinc":
        x = np.linspace(0.50, 3.00, 81)
        xt = np.linspace(0.30, 6.00, 401)
        k = float(rng.uniform(0.80, 1.40))
        amplitude = float(rng.uniform(0.6, 1.4) * rng.choice([-1, 1]))

        def law(z):
            z = np.asarray(z, dtype=float)
            t = k * z
            return amplitude * np.sin(t) / t

        params = {"k": k}

    elif family == "polynomial":
        x = np.linspace(-1.5, 1.5, 81)
        xt = np.linspace(-3.0, 3.0, 401)
        degree = int(rng.integers(2, 6))
        coefficients = rng.uniform(-1.2, 1.2, degree + 1)
        coefficients[-1] += np.sign(coefficients[-1] or 1.0) * 0.6

        def law(z):
            z = np.asarray(z, dtype=float)
            return sum(c * z**p for p, c in enumerate(coefficients))

        params = {"degree": degree}

    elif family == "trig":
        x = np.linspace(-2.0, 2.0, 81)
        xt = np.linspace(-4.0, 4.0, 401)
        a, b = rng.uniform(0.5, 1.5, 2) * rng.choice([-1, 1], 2)
        slope = float(rng.uniform(-0.35, 0.35))
        offset = float(rng.uniform(-0.3, 0.3))

        def law(z):
            z = np.asarray(z, dtype=float)
            return a * np.sin(z) + b * np.cos(z) + slope * z + offset

        params = {"a": float(a), "b": float(b)}

    else:
        raise ValueError(f"unknown family: {family}")

    clean = np.asarray(law(x), dtype=float)
    y = _noise(rng, clean)
    truth = np.asarray(law(xt), dtype=float)
    return x, y, xt, truth, params


def polynomial_baseline(x, y, xt):
    qlo, qhi = np.quantile(x, [0.15, 0.85])
    inner = (x >= qlo) & (x <= qhi)
    best = None
    for degree in range(1, 13):
        model = Polynomial.fit(x[inner], y[inner], degree)
        score = normalized_rmse(model(x[~inner]), y[~inner])
        if best is None or score < best[0]:
            best = (score, degree)
    model = Polynomial.fit(x, y, best[1])
    return np.asarray(model(xt), dtype=float), int(best[1]), float(best[0])


def evaluate_one(family, seed):
    x, y, xt, truth, params = make_task(family, seed)
    bounds = (float(xt.min()), float(xt.max()))

    explicit, _ = CompositionalTheorySynthesizer(trial_width=200).fit(x, y)
    explicit_nrmse = normalized_rmse(explicit.predict(xt), truth)

    poly_pred, poly_degree, poly_validation = polynomial_baseline(x, y, xt)
    poly_nrmse = normalized_rmse(poly_pred, truth)

    closure = RepresentationClosureScientist().fit(x, y, bounds=bounds)
    closure_nrmse = normalized_rmse(closure.predict(xt), truth)

    row = {
        "family": family,
        "seed": seed,
        "params": params,
        "explicit_nrmse": explicit_nrmse,
        "poly12_nrmse": poly_nrmse,
        "poly12_selected_degree": poly_degree,
        "poly12_validation_nrmse": poly_validation,
        "closure_nrmse": closure_nrmse,
        "closure_mode": closure.mode,
        "explicit_validation_nrmse": closure.explicit_validation_nrmse,
        "operator_validation_nrmse": closure.operator_validation_nrmse,
        "validation_ratio": closure.validation_ratio,
        "theory_expression": closure.theory.expression,
    }
    if closure.mode == "operator":
        row["operator_terms"] = len(closure.theory.support)
        row["operator_support"] = [list(t) for t in closure.theory.support]
        row["operator_coefficients"] = list(closure.theory.coefficients)
        row["operator_weak_cv"] = closure.theory.weak_cv
    return row


def summarize(records):
    ood_names = {"gaussian", "erf", "dawson", "sinc"}
    ood = [r for r in records if r["family"] in ood_names]
    controls = [r for r in records if r["family"] not in ood_names]

    explicit = np.array([r["explicit_nrmse"] for r in ood], dtype=float)
    closure = np.array([r["closure_nrmse"] for r in ood], dtype=float)
    poly = np.array([r["poly12_nrmse"] for r in ood], dtype=float)
    paired = explicit - closure

    rng = np.random.default_rng(20260924)
    bootstrap = np.array([
        np.mean(rng.choice(paired, size=len(paired), replace=True))
        for _ in range(10000)
    ])
    ci = np.quantile(bootstrap, [0.025, 0.975])

    control_explicit = np.array(
        [r["explicit_nrmse"] for r in controls], dtype=float
    )
    control_closure = np.array(
        [r["closure_nrmse"] for r in controls], dtype=float
    )

    family_summary = {}
    for family in sorted({r["family"] for r in records}):
        rows = [r for r in records if r["family"] == family]
        family_summary[family] = {
            "n": len(rows),
            "explicit_median_nrmse": float(
                np.median([r["explicit_nrmse"] for r in rows])
            ),
            "closure_median_nrmse": float(
                np.median([r["closure_nrmse"] for r in rows])
            ),
            "poly12_median_nrmse": float(
                np.median([r["poly12_nrmse"] for r in rows])
            ),
            "operator_selected": int(
                sum(r["closure_mode"] == "operator" for r in rows)
            ),
            "closure_wins_vs_explicit": int(
                sum(r["closure_nrmse"] < r["explicit_nrmse"] for r in rows)
            ),
            "closure_wins_vs_poly12": int(
                sum(r["closure_nrmse"] < r["poly12_nrmse"] for r in rows)
            ),
        }

    return {
        "ood_n": len(ood),
        "control_n": len(controls),
        "ood_explicit_median_nrmse": float(np.median(explicit)),
        "ood_closure_median_nrmse": float(np.median(closure)),
        "ood_poly12_median_nrmse": float(np.median(poly)),
        "ood_closure_wins_vs_explicit": int(np.sum(closure < explicit)),
        "ood_closure_wins_vs_poly12": int(np.sum(closure < poly)),
        "ood_operator_selected": int(
            sum(r["closure_mode"] == "operator" for r in ood)
        ),
        "ood_mean_paired_improvement": float(np.mean(paired)),
        "ood_mean_paired_improvement_bootstrap_95ci": [
            float(ci[0]), float(ci[1])
        ],
        "ood_wilcoxon_one_sided_p": float(
            wilcoxon(explicit, closure, alternative="greater").pvalue
        ),
        "control_explicit_median_nrmse": float(np.median(control_explicit)),
        "control_closure_median_nrmse": float(np.median(control_closure)),
        "controls_retained_explicit": int(
            sum(r["closure_mode"] == "explicit" for r in controls)
        ),
        "family_summary": family_summary,
    }


def run():
    records = []
    for family, base in (
        ("gaussian", 20000),
        ("erf", 20100),
        ("dawson", 20200),
        ("sinc", 20300),
    ):
        for offset in range(20):
            records.append(evaluate_one(family, base + offset))

    for family, base in (("polynomial", 21000), ("trig", 21100)):
        for offset in range(20):
            records.append(evaluate_one(family, base + offset))

    summary = summarize(records)
    payload = {
        "experiment": "THEORICA representation closure v2 frozen long-range holdout",
        "date": "2026-09-24",
        "method_freeze_commit": "00d89b9613ce0e1443226f11217c1274a7664f75",
        "preregistration": "docs/REPRESENTATION_CLOSURE_V2_PREREGISTRATION.md",
        "summary": summary,
        "records": records,
    }
    out = Path("results/representation_closure_v2_holdout.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    assert summary["ood_closure_wins_vs_explicit"] >= 60
    assert summary["ood_closure_median_nrmse"] <= 0.02
    lo, hi = summary["ood_mean_paired_improvement_bootstrap_95ci"]
    assert lo > 0.0
    assert summary["ood_wilcoxon_one_sided_p"] < 0.01
    assert summary["controls_retained_explicit"] >= 38
    assert (
        summary["control_closure_median_nrmse"]
        <= 1.10 * summary["control_explicit_median_nrmse"]
    )


if __name__ == "__main__":
    run()
