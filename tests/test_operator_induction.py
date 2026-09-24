import numpy as np

from theorica.agents.operator_induction import CrossFittedSpectralClosure
from theorica.agents.symbolic_synthesis import CompositionalTheorySynthesizer


def _nrmse(pred, truth):
    pred = np.asarray(pred, float)
    truth = np.asarray(truth, float)
    span = np.quantile(truth, 0.95) - np.quantile(truth, 0.05)
    return float(np.sqrt(np.mean((pred - truth) ** 2)) / max(span, 1e-12))


def test_spectral_closure_recovers_unseen_frequency():
    rng = np.random.default_rng(7)
    x = np.linspace(-2.0, 2.0, 40)
    omega = 3.73
    y_clean = 1.2 * np.sin(omega * x + 0.47) + 0.21 * x - 0.13
    y = y_clean + rng.normal(0.0, 0.01 * np.std(y_clean), size=len(x))

    baseline, _ = CompositionalTheorySynthesizer(trial_width=200).fit(x, y)
    theory, diagnostic = CrossFittedSpectralClosure().fit(x, y)

    grid = np.linspace(-2.5, 2.5, 401)
    truth = 1.2 * np.sin(omega * grid + 0.47) + 0.21 * grid - 0.13

    assert diagnostic.expanded
    assert abs(diagnostic.omega - omega) < 0.05
    assert _nrmse(theory.predict(grid), truth) < 0.01
    assert _nrmse(theory.predict(grid), truth) < _nrmse(baseline.predict(grid), truth)


def test_exact_cubic_does_not_force_expansion():
    x = np.linspace(-2.0, 2.0, 40)
    y = 0.4 * x**3 - 0.2 * x + 1.0

    theory, diagnostic = CrossFittedSpectralClosure().fit(x, y)
    assert not diagnostic.expanded
    assert np.sqrt(np.mean((theory.predict(x) - y) ** 2)) < 1e-8
