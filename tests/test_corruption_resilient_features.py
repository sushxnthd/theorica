from fractions import Fraction

import pytest

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    certify_decision_query_corruption_radius,
    certify_multi_action_plan_from_ambiguous_transcript,
    certify_qary_three_level_insurance,
    certify_qary_two_level_insurance,
    certify_stacked_ambiguity_gap,
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
