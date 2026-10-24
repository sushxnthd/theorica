from dataclasses import replace
from fractions import Fraction
from itertools import combinations

import pytest

from theorica.agents.robust_provenance import (
    compress_rank_three_nature_certificate,
    deterministic_strictly_dominated,
    deterministic_tv_frontier,
    divergence_agnostic_symmetry_value,
    robust_provenance_frontier,
    sample_orbit_ambiguity_plan,
    sample_orbit_balanced_plan,
    sample_orbit_mixture_plan,
    sample_robust_randomized_plan,
    sample_uniform_ambiguity_plan,
    solve_two_action_robust_game,
    solve_two_by_two_robust_game,
    solve_two_vertex_robust_game,
    synthesize_additive_product_plan,
    synthesize_coupled_additive_plan,
    synthesize_fixed_scenario_additive_plan,
    synthesize_four_vertex_additive_plan,
    synthesize_orbit_ambiguity_plan,
    synthesize_orbit_balanced_plan,
    synthesize_orbit_mixture_plan,
    synthesize_rank_one_scenario_quotient_plan,
    synthesize_rank_three_scenario_polytope_plan,
    synthesize_rank_two_scenario_hull_plan,
    synthesize_robust_randomized_plan,
    synthesize_three_vertex_additive_plan,
    synthesize_two_vertex_additive_plan,
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


def test_orbit_quotient_frozen_strict_randomization_prediction():
    plan = synthesize_orbit_ambiguity_plan(
        7, 1, ((0, 1), (3, 4)), _product_action(3, 4),
        ((Fraction(3, 4), Fraction(1, 4)),
         (Fraction(1, 4), Fraction(3, 4))),
        ambiguity_kind="frozen-two-vertex",
        ambiguity_invariant=True,
    )
    assert plan.certificate_valid and plan.strict_randomization_advantage
    assert plan.minimax_value == Fraction(2, 7)
    assert plan.best_pure_value == Fraction(1, 6)
    assert plan.randomized_gain == Fraction(5, 42)
    by_composition = {
        component.orbit_composition: component.probability for component in plan.components
    }
    assert by_composition == {
        (Fraction(2, 3), Fraction(0)): Fraction(3, 7),
        (Fraction(0), Fraction(1, 2)): Fraction(4, 7),
    }
    assert sample_orbit_ambiguity_plan(plan, "quotient") == sample_orbit_ambiguity_plan(
        plan, "quotient",
    )
    # Canonical record/vertex sorting may exchange either axis; the protected
    # pairing certificate is permutation invariant.
    assert plan.reason == "two_by_two_anti_diagonal_certificate"


def test_two_by_two_protected_diagonal_formula():
    result = solve_two_by_two_robust_game((
        (Fraction(1, 2), Fraction(1, 6)),
        (Fraction(1, 8), Fraction(3, 8)),
    ))
    assert result.certificate_valid and result.strict_randomization_advantage
    assert result.protected_pairing == "diagonal"
    assert result.action_probabilities == (Fraction(3, 7), Fraction(4, 7))
    assert result.minimax_value == Fraction(2, 7)
    assert result.best_pure_value == Fraction(1, 6)
    assert result.randomized_gain == Fraction(5, 42)


def test_two_by_two_anti_diagonal_and_equality_boundaries():
    anti = solve_two_by_two_robust_game(((0, 1), (1, 0)))
    assert anti.certificate_valid and anti.protected_pairing == "anti_diagonal"
    assert anti.action_probabilities == (Fraction(1, 2), Fraction(1, 2))
    assert anti.minimax_value == Fraction(1, 2)
    boundary = solve_two_by_two_robust_game(((1, 0), (0, 0)))
    assert boundary.certificate_valid and not boundary.strict_randomization_advantage
    assert boundary.protected_pairing == "none"
    assert boundary.minimax_value == boundary.best_pure_value == 0


def test_two_by_two_rejects_wrong_shape():
    with pytest.raises(ValueError, match="exactly two"):
        solve_two_by_two_robust_game(((Fraction(1), Fraction(0)),))  # type: ignore[arg-type]


def test_two_action_supported_crossing_ignores_slack_vertex():
    result = solve_two_action_robust_game((
        (Fraction(1, 2), Fraction(1, 6), Fraction(1)),
        (Fraction(1, 8), Fraction(3, 8), Fraction(1)),
    ))
    assert result.certificate_valid and result.strict_randomization_advantage
    assert result.action_probabilities == (Fraction(3, 7), Fraction(4, 7))
    assert result.minimax_value == Fraction(2, 7)
    assert result.best_pure_value == Fraction(1, 6)
    assert result.supported_vertices == (0, 1)


def test_two_action_undercutting_vertex_kills_strict_advantage():
    result = solve_two_action_robust_game((
        (Fraction(1, 2), Fraction(1, 6), Fraction(0)),
        (Fraction(1, 8), Fraction(3, 8), Fraction(0)),
    ))
    assert result.certificate_valid and not result.strict_randomization_advantage
    assert result.minimax_value == result.best_pure_value == 0
    assert result.supported_vertices == ()


def test_two_action_rejects_ragged_or_empty_games():
    with pytest.raises(ValueError):
        solve_two_action_robust_game(((), ()))
    with pytest.raises(ValueError):
        solve_two_action_robust_game(((0, 1), (0,)))


def test_two_vertex_sparse_support_strict_witness_and_predictions():
    strict = solve_two_vertex_robust_game(((0, 2), (2, 0), (0, 0)))
    assert strict.certificate_valid and strict.strict_randomization_advantage
    assert strict.action_probabilities == (Fraction(1, 2), Fraction(1, 2), 0)
    assert strict.ambiguity_probabilities == (Fraction(1, 2), Fraction(1, 2))
    assert strict.supported_actions == (0, 1)
    assert strict.minimax_value == 1 and strict.best_pure_value == 0

    dominated = solve_two_vertex_robust_game(
        ((0, 2), (2, 0), (0, 0), (Fraction(1, 4), Fraction(1, 4)))
    )
    assert dominated.minimax_value == strict.minimax_value
    assert dominated.action_probabilities[:3] == strict.action_probabilities
    assert dominated.action_probabilities[3] == 0

    boundary = solve_two_vertex_robust_game(((0, 2), (2, 0), (0, 0), (1, 1)))
    assert boundary.certificate_valid and not boundary.strict_randomization_advantage
    assert boundary.supported_actions == (3,)
    assert boundary.minimax_value == 1

    overriding = solve_two_vertex_robust_game(
        ((0, 2), (2, 0), (0, 0), (Fraction(3, 2), Fraction(3, 2)))
    )
    assert overriding.certificate_valid and not overriding.strict_randomization_advantage
    assert overriding.supported_actions == (3,)
    assert overriding.minimax_value == Fraction(3, 2)


def test_two_vertex_rejects_ragged_or_empty_games():
    with pytest.raises(ValueError):
        solve_two_vertex_robust_game(())
    with pytest.raises(ValueError):
        solve_two_vertex_robust_game(((0, 1, 2),))


def test_additive_product_value_strictness_and_sparse_coupling():
    plan = synthesize_additive_product_plan(
        (
            ((0, 2), (2, 0)),
            ((0, 3), (3, 0)),
            ((1, 1), (0, 0)),
        ),
        payoff_additive_certified=True,
        ambiguity_rectangular_certified=True,
    )
    assert plan.certificate_valid and plan.strict_randomization_advantage
    assert plan.component_values == (1, Fraction(3, 2), 1)
    assert plan.minimax_value == Fraction(7, 2)
    assert plan.best_pure_value == 1
    assert len(plan.joint_components) == 2
    assert len(plan.joint_components) <= plan.support_bound == 3


def test_additive_product_uses_sum_not_product_support():
    plan = synthesize_additive_product_plan(
        tuple((((0, 2), (2, 0))) for _ in range(4)),
        payoff_additive_certified=True,
        ambiguity_rectangular_certified=True,
    )
    assert plan.certificate_valid and plan.minimax_value == 4
    assert len(plan.joint_components) == 2
    assert plan.support_bound == 5
    assert plan.expanded_action_count == plan.expanded_vertex_count == 16


def test_additive_product_fails_closed_without_structure_certificates():
    game = (((0, 1), (1, 0)),)
    with pytest.raises(ValueError, match="additive"):
        synthesize_additive_product_plan(
            game, payoff_additive_certified=False, ambiguity_rectangular_certified=True,
        )
    with pytest.raises(ValueError, match="rectangular"):
        synthesize_additive_product_plan(
            game, payoff_additive_certified=True, ambiguity_rectangular_certified=False,
        )



def test_coupled_additive_exact_correction_and_zero_bonus_boundary():
    crossing = ((0, 2), (2, 0))
    strict = synthesize_coupled_additive_plan(
        (crossing, crossing), ((0, 0),), payoff_additive_certified=True,
    )
    assert strict.certificate_valid
    assert strict.rectangular_baseline_value == 2
    assert strict.minimax_value == 4 and strict.coupling_bonus == 2
    assert not strict.rectangular_value_survives
    assert strict.zero_bonus_nature_witness == ()

    equality = synthesize_coupled_additive_plan(
        (crossing, crossing), ((0, 1), (1, 0)), payoff_additive_certified=True,
    )
    assert equality.certificate_valid
    assert equality.minimax_value == equality.rectangular_baseline_value == 2
    assert equality.rectangular_value_survives
    assert equality.zero_bonus_nature_witness == (Fraction(1, 2), Fraction(1, 2))
    assert len(equality.joint_components) <= equality.support_bound


def test_coupled_additive_policy_is_executable_on_three_factors():
    plan = synthesize_coupled_additive_plan(
        (((0, 2), (2, 0)), ((0, 3), (3, 0)), ((1, 1), (0, 0))),
        ((0, 0, 0), (1, 1, 1)), payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert sum(mass for _, mass in plan.joint_components) == 1
    assert len(plan.joint_components) <= plan.support_bound
    realized = tuple(
        sum(mass * sum(plan.component_payoff_matrices[t][actions[t]][vertex[t]]
                       for t in range(3))
            for actions, mass in plan.joint_components)
        for vertex in plan.ambiguity_vertices
    )
    assert min(realized) == plan.minimax_value


def test_coupled_additive_fails_closed_without_certified_structure():
    with pytest.raises(ValueError, match="additive"):
        synthesize_coupled_additive_plan(
            (((0, 1), (1, 0)),), ((0,),), payoff_additive_certified=False,
        )
    with pytest.raises(ValueError, match="unique"):
        synthesize_coupled_additive_plan(
            (((0, 1), (1, 0)),), ((0,), (0,)), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="outside"):
        synthesize_coupled_additive_plan(
            (((0, 1), (1, 0)),), ((2,),), payoff_additive_certified=True,
        )


def test_two_vertex_additive_envelope_detects_necessary_randomization():
    plan = synthesize_two_vertex_additive_plan(
        (((0, 2), (2, 0)), ((0, 3), (3, 0))),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == Fraction(5, 2)
    assert plan.nature_probability == Fraction(1, 2)
    assert plan.strict_randomization_necessary
    assert plan.pure_optimal_witness == ()
    assert len(plan.joint_actions) == plan.support_bound == 2
    assert plan.expanded_action_count == 4


def test_two_vertex_additive_envelope_returns_pure_zero_delta_witness():
    plan = synthesize_two_vertex_additive_plan(
        (((0, 2), (2, 0)), ((0, 2), (2, 0))),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == 2
    assert not plan.strict_randomization_necessary
    assert plan.pure_optimal_witness in ((0, 1), (1, 0))
    assert plan.joint_actions == ((plan.pure_optimal_witness, Fraction(1)),)


def test_two_vertex_additive_envelope_fails_closed():
    with pytest.raises(ValueError, match="additive"):
        synthesize_two_vertex_additive_plan(
            (((0, 1),),), payoff_additive_certified=False,
        )
    with pytest.raises(ValueError, match="two scenario"):
        synthesize_two_vertex_additive_plan(
            (((0, 1, 2),),), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="state limit"):
        synthesize_two_vertex_additive_plan(
            (((0, 2), (2, 0)), ((0, 3), (3, 0))),
            payoff_additive_certified=True, max_delta_states=1,
        )


def test_three_vertex_additive_arrangement_needs_three_way_randomization():
    plan = synthesize_three_vertex_additive_plan(
        (((2, 0, 0), (0, 2, 0), (0, 0, 2)),),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == Fraction(2, 3)
    assert plan.nature_probabilities == (Fraction(1, 3),) * 3
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 3
    assert tuple(mass for _, mass in plan.joint_actions) == (Fraction(1, 3),) * 3


def test_three_vertex_additive_arrangement_detects_two_and_one_support():
    two = synthesize_three_vertex_additive_plan(
        (((2, 0, 1), (0, 2, 1)),), payoff_additive_certified=True,
    )
    assert two.certificate_valid and two.minimax_value == 1
    assert len(two.joint_actions) == 2

    pure = synthesize_three_vertex_additive_plan(
        (((1, 1, 1), (3, 0, 0)), ((2, 2, 2), (0, 4, 0))),
        payoff_additive_certified=True,
    )
    assert pure.certificate_valid and pure.minimax_value == 3
    assert not pure.strict_randomization_necessary
    assert len(pure.joint_actions) == 1


def test_three_vertex_additive_arrangement_fails_closed():
    with pytest.raises(ValueError, match="additive"):
        synthesize_three_vertex_additive_plan(
            (((0, 1, 2),),), payoff_additive_certified=False,
        )
    with pytest.raises(ValueError, match="three scenario"):
        synthesize_three_vertex_additive_plan(
            (((0, 1),),), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="joint-action limit"):
        synthesize_three_vertex_additive_plan(
            (((1, 0, 0), (0, 1, 0), (0, 0, 1)),) * 2,
            payoff_additive_certified=True, max_active_joint_actions=1,
        )


def test_four_vertex_additive_arrangement_needs_four_way_randomization():
    plan = synthesize_four_vertex_additive_plan(
        (((4, 0, 0, 0), (0, 4, 0, 0), (0, 0, 4, 0), (0, 0, 0, 4)),),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == 1
    assert plan.nature_probabilities == (Fraction(1, 4),) * 4
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 4
    assert tuple(mass for _, mass in plan.joint_actions) == (Fraction(1, 4),) * 4


def test_four_vertex_additive_arrangement_detects_pure_optimum():
    plan = synthesize_four_vertex_additive_plan(
        (((2, 2, 2, 2), (4, 0, 0, 0)),
          ((1, 1, 1, 1), (0, 3, 0, 0))),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid and plan.minimax_value == 3
    assert not plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 1


def test_four_vertex_additive_arrangement_fails_closed():
    with pytest.raises(ValueError, match="additive"):
        synthesize_four_vertex_additive_plan(
            (((0, 1, 2, 3),),), payoff_additive_certified=False,
        )
    with pytest.raises(ValueError, match="four scenario"):
        synthesize_four_vertex_additive_plan(
            (((0, 1, 2),),), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="joint-action limit"):
        synthesize_four_vertex_additive_plan(
            (((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),) * 2,
            payoff_additive_certified=True, max_active_joint_actions=1,
        )


def test_fixed_scenario_arrangement_needs_five_way_randomization():
    plan = synthesize_fixed_scenario_additive_plan(
        (tuple(tuple(5 if i == j else 0 for i in range(5))
               for j in range(5)),),
        payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.scenario_count == 5
    assert plan.minimax_value == 1
    assert plan.nature_probabilities == (Fraction(1, 5),) * 5
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 5
    assert tuple(mass for _, mass in plan.joint_actions) == (Fraction(1, 5),) * 5


def test_fixed_scenario_matches_specialized_four_vertex_planner():
    components = (
        ((2, 2, 2, 2), (4, 0, 0, 0)),
        ((1, 1, 1, 1), (0, 3, 0, 0)),
    )
    fixed = synthesize_fixed_scenario_additive_plan(
        components, payoff_additive_certified=True,
    )
    specialized = synthesize_four_vertex_additive_plan(
        components, payoff_additive_certified=True,
    )
    assert fixed.certificate_valid
    assert fixed.minimax_value == specialized.minimax_value
    assert fixed.nature_probabilities == specialized.nature_probabilities
    assert fixed.strict_randomization_necessary == specialized.strict_randomization_necessary


def test_fixed_scenario_arrangement_fails_closed():
    with pytest.raises(ValueError, match="additive"):
        synthesize_fixed_scenario_additive_plan(
            (((0, 1),),), payoff_additive_certified=False,
        )
    with pytest.raises(ValueError, match="scenario count"):
        synthesize_fixed_scenario_additive_plan(
            (((0,),),), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="share one scenario count"):
        synthesize_fixed_scenario_additive_plan(
            (((0, 1), (0, 1, 2)),), payoff_additive_certified=True,
        )
    with pytest.raises(ValueError, match="boundary-combination limit"):
        synthesize_fixed_scenario_additive_plan(
            (((1, 0, 0, 0, 0), (0, 1, 0, 0, 0), (0, 0, 1, 0, 0)),),
            payoff_additive_certified=True, max_boundary_combinations=1,
        )
    with pytest.raises(ValueError, match="marginal variable limit"):
        synthesize_fixed_scenario_additive_plan(
            (((1, 0, 0, 0, 0), (0, 1, 0, 0, 0), (0, 0, 1, 0, 0),
              (0, 0, 0, 1, 0), (0, 0, 0, 0, 1)),) * 2,
            payoff_additive_certified=True, max_marginal_variables=1,
        )


def test_fixed_scenario_marginal_recovery_defeats_tie_product_explosion():
    basis = tuple(
        tuple(5 if scenario == action else 0 for scenario in range(5))
        for action in range(5)
    )
    plan = synthesize_fixed_scenario_additive_plan(
        (basis,) * 15,
        payoff_additive_certified=True,
        max_active_joint_actions=1,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == 15
    assert plan.nature_probabilities == (Fraction(1, 5),) * 5
    assert plan.tied_joint_action_count == 5 ** 15
    assert plan.marginal_variable_count == 75
    assert plan.pure_payoff_state_count == 3876
    assert len(plan.joint_actions) == 1
    assert not plan.strict_randomization_necessary
    assert plan.support_bound == 5
    assert plan.reason == "fixed_scenario_additive_arrangement_marginal_certificate"


def test_rank_one_scenario_quotient_removes_ambient_scenario_cap():
    coordinates = tuple(range(-5, 7))
    plan = synthesize_rank_one_scenario_quotient_plan(
        (((tuple(2 + z for z in coordinates),
           tuple(2 - z for z in coordinates))),),
        payoff_additive_certified=True,
    )
    assert plan.scenario_count == 12
    assert plan.effective_scenario_count == 2
    assert plan.affine_dimension == 1
    assert plan.endpoint_indices == (0, 11)
    assert plan.minimax_value == 2
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 2
    assert plan.certificate_valid


def test_rank_one_scenario_quotient_handles_constant_pure_game():
    plan = synthesize_rank_one_scenario_quotient_plan(
        (((3, 3, 3, 3), (1, 1, 1, 1)),),
        payoff_additive_certified=True,
    )
    assert plan.affine_dimension == 0
    assert plan.effective_scenario_count == 1
    assert plan.minimax_value == 3
    assert not plan.strict_randomization_necessary
    assert plan.joint_actions == (((0,), Fraction(1)),)
    assert plan.certificate_valid


def test_rank_one_scenario_quotient_rejects_rank_two_profiles(monkeypatch):
    calls = []

    def forbidden_planner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("rank-two input reached the endpoint planner")

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_two_vertex_additive_plan",
        forbidden_planner,
    )
    with pytest.raises(ValueError, match="affine dimension above one"):
        synthesize_rank_one_scenario_quotient_plan(
            (((0, 1, 0), (0, 0, 1)),),
            payoff_additive_certified=True,
        )
    assert calls == []


def test_rank_two_scenario_hull_removes_interior_scenarios():
    coordinates = (
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
        (Fraction(1, 4), Fraction(1, 4)),
        (Fraction(1, 3), Fraction(1, 3)),
        (Fraction(1, 5), Fraction(2, 5)),
        (Fraction(2, 5), Fraction(1, 5)),
        (Fraction(1, 6), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 6)),
        (Fraction(1, 4), Fraction(1, 4)),
        (Fraction(1, 8), Fraction(3, 8)),
        (Fraction(3, 8), Fraction(1, 8)),
    )
    plan = synthesize_rank_two_scenario_hull_plan(
        ((
            tuple(1 - x - y for x, y in coordinates),
            tuple(x for x, _ in coordinates),
            tuple(y for _, y in coordinates),
        ),),
        payoff_additive_certified=True,
    )
    assert plan.affine_dimension == 2
    assert plan.scenario_count == 12
    assert plan.effective_scenario_count == 3
    assert set(plan.extreme_indices) == {0, 1, 2}
    assert plan.minimax_value == Fraction(1, 3)
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 3
    assert plan.certificate_valid


def test_rank_two_scenario_hull_rejects_rank_three_before_planning(monkeypatch):
    calls = []

    def forbidden_planner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("invalid rank reached the fixed-scenario planner")

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_fixed_scenario_additive_plan",
        forbidden_planner,
    )
    with pytest.raises(ValueError, match="affine dimension above two"):
        synthesize_rank_two_scenario_hull_plan(
            (((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),),
            payoff_additive_certified=True,
        )
    assert calls == []


def test_rank_two_scenario_hull_rejects_more_than_eight_vertices(monkeypatch):
    calls = []

    def forbidden_planner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("over-cap hull reached the fixed-scenario planner")

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_fixed_scenario_additive_plan",
        forbidden_planner,
    )
    x = tuple(range(-4, 5))
    with pytest.raises(ValueError, match="hull exceeds"):
        synthesize_rank_two_scenario_hull_plan(
            ((x, tuple(value * value for value in x)),),
            payoff_additive_certified=True,
        )
    assert calls == []


def test_rank_three_scenario_polytope_removes_interior_scenarios():
    coordinates = (
        (Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)),
        (Fraction(1, 2), Fraction(1, 6), Fraction(1, 6)),
        (Fraction(1, 6), Fraction(1, 2), Fraction(1, 6)),
        (Fraction(1, 6), Fraction(1, 6), Fraction(1, 2)),
    )
    plan = synthesize_rank_three_scenario_polytope_plan(
        ((
            tuple(1 - x - y - z for x, y, z in coordinates),
            tuple(x for x, _, _ in coordinates),
            tuple(y for _, y, _ in coordinates),
            tuple(z for _, _, z in coordinates),
        ),),
        payoff_additive_certified=True,
    )
    assert plan.affine_dimension == 3
    assert plan.scenario_count == 8
    assert plan.effective_scenario_count == 4
    assert set(plan.extreme_indices) == {0, 1, 2, 3}
    assert plan.minimax_value == Fraction(1, 4)
    assert plan.strict_randomization_necessary
    assert len(plan.joint_actions) == 4
    assert sum(weight > 0 for weight in plan.nature_probabilities) == 4
    assert plan.support_bound == 4
    assert plan.certificate_valid


def test_rank_three_nature_certificate_compresses_dense_optimal_intervention(
    monkeypatch,
):
    coordinates = tuple(
        (Fraction(x), Fraction(y), Fraction(z))
        for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)
    )
    actions = tuple(
        tuple(sign * point[axis] for point in coordinates)
        for axis in range(3) for sign in (-1, 1)
    )
    real_planner = synthesize_fixed_scenario_additive_plan

    def dense_nature_planner(*args, **kwargs):
        plan = real_planner(*args, **kwargs)
        return replace(
            plan,
            nature_probabilities=(Fraction(1, 8),) * 8,
        )

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_fixed_scenario_additive_plan",
        dense_nature_planner,
    )
    plan = synthesize_rank_three_scenario_polytope_plan(
        (actions,),
        payoff_additive_certified=True,
    )
    assert plan.effective_scenario_count == 8
    assert sum(weight > 0 for weight in plan.nature_probabilities) <= 4
    assert plan.support_bound == 4
    assert all(
        sum(plan.nature_probabilities[index] * action[index]
            for index in range(8)) == 0
        for action in actions
    )
    assert plan.certificate_valid


def test_rank_three_nature_certificate_rejects_invalid_distribution():
    with pytest.raises(ValueError, match="probability distribution"):
        compress_rank_three_nature_certificate(
            ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
            (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)),
        )


def test_rank_three_scenario_polytope_rejects_rank_four_before_planning(monkeypatch):
    calls = []

    def forbidden_planner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("rank-four input reached the fixed-scenario planner")

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_fixed_scenario_additive_plan",
        forbidden_planner,
    )
    with pytest.raises(ValueError, match="affine dimension above three"):
        synthesize_rank_three_scenario_polytope_plan(
            (((0, 1, 0, 0, 0), (0, 0, 1, 0, 0),
              (0, 0, 0, 1, 0), (0, 0, 0, 0, 1)),),
            payoff_additive_certified=True,
        )
    assert calls == []


def test_rank_three_scenario_polytope_rejects_more_than_eight_vertices(monkeypatch):
    calls = []

    def forbidden_planner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("over-cap polytope reached the fixed-scenario planner")

    monkeypatch.setattr(
        "theorica.agents.robust_provenance.synthesize_fixed_scenario_additive_plan",
        forbidden_planner,
    )
    x = tuple(Fraction(value) for value in range(-4, 5))
    with pytest.raises(ValueError, match="polytope exceeds"):
        synthesize_rank_three_scenario_polytope_plan(
            ((x, tuple(value * value for value in x),
              tuple(value * value * value for value in x)),),
            payoff_additive_certified=True,
        )
    assert calls == []


def test_orbit_quotient_uses_two_vertex_sparse_support_fast_path():
    plan = synthesize_orbit_ambiguity_plan(
        3, 0, ((0,), (1,), (2,)), ((0, 1, 2),),
        ((1, 0, 0), (0, 1, 0)),
        ambiguity_kind="two-vertex-fast-path", ambiguity_invariant=True,
    )
    assert plan.certificate_valid and plan.strict_randomization_advantage
    assert plan.reason == "two_vertex_sparse_support_certificate"
    assert plan.minimax_value == Fraction(1, 2)
    assert len(plan.components) == 2
    assert tuple(component.probability for component in plan.components) == (
        Fraction(1, 2), Fraction(1, 2),
    )


def test_orbit_quotient_requires_invariance_certificate():
    with pytest.raises(ValueError, match="action-invariant"):
        synthesize_orbit_ambiguity_plan(
            3, 0, ((0,),), _product_action(1, 2),
            ((Fraction(1, 3), Fraction(2, 3)),),
            ambiguity_kind="uncertified", ambiguity_invariant=False,
        )
