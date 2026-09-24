from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.optimize import minimize_scalar

from theorica.agents.symbolic_synthesis import (
    CompositionalTheorySynthesizer,
    SymbolicTerm,
    SynthesizedTheory,
)


@dataclass(frozen=True)
class SpectralDiagnostic:
    """Cross-fitted evidence that the current grammar is missing a frequency scale."""

    omega: float
    cv_ratio: float
    base_mse: float
    augmented_mse: float
    expanded: bool


def _safe_values(fn, x):
    try:
        value = np.asarray(fn(np.asarray(x, dtype=float)), dtype=float)
        if value.shape == ():
            value = np.full(np.asarray(x).shape, float(value), dtype=float)
        if value.shape != np.asarray(x).shape or np.any(~np.isfinite(value)):
            return None
        return np.clip(value, -1e12, 1e12)
    except Exception:
        return None


def _fmt(v: float) -> str:
    if abs(v - round(v)) < 2e-9:
        return str(int(round(v)))
    return f"{v:.9g}"


class CrossFittedSpectralClosure:
    """Detect and repair one specific hypothesis-language failure.

    The v0.3 symbolic grammar contains fixed-frequency trigonometric primitives such
    as sin(x) and cos(x), plus bounded compositions. It does not contain a continuous
    frequency parameter. This class treats persistent held-out periodic structure as
    evidence that the grammar itself is misspecified.

    Procedure:
    1. Fit a deliberately low-complexity cubic scaffold in two parity folds.
    2. Ask whether adding sin(omega*x), cos(omega*x) sharply reduces held-out error.
    3. Search omega continuously from data rather than preloading a bank of complete
       equations or target-specific frequencies.
    4. If the cross-fitted error ratio crosses a frozen threshold, inject that operator
       pair into the full THEORICA grammar and refit with those terms mandatory.

    The scope is intentionally narrow. It is a project-level demonstration of
    data-driven grammar expansion for periodic structure, not a claim of universal
    operator invention.
    """

    def __init__(
        self,
        *,
        omega_min: float = 0.25,
        omega_max: float = 6.0,
        coarse_points: int = 116,
        expansion_ratio: float = 0.20,
        max_terms: int = 6,
        complexity_weight: float = 0.03,
    ):
        self.omega_min = float(omega_min)
        self.omega_max = float(omega_max)
        self.coarse_points = int(coarse_points)
        self.expansion_ratio = float(expansion_ratio)
        self.max_terms = int(max_terms)
        self.complexity_weight = float(complexity_weight)

    @staticmethod
    def _scaffold(z):
        z = np.asarray(z, dtype=float)
        return np.column_stack([np.ones(len(z)), z, z**2, z**3])

    def _cross_fitted_score(self, x, y, omega: float):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        idx = np.arange(len(x))
        base_errors = []
        aug_errors = []

        for parity in (0, 1):
            valid = (idx % 2) == parity
            train = ~valid

            btr = self._scaffold(x[train])
            bva = self._scaffold(x[valid])
            beta, *_ = np.linalg.lstsq(btr, y[train], rcond=None)
            base_errors.append(float(np.mean((y[valid] - bva @ beta) ** 2)))

            ftr = np.column_stack(
                [np.sin(omega * x[train]), np.cos(omega * x[train])]
            )
            fva = np.column_stack(
                [np.sin(omega * x[valid]), np.cos(omega * x[valid])]
            )
            dtr = np.column_stack([btr, ftr])
            dva = np.column_stack([bva, fva])
            beta2, *_ = np.linalg.lstsq(dtr, y[train], rcond=None)
            aug_errors.append(float(np.mean((y[valid] - dva @ beta2) ** 2)))

        base_mse = float(np.mean(base_errors))
        aug_mse = float(np.mean(aug_errors))
        if base_mse <= 1e-16:
            ratio = 1.0
        else:
            ratio = aug_mse / base_mse
        return ratio, base_mse, aug_mse

    def diagnose(self, xs, ys):
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        if len(x) < 12:
            raise ValueError("spectral closure requires at least 12 observations")

        grid = np.linspace(self.omega_min, self.omega_max, self.coarse_points)
        scored = [
            (*self._cross_fitted_score(x, y, float(w)), float(w)) for w in grid
        ]
        coarse = min(scored, key=lambda row: row[0])
        omega0 = coarse[3]

        step = (self.omega_max - self.omega_min) / max(self.coarse_points - 1, 1)
        lo = max(self.omega_min, omega0 - step)
        hi = min(self.omega_max, omega0 + step)

        result = minimize_scalar(
            lambda w: self._cross_fitted_score(x, y, float(w))[2],
            bounds=(lo, hi),
            method="bounded",
            options={"xatol": 1e-5},
        )
        omega = float(result.x)
        ratio, base_mse, aug_mse = self._cross_fitted_score(x, y, omega)
        return omega, ratio, base_mse, aug_mse

    def _fit_with_mandatory_frequency(self, x, y, omega: float):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        mandatory = [
            SymbolicTerm(
                f"sin({omega:.9g}*x)",
                lambda z, omega=omega: np.sin(omega * np.asarray(z, dtype=float)),
                4,
            ),
            SymbolicTerm(
                f"cos({omega:.9g}*x)",
                lambda z, omega=omega: np.cos(omega * np.asarray(z, dtype=float)),
                4,
            ),
        ]

        base = CompositionalTheorySynthesizer(
            max_terms=self.max_terms,
            complexity_weight=self.complexity_weight,
            trial_width=200,
        )
        seen = set()
        terms = []
        for term in mandatory + base.generate_terms():
            if term.expression in seen:
                continue
            seen.add(term.expression)
            terms.append(term)

        usable = []
        values = []
        for term in terms:
            v = _safe_values(term.fn, x)
            if v is None or float(np.std(v)) < 1e-12:
                continue
            usable.append(term)
            values.append(v)

        A = np.column_stack(values)
        means = A.mean(axis=0)
        stds = np.maximum(A.std(axis=0), 1e-12)
        Z = (A - means) / stds

        selected = [0, 1]

        def solve(indices):
            D = np.column_stack([A[:, indices], np.ones(len(y))])
            beta, *_ = np.linalg.lstsq(D, y, rcond=None)
            pred = D @ beta
            rss = max(float(np.sum((y - pred) ** 2)), 1e-20)
            structural = sum(usable[j].complexity for j in indices)
            bic = (
                len(y) * math.log(rss / len(y))
                + (len(indices) + 1) * math.log(len(y))
                + self.complexity_weight * structural
            )
            return beta, pred, rss, bic

        beta, pred, rss, bic = solve(selected)
        best_state = (selected.copy(), beta.copy(), rss, bic)

        while len(selected) < self.max_terms:
            residual = y - pred
            correlation = np.abs(Z.T @ residual)
            correlation[np.array(selected, dtype=int)] = -np.inf
            order = np.argsort(correlation)[::-1]

            best_trial = None
            for idx in order:
                if not np.isfinite(correlation[idx]):
                    continue
                inds = selected + [int(idx)]
                b, p, r, score = solve(inds)
                if best_trial is None or score < best_trial[0]:
                    best_trial = (score, int(idx), b, p, r)

            if best_trial is None or best_trial[0] >= bic - 1e-9:
                break

            bic, idx, beta, pred, rss = best_trial
            selected.append(idx)
            if bic < best_state[3]:
                best_state = (selected.copy(), beta.copy(), rss, bic)

        selected, beta, rss, bic = best_state
        chosen = [usable[j] for j in selected]
        coeffs = [float(v) for v in beta[:-1]]
        intercept = float(beta[-1])

        def predictor(z, chosen=tuple(chosen), coeffs=tuple(coeffs), intercept=intercept):
            z = np.asarray(z, dtype=float)
            out = np.full(z.shape, intercept, dtype=float)
            for coeff, term in zip(coeffs, chosen):
                v = _safe_values(term.fn, z)
                if v is None:
                    return np.full(z.shape, np.nan, dtype=float)
                out = out + coeff * v
            return out

        pieces = [
            f"({_fmt(coeff)})*({term.expression})"
            for coeff, term in zip(coeffs, chosen)
            if abs(coeff) > 1e-10
        ]
        if abs(intercept) > 1e-10 or not pieces:
            pieces.append(f"({_fmt(intercept)})")

        return SynthesizedTheory(
            expression=" + ".join(pieces),
            bic=float(bic),
            rss=float(rss),
            complexity=int(sum(t.complexity for t in chosen) + len(chosen)),
            term_expressions=[t.expression for t in chosen],
            coefficients=coeffs,
            intercept=intercept,
            predict_fn=predictor,
        )

    def fit(self, xs, ys):
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        omega, ratio, base_mse, aug_mse = self.diagnose(x, y)
        expanded = bool(ratio < self.expansion_ratio)

        if expanded:
            theory = self._fit_with_mandatory_frequency(x, y, omega)
        else:
            theory, _ = CompositionalTheorySynthesizer(trial_width=200).fit(x, y)

        diagnostic = SpectralDiagnostic(
            omega=omega,
            cv_ratio=float(ratio),
            base_mse=float(base_mse),
            augmented_mse=float(aug_mse),
            expanded=expanded,
        )
        return theory, diagnostic
