from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import cumulative_trapezoid

from theorica.agents.axiom_coordinate import (
    diagnose_operation,
    discover_coordinate,
    fit_rational_derivative,
    learn_additive_coordinate,
    predict_from_coordinate,
    sample_operation,
)


def _poly_features(X, degree=6):
    X = np.asarray(X, dtype=float)
    x = X[:, 0]
    y = X[:, 1]
    cols = []
    for d in range(degree + 1):
        for i in range(d + 1):
            j = d - i
            cols.append((x**i) * (y**j))
    return np.column_stack(cols)


def _fit_poly(samples, degree=6):
    D = _poly_features(samples[:, :2], degree)
    beta, *_ = np.linalg.lstsq(D, samples[:, 2], rcond=None)
    return beta


def _predict_poly(beta, X, degree=6):
    return _poly_features(np.asarray(X, dtype=float), degree) @ beta


def _sample_with_noise(oracle, domain, n, seed, noise_fraction):
    lo, hi = domain
    span = hi - lo
    rng = np.random.default_rng(seed)
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 100 * n:
        a, b = rng.uniform(lo, hi, size=2)
        attempts += 1
        z = float(oracle(float(a), float(b)))
        if not (np.isfinite(z) and lo <= z <= hi):
            continue
        z = z + float(rng.normal(0.0, noise_fraction * span))
        if lo <= z <= hi:
            rows.append((a, b, z))
    return np.asarray(rows, dtype=float)


def _make_hidden_world(seed):
    rng = np.random.default_rng(seed)
    lo, hi = -0.8, 0.8
    grid = np.linspace(lo, hi, 4001)

    for _ in range(100):
        b = float(rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0]))
        c = float(rng.choice([-1.0, -0.5, 0.5, 1.0, 1.5]))
        den = 1.0 + b * grid + c * grid**2
        if float(np.min(den)) > 0.25:
            break

    kind = int(rng.integers(0, 3))
    if kind == 0:
        num = np.ones_like(grid)
    elif kind == 1:
        p = float(rng.choice([-0.5, 0.5]))
        num = 1.0 + p * grid
        if float(np.min(num)) <= 0.2:
            num = np.ones_like(grid)
    else:
        q = float(rng.choice([0.5, 1.0, 1.5]))
        num = 1.0 + q * grid**2

    derivative = num / den
    generator = cumulative_trapezoid(derivative, grid, initial=0.0)
    generator = generator - np.interp(0.0, grid, generator)

    def oracle(x, y):
        gx = np.interp(x, grid, generator)
        gy = np.interp(y, grid, generator)
        target = gx + gy
        if target < generator[0] or target > generator[-1]:
            return np.nan
        return float(np.interp(target, generator, grid))

    return oracle, (lo, hi), grid, derivative


def _derivative_shape_error(p, q, grid, truth):
    pred = sum(p[j] * grid**j for j in range(len(p))) / sum(
        q[j] * grid**j for j in range(len(q))
    )
    scale = float(np.dot(pred, truth) / np.dot(pred, pred))
    rmse = float(np.sqrt(np.mean((scale * pred - truth) ** 2)))
    denom = max(float(np.std(truth)), float(np.mean(np.abs(truth))), 1e-12)
    return rmse / denom


def _operation_error(oracle, domain, knots, generator, seed, n=400):
    lo, hi = domain
    rng = np.random.default_rng(seed)
    err = []
    attempts = 0
    while len(err) < n and attempts < 50 * n:
        a, b = rng.uniform(lo, hi, size=2)
        attempts += 1
        z = float(oracle(float(a), float(b)))
        if not (np.isfinite(z) and lo <= z <= hi):
            continue
        pred = float(predict_from_coordinate(a, b, knots, generator))
        err.append((pred - z) ** 2)
    return float(np.sqrt(np.mean(err)) / (hi - lo))


def _canonical():
    x = sp.Symbol("x", real=True)
    worlds = [
        (
            "multiplication",
            lambda a, b: a * b,
            (0.2, 3.0),
            sp.sympify("1/x", locals={"x": x}),
        ),
        (
            "relativistic_velocity",
            lambda a, b: (a + b) / (1.0 + a * b),
            (-0.85, 0.85),
            sp.sympify("1/(1-x**2)", locals={"x": x}),
        ),
        (
            "probabilistic_or",
            lambda a, b: a + b - a * b,
            (0.0, 0.85),
            sp.sympify("1/(1-x)", locals={"x": x}),
        ),
        (
            "parallel_harmonic",
            lambda a, b: a * b / (a + b),
            (0.2, 3.0),
            sp.sympify("1/x**2", locals={"x": x}),
        ),
        (
            "p3_addition",
            lambda a, b: np.cbrt(a**3 + b**3),
            (0.0, 1.2),
            sp.sympify("x**2", locals={"x": x}),
        ),
    ]

    out = []
    for i, (name, oracle, domain, target) in enumerate(worlds):
        result = discover_coordinate(
            oracle, domain, seed=100 + i, n_samples=240
        )
        got = sp.sympify(result.derivative_expression, locals={"x": x})
        ratio = sp.simplify(got / target)
        shape_ok = bool(not ratio.has(x))
        out.append(
            {
                "name": name,
                "accepted": result.accepted,
                "derivative_expression": result.derivative_expression,
                "coordinate_expression": result.coordinate_expression,
                "shape_recovered": shape_ok,
            }
        )

    controls = [
        ("arithmetic_mean", lambda a, b: (a + b) / 2.0, (-1.0, 1.0)),
        ("subtraction", lambda a, b: a - b, (-1.0, 1.0)),
        ("quadratic_sum", lambda a, b: a + b + 0.2 * a * b**2, (-0.7, 0.7)),
    ]
    control_out = []
    for i, (name, oracle, domain) in enumerate(controls):
        diag = diagnose_operation(oracle, domain, seed=300 + i)
        accepted = bool(diag.comm_p95 <= 1e-6 and diag.assoc_p95 <= 1e-6)
        control_out.append(
            {
                "name": name,
                "accepted": accepted,
                "comm_p95": diag.comm_p95,
                "assoc_p95": diag.assoc_p95,
            }
        )

    return out, control_out


def run():
    canonical, controls = _canonical()

    derivative_errors = []
    coordinate_errors = []
    polynomial_errors = []
    paired_wins = 0
    records = []

    for seed in range(1000, 1050):
        oracle, domain, grid, true_derivative = _make_hidden_world(seed)
        lo, hi = domain
        samples = _sample_with_noise(
            oracle, domain, n=200, seed=seed + 10000, noise_fraction=0.001
        )

        knots, generator = learn_additive_coordinate(
            samples, domain, n_knots=101, smoothness=10.0
        )
        p, q, m, n = fit_rational_derivative(knots, generator, max_degree=3)

        interior = slice(100, -100)
        derr = _derivative_shape_error(
            p,
            q,
            grid[interior],
            true_derivative[interior],
        )
        cerr = _operation_error(
            oracle, domain, knots, generator, seed=seed + 20000
        )

        beta = _fit_poly(samples, degree=6)
        rng = np.random.default_rng(seed + 30000)
        pairs = []
        truth = []
        attempts = 0
        while len(truth) < 400 and attempts < 20000:
            a, b = rng.uniform(lo, hi, size=2)
            attempts += 1
            z = float(oracle(float(a), float(b)))
            if np.isfinite(z) and lo <= z <= hi:
                pairs.append((a, b))
                truth.append(z)
        pairs = np.asarray(pairs)
        truth = np.asarray(truth)
        poly_pred = _predict_poly(beta, pairs, degree=6)
        perr = float(
            np.sqrt(np.mean((poly_pred - truth) ** 2)) / (hi - lo)
        )

        derivative_errors.append(derr)
        coordinate_errors.append(cerr)
        polynomial_errors.append(perr)
        paired_wins += int(cerr < perr)
        records.append(
            {
                "seed": seed,
                "derivative_shape_error": derr,
                "coordinate_operation_error": cerr,
                "degree6_polynomial_error": perr,
                "rational_degree": [m, n],
            }
        )

    summary = {
        "canonical_axiom_worlds_accepted": int(
            sum(r["accepted"] for r in canonical)
        ),
        "canonical_symbolic_coordinates_recovered": int(
            sum(r["shape_recovered"] for r in canonical)
        ),
        "negative_controls_rejected": int(
            sum(not r["accepted"] for r in controls)
        ),
        "hidden_worlds": 50,
        "hidden_world_successes": int(
            sum(
                d < 0.10 and c < 0.01
                for d, c in zip(derivative_errors, coordinate_errors)
            )
        ),
        "median_derivative_shape_error": float(np.median(derivative_errors)),
        "p90_derivative_shape_error": float(
            np.quantile(derivative_errors, 0.90)
        ),
        "max_derivative_shape_error": float(np.max(derivative_errors)),
        "median_coordinate_operation_error": float(
            np.median(coordinate_errors)
        ),
        "p90_coordinate_operation_error": float(
            np.quantile(coordinate_errors, 0.90)
        ),
        "median_degree6_polynomial_error": float(
            np.median(polynomial_errors)
        ),
        "coordinate_wins_vs_degree6_polynomial": int(paired_wins),
    }

    payload = {
        "experiment": "THEORICA blind axiom-to-coordinate discovery",
        "date": "2026-09-24",
        "canonical": canonical,
        "negative_controls": controls,
        "hidden_world_design": {
            "seeds": [1000, 1049],
            "training_samples_per_world": 200,
            "measurement_noise_fraction_of_domain": 0.001,
            "hidden_generator_derivative": "random rational P(x)/Q(x), degree <= 2",
            "agent_rational_derivative_max_degree": 3,
            "baseline": "direct bivariate polynomial regression, total degree 6",
        },
        "summary": summary,
        "records": records,
    }

    Path("results/axiom_coordinate_holdout.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    assert summary["canonical_axiom_worlds_accepted"] == 5
    assert summary["canonical_symbolic_coordinates_recovered"] == 5
    assert summary["negative_controls_rejected"] == 3
    assert summary["hidden_world_successes"] == 50
    assert summary["median_derivative_shape_error"] < 0.03
    assert summary["median_coordinate_operation_error"] < 0.001
    assert summary["coordinate_wins_vs_degree6_polynomial"] >= 45


if __name__ == "__main__":
    run()
