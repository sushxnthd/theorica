import numpy as np
from scipy.special import airy

from theorica.agents.representation_closure import (
    RepresentationClosureScientist,
    WeakAnnihilatorSynthesizer,
    normalized_rmse,
)


def test_in_language_polynomial_stays_explicit():
    x = np.linspace(-1.5, 1.5, 81)
    y = 0.7 * x**4 - 0.2 * x**2 + 0.4 * x - 0.1
    result = RepresentationClosureScientist().fit(
        x, y, bounds=(-2.0, 2.0)
    )
    assert result.mode == "explicit"
    xt = np.linspace(-2.0, 2.0, 201)
    truth = 0.7 * xt**4 - 0.2 * xt**2 + 0.4 * xt - 0.1
    assert normalized_rmse(result.predict(xt), truth) < 1e-6


def test_operator_meta_grammar_has_no_named_special_functions():
    synth = WeakAnnihilatorSynthesizer()
    assert all(
        isinstance(order, int) and isinstance(power, int)
        for order, power in synth.terms
    )


def test_airy_can_trigger_operator_closure():
    rng = np.random.default_rng(3)
    x = np.linspace(-1.1, 1.1, 81)
    xt = np.linspace(-1.55, 1.55, 301)
    clean = airy(1.13 * x + 0.27)[0]
    y = clean + rng.normal(0.0, 0.002 * np.std(clean), size=len(x))
    result = RepresentationClosureScientist().fit(
        x, y, bounds=(float(xt.min()), float(xt.max()))
    )
    assert result.mode == "operator"
    truth = airy(1.13 * xt + 0.27)[0]
    assert normalized_rmse(result.predict(xt), truth) < 0.03
