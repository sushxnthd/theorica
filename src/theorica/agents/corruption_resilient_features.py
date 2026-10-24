"""Exact feature-span reconstruction under bounded adversarial query errors."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from theorica.agents.robust_provenance import (
    _fraction_matrix_rank,
    _solve_fraction_system,
)


@dataclass(frozen=True)
class CorruptionResilientFeatureReconstruction:
    """Exact feature-span reconstruction with adversarial query correction."""

    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    feature_rows: tuple[tuple[Fraction, ...], ...]
    query_indices: tuple[int, ...]
    pivot_columns: tuple[int, ...]
    corrected_query_indices: tuple[int, ...]
    feature_rank: int
    feature_width: int
    scenario_count: int
    corruption_budget: int
    query_count: int
    minimum_distance: int
    candidate_subsets_tested: int
    certificate_valid: bool
    reason: str


def _feature_code_minimum_distance(rows, rank):
    """Return the exact Hamming distance of the rational evaluation code."""
    maximum_zero_count = 0
    for size in range(rank):
        for indices in combinations(range(len(rows)), size):
            basis = tuple(rows[index] for index in indices)
            basis_rank = _fraction_matrix_rank(basis)
            if basis_rank != size:
                continue
            zero_count = sum(
                _fraction_matrix_rank(basis + (row,)) == basis_rank for row in rows
            )
            maximum_zero_count = max(maximum_zero_count, zero_count)
    return len(rows) - maximum_zero_count


def reconstruct_corruption_resilient_feature_payoffs(
    feature_rows,
    scenario_oracle,
    *,
    payoff_in_feature_span_certified: bool,
    corruption_budget: int,
    max_query_count: int = 12,
    max_candidate_subsets: int = 100_000,
) -> CorruptionResilientFeatureReconstruction:
    """Recover feature-span payoffs despite bounded adversarial query errors.

    Query selection is outcome-independent. A set is accepted exactly when its
    rational evaluation code has minimum distance at least ``2t + 1``.
    """
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    if corruption_budget < 0:
        raise ValueError("corruption budget must be nonnegative")
    features = tuple(tuple(Fraction(value) for value in row) for row in feature_rows)
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    width = len(features[0])
    if any(len(row) != width for row in features):
        raise ValueError("feature rows must share one width")
    rank = _fraction_matrix_rank(features)
    if rank == 0:
        raise ValueError("feature rows have zero rank")

    minimum_queries = rank + 2 * corruption_budget
    upper = min(len(features), int(max_query_count))
    tested = 0
    selected = None
    selected_distance = 0
    for query_count in range(minimum_queries, upper + 1):
        for indices in combinations(range(len(features)), query_count):
            tested += 1
            if tested > int(max_candidate_subsets):
                raise ValueError("corruption-resilient query search limit exceeded")
            rows = tuple(features[index] for index in indices)
            if _fraction_matrix_rank(rows) != rank:
                continue
            distance = _feature_code_minimum_distance(rows, rank)
            if distance >= 2 * corruption_budget + 1:
                selected = indices
                selected_distance = distance
                break
        if selected is not None:
            break
    if selected is None:
        raise ValueError(
            "no query subset within the cap corrects the certified corruption budget"
        )

    queried_rows = tuple(features[index] for index in selected)
    pivots = next(
        (
            columns
            for columns in combinations(range(width), rank)
            if _fraction_matrix_rank(
                tuple(tuple(row[column] for column in columns) for row in queried_rows)
            )
            == rank
        ),
        None,
    )
    if pivots is None:
        raise RuntimeError("selected feature rows lack exact pivot columns")
    reduced_rows = tuple(
        tuple(row[column] for column in pivots) for row in queried_rows
    )
    all_reduced = tuple(tuple(row[column] for column in pivots) for row in features)

    queried = []
    for index in selected:
        response = tuple(
            tuple(Fraction(value) for value in component)
            for component in scenario_oracle(index)
        )
        if not response or any(not component for component in response):
            raise ValueError("the scenario oracle returned an empty payoff shape")
        queried.append(response)
    shape = tuple(len(component) for component in queried[0])
    if any(
        tuple(len(component) for component in response) != shape for response in queried
    ):
        raise ValueError("the scenario oracle returned inconsistent payoff shapes")

    decoded = [[None for _ in range(action_count)] for action_count in shape]
    corrected = set()
    for component, action_count in enumerate(shape):
        for action in range(action_count):
            observations = tuple(response[component][action] for response in queried)
            candidates = {}
            for basis_indices in combinations(range(len(selected)), rank):
                matrix = tuple(reduced_rows[index] for index in basis_indices)
                coefficients = _solve_fraction_system(
                    matrix, tuple(observations[index] for index in basis_indices)
                )
                if coefficients is None:
                    continue
                predictions = tuple(
                    sum(
                        (
                            value * coefficient
                            for value, coefficient in zip(row, coefficients)
                        ),
                        Fraction(0),
                    )
                    for row in all_reduced
                )
                query_predictions = tuple(predictions[index] for index in selected)
                disagreements = tuple(
                    position
                    for position, (expected, observed) in enumerate(
                        zip(query_predictions, observations)
                    )
                    if expected != observed
                )
                if len(disagreements) <= corruption_budget:
                    candidates[predictions] = disagreements
            if len(candidates) != 1:
                raise ValueError("query transcript is not uniquely decodable")
            predictions, disagreements = next(iter(candidates.items()))
            decoded[component][action] = predictions
            corrected.update(selected[position] for position in disagreements)

    reconstructed = tuple(tuple(action for action in component) for component in decoded)
    valid = all(
        reconstructed[component][action][scenario]
        == queried[position][component][action]
        for position, scenario in enumerate(selected)
        if scenario not in corrected
        for component in range(len(shape))
        for action in range(shape[component])
    )
    return CorruptionResilientFeatureReconstruction(
        component_payoff_vectors=reconstructed,
        feature_rows=features,
        query_indices=tuple(selected),
        pivot_columns=tuple(pivots),
        corrected_query_indices=tuple(sorted(corrected)),
        feature_rank=rank,
        feature_width=width,
        scenario_count=len(features),
        corruption_budget=corruption_budget,
        query_count=len(selected),
        minimum_distance=selected_distance,
        candidate_subsets_tested=tested,
        certificate_valid=valid,
        reason="exact_adversarial_feature_code_decoding_certificate",
    )
