from fractions import Fraction

from theorica.agents.robust_provenance import (
    deterministic_tv_frontier,
    robust_provenance_frontier,
)


def test_exact_deterministic_tv_law():
    assert deterministic_tv_frontier((9, 5, 4, 3, 2, 1), 2, Fraction(1, 10)) == Fraction(13, 20)


def test_uniform_prior_forces_randomization_under_uncertainty():
    result = robust_provenance_frontier((1, 1, 1, 1, 1), 1, Fraction(1, 10))
    assert result.deterministic_value == Fraction(3, 10)
    assert abs(result.randomized_value - 0.4) < 1e-9
    assert not result.deterministic_plan_minimax
    assert result.action == "refuse_dominated_deterministic_plan"


def test_zero_radius_recovers_nominal_frontier():
    result = robust_provenance_frontier((8, 4, 2, 1), 1, Fraction(0))
    assert result.deterministic_value == Fraction(4, 5)
    assert abs(result.randomized_value - 0.8) < 1e-9
    assert result.deterministic_plan_minimax

