"""Exact feature-span reconstruction under bounded adversarial query errors."""

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations, product

from theorica.agents.robust_provenance import (
    _fraction_matrix_rank,
    _solve_fraction_system,
    solve_two_action_robust_game,
)


@dataclass(frozen=True)
class CorruptionResilientFeatureReconstruction:
    """Exact feature-span reconstruction with adversarial query correction."""

    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    feature_rows: tuple[tuple[Fraction, ...], ...]
    query_indices: tuple[int, ...]
    pivot_columns: tuple[int, ...]
    corrected_query_indices: tuple[int, ...]
    erased_query_indices: tuple[int, ...]
    feature_rank: int
    feature_width: int
    scenario_count: int
    corruption_budget: int
    erasure_budget: int
    query_count: int
    minimum_distance: int
    candidate_subsets_tested: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class DecisionIdentifiableTwoActionPlan:
    """Exact robust-plan certificate over an ambiguous algebraic version space."""

    action_probabilities: tuple[Fraction, Fraction] | None
    minimax_value: Fraction | None
    common_optimal_interval: tuple[Fraction, Fraction] | None
    version_space_size: int
    model_identifiable: bool
    value_identifiable: bool
    policy_identifiable: bool
    finite_list_minimum_distance: int
    candidate_pairs_tested: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class FiniteListFeatureQueryPlan:
    """Outcome-independent query geometry certifying a finite completion list."""

    feature_rows: tuple[tuple[Fraction, ...], ...]
    query_indices: tuple[int, ...]
    feature_rank: int
    feature_width: int
    corruption_budget: int
    erasure_budget: int
    query_count: int
    minimum_distance: int
    candidate_subsets_tested: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class DecisionIdentifiableMultiActionPlan:
    """Exact common-policy certificate for a finite family of robust games."""

    action_probabilities: tuple[Fraction, ...] | None
    minimax_value: Fraction | None
    version_space_size: int
    action_count: int
    model_identifiable: bool
    value_identifiable: bool
    policy_identifiable: bool
    finite_list_minimum_distance: int | None
    impossibility_witness: tuple[int, ...]
    candidate_combinations_tested: int
    certificate_valid: bool
    reason: str
    stacked_value: Fraction | None = None
    ambiguity_gap: Fraction | None = None
    scenario_witness: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class StackedAmbiguityGapCertificate:
    """Exact scalar and sparse witness for multi-completion decision ambiguity."""

    action_probabilities: tuple[Fraction, ...] | None
    common_value: Fraction | None
    stacked_value: Fraction | None
    ambiguity_gap: Fraction | None
    completion_count: int
    action_count: int
    value_identifiable: bool
    policy_identifiable: bool
    scenario_witness: tuple[tuple[int, int], ...]
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


def _two_action_optimal_interval(payoff_matrix, value):
    """Return all action-zero probabilities attaining an exact robust value."""
    lower, upper = Fraction(0), Fraction(1)
    for left, right in zip(payoff_matrix[0], payoff_matrix[1]):
        slope = left - right
        if slope > 0:
            lower = max(lower, (value - right) / slope)
        elif slope < 0:
            upper = min(upper, (value - right) / slope)
        elif right < value:
            return None
    if lower > upper:
        return None
    return lower, upper


def select_finite_list_feature_queries(
    feature_rows,
    *,
    payoff_in_feature_span_certified: bool,
    corruption_budget: int,
    erasure_budget: int = 0,
    max_query_count: int = 12,
    max_candidate_subsets: int = 100_000,
) -> FiniteListFeatureQueryPlan:
    """Select the smallest geometry finite after all certified faults.

    A selected code is accepted exactly when its minimum distance is at least
    ``t + s + 1``.  This is equivalent to retaining full feature rank after
    every deletion of ``t + s`` rows, and guarantees that any realized set of
    at most ``s`` erasures leaves the transcript-level finite-list distance at
    least ``t + 1``.
    """
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    if corruption_budget < 0 or erasure_budget < 0:
        raise ValueError("error and erasure budgets must be nonnegative")
    features = tuple(tuple(Fraction(value) for value in row) for row in feature_rows)
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    width = len(features[0])
    if any(len(row) != width for row in features):
        raise ValueError("feature rows must share one width")
    rank = _fraction_matrix_rank(features)
    if rank == 0:
        raise ValueError("feature rows have zero rank")

    minimum_queries = rank + corruption_budget + erasure_budget
    upper = min(len(features), int(max_query_count))
    tested = 0
    target_distance = corruption_budget + erasure_budget + 1
    for query_count in range(minimum_queries, upper + 1):
        for indices in combinations(range(len(features)), query_count):
            tested += 1
            if tested > int(max_candidate_subsets):
                raise ValueError("finite-list query search limit exceeded")
            rows = tuple(features[index] for index in indices)
            if _fraction_matrix_rank(rows) != rank:
                continue
            distance = _feature_code_minimum_distance(rows, rank)
            if distance >= target_distance:
                return FiniteListFeatureQueryPlan(
                    features,
                    tuple(indices),
                    rank,
                    width,
                    corruption_budget,
                    erasure_budget,
                    query_count,
                    distance,
                    tested,
                    True,
                    "finite_list_error_erasure_geometry_certificate",
                )
    raise ValueError(
        "no query subset within the cap guarantees a finite completion list "
        "under the certified error-erasure budget"
    )


def _solve_multi_action_robust_game(game):
    """Return an exact maximin value and one canonical optimal policy."""
    matrix = tuple(tuple(Fraction(value) for value in row) for row in game)
    if len(matrix) < 2 or not matrix[0]:
        raise ValueError("a robust game needs at least two actions and one scenario")
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("robust-game payoff rows must have equal length")
    action_count = len(matrix)
    scenario_count = len(matrix[0])
    candidates = []
    for support_size in range(1, min(action_count, scenario_count) + 1):
        for support in combinations(range(action_count), support_size):
            for active in combinations(range(scenario_count), support_size):
                rows = [tuple(Fraction(1) for _ in support) + (Fraction(0),)]
                rhs = [Fraction(1)]
                for scenario in active:
                    rows.append(
                        tuple(matrix[action][scenario] for action in support)
                        + (Fraction(-1),)
                    )
                    rhs.append(Fraction(0))
                solved = _solve_fraction_system(tuple(rows), tuple(rhs))
                if solved is None:
                    continue
                weights, value = solved[:-1], solved[-1]
                if any(weight < 0 for weight in weights):
                    continue
                policy = tuple(
                    next((weights[i] for i, action in enumerate(support)
                          if action == target), Fraction(0))
                    for target in range(action_count)
                )
                realized = tuple(
                    sum((policy[action] * matrix[action][scenario]
                         for action in range(action_count)), Fraction(0))
                    for scenario in range(scenario_count)
                )
                if min(realized) >= value:
                    candidates.append((value, policy))
    if not candidates:
        raise RuntimeError("exact robust-game vertex enumeration found no policy")
    value = max(candidate[0] for candidate in candidates)
    policy = min(candidate[1] for candidate in candidates if candidate[0] == value)
    if min(
        sum((policy[action] * matrix[action][scenario]
             for action in range(action_count)), Fraction(0))
        for scenario in range(scenario_count)
    ) != value:
        raise RuntimeError("exact robust-game policy failed replay")
    return value, policy


def _common_optimal_policy(games, values, selected=None):
    """Find an exact point in the selected optimal-policy-polytope intersection."""
    indices = tuple(range(len(games))) if selected is None else tuple(selected)
    action_count = len(games[0])
    constraints = tuple(
        (tuple(games[index][action][scenario] for action in range(action_count)),
         values[index])
        for index in indices
        for scenario in range(len(games[index][0]))
    )
    for support_size in range(1, action_count + 1):
        for support in combinations(range(action_count), support_size):
            active_count = support_size - 1
            for active in combinations(range(len(constraints)), active_count):
                rows = [tuple(Fraction(1) for _ in support)]
                rhs = [Fraction(1)]
                for constraint_index in active:
                    coefficients, bound = constraints[constraint_index]
                    rows.append(tuple(coefficients[action] for action in support))
                    rhs.append(bound)
                solved = _solve_fraction_system(tuple(rows), tuple(rhs))
                if solved is None or any(weight < 0 for weight in solved):
                    continue
                policy = tuple(
                    next((solved[i] for i, action in enumerate(support)
                          if action == target), Fraction(0))
                    for target in range(action_count)
                )
                if all(
                    sum((policy[action] * coefficients[action]
                         for action in range(action_count)), Fraction(0)) >= bound
                    for coefficients, bound in constraints
                ):
                    return policy
    return None


def certify_stacked_ambiguity_gap(games) -> StackedAmbiguityGapCertificate:
    """Reduce common-policy identifiability to one exact stacked robust game.

    When every completion has robust value ``v``, concatenating their scenario
    columns produces value ``v_stack <= v``.  Equality holds exactly when one
    policy is optimal for every completion.  A strict gap has a witness of at
    most ``a`` individual scenario columns for ``a`` actions.
    """
    exact_games = tuple(
        tuple(tuple(Fraction(value) for value in row) for row in game)
        for game in games
    )
    if not exact_games:
        raise ValueError("at least one feasible completion is required")
    action_count = len(exact_games[0])
    if action_count < 2 or any(len(game) != action_count for game in exact_games):
        raise ValueError("all completions must share at least two actions")
    if any(
        not game[0] or any(len(row) != len(game[0]) for row in game)
        for game in exact_games
    ):
        raise ValueError("each completion must be a nonempty rectangular game")

    solved = tuple(_solve_multi_action_robust_game(game) for game in exact_games)
    values = tuple(item[0] for item in solved)
    if len(set(values)) != 1:
        return StackedAmbiguityGapCertificate(
            None,
            None,
            None,
            None,
            len(exact_games),
            action_count,
            False,
            False,
            (),
            True,
            "ambiguous_transcript_has_multiple_robust_values",
        )

    common_value = values[0]
    labelled_columns = tuple(
        (
            (completion, scenario),
            tuple(game[action][scenario] for action in range(action_count)),
        )
        for completion, game in enumerate(exact_games)
        for scenario in range(len(game[0]))
    )
    stacked_game = tuple(
        tuple(column[action] for _, column in labelled_columns)
        for action in range(action_count)
    )
    stacked_value, stacked_policy = _solve_multi_action_robust_game(stacked_game)
    gap = common_value - stacked_value
    if gap < 0:
        raise RuntimeError("stacked robust value exceeded an individual value")
    if gap == 0:
        valid = all(
            min(
                sum(
                    (stacked_policy[action] * game[action][scenario]
                     for action in range(action_count)),
                    Fraction(0),
                )
                for scenario in range(len(game[0]))
            ) == common_value
            for game in exact_games
        )
        return StackedAmbiguityGapCertificate(
            stacked_policy,
            common_value,
            stacked_value,
            gap,
            len(exact_games),
            action_count,
            True,
            True,
            (),
            valid,
            "zero_stacked_ambiguity_gap_common_policy",
        )

    witness: tuple[tuple[int, int], ...] = ()
    witness_value = common_value
    for size in range(1, min(action_count, len(labelled_columns)) + 1):
        for selected in combinations(range(len(labelled_columns)), size):
            selected_game = tuple(
                tuple(labelled_columns[index][1][action] for index in selected)
                for action in range(action_count)
            )
            candidate_value, _ = _solve_multi_action_robust_game(selected_game)
            if candidate_value < common_value:
                witness = tuple(labelled_columns[index][0] for index in selected)
                witness_value = candidate_value
                break
        if witness:
            break
    valid = bool(witness) and len(witness) <= action_count and witness_value < common_value
    return StackedAmbiguityGapCertificate(
        None,
        common_value,
        stacked_value,
        gap,
        len(exact_games),
        action_count,
        True,
        False,
        witness,
        valid,
        "positive_stacked_ambiguity_gap_requires_abstention",
    )


def certify_common_robust_plan(
    games,
    *,
    finite_list_minimum_distance: int | None = None,
    candidate_combinations_tested: int = 0,
) -> DecisionIdentifiableMultiActionPlan:
    """Certify one exact robust policy across a finite completion family."""
    exact_games = tuple(
        tuple(tuple(Fraction(value) for value in row) for row in game)
        for game in games
    )
    if not exact_games:
        raise ValueError("at least one feasible completion is required")
    action_count = len(exact_games[0])
    if action_count < 2 or any(len(game) != action_count for game in exact_games):
        raise ValueError("all completions must share at least two actions")
    if any(not game[0] or any(len(row) != len(game[0]) for row in game)
           for game in exact_games):
        raise ValueError("each completion must be a nonempty rectangular game")
    stacked = certify_stacked_ambiguity_gap(exact_games)
    solved = tuple(_solve_multi_action_robust_game(game) for game in exact_games)
    values = tuple(item[0] for item in solved)
    distinct_values = set(values)
    if len(distinct_values) != 1:
        first = next(
            (0, index) for index in range(1, len(values))
            if values[index] != values[0]
        )
        result = DecisionIdentifiableMultiActionPlan(
            None, None, len(exact_games), action_count, len(exact_games) == 1,
            False, False, finite_list_minimum_distance, first,
            candidate_combinations_tested, True,
            "ambiguous_transcript_has_multiple_robust_values",
        )
        return replace(
            result,
            stacked_value=stacked.stacked_value,
            ambiguity_gap=stacked.ambiguity_gap,
            scenario_witness=stacked.scenario_witness,
        )
    policy = _common_optimal_policy(exact_games, values)
    if policy is None:
        witness = tuple(range(len(exact_games)))
        for size in range(2, min(action_count, len(exact_games)) + 1):
            found = next(
                (subset for subset in combinations(range(len(exact_games)), size)
                 if _common_optimal_policy(exact_games, values, subset) is None),
                None,
            )
            if found is not None:
                witness = found
                break
        valid = len(witness) <= action_count and _common_optimal_policy(
            exact_games, values, witness
        ) is None
        result = DecisionIdentifiableMultiActionPlan(
            None, values[0], len(exact_games), action_count,
            len(exact_games) == 1, True, False, finite_list_minimum_distance,
            witness, candidate_combinations_tested, valid,
            "ambiguous_transcript_has_disjoint_optimal_policy_polytopes",
        )
        return replace(
            result,
            stacked_value=stacked.stacked_value,
            ambiguity_gap=stacked.ambiguity_gap,
            scenario_witness=stacked.scenario_witness,
        )
    valid = all(
        min(
            sum((policy[action] * game[action][scenario]
                 for action in range(action_count)), Fraction(0))
            for scenario in range(len(game[0]))
        ) == values[index]
        for index, game in enumerate(exact_games)
    )
    result = DecisionIdentifiableMultiActionPlan(
        policy, values[0], len(exact_games), action_count,
        len(exact_games) == 1, True, True, finite_list_minimum_distance, (),
        candidate_combinations_tested, valid,
        "decision_identifiable_despite_model_ambiguity"
        if len(exact_games) > 1 else "uniquely_decoded_model",
    )
    return replace(
        result,
        stacked_value=stacked.stacked_value,
        ambiguity_gap=stacked.ambiguity_gap,
        scenario_witness=stacked.scenario_witness,
    )


def certify_multi_action_plan_from_ambiguous_transcript(
    feature_rows,
    query_indices,
    observed_payoffs,
    *,
    payoff_in_feature_span_certified: bool,
    corruption_budget: int,
    erasure_budget: int = 0,
    max_version_space: int = 10_000,
) -> DecisionIdentifiableMultiActionPlan:
    """Enumerate a finite corrupted completion list and certify its decision quotient."""
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    if corruption_budget < 0 or erasure_budget < 0:
        raise ValueError("error and erasure budgets must be nonnegative")
    features = tuple(tuple(Fraction(value) for value in row) for row in feature_rows)
    indices = tuple(int(index) for index in query_indices)
    observations = tuple(
        None if row is None else tuple(Fraction(value) for value in row)
        for row in observed_payoffs
    )
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    if len(indices) != len(observations) or len(set(indices)) != len(indices):
        raise ValueError("query indices and observations must align without duplicates")
    erased = tuple(position for position, row in enumerate(observations) if row is None)
    if len(erased) > erasure_budget:
        raise ValueError("the transcript exceeds the certified erasure budget")
    available = tuple(position for position, row in enumerate(observations) if row is not None)
    if not available:
        raise ValueError("the transcript has no available observations")
    action_count = len(observations[available[0]])
    if action_count < 2 or any(
        row is not None and len(row) != action_count for row in observations
    ):
        raise ValueError("available observations must share at least two actions")
    rank = _fraction_matrix_rank(features)
    available_rows = tuple(features[indices[position]] for position in available)
    if len(available) < rank or _fraction_matrix_rank(available_rows) != rank:
        raise ValueError("available query rows do not span the feature rank")
    distance = _feature_code_minimum_distance(available_rows, rank)
    if distance < corruption_budget + 1:
        raise ValueError(
            "query geometry does not guarantee a finite completion list under "
            "the certified corruption budget"
        )
    width = len(features[0])
    pivots = next(
        (columns for columns in combinations(range(width), rank)
         if _fraction_matrix_rank(tuple(
             tuple(row[column] for column in columns) for row in features
         )) == rank),
        None,
    )
    if pivots is None:
        raise RuntimeError("feature table lacks exact pivot columns")
    reduced = tuple(tuple(row[column] for column in pivots) for row in features)
    action_candidates = []
    for action in range(action_count):
        candidates = {}
        for basis in combinations(available, rank):
            coefficients = _solve_fraction_system(
                tuple(reduced[indices[position]] for position in basis),
                tuple(observations[position][action] for position in basis),
            )
            if coefficients is None:
                continue
            predictions = tuple(
                sum((value * coefficient for value, coefficient in zip(row, coefficients)),
                    Fraction(0))
                for row in reduced
            )
            disagreements = frozenset(
                position for position in available
                if predictions[indices[position]] != observations[position][action]
            )
            if len(disagreements) <= corruption_budget:
                candidates[predictions] = disagreements
        action_candidates.append(tuple(candidates.items()))
    version_space = {}
    tested = 0
    for candidate_tuple in product(*action_candidates):
        tested += 1
        if tested > max_version_space:
            raise ValueError("decision version-space cap exceeded")
        disagreements = frozenset().union(
            *(candidate[1] for candidate in candidate_tuple)
        )
        if len(disagreements) <= corruption_budget:
            version_space[tuple(candidate[0] for candidate in candidate_tuple)] = disagreements
    if not version_space:
        raise ValueError("no feature-span completion matches the certified transcript")
    return certify_common_robust_plan(
        tuple(version_space),
        finite_list_minimum_distance=distance,
        candidate_combinations_tested=tested,
    )


def certify_two_action_plan_from_ambiguous_transcript(
    feature_rows,
    query_indices,
    observed_payoffs,
    *,
    payoff_in_feature_span_certified: bool,
    corruption_budget: int,
    erasure_budget: int = 0,
    max_version_space: int = 10_000,
) -> DecisionIdentifiableTwoActionPlan:
    """Plan exactly when every feasible corrupted completion agrees on a policy.

    Unlike unique decoding, this routine keeps every feature-span completion
    within the shared row-corruption budget.  It then applies the necessary and
    sufficient two-action decision quotient: invariant value plus intersecting
    exact optimal-policy intervals.
    """
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    if corruption_budget < 0 or erasure_budget < 0:
        raise ValueError("error and erasure budgets must be nonnegative")
    features = tuple(tuple(Fraction(value) for value in row) for row in feature_rows)
    indices = tuple(int(index) for index in query_indices)
    observations = tuple(
        None if row is None else tuple(Fraction(value) for value in row)
        for row in observed_payoffs
    )
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    if len(indices) != len(observations) or len(set(indices)) != len(indices):
        raise ValueError("query indices and observations must align without duplicates")
    if any(index < 0 or index >= len(features) for index in indices):
        raise ValueError("query index is outside the feature table")
    if any(row is not None and len(row) != 2 for row in observations):
        raise ValueError("each available observation must contain exactly two actions")
    erased = tuple(position for position, row in enumerate(observations) if row is None)
    if len(erased) > erasure_budget:
        raise ValueError("the transcript exceeds the certified erasure budget")
    available = tuple(position for position, row in enumerate(observations) if row is not None)
    rank = _fraction_matrix_rank(features)
    if len(available) < rank:
        raise ValueError("too few available rows span the feature rank")
    available_rows = tuple(features[indices[position]] for position in available)
    if _fraction_matrix_rank(available_rows) != rank:
        raise ValueError("available query rows do not span the feature rank")
    finite_list_distance = _feature_code_minimum_distance(available_rows, rank)
    if finite_list_distance < corruption_budget + 1:
        raise ValueError(
            "query geometry does not guarantee a finite completion list under "
            "the certified corruption budget"
        )
    width = len(features[0])
    pivots = next(
        (
            columns
            for columns in combinations(range(width), rank)
            if _fraction_matrix_rank(
                tuple(tuple(row[column] for column in columns) for row in features)
            ) == rank
        ),
        None,
    )
    if pivots is None:
        raise RuntimeError("feature table lacks exact pivot columns")
    reduced = tuple(tuple(row[column] for column in pivots) for row in features)

    action_candidates = []
    for action in range(2):
        candidates = {}
        for basis_positions in combinations(available, rank):
            coefficients = _solve_fraction_system(
                tuple(reduced[indices[position]] for position in basis_positions),
                tuple(observations[position][action] for position in basis_positions),
            )
            if coefficients is None:
                continue
            predictions = tuple(
                sum((value * coefficient for value, coefficient in zip(row, coefficients)),
                    Fraction(0))
                for row in reduced
            )
            disagreements = frozenset(
                position for position in available
                if predictions[indices[position]] != observations[position][action]
            )
            if len(disagreements) <= corruption_budget:
                candidates[predictions] = disagreements
        action_candidates.append(tuple(candidates.items()))

    version_space = {}
    tested = 0
    for left, right in product(*action_candidates):
        tested += 1
        if tested > max_version_space:
            raise ValueError("decision version-space cap exceeded")
        if len(left[1] | right[1]) <= corruption_budget:
            version_space[(left[0], right[0])] = left[1] | right[1]
    if not version_space:
        raise ValueError("no feature-span completion matches the certified transcript")

    games = tuple(version_space)
    solutions = tuple(solve_two_action_robust_game(game) for game in games)
    if any(not solution.certificate_valid for solution in solutions):
        raise RuntimeError("an exact robust-game certificate failed")
    values = {solution.minimax_value for solution in solutions}
    intervals = tuple(
        _two_action_optimal_interval(game, solution.minimax_value)
        for game, solution in zip(games, solutions)
    )
    if any(interval is None for interval in intervals):
        raise RuntimeError("an exact optimal-policy interval failed")
    common_lower = max(interval[0] for interval in intervals if interval is not None)
    common_upper = min(interval[1] for interval in intervals if interval is not None)
    value_identifiable = len(values) == 1
    policy_identifiable = value_identifiable and common_lower <= common_upper
    if not policy_identifiable:
        reason = (
            "ambiguous_transcript_has_multiple_robust_values"
            if not value_identifiable
            else "ambiguous_transcript_has_disjoint_optimal_policy_sets"
        )
        return DecisionIdentifiableTwoActionPlan(
            None, None, None, len(games), len(games) == 1, value_identifiable,
            False, finite_list_distance, tested, True, reason,
        )

    weight = common_lower
    value = next(iter(values))
    valid = all(
        min(weight * game[0][scenario] + (1 - weight) * game[1][scenario]
            for scenario in range(len(features))) == value
        for game in games
    )
    return DecisionIdentifiableTwoActionPlan(
        (weight, 1 - weight), value, (common_lower, common_upper), len(games),
        len(games) == 1, True, True, finite_list_distance, tested, valid,
        "decision_identifiable_despite_model_ambiguity"
        if len(games) > 1 else "uniquely_decoded_model",
    )


def reconstruct_corruption_resilient_feature_payoffs(
    feature_rows,
    scenario_oracle,
    *,
    payoff_in_feature_span_certified: bool,
    corruption_budget: int,
    erasure_budget: int = 0,
    max_query_count: int = 12,
    max_candidate_subsets: int = 100_000,
) -> CorruptionResilientFeatureReconstruction:
    """Recover feature-span payoffs despite bounded adversarial query errors.

    Query selection is outcome-independent. A set is accepted exactly when its
    rational evaluation code has minimum distance at least ``2t + s + 1``,
    where ``s`` is the number of explicitly missing responses tolerated.
    """
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    if corruption_budget < 0:
        raise ValueError("corruption budget must be nonnegative")
    if erasure_budget < 0:
        raise ValueError("erasure budget must be nonnegative")
    features = tuple(tuple(Fraction(value) for value in row) for row in feature_rows)
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    width = len(features[0])
    if any(len(row) != width for row in features):
        raise ValueError("feature rows must share one width")
    rank = _fraction_matrix_rank(features)
    if rank == 0:
        raise ValueError("feature rows have zero rank")

    minimum_queries = rank + 2 * corruption_budget + erasure_budget
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
            if distance >= 2 * corruption_budget + erasure_budget + 1:
                selected = indices
                selected_distance = distance
                break
        if selected is not None:
            break
    if selected is None:
        raise ValueError(
            "no query subset within the cap corrects the certified error-erasure budget"
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
    available_positions = []
    erased = []
    for index in selected:
        raw_response = scenario_oracle(index)
        if raw_response is None:
            erased.append(index)
            queried.append(None)
            continue
        response = tuple(
            tuple(Fraction(value) for value in component)
            for component in raw_response
        )
        if not response or any(not component for component in response):
            raise ValueError("the scenario oracle returned an empty payoff shape")
        available_positions.append(len(queried))
        queried.append(response)
    if len(erased) > erasure_budget:
        raise ValueError("the scenario oracle exceeded the certified erasure budget")
    first_available = next(
        (response for response in queried if response is not None), None
    )
    if first_available is None:
        raise ValueError("the scenario oracle erased every selected response")
    shape = tuple(len(component) for component in first_available)
    if any(
        tuple(len(component) for component in response) != shape for response in queried
        if response is not None
    ):
        raise ValueError("the scenario oracle returned inconsistent payoff shapes")

    decoded = [[None for _ in range(action_count)] for action_count in shape]
    corrected = set()
    for component, action_count in enumerate(shape):
        for action in range(action_count):
            observations = tuple(
                queried[position][component][action]
                for position in available_positions
            )
            candidates = {}
            for basis_indices in combinations(available_positions, rank):
                matrix = tuple(reduced_rows[position] for position in basis_indices)
                coefficients = _solve_fraction_system(
                    matrix,
                    tuple(
                        queried[position][component][action]
                        for position in basis_indices
                    ),
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
                    for position, observed in zip(available_positions, observations)
                    if query_predictions[position] != observed
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
        if scenario not in corrected and scenario not in erased
        for component in range(len(shape))
        for action in range(shape[component])
    )
    return CorruptionResilientFeatureReconstruction(
        component_payoff_vectors=reconstructed,
        feature_rows=features,
        query_indices=tuple(selected),
        pivot_columns=tuple(pivots),
        corrected_query_indices=tuple(sorted(corrected)),
        erased_query_indices=tuple(sorted(erased)),
        feature_rank=rank,
        feature_width=width,
        scenario_count=len(features),
        corruption_budget=corruption_budget,
        erasure_budget=erasure_budget,
        query_count=len(selected),
        minimum_distance=selected_distance,
        candidate_subsets_tested=tested,
        certificate_valid=valid,
        reason="exact_adversarial_feature_code_decoding_certificate",
    )
