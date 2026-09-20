from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable
import numpy as np


@dataclass(frozen=True)
class SymbolicTerm:
    """One grammar-generated scalar feature."""
    expression: str
    fn: Callable[[np.ndarray], np.ndarray]
    complexity: int


@dataclass
class SynthesizedTheory:
    """Sparse linear composition of grammar-generated terms."""
    expression: str
    bic: float
    rss: float
    complexity: int
    term_expressions: list[str]
    coefficients: list[float]
    intercept: float
    predict_fn: Callable[[np.ndarray], np.ndarray]

    def predict(self, xs):
        z = np.asarray(xs, dtype=float)
        return np.asarray(self.predict_fn(z), dtype=float)


def _safe_values(fn: Callable[[np.ndarray], np.ndarray], x: np.ndarray):
    try:
        value = np.asarray(fn(x), dtype=float)
        if value.shape == ():
            value = np.full_like(x, float(value), dtype=float)
        if value.shape != x.shape or np.any(~np.isfinite(value)):
            return None
        return np.clip(value, -1e12, 1e12)
    except Exception:
        return None


def _fmt_coeff(v: float) -> str:
    if abs(v - round(v)) < 2e-9:
        return str(int(round(v)))
    return f"{v:.9g}"


class CompositionalTheorySynthesizer:
    """Open-ended *compositional* symbolic regressor for one controllable variable.

    The system does not select from a list of complete equations. Instead it creates a
    grammar of reusable terms (powers, transformed subexpressions and products) and
    assembles sparse theories by forward search under a BIC + structural-complexity
    objective. Complete benchmark equations are never stored in the library.

    This is deliberately bounded rather than an unrestricted program synthesizer: the
    current v0.3 grammar uses polynomial atoms up to degree 6 and a small set of safe
    unary/binary operators. The bounded grammar keeps the experiment reproducible and
    provides an explicit next frontier for later work.
    """

    def __init__(self, *, max_degree: int = 6, max_terms: int = 6,
                 complexity_weight: float = 0.03, trial_width: int = 30):
        self.max_degree = int(max_degree)
        self.max_terms = int(max_terms)
        self.complexity_weight = float(complexity_weight)
        self.trial_width = int(trial_width)

    def generate_terms(self) -> list[SymbolicTerm]:
        terms: list[SymbolicTerm] = []
        seen: set[str] = set()

        def add(expr: str, fn, complexity: int):
            if expr in seen:
                return
            seen.add(expr)
            terms.append(SymbolicTerm(expr, fn, int(complexity)))

        monomials: list[tuple[str, Callable, int]] = []
        for degree in range(1, self.max_degree + 1):
            expr = "x" if degree == 1 else f"x**{degree}"
            fn = lambda z, degree=degree: np.asarray(z, dtype=float) ** degree
            comp = degree
            add(expr, fn, comp)
            monomials.append((expr, fn, comp))

        inner = list(monomials[: min(3, len(monomials))])
        for i in range(min(3, len(monomials))):
            for j in range(i + 1, min(3, len(monomials))):
                ei, fi, ci = monomials[i]
                ej, fj, cj = monomials[j]
                for sign in (1.0, -1.0):
                    op = "+" if sign > 0 else "-"
                    expr = f"({ei}{op}{ej})"
                    fn = lambda z, fi=fi, fj=fj, sign=sign: fi(z) + sign * fj(z)
                    inner.append((expr, fn, ci + cj + 1))

        trig_terms: list[tuple[str, Callable, int]] = []
        for expr, fn, comp in inner:
            s_expr = f"sin({expr})"
            s_fn = lambda z, fn=fn: np.sin(fn(z))
            add(s_expr, s_fn, comp + 2)
            trig_terms.append((s_expr, s_fn, comp + 2))

            c_expr = f"cos({expr})"
            c_fn = lambda z, fn=fn: np.cos(fn(z))
            add(c_expr, c_fn, comp + 2)
            trig_terms.append((c_expr, c_fn, comp + 2))

            l_expr = f"log(1+abs({expr}))"
            l_fn = lambda z, fn=fn: np.log1p(np.abs(fn(z)))
            add(l_expr, l_fn, comp + 3)

            q_expr = f"sqrt(abs({expr}))"
            q_fn = lambda z, fn=fn: np.sqrt(np.abs(fn(z)))
            add(q_expr, q_fn, comp + 3)

        for i, (e1, f1, c1) in enumerate(trig_terms):
            for e2, f2, c2 in trig_terms[i + 1:]:
                if c1 + c2 > 10:
                    continue
                add(
                    f"({e1})*({e2})",
                    lambda z, f1=f1, f2=f2: f1(z) * f2(z),
                    c1 + c2 + 1,
                )
        return terms

    def _matrix(self, x: np.ndarray):
        usable_terms: list[SymbolicTerm] = []
        values: list[np.ndarray] = []
        for term in self.generate_terms():
            v = _safe_values(term.fn, x)
            if v is None or float(np.std(v)) < 1e-12:
                continue
            usable_terms.append(term)
            values.append(v)
        if not values:
            raise RuntimeError("symbolic grammar produced no usable terms")
        return usable_terms, np.column_stack(values)

    def fit(self, xs: Iterable[float], ys: Iterable[float]) -> tuple[SynthesizedTheory, list[SynthesizedTheory]]:
        x = np.asarray(list(xs), dtype=float)
        y = np.asarray(list(ys), dtype=float)
        if len(x) < 6:
            raise ValueError("theory synthesis requires at least six observations")
        terms, A = self._matrix(x)
        means = A.mean(axis=0)
        stds = A.std(axis=0)
        Z = (A - means) / np.maximum(stds, 1e-12)

        candidates: list[SynthesizedTheory] = []

        def assemble(indices: list[int], beta: np.ndarray, rss: float) -> SynthesizedTheory:
            structural = sum(terms[j].complexity for j in indices)
            k = len(indices) + 1
            bic = len(y) * math.log(max(rss, 1e-20) / len(y)) + k * math.log(len(y)) + self.complexity_weight * structural
            chosen_terms = [terms[j] for j in indices]
            coeffs = [float(v) for v in beta[:-1]]
            intercept = float(beta[-1])

            def predictor(z, chosen_terms=tuple(chosen_terms), coeffs=tuple(coeffs), intercept=intercept):
                z = np.asarray(z, dtype=float)
                out = np.full(z.shape, intercept, dtype=float)
                for coeff, term in zip(coeffs, chosen_terms):
                    v = _safe_values(term.fn, z)
                    if v is None:
                        return np.full(z.shape, np.nan, dtype=float)
                    out = out + coeff * v
                return out

            pieces = []
            for coeff, term in zip(coeffs, chosen_terms):
                if abs(coeff) > 1e-10:
                    pieces.append(f"({_fmt_coeff(coeff)})*({term.expression})")
            if abs(intercept) > 1e-10 or not pieces:
                pieces.append(f"({_fmt_coeff(intercept)})")
            return SynthesizedTheory(
                expression=" + ".join(pieces),
                bic=float(bic),
                rss=float(rss),
                complexity=int(structural + len(indices)),
                term_expressions=[t.expression for t in chosen_terms],
                coefficients=coeffs,
                intercept=intercept,
                predict_fn=predictor,
            )

        index_by_expr = {term.expression: i for i, term in enumerate(terms)}
        for degree in range(1, min(self.max_degree, len(x) - 2) + 1):
            exprs = ["x" if d == 1 else f"x**{d}" for d in range(1, degree + 1)]
            if not all(e in index_by_expr for e in exprs):
                continue
            inds = [index_by_expr[e] for e in exprs]
            X = np.column_stack([A[:, inds], np.ones(len(y))])
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            pred = X @ beta
            rss = max(float(np.sum((y - pred) ** 2)), 1e-20)
            candidates.append(assemble(inds, beta, rss))

        selected: list[int] = []
        pred = np.full(len(y), float(np.mean(y)), dtype=float)
        max_terms = min(self.max_terms, max(1, len(x) - 2))
        for _ in range(max_terms):
            residual = y - pred
            correlation = np.abs(Z.T @ residual)
            if selected:
                correlation[np.array(selected, dtype=int)] = -np.inf
            finite = np.where(np.isfinite(correlation))[0]
            if len(finite) == 0:
                break
            order = finite[np.argsort(correlation[finite])]
            trial_indices = order[-min(self.trial_width, len(order)):]

            best_trial = None
            for idx in trial_indices:
                inds = selected + [int(idx)]
                X = np.column_stack([A[:, inds], np.ones(len(y))])
                beta, *_ = np.linalg.lstsq(X, y, rcond=None)
                p = X @ beta
                rss = max(float(np.sum((y - p) ** 2)), 1e-20)
                structural = sum(terms[j].complexity for j in inds)
                bic = len(y) * math.log(rss / len(y)) + (len(inds) + 1) * math.log(len(y)) + self.complexity_weight * structural
                if best_trial is None or bic < best_trial[0]:
                    best_trial = (bic, int(idx))
            if best_trial is None:
                break

            selected.append(best_trial[1])
            X = np.column_stack([A[:, selected], np.ones(len(y))])
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            pred = X @ beta
            rss = max(float(np.sum((y - pred) ** 2)), 1e-20)
            candidates.append(assemble(selected.copy(), beta, rss))

        if not candidates:
            raise RuntimeError("theory synthesis produced no candidate")
        unique = {}
        for theory in candidates:
            old = unique.get(theory.expression)
            if old is None or theory.bic < old.bic:
                unique[theory.expression] = theory
        candidates = sorted(unique.values(), key=lambda t: t.bic)
        return candidates[0], candidates
