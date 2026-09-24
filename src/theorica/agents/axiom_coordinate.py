from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

import numpy as np
import sympy as sp


@dataclass
class AxiomDiagnostics:
    comm_median: float
    comm_p95: float
    assoc_median: float
    assoc_p95: float
    closure_rate: float
    assoc_samples: int


@dataclass
class CoordinateDiscovery:
    accepted: bool
    diagnostics: AxiomDiagnostics
    knots: np.ndarray | None = None
    generator: np.ndarray | None = None
    derivative_expression: str | None = None
    coordinate_expression: str | None = None
    derivative_degree_num: int | None = None
    derivative_degree_den: int | None = None


def _interp_weights(x: np.ndarray, knots: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    idx = np.searchsorted(knots, x, side="right") - 1
    idx = np.clip(idx, 0, len(knots) - 2)
    t = (x - knots[idx]) / np.maximum(knots[idx + 1] - knots[idx], 1e-15)
    W = np.zeros((len(x), len(knots)), dtype=float)
    rows = np.arange(len(x))
    W[rows, idx] = 1.0 - t
    W[rows, idx + 1] = t
    return W


def diagnose_operation(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    seed: int = 0,
    n: int = 300,
) -> AxiomDiagnostics:
    """Probe a black-box binary operation for commutativity and associativity.

    No formula is inspected. All diagnostics are based on oracle calls.
    """
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    rng = np.random.default_rng(seed)

    comm = []
    closure = 0
    for a, b in rng.uniform(lo, hi, size=(n, 2)):
        try:
            ab = float(oracle(float(a), float(b)))
            ba = float(oracle(float(b), float(a)))
        except Exception:
            continue
        if np.isfinite(ab) and lo <= ab <= hi:
            closure += 1
        if np.isfinite(ab) and np.isfinite(ba):
            comm.append(abs(ab - ba) / span)

    assoc = []
    attempts = 0
    while len(assoc) < n and attempts < 30 * n:
        a, b, c = rng.uniform(lo, hi, size=3)
        attempts += 1
        try:
            ab = float(oracle(float(a), float(b)))
            bc = float(oracle(float(b), float(c)))
            if not (lo <= ab <= hi and lo <= bc <= hi):
                continue
            left = float(oracle(ab, float(c)))
            right = float(oracle(float(a), bc))
        except Exception:
            continue
        if np.isfinite(left) and np.isfinite(right):
            assoc.append(abs(left - right) / span)

    def med(v):
        return float(np.median(v)) if v else float("inf")

    def p95(v):
        return float(np.quantile(v, 0.95)) if v else float("inf")

    return AxiomDiagnostics(
        comm_median=med(comm),
        comm_p95=p95(comm),
        assoc_median=med(assoc),
        assoc_p95=p95(assoc),
        closure_rate=float(closure / max(n, 1)),
        assoc_samples=len(assoc),
    )


def sample_operation(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    n: int = 200,
    seed: int = 1,
    noise_fraction: float = 0.0,
) -> np.ndarray:
    lo, hi = map(float, domain)
    span = hi - lo
    rng = np.random.default_rng(seed)
    rows: list[tuple[float, float, float]] = []
    attempts = 0
    while len(rows) < n and attempts < 100 * n:
        a, b = rng.uniform(lo, hi, size=2)
        attempts += 1
        try:
            z = float(oracle(float(a), float(b)))
        except Exception:
            continue
        if not (np.isfinite(z) and lo <= z <= hi):
            continue
        if noise_fraction > 0:
            z += float(rng.normal(0.0, noise_fraction * span))
        if lo <= z <= hi:
            rows.append((float(a), float(b), float(z)))
    if len(rows) < max(20, n // 2):
        raise RuntimeError("too few valid operation samples inside the stated domain")
    return np.asarray(rows, dtype=float)


def learn_additive_coordinate(
    samples: np.ndarray,
    domain: tuple[float, float],
    *,
    n_knots: int = 101,
    smoothness: float = 10.0,
    anchor_fraction: float = 0.68,
) -> tuple[np.ndarray, np.ndarray]:
    """Learn g such that g(F(x,y)) ~= g(x)+g(y).

    g is represented nonparametrically as a piecewise-linear function. The
    constraints are linear in knot values. A single anchor fixes the otherwise
    irrelevant multiplicative scale.
    """
    samples = np.asarray(samples, dtype=float)
    lo, hi = map(float, domain)
    knots = np.linspace(lo, hi, int(n_knots))
    Wx = _interp_weights(samples[:, 0], knots)
    Wy = _interp_weights(samples[:, 1], knots)
    Wz = _interp_weights(samples[:, 2], knots)
    A = Wz - Wx - Wy

    D = np.zeros((len(knots) - 2, len(knots)), dtype=float)
    for i in range(len(knots) - 2):
        D[i, i] = 1.0
        D[i, i + 1] = -2.0
        D[i, i + 2] = 1.0

    anchor = lo + float(anchor_fraction) * (hi - lo)
    Wa = _interp_weights(np.asarray([anchor]), knots)

    design = np.vstack([A, np.sqrt(float(smoothness)) * D, 100.0 * Wa])
    target = np.concatenate(
        [np.zeros(len(samples)), np.zeros(len(D)), np.asarray([100.0])]
    )
    g, *_ = np.linalg.lstsq(design, target, rcond=None)

    # Orientation is arbitrary. Choose increasing orientation when possible.
    if np.corrcoef(knots, g)[0, 1] < 0:
        g = -g
    return knots, np.asarray(g, dtype=float)


def predict_from_coordinate(
    x: float | np.ndarray,
    y: float | np.ndarray,
    knots: np.ndarray,
    generator: np.ndarray,
) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    gx = np.interp(x, knots, generator)
    gy = np.interp(y, knots, generator)
    target = gx + gy

    order = np.argsort(generator)
    return np.interp(target, generator[order], knots[order])


def fit_rational_derivative(
    knots: np.ndarray,
    generator: np.ndarray,
    *,
    max_degree: int = 3,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Compress the discovered coordinate through g'(x)=P(x)/Q(x).

    Uses homogeneous total least squares so either polynomial may have zero
    constant term. Model degree is chosen by a BIC-like fit/complexity score.
    """
    knots = np.asarray(knots, dtype=float)
    generator = np.asarray(generator, dtype=float)
    derivative = np.gradient(generator, knots)
    X = knots[3:-3]
    Y = derivative[3:-3]

    best = None
    for m in range(max_degree + 1):
        for n in range(max_degree + 1):
            M = np.column_stack(
                [-(X**j) for j in range(m + 1)]
                + [Y * (X**j) for j in range(n + 1)]
            )
            _, _, Vt = np.linalg.svd(M, full_matrices=False)
            vec = Vt[-1]
            p = vec[: m + 1]
            q = vec[m + 1 :]
            if np.linalg.norm(q) < 1e-10:
                continue
            scale = q[int(np.argmax(np.abs(q)))]
            p = p / scale
            q = q / scale
            den = sum(q[j] * X**j for j in range(n + 1))
            if float(np.min(np.abs(den))) < 1e-4:
                continue
            pred = sum(p[j] * X**j for j in range(m + 1)) / den
            rss = float(np.sum((Y - pred) ** 2))
            k = m + n + 1
            score = (
                len(Y) * np.log(max(rss / len(Y), 1e-24))
                + k * np.log(len(Y))
                + 5.0 * (m + n)
            )
            if best is None or score < best[0]:
                best = (score, p.copy(), q.copy(), m, n)

    if best is None:
        raise RuntimeError("no stable rational derivative model found")
    _, p, q, m, n = best
    return p, q, int(m), int(n)


def symbolic_coordinate_from_rational(
    numerator: np.ndarray,
    denominator: np.ndarray,
    *,
    zero_tolerance: float = 0.03,
    max_denominator: int = 20,
) -> tuple[str, str]:
    """Return a scale-free rational derivative and its symbolic integral.

    The additive coordinate is only identifiable up to multiplication by a
    nonzero constant, so numerator and denominator shapes can be normalized
    independently before rationalization.
    """
    numerator = np.asarray(numerator, dtype=float).copy()
    denominator = np.asarray(denominator, dtype=float).copy()
    numerator /= max(float(np.max(np.abs(numerator))), 1e-15)
    denominator /= max(float(np.max(np.abs(denominator))), 1e-15)

    def rationalize(v: float):
        if abs(v) < zero_tolerance:
            return sp.Integer(0)
        return sp.Rational(Fraction(float(v)).limit_denominator(max_denominator))

    x = sp.Symbol("x", real=True)
    P = sum(rationalize(v) * x**j for j, v in enumerate(numerator))
    Q = sum(rationalize(v) * x**j for j, v in enumerate(denominator))
    derivative = sp.cancel(P / Q)
    coordinate = sp.simplify(sp.integrate(derivative, x))
    return str(derivative), str(coordinate)


def discover_coordinate(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    seed: int = 0,
    n_diagnostic: int = 300,
    n_samples: int = 200,
    noise_fraction: float = 0.0,
    axiom_tolerance: float = 1e-6,
    smoothness: float = 1e-4,
) -> CoordinateDiscovery:
    """Blind black-box path: axioms -> latent coordinate -> symbolic coordinate."""
    diagnostics = diagnose_operation(
        oracle, domain, seed=seed, n=n_diagnostic
    )
    accepted = bool(
        diagnostics.comm_p95 <= axiom_tolerance
        and diagnostics.assoc_p95 <= axiom_tolerance
        and diagnostics.assoc_samples >= max(30, n_diagnostic // 3)
    )
    if not accepted:
        return CoordinateDiscovery(accepted=False, diagnostics=diagnostics)

    samples = sample_operation(
        oracle,
        domain,
        n=n_samples,
        seed=seed + 1,
        noise_fraction=noise_fraction,
    )
    knots, generator = learn_additive_coordinate(
        samples, domain, smoothness=smoothness
    )
    p, q, m, n = fit_rational_derivative(knots, generator)
    derivative, coordinate = symbolic_coordinate_from_rational(p, q)
    return CoordinateDiscovery(
        accepted=True,
        diagnostics=diagnostics,
        knots=knots,
        generator=generator,
        derivative_expression=derivative,
        coordinate_expression=coordinate,
        derivative_degree_num=m,
        derivative_degree_den=n,
    )
