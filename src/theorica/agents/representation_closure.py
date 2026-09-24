from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
import warnings

import numpy as np
from scipy.integrate import solve_ivp

from theorica.agents.symbolic_synthesis import (
    CompositionalTheorySynthesizer,
    SynthesizedTheory,
)


@dataclass(frozen=True)
class OperatorCandidate:
    support: tuple[tuple[int, int], ...]
    coefficients: tuple[float, ...]
    weak_cv: float
    validation_nrmse: float
    complexity: int


@dataclass
class AnnihilatorTheory:
    support: tuple[tuple[int, int], ...]
    coefficients: tuple[float, ...]
    amplitudes: np.ndarray
    bounds: tuple[float, float]
    validation_nrmse: float
    weak_cv: float

    @property
    def expression(self) -> str:
        pieces = []
        for (order, power), coeff in zip(self.support, self.coefficients):
            if abs(coeff) < 1e-12:
                continue
            xpart = "" if power == 0 else ("x*" if power == 1 else f"x**{power}*")
            ypart = "y" if order == 0 else ("D[y]" if order == 1 else f"D**{order}[y]")
            pieces.append(f"({coeff:.8g})*{xpart}{ypart}")
        return " + ".join(pieces) + " = 0"

    def predict(self, xs):
        basis = _fundamental_basis(
            self.support,
            np.asarray(self.coefficients, dtype=float),
            self.bounds,
            np.asarray(xs, dtype=float),
        )
        if basis is None:
            return np.full(np.asarray(xs).shape, np.nan, dtype=float)
        return basis @ self.amplitudes


@dataclass
class RepresentationClosureResult:
    mode: str
    theory: SynthesizedTheory | AnnihilatorTheory
    explicit_validation_nrmse: float
    operator_validation_nrmse: float | None
    validation_ratio: float | None

    def predict(self, xs):
        return self.theory.predict(xs)


def normalized_rmse(pred, truth) -> float:
    pred = np.asarray(pred, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if pred.shape != truth.shape or np.any(~np.isfinite(pred)):
        return float("inf")
    span = float(np.quantile(truth, 0.95) - np.quantile(truth, 0.05))
    return float(np.sqrt(np.mean((pred - truth) ** 2)) / max(abs(span), 1e-12))


class WeakAnnihilatorSynthesizer:
    """Learn a compact differential operator from static noisy measurements.

    The hypothesis language is not a library of named functions. It is a small
    meta-grammar of terms x^k D^j[y], with j <= 2 and k <= 2. Weak-form test
    functions move derivatives off the measured signal by integration by parts,
    avoiding numerical differentiation of y.

    A learned operator becomes a new theory primitive through its numerical
    null space. The implementation is intentionally bounded and auditable.
    """

    def __init__(
        self,
        *,
        max_order: int = 2,
        max_poly_degree: int = 2,
        max_terms: int = 4,
        top_k: int = 30,
        min_leading_ratio: float = 0.015,
    ):
        self.max_order = int(max_order)
        self.max_poly_degree = int(max_poly_degree)
        self.max_terms = int(max_terms)
        self.top_k = int(top_k)
        self.min_leading_ratio = float(min_leading_ratio)
        self.terms = tuple(
            (j, k)
            for j in range(self.max_order + 1)
            for k in range(self.max_poly_degree + 1)
        )
        self.supports = tuple(
            s
            for r in range(2, self.max_terms + 1)
            for s in combinations(self.terms, r)
            if len({j for j, _ in s}) >= 2
        )

    @staticmethod
    def _phi_parts(x, center, width, q=4):
        z = (x - center) / width
        inside = np.abs(z) < 1.0
        phi = np.zeros_like(x, dtype=float)
        d1 = np.zeros_like(x, dtype=float)
        d2 = np.zeros_like(x, dtype=float)
        zi = z[inside]
        a = 1.0 - zi**2
        phi[inside] = a**q
        d1[inside] = (-2.0 * q * zi / width) * a ** (q - 1)
        d2[inside] = (
            (-2.0 * q / width**2) * a ** (q - 1)
            + (4.0 * q * (q - 1) * zi**2 / width**2) * a ** (q - 2)
        )
        return phi, d1, d2

    @staticmethod
    def _test_derivative(x, power, order, phi, d1, d2):
        if order == 0:
            return phi * x**power
        if order == 1:
            out = d1 * x**power
            if power >= 1:
                out = out + phi * power * x ** (power - 1)
            return out
        out = d2 * x**power
        if power >= 1:
            out = out + 2.0 * d1 * power * x ** (power - 1)
        if power >= 2:
            out = out + phi * power * (power - 1) * x ** (power - 2)
        return out

    def _weak_matrix(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        lo, hi = float(x.min()), float(x.max())
        span = hi - lo
        rows = []
        for width_fraction in (0.20, 0.28, 0.36):
            width = width_fraction * span
            centers = np.linspace(lo + width, hi - width, 15)
            for center in centers:
                phi, d1, d2 = self._phi_parts(x, center, width)
                row = []
                for order, power in self.terms:
                    g = self._test_derivative(x, power, order, phi, d1, d2)
                    integral = np.trapezoid(g * y, x)
                    row.append(((-1) ** order) * integral)
                rows.append(row)
        W = np.asarray(rows, dtype=float)
        norms = np.maximum(np.linalg.norm(W, axis=0), 1e-14)
        return W / norms, norms

    def _fit_support(self, W, norms, support):
        indices = [self.terms.index(term) for term in support]
        A = W[:, indices]
        _, _, vt = np.linalg.svd(A, full_matrices=False)
        vector = vt[-1]

        fold_scores = []
        for fold in range(3):
            valid = np.arange(len(A)) % 3 == fold
            train = ~valid
            _, _, vt_fold = np.linalg.svd(A[train], full_matrices=False)
            coeff = vt_fold[-1]
            residual = A[valid] @ coeff
            denom = np.sqrt(np.mean(np.sum(A[valid] ** 2, axis=1))) + 1e-12
            fold_scores.append(float(np.sqrt(np.mean(residual**2)) / denom))

        original = np.array(
            [vector[i] / norms[index] for i, index in enumerate(indices)],
            dtype=float,
        )
        original /= np.max(np.abs(original)) + 1e-30
        return original, float(np.mean(fold_scores))

    def _leading_regular(self, support, coefficients, bounds):
        order = max(j for j, _ in support)
        grid = np.linspace(float(bounds[0]), float(bounds[1]), 400)
        leading = np.zeros_like(grid)
        for (j, power), coeff in zip(support, coefficients):
            if j == order:
                leading += coeff * grid**power
        ratio = float(
            np.min(np.abs(leading)) / (np.max(np.abs(leading)) + 1e-12)
        )
        return ratio >= self.min_leading_ratio

    def ranked_candidates(self, x, y, bounds):
        W, norms = self._weak_matrix(x, y)
        ranked = []
        for support in self.supports:
            try:
                coefficients, weak_cv = self._fit_support(W, norms, support)
            except np.linalg.LinAlgError:
                continue
            if not self._leading_regular(support, coefficients, bounds):
                continue
            degree_sum = sum(power for _, power in support)
            score = (
                math.log10(weak_cv + 1e-12)
                + 0.07 * len(support)
                + 0.12 * degree_sum
            )
            ranked.append((score, support, coefficients, weak_cv))
        ranked.sort(key=lambda item: item[0])
        return ranked[: self.top_k]

    def choose_by_forecast(self, x_train, y_train, x_valid, y_valid, bounds):
        x_train = np.asarray(x_train, dtype=float)
        y_train = np.asarray(y_train, dtype=float)
        x_valid = np.asarray(x_valid, dtype=float)
        y_valid = np.asarray(y_valid, dtype=float)
        candidates = self.ranked_candidates(x_train, y_train, bounds)
        best = None
        combined_x = np.concatenate([x_train, x_valid])
        for _, support, coefficients, weak_cv in candidates:
            basis = _fundamental_basis(support, coefficients, bounds, combined_x)
            if basis is None:
                continue
            train_basis = basis[: len(x_train)]
            valid_basis = basis[len(x_train) :]
            amplitudes, *_ = np.linalg.lstsq(train_basis, y_train, rcond=None)
            pred = valid_basis @ amplitudes
            error = normalized_rmse(pred, y_valid)
            if not np.isfinite(error):
                continue
            complexity = len(support) + sum(power for _, power in support)
            objective = math.log10(error + 1e-10) + 0.02 * complexity
            if best is None or objective < best[0]:
                best = (
                    objective,
                    OperatorCandidate(
                        support=tuple(support),
                        coefficients=tuple(float(v) for v in coefficients),
                        weak_cv=float(weak_cv),
                        validation_nrmse=float(error),
                        complexity=int(complexity),
                    ),
                )
        return None if best is None else best[1]

    @staticmethod
    def finalize(candidate, x, y, bounds):
        basis = _fundamental_basis(
            candidate.support,
            np.asarray(candidate.coefficients, dtype=float),
            bounds,
            np.asarray(x, dtype=float),
        )
        if basis is None:
            raise RuntimeError("learned annihilator is not numerically stable")
        amplitudes, *_ = np.linalg.lstsq(
            basis, np.asarray(y, dtype=float), rcond=None
        )
        return AnnihilatorTheory(
            support=candidate.support,
            coefficients=candidate.coefficients,
            amplitudes=np.asarray(amplitudes, dtype=float),
            bounds=(float(bounds[0]), float(bounds[1])),
            validation_nrmse=float(candidate.validation_nrmse),
            weak_cv=float(candidate.weak_cv),
        )


class RepresentationClosureScientist:
    """Falsification-gated switching between explicit and operator theories.

    The scientist first asks whether THEORICA's explicit symbolic grammar
    extrapolates to held-out edge measurements. A generic weak-form annihilator
    language competes on exactly the same held-out points. The representation is
    changed only if the operator theory wins by a frozen multiplicative margin.
    """

    def __init__(
        self,
        *,
        gate_ratio: float = 0.50,
        operator_max_validation_nrmse: float = 0.08,
        explicit_inadequacy_nrmse: float = 0.01,
        symbolic_trial_width: int = 200,
        operator_top_k: int = 30,
    ):
        self.gate_ratio = float(gate_ratio)
        self.operator_max_validation_nrmse = float(
            operator_max_validation_nrmse
        )
        self.explicit_inadequacy_nrmse = float(explicit_inadequacy_nrmse)
        self.symbolic_trial_width = int(symbolic_trial_width)
        self.operator = WeakAnnihilatorSynthesizer(top_k=operator_top_k)

    def fit(self, xs, ys, *, bounds=None):
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        if bounds is None:
            bounds = (float(x.min()), float(x.max()))
        else:
            bounds = (float(bounds[0]), float(bounds[1]))

        qlo, qhi = np.quantile(x, [0.15, 0.85])
        inner = (x >= qlo) & (x <= qhi)
        x_train, y_train = x[inner], y[inner]
        x_valid, y_valid = x[~inner], y[~inner]

        explicit_inner, _ = CompositionalTheorySynthesizer(
            trial_width=self.symbolic_trial_width
        ).fit(x_train, y_train)
        explicit_validation = normalized_rmse(
            explicit_inner.predict(x_valid), y_valid
        )

        candidate = self.operator.choose_by_forecast(
            x_train, y_train, x_valid, y_valid, bounds
        )
        operator_validation = (
            None if candidate is None else candidate.validation_nrmse
        )

        use_operator = False
        ratio = None
        if candidate is not None and np.isfinite(explicit_validation):
            ratio = float(
                candidate.validation_nrmse / max(explicit_validation, 1e-12)
            )
            use_operator = (
                explicit_validation >= self.explicit_inadequacy_nrmse
                and candidate.validation_nrmse
                <= self.operator_max_validation_nrmse
                and ratio <= self.gate_ratio
            )

        if use_operator:
            theory = self.operator.finalize(candidate, x, y, bounds)
            return RepresentationClosureResult(
                mode="operator",
                theory=theory,
                explicit_validation_nrmse=float(explicit_validation),
                operator_validation_nrmse=float(candidate.validation_nrmse),
                validation_ratio=ratio,
            )

        explicit_full, _ = CompositionalTheorySynthesizer(
            trial_width=self.symbolic_trial_width
        ).fit(x, y)
        return RepresentationClosureResult(
            mode="explicit",
            theory=explicit_full,
            explicit_validation_nrmse=float(explicit_validation),
            operator_validation_nrmse=(
                None if candidate is None else float(candidate.validation_nrmse)
            ),
            validation_ratio=ratio,
        )


def _fundamental_basis(support, coefficients, bounds, xs):
    support = tuple(support)
    coefficients = np.asarray(coefficients, dtype=float)
    order = max(j for j, _ in support)
    coeffs = {j: {} for j in range(order + 1)}
    for (j, power), coeff in zip(support, coefficients):
        coeffs.setdefault(j, {})[power] = (
            coeffs.setdefault(j, {}).get(power, 0.0) + float(coeff)
        )

    def a(j, t):
        return sum(value * t**power for power, value in coeffs.get(j, {}).items())

    lo, hi = float(bounds[0]), float(bounds[1])
    anchor = 0.5 * (lo + hi)
    x = np.asarray(xs, dtype=float)
    unique_x, inverse = np.unique(x, return_inverse=True)

    if order == 1:
        initials = ([1.0],)

        def rhs(t, state):
            den = a(1, t)
            if abs(den) < 1e-10:
                raise FloatingPointError("singular leading coefficient")
            return [-a(0, t) * state[0] / den]

    elif order == 2:
        initials = ([1.0, 0.0], [0.0, 1.0])

        def rhs(t, state):
            den = a(2, t)
            if abs(den) < 1e-10:
                raise FloatingPointError("singular leading coefficient")
            return [
                state[1],
                -(a(1, t) * state[1] + a(0, t) * state[0]) / den,
            ]

    else:
        return None

    columns = []
    max_step = max((hi - lo) / 35.0, 1e-3)
    for initial in initials:
        values_unique = np.empty_like(unique_x)
        for mask in (unique_x >= anchor, unique_x < anchor):
            if not np.any(mask):
                continue
            times = np.sort(unique_x[mask])
            if times[0] < anchor:
                times = times[::-1]
            end = float(times[-1])
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    solution = solve_ivp(
                        rhs,
                        (anchor, end),
                        initial,
                        t_eval=times,
                        rtol=2e-6,
                        atol=1e-8,
                        max_step=max_step,
                    )
            except (FloatingPointError, ValueError, OverflowError):
                return None
            if (
                not solution.success
                or len(solution.t) != len(times)
                or np.any(~np.isfinite(solution.y))
                or np.max(np.abs(solution.y)) > 1e9
            ):
                return None
            mapping = {
                round(float(t), 12): float(v)
                for t, v in zip(solution.t, solution.y[0])
            }
            for index in np.where(mask)[0]:
                values_unique[index] = mapping[round(float(unique_x[index]), 12)]
        columns.append(values_unique[inverse])
    return np.column_stack(columns)
