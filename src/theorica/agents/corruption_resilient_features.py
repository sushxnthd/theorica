Warning: truncated output (original token count: 27339)
Total output lines: 3071

"""Exact feature-span reconstruction under bounded adversarial query errors."""

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations, product
from math import comb

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
    adversary_scenario_weights: tuple[tuple[int, int, Fraction], ...] = ()
    adversary_action_payoffs: tuple[Fraction, ...] = ()
    stacked_action_probabilities: tuple[Fraction, ...] | None = None


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
    adversary_scenario_weights: tuple[tuple[int, int, Fraction], ...] = ()
    adversary_action_payoffs: tuple[Fraction, ...] = ()
    stacked_action_probabilities: tuple[Fraction, ...] | None = None


@dataclass(frozen=True)
class DecisionQueryNode:
    """One node in an exact adaptive decision-identification query tree."""

    completion_indices: tuple[int, ...]
    query_index: int | None
    action_probabilities: tuple[Fraction, ...] | None
    minimax_value: Fraction | None
    children: tuple[tuple[object, "DecisionQueryNode"], ...] = ()


@dataclass(frozen=True)
class DecisionQueryPlan:
    """Minimum worst-case query plan for identifying a robust decision."""

    root: DecisionQueryNode | None
    worst_case_depth: int | None
    completion_count: int
    query_count: int
    states_solved: int
    policy_identifiable_without_queries: bool
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class DecisionCorruptionRadiusCertificate:
    """Exact adversarial-error radius of a fixed decision-query code."""

    decision_radius: int | None
    max_certified_corruptions: int | None
    corruption_budget: int
    robust_to_budget: bool
    completion_count: int
    query_count: int
    action_count: int
    closest_incompatible_center: tuple[object, ...]
    incompatibility_witness: tuple[int, ...]
    minimal_witnesses_tested: int
    centers_tested: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class AdaptiveDecisionLieNode:
    """One state in an exact adaptive decision tree with bounded lies."""

    lie_counts: tuple[int, ...]
    feasible_completion_indices: tuple[int, ...]
    query_index: int | None
    action_probabilities: tuple[Fraction, ...] | None
    minimax_value: Fraction | None
    children: tuple[tuple[object, "AdaptiveDecisionLieNode"], ...] = ()


@dataclass(frozen=True)
class AdaptiveDecisionLiePlan:
    """Exact minimum-depth decision query policy against answer substitutions."""

    root: AdaptiveDecisionLieNode | None
    worst_case_depth: int | None
    corruption_budget: int
    completion_count: int
    query_count: int
    states_solved: int
    compatibility_states_solved: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class AdaptiveDecisionFaultNode:
    """One state in an exact adaptive tree with substitutions and erasures."""

    lie_counts: tuple[int, ...]
    erasures_used: int
    feasible_completion_indices: tuple[int, ...]
    query_index: int | None
    action_probabilities: tuple[Fraction, ...] | None
    minimax_value: Fraction | None
    children: tuple[tuple[object | None, "AdaptiveDecisionFaultNode"], ...] = ()


@dataclass(frozen=True)
class AdaptiveDecisionFaultPlan:
    """Exact minimum-depth decision policy under substitutions and erasures."""

    root: AdaptiveDecisionFaultNode | None
    worst_case_depth: int | None
    corruption_budget: int
    erasure_budget: int
    completion_count: int
    query_count: int
    states_solved: int
    compatibility_states_solved: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class AdaptiveDecisionWeightedFaultPlan:
    """Exact minimum-cost decision policy under substitutions and erasures."""

    root: AdaptiveDecisionFaultNode | None
    worst_case_cost: int | None
    worst_case_depth: int | None
    corruption_budget: int
    erasure_budget: int
    completion_count: int
    query_count: int
    states_solved: int
    compatibility_states_solved: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class QaryTwoLevelInsuranceCertificate:
    """Closed-form weighted certificate for one substitution and erasure."""

    arity: int
    root_cost: int
    child_cost: int
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_regime: str
    certificate_valid: bool


@dataclass(frozen=True)
class QaryThreeLevelInsuranceCertificate:
    """Six-face weighted certificate with an explicit policy-class scope."""

    arity: int
    level_costs: tuple[int, int, int]
    adversary_lower_bounds: tuple[int, int, int, int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryThreeLevelMiddleFirstCertificate:
    """Candidate six-face law conditioned on a middle-level first query."""

    level_costs: tuple[int, int, int]
    adversary_lower_bounds: tuple[int, int, int, int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstSymmetricCertificate:
    """Exact middle-first law when root and middle queries have equal cost."""

    root_middle_cost: int
    leaf_cost: int
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class TernaryMiddleFirstSymmetricCertificate:
    """Exact equal-level-cost law for ternary middle-first planning."""

    level_cost: int
    arity: int
    exact_worst_case_cost: int
    exact_worst_case_depth: int
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class TernaryMiddleFirstAncestorSymmetricCertificate:
    """Exact ternary law when root and middle query costs are equal."""

    root_middle_cost: int
    leaf_cost: int
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class TernaryMiddleFirstDescendantSymmetricCertificate:
    """Exact ternary law when middle and leaf query costs are equal."""

    root_cost: int
    middle_leaf_cost: int
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstRatioTwoCertificate:
    """Exact middle-first law when one ancestor level costs twice the other."""

    doubled_level: str
    base_cost: int
    leaf_cost: int
    level_costs: tuple[int, int, int]
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstIntegerRatioCertificate:
    """Exact middle-first law for an integer ancestor-cost ratio at least two."""

    heavy_level: str
    cost_ratio: int
    base_cost: int
    leaf_cost: int
    level_costs: tuple[int, int, int]
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstRationalRatioCertificate:
    """Exact middle-first law for a rational ancestor-cost ratio at least two."""

    heavy_level: str
    ratio_numerator: int
    ratio_denominator: int
    unit_cost: int
    leaf_cost: int
    level_costs: tuple[int, int, int]
    projected_face_vectors: tuple[tuple[int, int], ...]
    adversary_lower_bounds: tuple[int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    phase_boundaries: tuple[str, str]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstAllRatioLowerBoundCertificate:
    """Universal adversarial lower bound for every positive ancestor ratio."""

    ratio_numerator: int
    ratio_denominator: int
    unit_cost: int
    leaf_cost: int
    level_costs: tuple[int, int, int]
    exposure_vectors: tuple[tuple[int, int, int], ...]
    adversary_lower_bounds: tuple[int, int, int, int, int, int]
    certified_lower_bound: int
    active_faces: tuple[str, ...]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class BinaryMiddleFirstAllCostCertificate:
    """Exact middle-first law for every positive three-level cost triple."""

    level_costs: tuple[int, int, int]
    exposure_vectors: tuple[tuple[int, int, int], ...]
    adversary_lower_bounds: tuple[int, int, int, int, int, int]
    exact_worst_case_cost: int
    active_faces: tuple[str, ...]
    certificate_valid: bool
    policy_class: str


@dataclass(frozen=True)
class ThreeLevelMonotonicityCertificate:
    """Impossibility witness for a lower face that exceeds a feasible policy."""

    arity: int
    level_costs: tuple[int, int, int]
    feasible_root_respecting_cost: int
    retired_bypass_face_cost: int
    lower_face_impossible: bool
    analytic_violation_cone: bool
    leaf_margin: int
    middle_margin: int
    certificate_valid: bool


@dataclass(frozen=True)
class QaryRootRespectingInsuranceCertificate:
    """Arbitrary-depth max-plus certificate for root-respecting policies."""

    arity: int
    level_costs: tuple[int, ...]
    available_copies: tuple[int, ...]
    face_vectors: tuple[tuple[int, ...], ...]
    face_costs: tuple[int, ...]
    exact_worst_case_cost: int | None
    recurrence_cost: int | None
    active_face_vectors: tuple[tuple[int, ...], ...]
    certificate_valid: bool
    reason: str


def certify_qary_two_level_insurance(
    arity: int,
    root_cost: int,
    child_cost: int,
) -> QaryTwoLevelInsuranceCertificate:
    """Return the sharp two-level cost law for one substitution and erasure."""
    if arity < 2:
        raise ValueError("arity must be at least two")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in (root_cost, child_cost)
    ):
        raise ValueError("query costs must be positive integers")
    bounds = (
        2 * root_cost + 4 * child_cost,
        3 * root_cost + 3 * child_cost,
        4 * root_cost + child_cost,
    )
    if root_cost <= child_cost:
        regime = "child_expensive_or_equal"
    elif root_cost <= 2 * child_cost:
        regime = "intermediate_insurance"
    else:
        regime = "root_expensive"
    return QaryTwoLevelInsuranceCertificate(
        arity,
        root_cost,
        child_cost,
        bounds,
        max(bounds),
        regime,
        True,
    )


def certify_qary_three_level_insurance(
    arity: int,
    root_cost: int,
    middle_cost: int,
    leaf_cost: int,
) -> QaryThreeLevelInsuranceCertificate:
    """Return the corrected six-face depth-three insurance certificate.

    Each affine face is the price of an adversarial transcript class with a
    different level at which conflicts expose the global fault budget.  Taking
    their maximum is the root-respecting exact cost for q-ary prefixes. The
    previously asserted unrestricted q-ary interpretation is deliberately not
    encoded by this certificate; separate exact searches may validate bounded
    unrestricted instances.
    """
    if arity < 2:
        raise ValueError("arity must be at least two")
    costs = (root_cost, middle_cost, leaf_cost)
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    a, b, c = costs
    names = (
        "leaf_faults_hidden",
        "late_partial_exposure",
        "middle_insurance",
        "early_partial_exposure",
        "root_middle_insurance",
        "root_faults_hidden",
    )
    bounds = (
        2 * a + 2 * b + 4 * c,
        2 * a + 3 * b + 3 * c,
        2 * a + 4 * b + c,
        3 * a + 2 * b + 3 * c,
        3 * a + 3 * b + c,
        4 * a + b + c,
    )
    optimum = max(bounds)
    return QaryThreeLevelInsuranceCertificate(
        arity,
        costs,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        True,
        "root_respecting_qary",
    )


def certify_binary_three_level_middle_first(
    root_cost: int,
    middle_cost: int,
    leaf_cost: int,
) -> BinaryThreeLevelMiddleFirstCertificate:
    """Return the prospective binary middle-first conditioned cost law.

    The first physical query is required to be at the middle level, while all
    later adaptive actions remain unrestricted. This deliberately does not
    claim unrestricted or q-ary exactness.
    """
    costs = (root_cost, middle_cost, leaf_cost)
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    a, b, c = costs
    names = (
        "middle_frontloaded",
        "leaf_heavy_after_middle",
        "middle_leaf_transition",
        "balanced_exposure",
        "root_middle_transition",
        "root_heavy_after_middle",
    )
    bounds = (
        a + 5 * b + c,
        2 * a + 3 * b + 4 * c,
        2 * a + 4 * b + 3 * c,
        3 * a + 3 * b + 3 * c,
        3 * a + 4 * b + c,
        4 * a + 2 * b + c,
    )
    optimum = max(bounds)
    return BinaryThreeLevelMiddleFirstCertificate(
        costs,
        bounds,
        optimum,
        tuple(name for name, value in zip(names, bounds) if value == optimum),
        True,
        "binary_middle_first",
    )


def certify_binary_middle_first_symmetric(
    root_middle_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstSymmetricCertificate:
    """Return the proved exact law on the ``root_cost == middle_cost`` slice.

    Projecting transcript exposure ``(r, m, l)`` to ``(r + m, l)`` gives the
    complete maximal adversary antichain ``(7,1), (6,3), (5,4)``.  Matching
    policies are certified on the three cones separated by ``x=y`` and
    ``x=2y``.  The result is exact for the binary, four-copy, middle-first
    conditioned class only.
    """
    costs = (root_middle_cost, leaf_cost)
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    x, y = costs
    vectors = ((7, 1), (6, 3), (5, 4))
    names = (
        "root_middle_heavy",
        "transition",
        "leaf_heavy",
    )
    bounds = tuple(a * x + b * y for a, b in vectors)
    optimum = max(bounds)
    return BinaryMiddleFirstSymmetricCertificate(
        x,
        y,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("x=y", "x=2y"),
        True,
        "binary_middle_first_symmetric",
    )


def certify_ternary_middle_first_symmetric(
    level_cost: int,
) -> TernaryMiddleFirstSymmetricCertificate:
    """Return the exact ternary equal-cost middle-first certificate.

    The unit-cost ternary problem has exact robust query depth nine.  Positive
    equal level costs scale every transcript by ``level_cost``.  The guarantee
    is restricted to arity three, depth three, four copies, one substitution,
    one erasure, and a middle-level initial query.
    """
    if isinstance(level_cost, bool) or not isinstance(level_cost, int) or level_cost < 1:
        raise ValueError("level cost must be a positive integer")
    return TernaryMiddleFirstSymmetricCertificate(
        level_cost,
        3,
        9 * level_cost,
        9,
        True,
        "ternary_middle_first_equal_level_costs",
    )


def certify_ternary_middle_first_ancestor_symmetric(
    root_middle_cost: int,
    leaf_cost: int,
) -> TernaryMiddleFirstAncestorSymmetricCertificate:
    """Return the exact ternary middle-first law for costs ``(x,x,y)``.

    One depth-nine ternary policy satisfies the complete extreme-ray budgets
    for all three cost cones.  The binary completion embedding supplies the
    matching lower faces.
    """
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in (root_middle_cost, leaf_cost)
    ):
        raise ValueError("query costs must be positive integers")
    x, y = root_middle_cost, leaf_cost
    vectors = ((7, 1), (6, 3), (5, 4))
    names = ("ancestor_heavy", "transition", "leaf_heavy")
    bounds = tuple(a * x + b * y for a, b in vectors)
    optimum = max(bounds)
    return TernaryMiddleFirstAncestorSymmetricCertificate(
        x,
        y,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("x=y", "x=2y"),
        True,
        "ternary_middle_first_equal_ancestor_costs",
    )


def certify_ternary_middle_first_descendant_symmetric(
    root_cost: int,
    middle_leaf_cost: int,
) -> TernaryMiddleFirstDescendantSymmetricCertificate:
    """Return the exact ternary middle-first law for costs ``(x,y,y)``.

    The frozen depth-nine ternary policy satisfies all extreme-ray budgets of
    the three projected cost cones.  The embedded binary completion family
    supplies matching lower faces.
    """
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in (root_cost, middle_leaf_cost)
    ):
        raise ValueError("query costs must be positive integers")
    x, y = root_cost, middle_leaf_cost
    vectors = ((2, 7), (3, 6), (4, 3))
    names = ("descendant_heavy", "transition", "root_heavy")
    bounds = tuple(a * x + b * y for a, b in vectors)
    optimum = max(bounds)
    return TernaryMiddleFirstDescendantSymmetricCertificate(
        x,
        y,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("x=y", "x=3y"),
        True,
        "ternary_middle_first_equal_descendant_costs",
    )


def certify_binary_middle_first_ratio_two(
    doubled_level: str,
    base_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstRatioTwoCertificate:
    """Return either proved binary middle-first ratio-two slice.

    ``doubled_level`` is ``"root"`` for costs ``(2x,x,y)`` or ``"middle"``
    for costs ``(x,2x,y)``. Exact projected adversary antichains and matching
    two-budget boundary policies certify all three cones separated by
    ``y=x/2`` and ``y=2x``.
    """
    if doubled_level not in {"root", "middle"}:
        raise ValueError("doubled_level must be 'root' or 'middle'")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in (base_cost, leaf_cost)
    ):
        raise ValueError("query costs must be positive integers")
    x, y = base_cost, leaf_cost
    if doubled_level == "root":
        level_costs = (2 * x, x, y)
        vectors = ((10, 1), (9, 3), (7, 4))
    else:
        level_costs = (x, 2 * x, y)
        vectors = ((11, 1), (10, 3), (8, 4))
    names = ("ancestor_heavy", "transition", "leaf_heavy")
    bounds = tuple(a * x + b * y for a, b in vectors)
    optimum = max(bounds)
    return BinaryMiddleFirstRatioTwoCertificate(
        doubled_level,
        x,
        y,
        level_costs,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("y=x/2", "y=2x"),
        True,
        "binary_middle_first_ratio_two",
    )


def certify_binary_middle_first_integer_ratio(
    heavy_level: str,
    cost_ratio: int,
    base_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstIntegerRatioCertificate:
    """Return the proved exact law for integer ``cost_ratio >= 2``.

    ``heavy_level`` is ``"root"`` for costs ``(kx,x,y)`` or ``"middle"``
    for costs ``(x,kx,y)``. The exact phase boundaries are
    ``y=(k-1)x/2`` and ``y=kx``.
    """
    if heavy_level not in {"root", "middle"}:
        raise ValueError("heavy_level must be 'root' or 'middle'")
    if (
        isinstance(cost_ratio, bool)
        or not isinstance(cost_ratio, int)
        or cost_ratio < 2
    ):
        raise ValueError("cost_ratio must be an integer at least two")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in (base_cost, leaf_cost)
    ):
        raise ValueError("query costs must be positive integers")
    k, x, y = cost_ratio, base_cost, leaf_cost
    if heavy_level == "root":
        level_costs = (k * x, x, y)
        vectors = ((4 * k + 2, 1), (3 * k + 3, 3), (2 * k + 3, 4))
    else:
        level_costs = (x, k * x, y)
        vectors = ((5 * k + 1, 1), (4 * k + 2, 3), (3 * k + 2, 4))
    names = ("ancestor_heavy", "transition", "leaf_heavy")
    bounds = tuple(a * x + b * y for a, b in vectors)
    optimum = max(bounds)
    return BinaryMiddleFirstIntegerRatioCertificate(
        heavy_level,
        k,
        x,
        y,
        level_costs,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("2y=(k-1)x", "y=kx"),
        True,
        "binary_middle_first_integer_ratio",
    )


def certify_binary_middle_first_rational_ratio(
    heavy_level: str,
    ratio_numerator: int,
    ratio_denominator: int,
    unit_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstRationalRatioCertificate:
    """Return the exact law for rational ratio ``p/q >= 2``.

    ``heavy_level`` is ``"root"`` for costs ``(pu,qu,y)`` or ``"middle"``
    for costs ``(qu,pu,y)``. Inputs remain integral while representing every
    positive rational ancestor-cost ratio in the proved domain.
    """
    if heavy_level not in {"root", "middle"}:
        raise ValueError("heavy_level must be 'root' or 'middle'")
    values = (ratio_numerator, ratio_denominator, unit_cost, leaf_cost)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError("ratio and query-cost inputs must be integers")
    p, q, unit, leaf = values
    if q < 1 or p < 2 * q:
        raise ValueError("ratio_numerator/ratio_denominator must be at least two")
    if unit < 1 or leaf < 1:
        raise ValueError("query costs must be positive integers")
    if heavy_level == "root":
        level_costs = (p * unit, q * unit, leaf)
        vectors = (
            (4 * p + 2 * q, 1),
            (3 * p + 3 * q, 3),
            (2 * p + 3 * q, 4),
        )
    else:
        level_costs = (q * unit, p * unit, leaf)
        vectors = (
            (5 * p + q, 1),
            (4 * p + 2 * q, 3),
            (3 * p + 2 * q, 4),
        )
    names = ("ancestor_heavy", "transition", "leaf_heavy")
    bounds = tuple(a * unit + b * leaf for a, b in vectors)
    optimum = max(bounds)
    return BinaryMiddleFirstRationalRatioCertificate(
        heavy_level,
        p,
        q,
        unit,
        leaf,
        level_costs,
        vectors,
        bounds,
        optimum,
        tuple(name for name, bound in zip(names, bounds) if bound == optimum),
        ("2y=(p-q)u", "y=pu"),
        True,
        "binary_middle_first_rational_ratio",
    )


def certify_binary_middle_first_all_ratio_lower_bound(
    ratio_numerator: int,
    ratio_denominator: int,
    unit_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstAllRatioLowerBoundCertificate:
    """Return the proved six-face lower bound for every positive ratio.

    Costs are ``(p*u, q*u, y)``.  The exact affine decision-trace partition
    proves that these six exposure vectors generate the complete projected
    adversary antichain for all positive rational ``p/q``.  This certificate
    is deliberately a lower/impossibility boundary: universal matching upper
    policies are not claimed in the moderate-ratio regime.
    """
    values = (ratio_numerator, ratio_denominator, unit_cost, leaf_cost)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError("ratio and query-cost inputs must be integers")
    p, q, unit, leaf = values
    if p < 1 or q < 1:
        raise ValueError("ratio numerator and denominator must be positive")
    if unit < 1 or leaf < 1:
        raise ValueError("query costs must be positive integers")
    level_costs = (p * unit, q * unit, leaf)
    vectors = (
        (1, 5, 1),
        (2, 3, 4),
        (2, 4, 3),
        (3, 3, 3),
        (3, 4, 1),
        (4, 2, 1),
    )
    names = (
        "middle_frontloaded",
        "leaf_heavy_after_middle",
        "middle_leaf_transition",
        "balanced_exposure",
        "root_middle_transition",
        "root_heavy_after_middle",
    )
    bounds = tuple(
        (root * p + middle * q) * unit + leaves * leaf
        for root, middle, leaves in vectors
    )
    lower_bound = max(bounds)
    return BinaryMiddleFirstAllRatioLowerBoundCertificate(
        p,
        q,
        unit,
        leaf,
        level_costs,
        vectors,
        bounds,
        lower_bound,
        tuple(name for name, value in zip(names, bounds) if value == lower_bound),
        True,
        "binary_middle_first_all_ratio_lower_bound",
    )


def certify_binary_middle_first_all_costs(
    root_cost: int,
    middle_cost: int,
    leaf_cost: int,
) -> BinaryMiddleFirstAllCostCertificate:
    """Return the exact law for all positive three-level query costs.

    The complete affine adversary antichain gives the six lower faces. Five
    face-active cones have one matching policy each. The exceptional
    ``(3,4,1)`` cone is covered by a six-cell policy fan whose zero-leaf edge
    breaks at ancestor ratios ``1/2, 2/3, 1, 3/2, 2``.
    """
    costs = (root_cost, middle_cost, leaf_cost)
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    vectors = (
        (1, 5, 1),
        (2, 3, 4),
        (2, 4, 3),
        (3, 3, 3),
        (3, 4, 1),
        (4, 2, 1),
    )
    names = (
        "middle_frontloaded",
        "leaf_heavy_after_middle",
        "middle_leaf_transition",
        "balanced_exposure",
        "root_middle_transition",
        "root_heavy_after_middle",
    )
    bounds = tuple(
        sum(exposure * cost for exposure, cost in zip(vector, costs))
        for vector in vectors
    )
    optimum = max(bounds)
    return BinaryMiddleFirstAllCostCertificate(
        costs,
        vectors,
        bounds,
        optimum,
        tuple(name for name, value in zip(names, bounds) if value == optimum),
        True,
        "binary_middle_first_all_positive_costs",
    )


def certify_three_level_monotonicity(
    arity: int,
    root_cost: int,
    middle_cost: int,
    leaf_cost: int,
) -> ThreeLevelMonotonicityCertificate:
    """Reject the retired ``(0,4,2)`` face exactly on its violation cone.

    The complete root-respecting class is a subset of the unrestricted class,
    so its exact cost is an executable upper bound on the unrestricted optimum.
    The alleged lower face ``4b+2c`` exceeds that upper bound exactly when
    ``c > 2a`` and ``b > 2a+c``.  On this cone it cannot be a valid adversarial
    lower certificate for any arity.
    """
    certificate = certify_qary_three_level_insurance(
        arity,
        root_cost,
        middle_cost,
        leaf_cost,
    )
    a, b, c = certificate.level_costs
    retired = 4 * b + 2 * c
    impossible = retired > certificate.exact_worst_case_cost
    cone = c > 2 * a and b > 2 * a + c
    return ThreeLevelMonotonicityCertificate(
        arity,
        certificate.level_costs,
        certificate.exact_worst_case_cost,
        retired,
        impossible,
        cone,
        c - 2 * a,
        b - (2 * a + c),
        impossible == cone,
    )


def certify_qary_root_respecting_insurance(
    arity: int,
    level_costs,
    *,
    available_copies=None,
) -> QaryRootRespectingInsuranceCertificate:
    """Certify the exact arbitrary-depth root-respecting insurance cost.

    The policy resolves each current prefix before querying a strict
    descendant.  Its adversarial paths either hide both faults until one level
    (a single coefficient ``4``), or expose the erasure and substitution at
    two levels (two coefficients ``3``).  Earlier levels cost two copies and
    levels after both exposures cost one.
    """
    if arity < 2:
        raise ValueError("arity must be at least two")
    costs = tuple(level_costs)
    if not costs:
        raise ValueError("at least one level cost is required")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    copies = (4,) * len(costs) if available_copies is None else tuple(available_copies)
    if len(copies) != len(costs):
        raise ValueError("available_copies must align with level_costs")
    if any(
        isinstance(count, bool) or not isinstance(count, int) or count < 0
        for count in copies
    ):
        raise ValueError("available copy counts must be nonnegative integers")

    depth = len(costs)
    faces = []
    for hidden in range(depth):
        faces.append((2,) * hidden + (4,) + (1,) * (depth - hidden - 1))
    for erasure_hidden in range(depth - 1):
        for substitution_hidden in range(depth - erasure_hidden - 1):
            faces.append(
                (2,) * erasure_hidden
                + (3,)
                + (2,) * substitution_hidden
                + (3,)
                + (1,) * (depth - erasure_hidden - substitution_hidden - 2)
            )
    face_vectors = tuple(faces)
    face_costs = tuple(
        sum(coefficient * cost for coefficient, cost in zip(face, costs))
        for face in face_vectors
    )

    no_fault = costs[-1]
    substitution = 3 * costs[-1]
    mixed = 4 * costs[-1]
    for cost in reversed(costs[:-1]):
        mixed = max(2 * cost + mixed, 3 * cost + substitution, 4 * cost + no_fault)
        substitution = max(2 * cost + substitution, 3 * cost + no_fault)
        no_fault = cost + no_fault
    face_maximum = max(face_costs)
    active = tuple(
        face for face, value in zip(face_vectors, face_costs) if value == face_maximum
    )
    enough_copies = all(count >= 4 for count in copies)
    valid = (
        enough_copies
        and len(face_vectors) == depth * (depth + 1) // 2
        and face_maximum == mixed
    )
    return QaryRootRespectingInsuranceCertificate(
        arity,
        costs,
        copies,
        face_vectors,
        face_costs,
        face_maximum if valid else None,
        mixed if enough_copies else None,
        active if valid else (),
        valid,
        (
            "exact_root_respecting_fault_budget_insurance"
            if valid
            else "fewer_than_four_copies_cannot_certify_root_respecting_policy"
        ),
    )


def qary_prefix_query_library(
    arity: int,
    depth: int,
    *,
    copies: int = 3,
) -> tuple[tuple[int, ...], ...]:
    """Construct the q-ary prefix-query family used by the adaptive lie law.

    Completions are lexicographically indexed length-``depth`` q-ary words.
    A prefix query returns the next symbol inside its subtree and zero outside.
    Repeated physical measurements are represented by repeated rows.
    """
    if arity < 2:
        raise ValueError("arity must be at least two")
    if depth < 1:
        raise ValueError("depth must be positive")
    if copies < 1:
        raise ValueError("copies must be positive")

    completion_count = arity**depth
    rows = []
    for level in range(depth):
        prefix_divisor = arity ** (depth - level)
        symbol_divisor = arity ** (depth - level - 1)
        for prefix in range(arity**level):
            row = tuple(
                (completion // symbol_divisor) % arity
                if completion // prefix_divisor == prefix
                else 0
                for completion in range(completion_count)
            )
            rows.extend((row,) * copies)
    return tuple(rows)


def qary_prefix_query_costs(
    arity: int,
    depth: int,
    *,
    copies: int = 3,
    level_costs,
) -> tuple[int, ...]:
    """Return costs aligned with :func:`qary_prefix_query_library` rows."""
    if arity < 2:
        raise ValueError("arity must be at least two")
    if depth < 1:
        raise ValueError("depth must be positive")
    if copies < 1:
        raise ValueError("copies must be positive")
    costs = tuple(level_costs)
    if len(costs) != depth:
        raise ValueError("level_costs must contain one cost per level")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    return tuple(
        cost for level, cost in enumerate(costs) for _ in range(copies * arity**level)
    )


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
        raise ValueError(
            "a certificate that payoffs lie in the feature span is required"
        )
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
              …7339 tokens truncated…      for row in outcomes
    )
    eliminated = corruption_budget + 1
    compatibility_cache = {}
    pair_compatibility_cache = {}
    solution_cache = {}

    def feasible(lie_counts):
        return tuple(
            index
            for index, count in enumerate(lie_counts)
            if count <= corruption_budget
        )

    def compatible(indices):
        if indices in compatibility_cache:
            return compatibility_cache[indices]
        for left, right in combinations(indices, 2):
            pair = (left, right)
            if pair not in pair_compatibility_cache:
                pair_compatibility_cache[pair] = certify_common_robust_plan(
                    (exact_games[left], exact_games[right])
                ).policy_identifiable
            if not pair_compatibility_cache[pair]:
                compatibility_cache[indices] = None
                return None
        compatibility_cache[indices] = certify_common_robust_plan(
            tuple(exact_games[index] for index in indices)
        )
        return compatibility_cache[indices]

    def updated_counts(lie_counts, query, answer):
        return tuple(
            min(eliminated, count + (outcomes[query][index] != answer))
            for index, count in enumerate(lie_counts)
        )

    def search(lie_counts, erasures_used, remaining, depth_limit):
        key = (lie_counts, erasures_used, remaining, depth_limit)
        if key in solution_cache:
            return solution_cache[key]
        indices = feasible(lie_counts)
        certificate = compatible(indices)
        if (
            certificate is not None
            and certificate.policy_identifiable
            and certificate.certificate_valid
        ):
            result = AdaptiveDecisionFaultNode(
                lie_counts,
                erasures_used,
                indices,
                None,
                certificate.action_probabilities,
                certificate.minimax_value,
            )
            solution_cache[key] = result
            return result
        if depth_limit == 0 or not remaining:
            solution_cache[key] = None
            return None

        seen_rows = set()
        for query in remaining:
            row = outcomes[query]
            if row in seen_rows:
                continue
            seen_rows.add(row)
            if len({row[index] for index in indices}) < 2:
                continue
            next_remaining = tuple(item for item in remaining if item != query)
            answer_states = [
                (answer, child_counts, erasures_used)
                for answer in alphabets[query]
                if feasible(child_counts := updated_counts(lie_counts, query, answer))
            ]
            if erasures_used < erasure_budget:
                answer_states.append((None, lie_counts, erasures_used + 1))
            branches = []
            for answer, child_counts, child_erasures in answer_states:
                child = search(
                    child_counts,
                    child_erasures,
                    next_remaining,
                    depth_limit - 1,
                )
                if child is None:
                    break
                branches.append((answer, child))
            if len(branches) != len(answer_states) or not branches:
                continue
            node = AdaptiveDecisionFaultNode(
                lie_counts,
                erasures_used,
                indices,
                query,
                None,
                None,
                tuple(branches),
            )
            solution_cache[key] = node
            return node
        solution_cache[key] = None
        return None

    initial_counts = (0,) * completion_count
    remaining = tuple(range(len(outcomes)))
    root = None
    depth = None
    for depth_limit in range(len(outcomes) + 1):
        root = search(initial_counts, 0, remaining, depth_limit)
        if root is not None:
            depth = depth_limit
            break
    if root is None:
        return AdaptiveDecisionFaultPlan(
            None,
            None,
            corruption_budget,
            erasure_budget,
            completion_count,
            len(outcomes),
            len(solution_cache),
            len(compatibility_cache),
            True,
            "available_queries_cannot_identify_a_decision_under_mixed_faults",
        )
    return AdaptiveDecisionFaultPlan(
        root,
        depth,
        corruption_budget,
        erasure_budget,
        completion_count,
        len(outcomes),
        len(solution_cache),
        len(compatibility_cache),
        True,
        "exact_minimax_adaptive_decision_tree_with_mixed_faults",
    )


def plan_adaptive_decision_queries_with_weighted_faults(
    games,
    query_outcomes,
    *,
    query_costs,
    corruption_budget: int,
    erasure_budget: int,
    known_feasible_cost_upper_bound: int | None = None,
    allowed_initial_query_indices=None,
) -> AdaptiveDecisionWeightedFaultPlan:
    """Return an exact minimum-cost tree under substitutions and erasures.

    Monotone cost-bounded search followed by integer binary search certifies
    the exact optimum. A caller may supply the cost of an independently known
    feasible tree to avoid an unnecessarily loose sum-of-all-queries initial
    bound. ``allowed_initial_query_indices`` can condition the optimum on an
    exact set of permitted first physical queries; later actions remain
    unrestricted. ``None`` remains reserved for a recognized erasure. The
    solver fails closed when no available tree forces a common exact robust
    decision.
    """
    if corruption_budget < 0 or erasure_budget < 0:
        raise ValueError("corruption and erasure budgets must be nonnegative")
    exact_games = tuple(
        tuple(tuple(Fraction(value) for value in row) for row in game) for game in games
    )
    if not exact_games:
        raise ValueError("at least one feasible completion is required")
    outcomes = tuple(tuple(row) for row in query_outcomes)
    costs = tuple(query_costs)
    completion_count = len(exact_games)
    if any(len(row) != completion_count for row in outcomes):
        raise ValueError("every query must define one outcome per completion")
    if len(costs) != len(outcomes):
        raise ValueError("query_costs must align with query_outcomes")
    if any(
        isinstance(cost, bool) or not isinstance(cost, int) or cost < 1
        for cost in costs
    ):
        raise ValueError("query costs must be positive integers")
    if known_feasible_cost_upper_bound is not None and (
        isinstance(known_feasible_cost_upper_bound, bool)
        or not isinstance(known_feasible_cost_upper_bound, int)
        or known_feasible_cost_upper_bound < 0
        or known_feasible_cost_upper_bound > sum(costs)
    ):
        raise ValueError(
            "known feasible cost upper bound must be an integer within total cost"
        )
    if any(value is None for row in outcomes for value in row):
        raise ValueError("None is reserved for recognized erasures")
    for row in outcomes:
        try:
            tuple(hash(value) for value in row)
        except TypeError as exc:
            raise ValueError("query outcomes must be hashable") from exc

    if allowed_initial_query_indices is None:
        allowed_initial = None
    else:
        try:
            allowed_initial = tuple(allowed_initial_query_indices)
        except TypeError as exc:
            raise ValueError("allowed initial query indices must be iterable") from exc
        if not allowed_initial:
            raise ValueError("allowed initial query indices must be nonempty")
        if any(
            isinstance(index, bool)
            or not isinstance(index, int)
            or index < 0
            or index >= len(outcomes)
            for index in allowed_initial
        ):
            raise ValueError("allowed initial query indices must be valid integers")
        if len(set(allowed_initial)) != len(allowed_initial):
            raise ValueError("allowed initial query indices must be unique")
        allowed_initial = frozenset(allowed_initial)

    grouped = {}
    for query, (row, cost) in enumerate(zip(outcomes, costs)):
        grouped.setdefault((row, cost), []).append(query)
    group_rows = tuple(key[0] for key in grouped)
    group_costs = tuple(key[1] for key in grouped)
    group_indices = tuple(
        tuple(
            sorted(
                indices,
                key=(
                    (lambda index: (index not in allowed_initial, index))
                    if allowed_initial is not None
                    else (lambda index: index)
                ),
            )
        )
        for indices in grouped.values()
    )
    initial_remaining = tuple(len(indices) for indices in group_indices)
    alphabets = tuple(
        tuple(sorted(set(row), key=lambda value: (type(value).__name__, repr(value))))
        for row in group_rows
    )
    eliminated = corruption_budget + 1
    compatibility_cache = {}
    pair_compatibility_cache = {}
    solution_cache = {}

    def feasible(lie_counts):
        return tuple(
            index
            for index, count in enumerate(lie_counts)
            if count <= corruption_budget
        )

    def compatible(indices):
        if indices in compatibility_cache:
            return compatibility_cache[indices]
        for left, right in combinations(indices, 2):
            pair = (left, right)
            if pair not in pair_compatibility_cache:
                pair_compatibility_cache[pair] = certify_common_robust_plan(
                    (exact_games[left], exact_games[right])
                ).policy_identifiable
            if not pair_compatibility_cache[pair]:
                compatibility_cache[indices] = None
                return None
        compatibility_cache[indices] = certify_common_robust_plan(
            tuple(exact_games[index] for index in indices)
        )
        return compatibility_cache[indices]

    def updated_counts(lie_counts, row, answer):
        return tuple(
            min(eliminated, count + (row[index] != answer))
            for index, count in enumerate(lie_counts)
        )

    def search(lie_counts, erasures_used, remaining, cost_limit):
        key = (lie_counts, erasures_used, remaining, cost_limit)
        if key in solution_cache:
            return solution_cache[key]
        indices = feasible(lie_counts)
        certificate = compatible(indices)
        if (
            certificate is not None
            and certificate.policy_identifiable
            and certificate.certificate_valid
        ):
            result = AdaptiveDecisionFaultNode(
                lie_counts,
                erasures_used,
                indices,
                None,
                certificate.action_probabilities,
                certificate.minimax_value,
            )
            solution_cache[key] = result
            return result
        if not any(remaining):
            solution_cache[key] = None
            return None

        initial_state = (
            lie_counts == initial_counts
            and erasures_used == 0
            and remaining == initial_remaining
        )
        candidates = []
        for group, count in enumerate(remaining):
            if count == 0 or group_costs[group] > cost_limit:
                continue
            if (
                initial_state
                and allowed_initial is not None
                and not any(index in allowed_initial for index in group_indices[group])
            ):
                continue
            cells = {}
            for index in indices:
                cells[group_rows[group][index]] = (
                    cells.get(group_rows[group][index], 0) + 1
                )
            if len(cells) < 2:
                continue
            candidates.append((group_costs[group], max(cells.values()), group))

        for _, _, group in sorted(candidates):
            count = remaining[group]
            row = group_rows[group]
            query = group_indices[group][initial_remaining[group] - count]
            next_remaining = tuple(
                remaining[index] - (index == group) for index in range(len(remaining))
            )
            answer_states = [
                (answer, child_counts, erasures_used)
                for answer in alphabets[group]
                if feasible(child_counts := updated_counts(lie_counts, row, answer))
            ]
            if erasures_used < erasure_budget:
                answer_states.append((None, lie_counts, erasures_used + 1))
            branches = []
            for answer, child_counts, child_erasures in answer_states:
                child = search(
                    child_counts,
                    child_erasures,
                    next_remaining,
                    cost_limit - group_costs[group],
                )
                if child is None:
                    break
                branches.append((answer, child))
            if len(branches) != len(answer_states) or not branches:
                continue
            node = AdaptiveDecisionFaultNode(
                lie_counts,
                erasures_used,
                indices,
                query,
                None,
                None,
                tuple(branches),
            )
            solution_cache[key] = node
            return node
        solution_cache[key] = None
        return None

    initial_counts = (0,) * completion_count
    remaining = initial_remaining
    lower = -1
    upper = (
        sum(costs)
        if known_feasible_cost_upper_bound is None
        else known_feasible_cost_upper_bound
    )
    root = search(initial_counts, 0, remaining, upper)
    if root is None and known_feasible_cost_upper_bound is not None:
        raise ValueError(
            "known feasible cost upper bound did not admit a feasible tree"
        )
    if root is not None:
        while upper - lower > 1:
            middle = (lower + upper) // 2
            candidate = search(initial_counts, 0, remaining, middle)
            if candidate is None:
                lower = middle
            else:
                upper = middle
                root = candidate
        optimum = upper
        root = search(initial_counts, 0, remaining, optimum)
    else:
        optimum = None
    if root is None:
        return AdaptiveDecisionWeightedFaultPlan(
            None,
            None,
            None,
            corruption_budget,
            erasure_budget,
            completion_count,
            len(outcomes),
            len(solution_cache),
            len(compatibility_cache),
            True,
            "available_queries_cannot_identify_a_decision_under_weighted_mixed_faults",
        )

    def tree_depth(node):
        if node.query_index is None:
            return 0
        return 1 + max(tree_depth(child) for _, child in node.children)

    return AdaptiveDecisionWeightedFaultPlan(
        root,
        optimum,
        tree_depth(root),
        corruption_budget,
        erasure_budget,
        completion_count,
        len(outcomes),
        len(solution_cache),
        len(compatibility_cache),
        True,
        "exact_minimax_weighted_adaptive_decision_tree_with_mixed_faults",
    )


def certify_decision_query_corruption_radius(
    games,
    query_outcomes,
    *,
    corruption_budget: int,
) -> DecisionCorruptionRadiusCertificate:
    """Certify the exact answer-corruption radius of fixed follow-up queries.

    ``query_outcomes[q][completion]`` defines the clean query code. The result
    is fail closed unless every Hamming ball of the requested radius leaves a
    completion list with one common exact robust policy and value.
    """
    if corruption_budget < 0:
        raise ValueError("corruption_budget must be nonnegative")
    exact_games = tuple(
        tuple(tuple(Fraction(value) for value in row) for row in game) for game in games
    )
    if not exact_games:
        raise ValueError("at least one feasible completion is required")
    outcomes = tuple(tuple(row) for row in query_outcomes)
    completion_count = len(exact_games)
    if any(len(row) != completion_count for row in outcomes):
        raise ValueError("every query must define one outcome per completion")
    for row in outcomes:
        try:
            tuple(hash(value) for value in row)
        except TypeError as exc:
            raise ValueError("query outcomes must be hashable") from exc

    full = certify_common_robust_plan(exact_games)
    action_count = len(exact_games[0])
    if full.policy_identifiable and full.certificate_valid:
        return DecisionCorruptionRadiusCertificate(
            None,
            None,
            corruption_budget,
            True,
            completion_count,
            len(outcomes),
            action_count,
            (),
            (),
            0,
            0,
            True,
            "all_completions_share_one_robust_decision",
        )

    codewords = tuple(
        tuple(row[completion] for row in outcomes)
        for completion in range(completion_count)
    )
    minimal_witnesses = []
    witnesses_tested = 0
    for size in range(2, min(action_count, completion_count) + 1):
        for indices in combinations(range(completion_count), size):
            if any(set(witness).issubset(indices) for witness in minimal_witnesses):
                continue
            certificate = certify_common_robust_plan(
                tuple(exact_games[index] for index in indices)
            )
            witnesses_tested += 1
            if not certificate.policy_identifiable:
                minimal_witnesses.append(indices)

    if not minimal_witnesses:
        raise AssertionError("incompatible games lacked a bounded witness")

    centers_tested = 0

    def hamming(left, right):
        return sum(a != b for a, b in zip(left, right))

    def witness_radius(indices):
        nonlocal centers_tested
        words = tuple(codewords[index] for index in indices)
        if len(words) == 2:
            first, second = words
            center = list(first)
            differences = [
                position
                for position, (left, right) in enumerate(zip(first, second))
                if left != right
            ]
            for position in differences[: len(differences) // 2]:
                center[position] = second[position]
            centers_tested += 1
            center = tuple(center)
            return max(hamming(center, word) for word in words), center

        alphabets = tuple(
            tuple(
                sorted(
                    {word[position] for word in words},
                    key=lambda value: (type(value).__name__, repr(value)),
                )
            )
            for position in range(len(outcomes))
        )
        best = None
        for center in product(*alphabets):
            centers_tested += 1
            radius = max(hamming(center, word) for word in words)
            candidate = (
                radius,
                tuple((type(value).__name__, repr(value)) for value in center),
                center,
            )
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        return best[0], best[2]

    closest = None
    for witness in minimal_witnesses:
        radius, center = witness_radius(witness)
        candidate = (radius, witness, center)
        if closest is None or candidate[:2] < closest[:2]:
            closest = candidate

    decision_radius, witness, center = closest
    witness_certificate = certify_common_robust_plan(
        tuple(exact_games[index] for index in witness)
    )
    valid = (
        witness_certificate.certificate_valid
        and not witness_certificate.policy_identifiable
        and max(hamming(center, codewords[index]) for index in witness)
        == decision_radius
    )
    robust = decision_radius > corruption_budget
    return DecisionCorruptionRadiusCertificate(
        decision_radius,
        decision_radius - 1,
        corruption_budget,
        robust,
        completion_count,
        len(outcomes),
        action_count,
        center,
        witness,
        witnesses_tested,
        centers_tested,
        valid,
        (
            "query_code_certifies_requested_corruption_budget"
            if robust
            else "adversarial_transcript_has_no_common_robust_decision"
        ),
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
        raise ValueError(
            "a certificate that payoffs lie in the feature span is required"
        )
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
    available = tuple(
        position for position, row in enumerate(observations) if row is not None
    )
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
        (
            columns
            for columns in combinations(range(width), rank)
            if _fraction_matrix_rank(
                tuple(tuple(row[column] for column in columns) for row in features)
            )
            == rank
        ),
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
                sum(
                    (
                        value * coefficient
                        for value, coefficient in zip(row, coefficients)
                    ),
                    Fraction(0),
                )
                for row in reduced
            )
            disagreements = frozenset(
                position
                for position in available
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
            version_space[tuple(candidate[0] for candidate in candidate_tuple)] = (
                disagreements
            )
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
        raise ValueError(
            "a certificate that payoffs lie in the feature span is required"
        )
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
    available = tuple(
        position for position, row in enumerate(observations) if row is not None
    )
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
            )
            == rank
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
                sum(
                    (
                        value * coefficient
                        for value, coefficient in zip(row, coefficients)
                    ),
                    Fraction(0),
                )
                for row in reduced
            )
            disagreements = frozenset(
                position
                for position in available
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
            None,
            None,
            None,
            len(games),
            len(games) == 1,
            value_identifiable,
            False,
            finite_list_distance,
            tested,
            True,
            reason,
        )

    weight = common_lower
    value = next(iter(values))
    valid = all(
        min(
            weight * game[0][scenario] + (1 - weight) * game[1][scenario]
            for scenario in range(len(features))
        )
        == value
        for game in games
    )
    return DecisionIdentifiableTwoActionPlan(
        (weight, 1 - weight),
        value,
        (common_lower, common_upper),
        len(games),
        len(games) == 1,
        True,
        True,
        finite_list_distance,
        tested,
        valid,
        "decision_identifiable_despite_model_ambiguity"
        if len(games) > 1
        else "uniquely_decoded_model",
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
        raise ValueError(
            "a certificate that payoffs lie in the feature span is required"
        )
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
            tuple(Fraction(value) for value in component) for component in raw_response
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
        tuple(len(component) for component in response) != shape
        for response in queried
        if response is not None
    ):
        raise ValueError("the scenario oracle returned inconsistent payoff shapes")

    decoded = [[None for _ in range(action_count)] for action_count in shape]
    corrected = set()
    for component, action_count in enumerate(shape):
        for action in range(action_count):
            observations = tuple(
                queried[position][component][action] for position in available_positions
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

    reconstructed = tuple(
        tuple(action for action in component) for component in decoded
    )
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
