import numpy as np
import sympy as sp

from theorica.agents.axiom_coordinate import (
    diagnose_operation,
    discover_coordinate,
    predict_from_coordinate,
)


def _equiv_derivative(expr: str, target: str):
    x = sp.Symbol("x", real=True)
    a = sp.sympify(expr, locals={"x": x})
    b = sp.sympify(target, locals={"x": x})
    ratio = sp.simplify(a / b)
    return not ratio.has(x)


def test_rejects_nonassociative_mean():
    F = lambda x, y: (x + y) / 2.0
    d = diagnose_operation(F, (-1.0, 1.0), seed=3)
    assert d.comm_p95 < 1e-12
    assert d.assoc_p95 > 1e-3
    result = discover_coordinate(F, (-1.0, 1.0), seed=3)
    assert not result.accepted


def test_rediscovers_multiplicative_log_coordinate():
    F = lambda x, y: x * y
    result = discover_coordinate(F, (0.2, 3.0), seed=4, n_samples=240)
    assert result.accepted
    assert _equiv_derivative(result.derivative_expression, "1/x")


def test_rediscovers_relativistic_rapidity_coordinate():
    F = lambda u, v: (u + v) / (1.0 + u * v)
    result = discover_coordinate(F, (-0.85, 0.85), seed=5, n_samples=240)
    assert result.accepted
    assert _equiv_derivative(result.derivative_expression, "1/(1-x**2)")

    rng = np.random.default_rng(6)
    errs = []
    for _ in range(300):
        u, v = rng.uniform(-0.7, 0.7, size=2)
        truth = F(u, v)
        pred = float(
            predict_from_coordinate(
                u, v, result.knots, result.generator
            )
        )
        errs.append((truth - pred) ** 2)
    assert np.sqrt(np.mean(errs)) < 2e-3
