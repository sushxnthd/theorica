from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial
from scipy.special import eval_hermite, eval_laguerre, hyp1f1, iv
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

    if family == "hermite":
        x = np.linspace(-0.75, 0.75, 81)
        xt = np.linspace(-0.95, 0.95, 401)
        order = int(rng.integers(8, 13))
        k = float(rng.uniform(0.8, 1.2))
        amplitude = float(rng.uniform(0.5, 1.4) * rng.choice([-1, 1]))

        def law(z):
            return amplitude * eval_hermite(order, k * np.asarray(z, dtype=float))

        params = {"order": order, "k": k}

    elif family == "laguerre":
        x = np.linspace(0.15, 2.4, 81)
        xt = np.linspace(0.08, 3.0, 401)
        order = int(rng.integers(8, 13))
        k = float(rng.uniform(0.55, 1.05))
        amplitude = float(rng.uniform(0.5, 1.4) * rng.choice([-1, 1]))

        def law(z):
            return amplitude * eval_laguerre(order, k * np.asarray(z, dtype=float))

        params = {"order": order, "k": k}

    elif family == "hyp1f1":
        x = np.linspace(-1.0, 1.0, 81)
        xt = np.linspace(-1.4, 1.4, 401)
        a = float(rng.uniform(-2.4, 2.4))
        if abs(a - round(a)) < 0.12:
            a += 0.19
        b = float(rng.uniform(0.8, 2.8))
        k = float(rng.uniform(0.55, 1.35))
        amplitude = float(rng.uniform(0.5, 1.4) * rng.choice([-1, 1]))

        def law(z):
            return amplitude * hyp1f1(a, b, k * np.asarray(z, dtype=float))

        params = {"a": a, "b": b, "k": k}

    elif family == "modified_bessel":
        x = np.linspace(0.45, 2.5, 81)
        xt = np.linspace(0.30, 3.2, 401)
        nu = float(rng.uniform(0.2, 2.2))
        k = float(rng.uniform(0.55, 1.25))
        amplitude = float(rng.uniform(0.5, 1.4) * rng.choice([-1, 1]))

        def law(z):
            return amplitude * iv(nu, k * np.asarray(z, dtype=float))

        params = {"nu": nu, "k": k}

    elif family == "polynomial":
        x = np.linspace(-1.5, 1.5, 81)
        xt = np.linspace(-2.0, 2.0, 401)
        degree = int(rng.integers(2, 6))
        coefficients = rng.uniform(-1.2, 1.2, degree + 1)
        coefficients[-1] += np.sign(coefficients[-1] or 1.0) * 0.6

        def law(z):
            z = np.asarray(z, dtype=float)
            return sum(c * z**p for p, c in enumerate(coefficients))

        params = {"degree": degree}

    elif family == "trig":
        x = np.linspace(-2.0, 2.0, 81)
        xt = np.linspace(-2.6, 2.6, 401)
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
    explicit_pred = explicit.predict(xt)
    explicit_nrmse = normalized_rmse(explicit_pred, truth)

    poly_pred, poly_degree, poly_validation = polynomial_baseline(x, y, xt)
    poly_nrmse = normalized_rmse(poly_pred, truth)

    closure = RepresentationClosureScientist().fit(x, y, bounds=bounds)
    closure_pred = closure.predict(xt)
    closure_nrmse = normalized_rmse(closure_pred, truth)

    record = {
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
        record["operator_terms"] = len(closure.theory.support)
        record["operator_support"] = [list(t) for t in closure.theory.support]
        record["operator_coefficients"] = list(closure.theory.coefficients)
        record["operator_weak_cv"] = closure.theory.weak_cv
    return record


def summarize(records):
    ood_families = {"hermite", "laguerre", "hyp1f1", "modified_bessel"}
    ood = [r for r in records if r["family"] in ood_families]
    controls = [r for r in records if r["family"] not in ood_families]

    explicit = np.array([r["explicit_nrmse"] for r in ood], dtype=float)
    closure = np.array([r["closure_nrmse"] for r in ood], dtype=float)
    poly = np.array([r["poly12_nrmse"] for r in ood], dtype=float)
    paired = explicit - closure

    rng = np.random.default_rng(20260924)
    bootstrap = np.array(
        [
            np.mean(rng.choice(paired, size=len(paired), replace=True))
            for _ in range(10000)
        ]
    )
    ci = np.quantile(bootstrap, [0.025, 0.975])

    explicit_control = np.array(
        [r["explicit_nrmse"] for r in controls], dtype=float
    )
    closure_control = np.array(
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
        }

    pvalue = float(
        wilcoxon(explicit, closure, alternative="greater").pvalue
    )

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
            float(ci[0]),
            float(ci[1]),
        ],
        "ood_wilcoxon_one_sided_p": pvalue,
        "control_explicit_median_nrmse": float(np.median(explicit_control)),
        "control_closure_median_nrmse": float(np.median(closure_control)),
        "controls_retained_explicit": int(
            sum(r["closure_mode"] == "explicit" for r in controls)
        ),
        "family_summary": family_summary,
    }


def run():
    records = []

    for family in ("hermite", "laguerre", "hyp1f1", "modified_bessel"):
        for offset in range(20):
            records.append(evaluate_one(family, 10000 + offset))

    for family in ("polynomial", "trig"):
        for offset in range(20):
            records.append(evaluate_one(family, 11000 + offset))

    summary = summarize(records)
    payload = {
        "experiment": "THEORICA frozen falsification-gated representation closure",
        "date": "2026-09-24",
        "method_freeze_commit": "f3c3c6cdd89f4edd6970e90a7da817a425c04b8c",
        "preregistration": "docs/REPRESENTATION_CLOSURE_PREREGISTRATION.md",
        "summary": summary,
        "records": records,
    }

    out = Path("results/representation_closure_holdout.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    # Frozen preregistered primary gates.
    assert summary["ood_closure_wins_vs_explicit"] >= 60
    assert summary["ood_closure_median_nrmse"] <= 0.03
    assert summary["controls_retained_explicit"] >= 30
    assert (
        summary["control_closure_median_nrmse"]
        <= 1.25 * summary["control_explicit_median_nrmse"]
    )


if __name__ == "__main__":
    run()
