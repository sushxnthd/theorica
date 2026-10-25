from fractions import Fraction

import pytest

from theorica.agents.corruption_resilient_features import (
    reconstruct_corruption_resilient_feature_payoffs,
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
