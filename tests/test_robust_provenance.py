from fractions import Fraction
from itertools import combinations

import pytest

from theorica.agents.robust_provenance import (
    deterministic_strictly_dominated,
    deterministic_tv_frontier,
    divergence_agnostic_symmetry_value,
    robust_provenance_frontier,
    sample_orbit_balanced_plan,
    sample_orbit_mixture_plan,
    sample_robust_randomized_plan,
    sample_uniform_ambiguity_plan,
    synthesize_orbit_balanced_plan,
    synthesize_orbit_mixture_plan,
    synthesize_robust_randomized_plan,
    synthesize_uniform_ambiguity_plan,
    unrank_uniform_k_subset,
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


@pytest.mark.parametrize("n,q", [(2, 0), (5, 1), (7, 5), (8, 7)])
def test_divergence_agnostic_value_is_exact(n, q):
    assert divergence_agnostic_symmetry_value(n, q, uniform_prior_in_set=True) == Fraction(q + 1, n)


def test_uniform_certificate_is_required():
    with pytest.raises(ValueError, match="uniform lies"):
        divergence_agnostic_symmetry_value(5, 1, uniform_prior_in_set=False)


def test_strict_domination_certificate():
    assert deterministic_strictly_dominated(Fraction(1, 3), 6, 2, uniform_prior_in_set=True)
    assert not deterministic_strictly_dominated(Fraction(1, 2), 6, 2, uniform_prior_in_set=True)
    assert not deterministic_strictly_dominated(Fraction(1), 6, 5, uniform_prior_in_set=True)


def test_exact_subset_unranking_matches_lexicographic_combinations():
    expected = list(combinations(range(6), 3))
    observed = [unrank_uniform_k_subset(6, 3, rank) for rank in range(len(expected))]
    assert observed == expected


def test_compact_uniform_plan_and_sampling():
    plan = synthesize_uniform_ambiguity_plan(9, 2, ambiguity_kind="test-family", uniform_prior_in_set=True)
    assert plan.covered_labels == 3
    assert plan.minimax_value == Fraction(1, 3)
    first = sample_uniform_ambiguity_plan(plan, "symmetry-seed")
    second = sample_uniform_ambiguity_plan(plan, "symmetry-seed")
    assert first == second
    assert len(first.covered_labels) == 3
    assert len(first.query_order) == 2
    assert first.terminal_guess not in first.query_order


def _cyclic_action(n):
    return tuple(tuple((i + shift) % n for i in range(n)) for shift in range(n))


def _product_action(left, right):
    return tuple(
        tuple(
            (i + a) % left if i < left else left + (i - left + b) % right
            for i in range(left + right)
        )
        for a in range(left) for b in range(right)
    )


def test_transitive_orbit_plan_is_exactly_balanced_and_compressed():
    plan = synthesize_orbit_balanced_plan(
        9, 2, (0, 1, 2), _cyclic_action(9),
        ambiguity_kind="cyclic-window", uniform_prior_in_set=True,
    )
    assert plan.certificate_valid and plan.balanced
    assert plan.universal_minimax_value == Fraction(1, 3)
    assert plan.inclusion_probabilities == (Fraction(1, 3),) * 9
    assert len(plan.query_orbit) == 9


def test_intransitive_balance_boundary_is_exact():
    group = _product_action(3, 3)
    balanced = synthesize_orbit_balanced_plan(
        6, 1, (0, 3), group, ambiguity_kind="two-orbits", uniform_prior_in_set=True,
    )
    unbalanced = synthesize_orbit_balanced_plan(
        6, 1, (0, 1), group, ambiguity_kind="two-orbits", uniform_prior_in_set=True,
    )
    assert balanced.balanced and balanced.orbit_balance_ratios == (Fraction(1, 3), Fraction(1, 3))
    assert not unbalanced.balanced
    assert unbalanced.universal_minimax_value is None
    assert unbalanced.orbit_balance_ratios == (Fraction(2, 3), Fraction(0))
    assert unbalanced.full_simplex_value == 0


def test_orbit_sampler_is_reproducible_and_executable():
    plan = synthesize_orbit_balanced_plan(
        8, 2, (0, 1, 2), _cyclic_action(8),
        ambiguity_kind="cyclic-window", uniform_prior_in_set=True,
    )
    first = sample_orbit_balanced_plan(plan, "orbit-receipt")
    second = sample_orbit_balanced_plan(plan, "orbit-receipt")
    assert first == second
    assert first.covered_labels in plan.query_orbit
    assert len(first.query_order) == 2


def test_orbit_planner_rejects_non_group_and_unbalanced_sampling():
    with pytest.raises(ValueError, match="closed"):
        synthesize_orbit_balanced_plan(
            4, 1, (0, 1), ((0, 1, 2, 3), (1, 2, 3, 0)),
            ambiguity_kind="invalid", uniform_prior_in_set=True,
        )
    plan = synthesize_orbit_balanced_plan(
        6, 1, (0, 1), _product_action(3, 3),
        ambiguity_kind="unbalanced", uniform_prior_in_set=True,
    )
    with pytest.raises(ValueError, match="balanced"):
        sample_orbit_balanced_plan(plan, "reject")


def test_sparse_orbit_mixture_repairs_integrality_obstruction():
    group = _product_action(3, 4)
    plan = synthesize_orbit_mixture_plan(
        7, 1, ((0, 3), (3, 4)), group,
        ambiguity_kind="two-orbit-repair", uniform_prior_in_set=True,
    )
    assert plan.feasible and plan.certificate_valid
    assert len(plan.components) == 2
    assert tuple(component.probability for component in plan.components) == (
        Fraction(6, 7), Fraction(1, 7),
    )
    assert plan.inclusion_probabilities == (Fraction(2, 7),) * 7
    assert all(component.orbit_composition != (Fraction(2, 7),) * 2
               for component in plan.components)
    assert sample_orbit_mixture_plan(plan, "mixture-receipt") == sample_orbit_mixture_plan(
        plan, "mixture-receipt",
    )


def test_orbit_mixture_exactly_refuses_one_sided_polytope():
    plan = synthesize_orbit_mixture_plan(
        7, 1, ((0, 3), (0, 1)), _product_action(3, 4),
        ambiguity_kind="infeasible", uniform_prior_in_set=True,
    )
    assert not plan.feasible and plan.certificate_valid
    assert plan.components == ()
    with pytest.raises(ValueError, match="feasible"):
        sample_orbit_mixture_plan(plan, "reject")
