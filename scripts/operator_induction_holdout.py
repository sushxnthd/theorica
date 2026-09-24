from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

from theorica.agents.operator_induction import CrossFittedSpectralClosure
from theorica.agents.symbolic_synthesis import (
    CompositionalTheorySynthesizer,
    SymbolicTerm,
)


def normalized_rmse(pred, truth):
    pred = np.asarray(pred, dtype=float)
    truth = np.asarray(truth, dtype=float)
    span = np.quantile(truth, 0.95) - np.quantile(truth, 0.05)
    return float(np.sqrt(np.mean((pred - truth) ** 2)) / max(span, 1e-12))


class FixedIntegerFourierBank(CompositionalTheorySynthesizer):
    """Stronger fixed-language baseline: preload integer frequencies 2..6."""

    def generate_terms(self):
        terms = list(super().generate_terms())
        seen = {t.expression for t in terms}
        for k in range(2, 7):
            for name, fn in (
                (f"sin({k}*x)", lambda z, k=k: np.sin(k * np.asarray(z, dtype=float))),
                (f"cos({k}*x)", lambda z, k=k: np.cos(k * np.asarray(z, dtype=float))),
            ):
                if name not in seen:
                    terms.append(SymbolicTerm(name, fn, 4))
                    seen.add(name)
        return terms


def make_task(seed):
    rng = np.random.default_rng(seed)
    x = np.linspace(-2.0, 2.0, 40)
    x_test = np.linspace(-2.5, 2.5, 401)

    omega = float(rng.uniform(1.35, 5.65))
    amplitude = float(rng.uniform(0.7, 1.5) * rng.choice([-1, 1]))
    phase = float(rng.uniform(-np.pi, np.pi))
    linear = float(rng.uniform(-0.4, 0.4))
    offset = float(rng.uniform(-0.3, 0.3))

    def law(z):
        z = np.asarray(z, dtype=float)
        return amplitude * np.sin(omega * z + phase) + linear * z + offset

    y_clean = law(x)
    noise = rng.normal(0.0, 0.01 * np.std(y_clean), size=len(x))
    y = y_clean + noise
    return x, y, x_test, law(x_test), omega


def run():
    current = CompositionalTheorySynthesizer(trial_width=200)
    fixed = FixedIntegerFourierBank(trial_width=200)
    closure = CrossFittedSpectralClosure()

    records = []
    for seed in range(1000, 1100):
        x, y, x_test, truth, omega_true = make_task(seed)

        current_theory, _ = current.fit(x, y)
        fixed_theory, _ = fixed.fit(x, y)
        closure_theory, diagnostic = closure.fit(x, y)

        records.append(
            {
                "seed": seed,
                "omega_true": omega_true,
                "omega_hat": diagnostic.omega,
                "cv_ratio": diagnostic.cv_ratio,
                "current_nrmse": normalized_rmse(current_theory.predict(x_test), truth),
                "fixed_integer_bank_nrmse": normalized_rmse(
                    fixed_theory.predict(x_test), truth
                ),
                "spectral_closure_nrmse": normalized_rmse(
                    closure_theory.predict(x_test), truth
                ),
            }
        )

    current_err = np.array([r["current_nrmse"] for r in records])
    fixed_err = np.array([r["fixed_integer_bank_nrmse"] for r in records])
    closure_err = np.array([r["spectral_closure_nrmse"] for r in records])
    freq_err = np.abs(
        np.array([r["omega_hat"] for r in records])
        - np.array([r["omega_true"] for r in records])
    )

    paired = current_err - closure_err
    rng = np.random.default_rng(20260924)
    bootstrap = np.array(
        [rng.choice(paired, size=len(paired), replace=True).mean() for _ in range(10000)]
    )
    ci = np.quantile(bootstrap, [0.025, 0.975])

    summary = {
        "n": len(records),
        "current_median_nrmse": float(np.median(current_err)),
        "fixed_integer_bank_median_nrmse": float(np.median(fixed_err)),
        "spectral_closure_median_nrmse": float(np.median(closure_err)),
        "current_mean_nrmse": float(np.mean(current_err)),
        "fixed_integer_bank_mean_nrmse": float(np.mean(fixed_err)),
        "spectral_closure_mean_nrmse": float(np.mean(closure_err)),
        "closure_wins_vs_current": int(np.sum(closure_err < current_err)),
        "closure_wins_vs_fixed_integer_bank": int(np.sum(closure_err < fixed_err)),
        "current_lt_0_01": int(np.sum(current_err < 0.01)),
        "fixed_integer_bank_lt_0_01": int(np.sum(fixed_err < 0.01)),
        "closure_lt_0_01": int(np.sum(closure_err < 0.01)),
        "median_abs_frequency_error": float(np.median(freq_err)),
        "p90_abs_frequency_error": float(np.quantile(freq_err, 0.90)),
        "mean_paired_improvement_vs_current": float(np.mean(paired)),
        "mean_paired_improvement_vs_current_bootstrap_95ci": [
            float(ci[0]),
            float(ci[1]),
        ],
        "wilcoxon_one_sided_p_vs_current": float(
            wilcoxon(current_err, closure_err, alternative="greater").pvalue
        ),
        "wilcoxon_one_sided_p_vs_fixed_integer_bank": float(
            wilcoxon(fixed_err, closure_err, alternative="greater").pvalue
        ),
    }

    payload = {
        "experiment": "THEORICA cross-fitted spectral closure frozen holdout",
        "date": "2026-09-24",
        "seeds": [1000, 1099],
        "design": {
            "n_train": 40,
            "train_domain": [-2.0, 2.0],
            "test_domain": [-2.5, 2.5],
            "noise_std_fraction": 0.01,
            "omega_range": [1.35, 5.65],
            "frozen_expansion_ratio": 0.20,
        },
        "summary": summary,
        "records": records,
    }

    out = Path("results/operator_induction_holdout.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    # Frozen regression gates. These are deliberately looser than observed values.
    assert summary["closure_wins_vs_current"] >= 95
    assert summary["closure_wins_vs_fixed_integer_bank"] >= 95
    assert summary["spectral_closure_median_nrmse"] <= 0.01
    assert summary["median_abs_frequency_error"] <= 0.03


if __name__ == "__main__":
    run()
