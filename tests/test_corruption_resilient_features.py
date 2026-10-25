from fractions import Fraction

import pytest

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    certify_multi_action_plan_from_ambiguous_transcript,
    certify_two_action_plan_from_ambiguous_transcript,
    reconstruct_corruption_resilient_feature_payoffs,
    select_finite_list_feature_queries,
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
