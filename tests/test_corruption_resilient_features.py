from fractions import Fraction

import pytest

from theorica.agents.corruption_resilient_features import (
    certify_binary_middle_first_symmetric,
    certify_binary_three_level_middle_first,
    certify_common_robust_plan,
    certify_decision_query_corruption_radius,
    certify_multi_action_plan_from_ambiguous_transcript,
    certify_qary_root_respecting_insurance,
    certify_qary_three_level_insurance,
    certify_qary_two_level_insurance,
    certify_stacked_ambiguity_gap,
    certify_three_level_monotonicity,
    certify_two_action_plan_from_ambiguous_transcript,
    plan_adaptive_decision_queries_with_faults,
    plan_adaptive_decision_queries_with_lies,
    plan_adaptive_decision_queries_with_weighted_faults,
    plan_decision_identifying_queries,
    qary_prefix_query_costs,
    qary_prefix_query_library,
    reconstruct_corruption_resilient_feature_payoffs,
    select_finite_list_feature_queries,
)


def _unique_mixing_game(probability):
    probability = Fraction(probability)
    return (
        (1 - probability, probability - 1),
        (-probability, probability),
    )


def test_corruption_resilient_feature_reconstruction_corrects_one_bad_query():
    xs = tuple(Fraction(index - 3, 5) for index in range(9))
    features = tuple((1, x, x * x) for x in xs)
    values = tuple(2 - 3 * x + 5 * x * x for x in xs)
    calls = []

    def oracle(index):
        calls.append(index)
        value = values[index] + (Fraction(11) if index == 2 else Fraction(0))
        return ((value,),)

    result = reconstruct_corruption_resilient_feature_payoffs(
        features,
        oracle,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    assert result.certificate_valid
    assert result.feature_rank == 3
    assert result.query_count == 5
    assert result.minimum_distance == 3
    assert calls == list(result.query_indices)
    assert result.corrected_query_indices == (2,)
    assert result.component_payoff_vectors == ((values,),)


def test_corruption_resilient_feature_reconstruction_rejects_bad_geometry():
    features = ((1, 0), (1, 0), (1, 0), (0, 1), (0, 1))
    calls = []
    with pytest.raises(ValueError, match="no query subset"):
        reconstruct_corruption_resilient_feature_payoffs(
            features,
            lambda index: calls.append(index),
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
            max_query_count=5,
        )
    assert calls == []


def test_feature_reconstruction_corrects_error_after_known_erasure():
    xs = tuple(Fraction(index - 4, 7) for index in range(10))
    features = tuple((1, x, x * x) for x in xs)
    values = tuple(3 + 2 * x - 4 * x * x for x in xs)
    calls = []

    def oracle(index):
        calls.append(index)
        if index == 0:
            return None
        return ((values[index] + (13 if index == 1 else 0),),)

    result = reconstruct_corruption_resilient_feature_payoffs(
        features,
        oracle,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
        erasure_budget=1,
    )
    assert result.certificate_valid
    assert result.query_count == 6
    assert result.minimum_distance == 4
    assert result.erased_query_indices == (0,)
    assert result.corrected_query_indices == (1,)
    assert result.component_payoff_vectors == ((values,),)
    assert calls == list(result.query_indices)


def test_feature_reconstruction_rejects_excess_erasure_budget():
    features = tuple((1, Fraction(index)) for index in range(7))
    calls = []

    def oracle(index):
        calls.append(index)
        return None if index in (0, 1) else ((Fraction(index),),)

    with pytest.raises(ValueError, match="exceeded the certified erasure budget"):
        reconstruct_corruption_resilient_feature_payoffs(
            features,
            oracle,
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
            erasure_budget=1,
        )
    assert len(calls) == 5


def test_ambiguous_model_can_have_identifiable_robust_decision():
    result = certify_two_action_plan_from_ambiguous_transcript(
        ((1, 0), (1, 1), (1, 2)),
        (0, 1, 2),
        ((0, 0), (0, 0), (0, 1)),
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    assert result.certificate_valid
    assert result.version_space_size == 3
    assert not result.model_identifiable
    assert result.value_identifiable and result.policy_identifiable
    assert result.minimax_value == 0
    assert result.action_probabilities == (Fraction(1), Fraction(0))
    assert result.finite_list_minimum_distance == 2


def test_ambiguous_transcript_abstains_when_values_differ():
    result = certify_two_action_plan_from_ambiguous_transcript(
        ((1, 0), (1, 1), (1, 2)),
        (0, 1, 2),
        ((0, 0), (0, 0), (1, 1)),
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    assert result.certificate_valid
    assert not result.value_identifiable
    assert not result.policy_identifiable
    assert result.action_probabilities is None


def test_equal_values_still_abstain_for_disjoint_optimal_policies():
    result = certify_two_action_plan_from_ambiguous_transcript(
        ((1, 0), (1, 1), (1, 2)),
        (0, 1, 2),
        ((-2, -1), (-1, -1), (-2, 0)),
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    assert result.certificate_valid
    assert result.value_identifiable
    assert not result.policy_identifiable
    assert result.reason == "ambiguous_transcript_has_disjoint_optimal_policy_sets"


def test_ambiguous_planner_rejects_infinite_list_geometry_before_enumeration():
    with pytest.raises(ValueError, match="finite completion list"):
        certify_two_action_plan_from_ambiguous_transcript(
            ((1, 0), (1, 0), (0, 1)),
            (0, 1, 2),
            ((0, 0), (0, 0), (0, 1)),
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
        )


def test_finite_list_selector_uses_t_plus_s_distance_boundary():
    features = tuple((1, Fraction(index), Fraction(index) ** 2) for index in range(8))
    result = select_finite_list_feature_queries(
        features,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
        erasure_budget=2,
    )
    assert result.certificate_valid
    assert result.feature_rank == 3
    assert result.query_count == 6
    assert result.minimum_distance == 4


def test_finite_list_selector_rejects_same_size_degenerate_geometry():
    features = ((1, 0), (1, 0), (1, 0), (1, 0), (0, 1))
    with pytest.raises(ValueError, match="no query subset"):
        select_finite_list_feature_queries(
            features,
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
            erasure_budget=2,
            max_query_count=5,
        )


def test_multi_action_common_policy_survives_model_ambiguity():
    result = certify_common_robust_plan((
        ((0,), (-1,), (-2,)),
        ((0,), (-3,), (-1,)),
    ))
    assert result.certificate_valid
    assert result.policy_identifiable and not result.model_identifiable
    assert result.action_probabilities == (1, 0, 0)
    assert result.minimax_value == 0


def test_three_action_helly_witness_is_sharp():
    result = certify_common_robust_plan((
        ((-1,), (0,), (0,)),
        ((0,), (-1,), (0,)),
        ((0,), (0,), (-1,)),
    ))
    assert result.certificate_valid
    assert result.value_identifiable and not result.policy_identifiable
    assert result.impossibility_witness == (0, 1, 2)


def test_multi_action_corrupted_transcript_returns_exact_certificate():
    result = certify_multi_action_plan_from_ambiguous_transcript(
        ((1, 0), (1, 1), (1, 2)),
        (0, 1, 2),
        ((0, -1, -2), (0, -1, -2), (0, 2, 3)),
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    assert result.certificate_valid
    assert result.action_count == 3
    assert result.finite_list_minimum_distance == 2


def test_stacked_gap_is_zero_exactly_for_a_common_policy():
    result = certify_stacked_ambiguity_gap((
        ((0,), (-1,), (-2,)),
        ((0,), (-3,), (-1,)),
    ))
    assert result.certificate_valid and result.policy_identifiable
    assert result.common_value == result.stacked_value == 0
    assert result.ambiguity_gap == 0
    assert result.action_probabilities == (1, 0, 0)
    assert len(result.adversary_scenario_weights) <= 3
    assert max(result.adversary_action_payoffs) == 0


def test_stacked_dual_handles_a_single_labelled_scenario():
    result = certify_stacked_ambiguity_gap((((1,), (0,), (-1,)),))
    assert result.certificate_valid and result.policy_identifiable
    assert result.common_value == result.stacked_value == 1
    assert result.ambiguity_gap == 0
    assert result.adversary_scenario_weights == ((0, 0, Fraction(1)),)
    assert result.adversary_action_payoffs == (1, 0, -1)


def test_stacked_gap_returns_sharp_scenario_witness():
    games = tuple(
        tuple((Fraction(-1 if action == excluded else 0),)
              for action in range(5))
        for excluded in range(5)
    )
    result = certify_stacked_ambiguity_gap(games)
    assert result.certificate_valid and not result.policy_identifiable
    assert result.common_value == 0
    assert result.stacked_value == Fraction(-1, 5)
    assert result.ambiguity_gap == Fraction(1, 5)
    assert result.scenario_witness == tuple((index, 0) for index in range(5))
    assert result.adversary_scenario_weights == tuple(
        (index, 0, Fraction(1, 5)) for index in range(5)
    )
    assert result.adversary_action_payoffs == (Fraction(-1, 5),) * 5
    assert result.stacked_action_probabilities == (Fraction(1, 5),) * 5


def test_stacked_dual_certificate_has_action_bounded_support():
    games = (
        ((0, 0, 0), (-1, 2, 3), (-1, -3, 4)),
        ((0, 0), (-1, 5), (-1, -2)),
    )
    result = certify_stacked_ambiguity_gap(games)
    assert result.certificate_valid
    assert len(result.adversary_scenario_weights) <= 3
    assert sum(weight for _, _, weight in result.adversary_scenario_weights) == 1
    assert max(result.adversary_action_payoffs) == result.stacked_value


def test_stacked_gap_abstains_when_values_differ():
    result = certify_stacked_ambiguity_gap((((0,), (-1,)), ((1,), (-1,))))
    assert result.certificate_valid
    assert not result.value_identifiable
    assert result.ambiguity_gap is None


def test_exact_decision_query_tree_matches_binary_depth():
    games = tuple(_unique_mixing_game(Fraction(index + 1, 5)) for index in range(4))
    plan = plan_decision_identifying_queries(
        games,
        ((0, 0, 1, 1), (0, 1, 0, 1)),
    )
    assert plan.certificate_valid
    assert plan.worst_case_depth == 2
    assert plan.root is not None and plan.root.query_index == 0


def test_decision_queries_can_beat_unique_model_recovery():
    games = tuple(
        _unique_mixing_game(Fraction(1, 3) if index < 4 else Fraction(2, 3))
        for index in range(8)
    )
    plan = plan_decision_identifying_queries(
        games,
        (
            tuple(index // 4 for index in range(8)),
            tuple((index >> 1) & 1 for index in range(8)),
            tuple(index & 1 for index in range(8)),
        ),
    )
    assert plan.worst_case_depth == 1
    assert plan.root is not None and plan.root.query_index == 0


def test_decision_query_tree_fails_closed_when_queries_cannot_separate_policies():
    games = tuple(_unique_mixing_game(Fraction(index + 1, 5)) for index in range(4))
    plan = plan_decision_identifying_queries(games, ((0, 0, 1, 1),))
    assert plan.certificate_valid
    assert plan.root is None and plan.worst_case_depth is None
    assert "cannot_identify" in plan.reason


def test_higher_order_conflict_is_resolved_despite_pairwise_compatibility():
    games = tuple(
        tuple((Fraction(-1 if action == excluded else 0),) for action in range(3))
        for excluded in range(3)
    )
    assert all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(3)
        for right in range(left + 1, 3)
    )
    plan = plan_decision_identifying_queries(games, ((0, 1, 1),))
    assert plan.worst_case_depth == 1


def test_tripled_coordinate_code_corrects_one_query_error():
    games = tuple(_unique_mixing_game(Fraction(index + 1, 5)) for index in range(4))
    bits = ((0, 0, 1, 1), (0, 1, 0, 1))
    result = certify_decision_query_corruption_radius(
        games,
        tuple(row for row in bits for _ in range(3)),
        corruption_budget=1,
    )

    assert result.certificate_valid
    assert result.decision_radius == 2
    assert result.max_certified_corruptions == 1
    assert result.robust_to_budget


def test_decision_code_can_be_shorter_than_unique_model_code():
    games = tuple(
        _unique_mixing_game(Fraction(1, 3) if index < 4 else Fraction(2, 3))
        for index in range(8)
    )
    result = certify_decision_query_corruption_radius(
        games,
        ((0, 0, 0, 0, 1, 1, 1, 1),) * 3,
        corruption_budget=1,
    )

    assert result.decision_radius == 2
    assert result.robust_to_budget
    assert result.query_count == 3


def test_higher_order_corruption_attack_defeats_pairwise_conflict_distance():
    games = tuple(
        tuple((Fraction(-1 if action == excluded else 0),) for action in range(3))
        for excluded in range(3)
    )
    assert all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(3)
        for right in range(left + 1, 3)
    )
    result = certify_decision_query_corruption_radius(
        games,
        ((0, 0, 1), (0, 1, 0), (0, 1, 1)),
        corruption_budget=1,
    )

    assert result.certificate_valid
    assert result.decision_radius == 1
    assert not result.robust_to_budget
    assert len(result.incompatibility_witness) == 3
    assert result.closest_incompatible_center == (0, 0, 1)


def test_corruption_radius_is_unbounded_when_decision_is_already_identified():
    game = _unique_mixing_game(Fraction(1, 3))
    result = certify_decision_query_corruption_radius(
        (game, game, game),
        ((0, 1, 0),),
        corruption_budget=10,
    )

    assert result.decision_radius is None
    assert result.max_certified_corruptions is None
    assert result.robust_to_budget


def test_adaptive_decision_tree_needs_three_repeated_answers_for_one_lie():
    games = (
        _unique_mixing_game(Fraction(1, 3)),
        _unique_mixing_game(Fraction(2, 3)),
    )
    plan = plan_adaptive_decision_queries_with_lies(
        games,
        ((0, 1),) * 3,
        corruption_budget=1,
    )

    assert plan.certificate_valid
    assert plan.worst_case_depth == 3
    assert plan.root is not None
    assert plan.root.lie_counts == (0, 0)


def test_adaptive_decision_tree_fails_closed_when_repetition_is_missing():
    games = (
        _unique_mixing_game(Fraction(1, 3)),
        _unique_mixing_game(Fraction(2, 3)),
    )
    plan = plan_adaptive_decision_queries_with_lies(
        games,
        ((0, 1),) * 2,
        corruption_budget=1,
    )

    assert plan.certificate_valid
    assert plan.root is None
    assert plan.worst_case_depth is None
    assert "under_corruption" in plan.reason


def test_adaptive_lie_tree_uses_full_higher_order_compatibility():
    games = tuple(
        tuple((Fraction(-1 if action == excluded else 0),) for action in range(3))
        for excluded in range(3)
    )
    assert all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(3)
        for right in range(left + 1, 3)
    )
    plan = plan_adaptive_decision_queries_with_lies(
        games,
        ((0, 1, 1),) * 3,
        corruption_budget=1,
    )

    assert plan.certificate_valid
    assert plan.worst_case_depth == 3


def test_qary_prefix_library_has_exact_nonbinary_lie_depth():
    arity, depth = 3, 2
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, arity**depth + 1))
        for index in range(arity**depth)
    )
    outcomes = qary_prefix_query_library(arity, depth)
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=1
    )

    assert len(outcomes) == 3 * sum(arity**level for level in range(depth))
    assert plan.certificate_valid
    assert plan.worst_case_depth == 2 * depth + 1


def test_qary_prefix_library_fails_closed_with_missing_parent_copy():
    arity, depth = 3, 2
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, arity**depth + 1))
        for index in range(arity**depth)
    )
    outcomes = qary_prefix_query_library(arity, depth)
    attacked = outcomes[:-1]
    plan = plan_adaptive_decision_queries_with_lies(
        games, attacked, corruption_budget=1
    )

    assert plan.certificate_valid
    assert plan.root is None
    assert plan.worst_case_depth is None


def test_qary_prefix_library_has_exact_two_lie_depth():
    arity, depth, corruption_budget = 3, 2, 2
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, arity**depth + 1))
        for index in range(arity**depth)
    )
    outcomes = qary_prefix_query_library(
        arity, depth, copies=2 * corruption_budget + 1
    )
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=corruption_budget
    )

    assert plan.certificate_valid
    assert plan.worst_case_depth == (corruption_budget + 1) * depth + corruption_budget


def test_qary_prefix_library_fails_closed_with_two_lies_and_missing_copy():
    arity, depth, corruption_budget = 3, 2, 2
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, arity**depth + 1))
        for index in range(arity**depth)
    )
    outcomes = qary_prefix_query_library(
        arity, depth, copies=2 * corruption_budget + 1
    )[:-1]
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=corruption_budget
    )

    assert plan.certificate_valid
    assert plan.root is None
    assert plan.worst_case_depth is None


def test_qary_prefix_library_has_exact_mixed_fault_depth():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    completion_count = arity**depth
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = qary_prefix_query_library(
        arity, depth, copies=2 * corruptions + erasures + 1
    )
    plan = plan_adaptive_decision_queries_with_faults(
        games,
        outcomes,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )

    assert plan.certificate_valid
    assert plan.worst_case_depth == 6
    assert plan.root is not None


def test_qary_mixed_fault_library_fails_closed_with_missing_copy():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    completion_count = arity**depth
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = qary_prefix_query_library(
        arity, depth, copies=2 * corruptions + erasures + 1
    )[:-1]
    plan = plan_adaptive_decision_queries_with_faults(
        games,
        outcomes,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )

    assert plan.certificate_valid
    assert plan.root is None
    assert plan.worst_case_depth is None


def test_qary_prefix_library_has_exact_weighted_mixed_fault_cost():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    level_costs = (1, 5)
    copies = 2 * corruptions + erasures + 1
    completion_count = arity**depth
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=level_costs
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games,
        outcomes,
        query_costs=costs,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )

    assert plan.certificate_valid
    assert plan.worst_case_cost == 22
    assert plan.worst_case_depth == 6
    assert plan.root is not None


def test_weighted_multiset_quotient_preserves_physical_query_identity():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    copies = 2 * corruptions + erasures + 1
    completion_count = arity**depth
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=(1, 5)
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games,
        outcomes,
        query_costs=costs,
        corruption_budget=corruptions,
        erasure_budget=erasures,
        known_feasible_cost_upper_bound=22,
    )

    def assert_unique_indices(node, used=()):
        if node.query_index is None:
            return
        assert node.query_index not in used
        for _, child in node.children:
            assert_unique_indices(child, used + (node.query_index,))

    assert plan.certificate_valid
    assert plan.worst_case_cost == 22
    assert plan.root is not None
    assert_unique_indices(plan.root)


def test_weighted_mixed_fault_plan_conditions_only_the_initial_query():
    arity, depth, copies = 2, 3, 4
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, 9))
        for index in range(arity**depth)
    )
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=(40, 1, 20)
    )
    root_first = plan_adaptive_decision_queries_with_weighted_faults(
        games,
        outcomes,
        query_costs=costs,
        corruption_budget=1,
        erasure_budget=1,
        known_feasible_cost_upper_bound=182,
        allowed_initial_query_indices=range(4),
    )

    assert root_first.certificate_valid
    assert root_first.worst_case_cost == 182
    assert root_first.root is not None
    assert root_first.root.query_index in range(4)
    assert any(
        child.query_index is not None and child.query_index >= 4
        for _, child in root_first.root.children
    )


@pytest.mark.parametrize(
    "indices",
    ((), (0, 0), (True,), (-1,), (28,), (0.5,), 3),
)
def test_weighted_mixed_fault_plan_rejects_invalid_initial_query_indices(indices):
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, 9))
        for index in range(8)
    )
    outcomes = qary_prefix_query_library(2, 3, copies=4)
    costs = qary_prefix_query_costs(2, 3, copies=4, level_costs=(1, 1, 1))

    with pytest.raises(ValueError, match="allowed initial query indices"):
        plan_adaptive_decision_queries_with_weighted_faults(
            games,
            outcomes,
            query_costs=costs,
            corruption_budget=1,
            erasure_budget=1,
            allowed_initial_query_indices=indices,
        )


def test_weighted_mixed_fault_library_fails_closed_with_missing_copy():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    copies = 2 * corruptions + erasures + 1
    completion_count = arity**depth
    games = tuple(
        _unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)[:-1]
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=(1, 5)
    )[:-1]
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games,
        outcomes,
        query_costs=costs,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )

    assert plan.certificate_valid
    assert plan.root is None
    assert plan.worst_case_cost is None


@pytest.mark.parametrize(
    ("arity", "root_cost", "child_cost", "expected", "regime"),
    (
        (3, 2, 7, 32, "child_expensive_or_equal"),
        (4, 5, 3, 24, "intermediate_insurance"),
        (5, 9, 4, 40, "root_expensive"),
        (3, 6, 6, 36, "child_expensive_or_equal"),
        (4, 8, 4, 36, "intermediate_insurance"),
    ),
)
def test_qary_two_level_insurance_closed_form(
    arity,
    root_cost,
    child_cost,
    expected,
    regime,
):
    certificate = certify_qary_two_level_insurance(
        arity,
        root_cost,
        child_cost,
    )

    assert certificate.certificate_valid
    assert certificate.exact_worst_case_cost == expected
    assert certificate.active_regime == regime
    assert certificate.exact_worst_case_cost == max(
        certificate.adversary_lower_bounds
    )


@pytest.mark.parametrize(
    ("arity", "costs", "expected"),
    (
        (2, (1, 7, 2), 32),
        (2, (7, 2, 1), 31),
        (2, (2, 1, 7), 34),
        (2, (3, 6, 2), 32),
        (3, (1, 2, 3), 18),
    ),
)
def test_qary_three_level_insurance_closed_form(arity, costs, expected):
    certificate = certify_qary_three_level_insurance(arity, *costs)

    assert certificate.certificate_valid
    assert certificate.exact_worst_case_cost == expected
    assert certificate.exact_worst_case_cost == max(certificate.adversary_lower_bounds)
    assert certificate.active_faces
    assert certificate.policy_class == "root_respecting_qary"


@pytest.mark.parametrize(
    ("costs", "expected", "active_face"),
    (
        ((1, 79, 1), 397, "middle_frontloaded"),
        ((1, 1, 79), 321, "leaf_heavy_after_middle"),
        ((1, 79, 53), 477, "middle_leaf_transition"),
        ((79, 1, 53), 399, "balanced_exposure"),
        ((79, 79, 1), 554, "root_middle_transition"),
        ((79, 1, 1), 319, "root_heavy_after_middle"),
    ),
)
def test_binary_three_level_middle_first_certificate(costs, expected, active_face):
    certificate = certify_binary_three_level_middle_first(*costs)

    assert certificate.certificate_valid
    assert certificate.exact_worst_case_cost == expected
    assert certificate.active_faces == (active_face,)
    assert certificate.policy_class == "binary_middle_first"


@pytest.mark.parametrize("costs", ((0, 1, 1), (True, 1, 1), (1.5, 1, 1)))
def test_binary_three_level_middle_first_certificate_rejects_invalid_costs(costs):
    with pytest.raises(ValueError, match="positive integers"):
        certify_binary_three_level_middle_first(*costs)


@pytest.mark.parametrize(
    ("costs", "expected", "active_faces"),
    (
        ((79, 1), 554, ("root_middle_heavy",)),
        ((3, 2), 24, ("transition",)),
        ((1, 79), 321, ("leaf_heavy",)),
        ((2, 1), 15, ("root_middle_heavy", "transition")),
        ((1, 1), 9, ("transition", "leaf_heavy")),
    ),
)
def test_binary_middle_first_symmetric_certificate(costs, expected, active_faces):
    certificate = certify_binary_middle_first_symmetric(*costs)

    assert certificate.certificate_valid
    assert certificate.exact_worst_case_cost == expected
    assert certificate.active_faces == active_faces
    assert certificate.projected_face_vectors == ((7, 1), (6, 3), (5, 4))
    assert certificate.policy_class == "binary_middle_first_symmetric"


@pytest.mark.parametrize("costs", ((0, 1), (True, 1), (1.5, 1)))
def test_binary_middle_first_symmetric_certificate_rejects_invalid_costs(costs):
    with pytest.raises(ValueError, match="positive integers"):
        certify_binary_middle_first_symmetric(*costs)


def test_three_level_certificate_obeys_policy_class_monotonicity():
    certificate = certify_qary_three_level_insurance(2, 1, 10, 3)
    root_respecting = certify_qary_root_respecting_insurance(2, (1, 10, 3))

    assert certificate.policy_class == "root_respecting_qary"
    assert certificate.exact_worst_case_cost == 45
    assert certificate.exact_worst_case_cost == root_respecting.exact_worst_case_cost
    assert len(certificate.adversary_lower_bounds) == 6
    assert "root_bypass" not in certificate.active_faces
    assert 4 * 10 + 2 * 3 > certificate.exact_worst_case_cost


def test_retired_bypass_face_has_exact_impossibility_cone():
    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                certificate = certify_three_level_monotonicity(2, a, b, c)
                assert certificate.certificate_valid
                assert certificate.lower_face_impossible == (
                    c > 2 * a and b > 2 * a + c
                )

    witness = certify_three_level_monotonicity(5, 1, 10, 3)
    assert witness.lower_face_impossible
    assert witness.analytic_violation_cone
    assert witness.retired_bypass_face_cost == 46
    assert witness.feasible_root_respecting_cost == 45


def test_root_respecting_faces_recover_depth_two_and_six_depth_three_faces():
    depth_two = certify_qary_root_respecting_insurance(3, (5, 3))
    assert set(depth_two.face_vectors) == {(2, 4), (3, 3), (4, 1)}
    assert depth_two.exact_worst_case_cost == 24

    depth_three = certify_qary_root_respecting_insurance(2, (1, 7, 2))
    assert len(depth_three.face_vectors) == 6
    assert set(depth_three.face_vectors) == {
        (2, 2, 4),
        (2, 3, 3),
        (2, 4, 1),
        (3, 2, 3),
        (3, 3, 1),
        (4, 1, 1),
    }
    assert (0, 4, 2) not in depth_three.face_vectors


def test_root_respecting_recurrence_matches_face_maximum_through_depth_six():
    from itertools import product

    for depth in range(1, 7):
        for costs in product((1, 2, 3), repeat=depth):
            certificate = certify_qary_root_respecting_insurance(2 + depth % 4, costs)
            assert certificate.certificate_valid
            assert len(certificate.face_vectors) == depth * (depth + 1) // 2
            assert certificate.exact_worst_case_cost == certificate.recurrence_cost
            assert certificate.exact_worst_case_cost == max(certificate.face_costs)
            assert certificate.active_face_vectors


def test_root_respecting_certificate_abstains_with_missing_copy():
    certificate = certify_qary_root_respecting_insurance(
        3,
        (2, 5, 1, 3),
        available_copies=(4, 4, 3, 4),
    )
    assert not certificate.certificate_valid
    assert certificate.exact_worst_case_cost is None
    assert certificate.active_face_vectors == ()
    assert "fewer_than_four" in certificate.reason
