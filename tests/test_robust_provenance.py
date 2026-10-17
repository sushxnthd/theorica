from fractions import Fraction

from theorica.agents.robust_provenance import (
    deterministic_tv_frontier,
    robust_provenance_frontier,
    sample_robust_randomized_plan,
    synthesize_robust_randomized_plan,
)


def test_exact_deterministic_tv_law():
    assert deterministic_tv_frontier((9, 5, 4, 3, 2, 1), 2, Fraction(1, 10)) == Fraction(13, 20)


def test_uniform_prior_forces_randomization_under_uncertainty():
    result = robust_provenance_frontier((1, 1, 1, 1, 1), 1, Fraction(1, 10))
    assert result.deterministic_value == Fraction(3, 10)
    assert abs(result.randomized_value - 0.4) < 1e-9
    assert not result.deterministic_plan_minimax
    assert result.action == "use_certified_randomized_plan"


def test_zero_radius_recovers_nominal_frontier():
    result = robust_provenance_frontier((8, 4, 2, 1), 1, Fraction(0))
    assert result.deterministic_value == Fraction(4, 5)
    assert abs(result.randomized_value - 0.8) < 1e-9
    assert result.deterministic_plan_minimax


def test_full_coverage_has_no_total_variation_penalty():
    result = robust_provenance_frontier((3, 2, 1), 2, Fraction(1, 4))
    assert result.deterministic_value == 1
    assert abs(result.randomized_value - 1.0) < 1e-9
    assert result.deterministic_plan_minimax
    assert result.action == "use_deterministic_top_mass"


def test_synthesized_uniform_mixture_hits_exact_robust_value():
    plan = synthesize_robust_randomized_plan((1, 1, 1, 1, 1), 1, Fraction(1, 10))
    assert plan.certificate_valid
    assert abs(plan.frontier_value - 0.4) < 1e-9
    assert abs(plan.certified_worst_case_payoff - 0.4) < 1e-9
    assert all(abs(value - 0.4) < 1e-9 for value in plan.inclusion_probabilities)


def test_seed_bound_sampling_is_reproducible_and_executable():
    plan = synthesize_robust_randomized_plan((9, 5, 4, 3, 2, 1), 2, Fraction(1, 10))
    first = sample_robust_randomized_plan(plan, "receipt-17")
    second = sample_robust_randomized_plan(plan, "receipt-17")
    assert first == second
    assert first.covered_labels in {component.covered_labels for component in plan.mixture}
    assert len(first.query_order) == 2
    assert first.terminal_guess not in first.query_order

