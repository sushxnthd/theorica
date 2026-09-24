import math

from theorica.agents.anytime_falsification import AnytimeRepresentationFalsifier


def test_log_e_increment_matches_simple_gaussian_lr_when_epsilon_zero():
    y, f, g, sigma = 1.2, 0.8, 1.1, 0.2
    got = AnytimeRepresentationFalsifier._log_e_increment(
        y, f, g, sigma, 0.0
    )
    expected = ((y - f) ** 2 - (y - g) ** 2) / (2 * sigma**2)
    assert abs(got - expected) < 1e-12


def test_composite_null_band_uses_closest_null_mean():
    y, f, g, sigma, epsilon = 1.3, 1.0, 1.25, 0.1, 0.2
    got = AnytimeRepresentationFalsifier._log_e_increment(
        y, f, g, sigma, epsilon
    )
    distance = max(abs(y - f) - epsilon, 0.0)
    expected = (distance**2 - (y - g) ** 2) / (2 * sigma**2)
    assert abs(got - expected) < 1e-12


def test_rejection_threshold_is_log_inverse_alpha():
    alpha = 0.01
    assert abs(math.log(1 / alpha) - math.log(100.0)) < 1e-12
