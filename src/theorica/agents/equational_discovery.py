from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class OperationTerm:
    kind: str
    left: "OperationTerm | None" = None
    right: "OperationTerm | None" = None
    name: str | None = None

    def __str__(self) -> str:
        if self.kind == "var":
            return str(self.name)
        return f"F({self.left},{self.right})"


@dataclass
class EquationalTheory:
    identities: list[tuple[str, str]]
    commutative: bool
    associative: bool
    idempotent: bool
    family: str
    assignments: int


@dataclass
class RepresentationEvidence:
    candidate_family: str
    verified_family: str
    monotonicity_rate: float
    bisymmetry_p95: float | None
    repeat_noise_p95: float
    effective_bisymmetry_tolerance: float
    probes: int
    passed: bool


@dataclass
class QueryEfficientRoute:
    verified_family: str
    coefficient: float | None
    oracle_calls: int
    repeat_noise_p95: float
    commutativity_p95: float
    idempotence_p95: float
    associativity_p95: float
    bisymmetry_p95: float | None
    monotonicity_rate: float | None
    thresholds: dict[str, float]


@dataclass
class CoordinateModel:
    knots: np.ndarray
    generator: np.ndarray
    coefficient: float

    def predict(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        gx = np.interp(x, self.knots, self.generator)
        gy = np.interp(y, self.knots, self.generator)
        target = self.coefficient * gx + self.coefficient * gy
        order = np.argsort(self.generator)
        return np.interp(target, self.generator[order], self.knots[order])


def _op_count(term: OperationTerm) -> int:
    if term.kind == "var":
        return 0
    return 1 + _op_count(term.left) + _op_count(term.right)


def enumerate_terms(max_operations: int = 2) -> list[OperationTerm]:
    variables = [
        OperationTerm("var", name="x"),
        OperationTerm("var", name="y"),
        OperationTerm("var", name="z"),
    ]
    by_count: dict[int, list[OperationTerm]] = {0: variables}
    all_terms = list(variables)

    for count in range(1, int(max_operations) + 1):
        generated: dict[str, OperationTerm] = {}
        for left_count in range(count):
            right_count = count - 1 - left_count
            for left in by_count[left_count]:
                for right in by_count[right_count]:
                    term = OperationTerm("op", left=left, right=right)
                    generated[str(term)] = term
        by_count[count] = list(generated.values())
        all_terms.extend(by_count[count])
    return all_terms


def _evaluate_term(
    term: OperationTerm,
    assignment: dict[str, float],
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    cache: dict[str, float],
):
    key = str(term)
    if key in cache:
        return cache[key]

    if term.kind == "var":
        value = float(assignment[str(term.name)])
    else:
        a = _evaluate_term(term.left, assignment, oracle, domain, cache)
        b = _evaluate_term(term.right, assignment, oracle, domain, cache)
        if not (np.isfinite(a) and np.isfinite(b)):
            value = np.nan
        else:
            try:
                value = float(oracle(float(a), float(b)))
            except Exception:
                value = np.nan
            if not np.isfinite(value) or not (domain[0] <= value <= domain[1]):
                value = np.nan

    cache[key] = value
    return value


class EquationalTheoryMiner:
    """Enumerate shallow terms over an unknown operation and mine empirical identities.

    The miner does not call bespoke tests for associativity, commutativity, or
    idempotence. It evaluates the full bounded term language and identifies pairs
    of terms whose observed functions are indistinguishable under the frozen
    noise tolerance. Named structural properties are read only after the generic
    equivalence relation has been mined.
    """

    def __init__(
        self,
        *,
        max_operations: int = 2,
        p95_tolerance: float = 0.02,
        min_common_fraction: float = 0.20,
    ):
        self.max_operations = int(max_operations)
        self.p95_tolerance = float(p95_tolerance)
        self.min_common_fraction = float(min_common_fraction)

    def mine(
        self,
        oracle: Callable[[float, float], float],
        domain: tuple[float, float],
        *,
        assignments: int = 20,
        seed: int = 0,
    ) -> EquationalTheory:
        terms = enumerate_terms(self.max_operations)
        rng = np.random.default_rng(seed)
        values = np.full((assignments, len(terms)), np.nan, dtype=float)

        for row in range(assignments):
            assignment = {
                "x": float(rng.uniform(*domain)),
                "y": float(rng.uniform(*domain)),
                "z": float(rng.uniform(*domain)),
            }
            cache: dict[str, float] = {}
            for col, term in enumerate(terms):
                values[row, col] = _evaluate_term(
                    term, assignment, oracle, domain, cache
                )

        span = max(float(domain[1] - domain[0]), 1e-12)
        identities: list[tuple[str, str]] = []
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                common = np.isfinite(values[:, i]) & np.isfinite(values[:, j])
                if float(np.mean(common)) < self.min_common_fraction:
                    continue
                residual = np.abs(values[common, i] - values[common, j]) / span
                if float(np.quantile(residual, 0.95)) <= self.p95_tolerance:
                    identities.append((str(terms[i]), str(terms[j])))

        equivalence = set(identities)
        equivalence |= {(b, a) for a, b in identities}

        commutative = ("F(x,y)", "F(y,x)") in equivalence
        associative = ("F(F(x,y),z)", "F(x,F(y,z))") in equivalence
        idempotent = ("x", "F(x,x)") in equivalence

        if associative and commutative and idempotent:
            family = "commutative_semilattice"
        elif associative and commutative and not idempotent:
            family = "additive_generator_candidate"
        elif commutative and idempotent and not associative:
            family = "quasi_arithmetic_mean_candidate"
        else:
            family = "unresolved"

        return EquationalTheory(
            identities=identities,
            commutative=commutative,
            associative=associative,
            idempotent=idempotent,
            family=family,
            assignments=int(assignments),
        )


class _CountingOracle:
    def __init__(self, oracle):
        self.oracle = oracle
        self.calls = 0

    def __call__(self, x, y):
        self.calls += 1
        return self.oracle(x, y)


def _p95_or_inf(values):
    if not values:
        return float("inf")
    return float(np.quantile(np.asarray(values, dtype=float), 0.95))


def _commutativity_p95(oracle, domain, probes, rng):
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    residuals = []
    for _ in range(int(probes)):
        x, y = rng.uniform(lo, hi, size=2)
        try:
            a = float(oracle(float(x), float(y)))
            b = float(oracle(float(y), float(x)))
        except Exception:
            continue
        if all(np.isfinite(v) and lo <= v <= hi for v in (a, b)):
            residuals.append(abs(a - b) / span)
    return _p95_or_inf(residuals)


def _idempotence_p95(oracle, domain, probes, rng):
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    residuals = []
    for _ in range(int(probes)):
        x = float(rng.uniform(lo, hi))
        try:
            z = float(oracle(x, x))
        except Exception:
            continue
        if np.isfinite(z) and lo <= z <= hi:
            residuals.append(abs(z - x) / span)
    return _p95_or_inf(residuals)


def _associativity_p95(oracle, domain, probes, rng):
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    residuals = []
    attempts = 0
    while len(residuals) < int(probes) and attempts < 20 * int(probes):
        x, y, z = rng.uniform(lo, hi, size=3)
        attempts += 1
        try:
            xy = float(oracle(float(x), float(y)))
            yz = float(oracle(float(y), float(z)))
            if not all(
                np.isfinite(v) and lo <= v <= hi for v in (xy, yz)
            ):
                continue
            left = float(oracle(xy, float(z)))
            right = float(oracle(float(x), yz))
        except Exception:
            continue
        if all(
            np.isfinite(v) and lo <= v <= hi for v in (left, right)
        ):
            residuals.append(abs(left - right) / span)
    return _p95_or_inf(residuals)


def _monotonicity_rate_margin(oracle, domain, probes, rng, margin):
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    positives = 0
    violations = 0
    conclusive = 0

    for _ in range(int(probes)):
        x1, x2 = sorted(rng.uniform(lo, hi, size=2))
        if x2 - x1 < 0.20 * span:
            mid = 0.5 * (x1 + x2)
            x1 = max(lo, mid - 0.12 * span)
            x2 = min(hi, mid + 0.12 * span)
        y = float(rng.uniform(lo, hi))
        for left_first in (True, False):
            try:
                if left_first:
                    a = float(oracle(float(x1), y))
                    b = float(oracle(float(x2), y))
                else:
                    a = float(oracle(y, float(x1)))
                    b = float(oracle(y, float(x2)))
            except Exception:
                continue
            if not all(
                np.isfinite(v) and lo <= v <= hi for v in (a, b)
            ):
                continue
            delta = (b - a) / span
            if delta > margin:
                positives += 1
                conclusive += 1
            elif delta < -margin:
                violations += 1
                conclusive += 1

    if conclusive == 0:
        return 0.0
    return float(positives / conclusive)


def query_efficient_theorem_route(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    seed: int = 0,
    probes: int = 8,
) -> QueryEfficientRoute:
    """Route among theorem-backed representation families with counted queries.

    This is the deployment counterpart to broad term enumeration. The theorem
    library is compiled into a staged premise test:
      1. estimate repeat noise;
      2. test cheap idempotence, associativity, and commutativity;
      3. run only the additional premises required by the surviving theorem
         family (bisymmetry and/or strict monotonicity).

    Failed premises cause abstention rather than forced classification.
    """
    counted = _CountingOracle(oracle)
    rng = np.random.default_rng(seed)
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)

    # Replicate noise: direct repeated measurements at identical inputs.
    repeat_diffs = []
    attempts = 0
    target_repeats = max(6, int(probes))
    while len(repeat_diffs) < target_repeats and attempts < 20 * target_repeats:
        x, y = rng.uniform(lo, hi, size=2)
        attempts += 1
        try:
            a = float(counted(float(x), float(y)))
            b = float(counted(float(x), float(y)))
        except Exception:
            continue
        if all(np.isfinite(v) and lo <= v <= hi for v in (a, b)):
            repeat_diffs.append(abs(a - b) / span)

    repeat_noise = _p95_or_inf(repeat_diffs)
    if not np.isfinite(repeat_noise):
        repeat_noise = 0.0

    thresholds = {
        "commutativity": max(0.008, 1.5 * repeat_noise),
        "idempotence": max(0.006, 1.1 * repeat_noise),
        "associativity": max(0.012, 2.0 * repeat_noise),
        "bisymmetry": max(0.012, 2.0 * repeat_noise),
        "monotonicity_margin": max(0.001, 1.2 * repeat_noise),
    }

    # Cheap discriminating premises first.
    idem = _idempotence_p95(counted, domain, probes, rng)
    assoc = _associativity_p95(counted, domain, probes, rng)
    comm = _commutativity_p95(counted, domain, probes, rng)

    is_idem = idem <= thresholds["idempotence"]
    is_assoc = assoc <= thresholds["associativity"]
    is_comm = comm <= thresholds["commutativity"]

    bisym = None
    monotonicity = None
    family = "unresolved"
    coefficient = None

    if is_comm and is_assoc and is_idem:
        family = "commutative_semilattice"
    elif is_comm and is_assoc and not is_idem:
        monotonicity = _monotonicity_rate_margin(
            counted,
            domain,
            probes,
            rng,
            thresholds["monotonicity_margin"],
        )
        if monotonicity >= 0.95:
            family = "additive_generator"
            coefficient = 1.0
    elif is_comm and is_idem and not is_assoc:
        bisym = _empirical_bisymmetry_p95(
            counted,
            domain,
            probes=probes,
            seed=int(rng.integers(0, 2**31 - 1)),
        )
        monotonicity = _monotonicity_rate_margin(
            counted,
            domain,
            probes,
            rng,
            thresholds["monotonicity_margin"],
        )
        if (
            bisym <= thresholds["bisymmetry"]
            and monotonicity >= 0.95
        ):
            family = "quasi_arithmetic_mean"
            coefficient = 0.5

    return QueryEfficientRoute(
        verified_family=family,
        coefficient=coefficient,
        oracle_calls=int(counted.calls),
        repeat_noise_p95=float(repeat_noise),
        commutativity_p95=float(comm),
        idempotence_p95=float(idem),
        associativity_p95=float(assoc),
        bisymmetry_p95=None if bisym is None else float(bisym),
        monotonicity_rate=(
            None if monotonicity is None else float(monotonicity)
        ),
        thresholds={k: float(v) for k, v in thresholds.items()},
    )


def _interp_weights(values, knots):
    values = np.atleast_1d(np.asarray(values, dtype=float))
    indices = np.searchsorted(knots, values, side="right") - 1
    indices = np.clip(indices, 0, len(knots) - 2)
    frac = (values - knots[indices]) / np.maximum(
        knots[indices + 1] - knots[indices], 1e-15
    )
    W = np.zeros((len(values), len(knots)), dtype=float)
    rows = np.arange(len(values))
    W[rows, indices] = 1.0 - frac
    W[rows, indices + 1] = frac
    return W


def _coordinate_system(
    samples: np.ndarray,
    domain: tuple[float, float],
    coefficient: float,
    *,
    n_knots: int,
    smoothness: float,
):
    samples = np.asarray(samples, dtype=float)
    lo, hi = map(float, domain)
    knots = np.linspace(lo, hi, int(n_knots))

    A = (
        _interp_weights(samples[:, 2], knots)
        - coefficient * _interp_weights(samples[:, 0], knots)
        - coefficient * _interp_weights(samples[:, 1], knots)
    )

    D = np.zeros((len(knots) - 2, len(knots)), dtype=float)
    for i in range(len(D)):
        D[i, i : i + 3] = [1.0, -2.0, 1.0]

    if abs(2.0 * coefficient - 1.0) < 1e-10:
        # Quasi-arithmetic means have affine coordinate ambiguity. Fix both
        # offset and scale with two anchors.
        Wlo = _interp_weights([lo], knots)
        Whi = _interp_weights([hi], knots)
        design = np.vstack([A, np.sqrt(smoothness) * D, 100.0 * Wlo, 100.0 * Whi])
        target = np.concatenate(
            [np.zeros(len(A) + len(D)), np.asarray([0.0, 100.0])]
        )
        regularizer = (
            smoothness * (D.T @ D)
            + 10000.0 * (Wlo.T @ Wlo + Whi.T @ Whi)
        )
    else:
        anchor = lo + 0.68 * (hi - lo)
        Wa = _interp_weights([anchor], knots)
        design = np.vstack([A, np.sqrt(smoothness) * D, 100.0 * Wa])
        target = np.concatenate(
            [np.zeros(len(A) + len(D)), np.asarray([100.0])]
        )
        regularizer = smoothness * (D.T @ D) + 10000.0 * (Wa.T @ Wa)

    generator, *_ = np.linalg.lstsq(design, target, rcond=None)
    if np.corrcoef(knots, generator)[0, 1] < 0:
        generator = -generator
    return knots, generator, A, regularizer


def fit_coordinate(
    samples: np.ndarray,
    domain: tuple[float, float],
    coefficient: float,
    *,
    n_knots: int = 31,
    smoothness: float = 3.0,
) -> CoordinateModel:
    knots, generator, _, _ = _coordinate_system(
        samples,
        domain,
        float(coefficient),
        n_knots=n_knots,
        smoothness=smoothness,
    )
    return CoordinateModel(knots, generator, float(coefficient))


def _empirical_monotonicity_rate(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    probes: int,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    lo, hi = map(float, domain)
    span = hi - lo
    passed = 0
    total = 0

    for _ in range(int(probes)):
        a, b = sorted(rng.uniform(lo, hi, size=2))
        if b - a < 0.20 * span:
            center = 0.5 * (a + b)
            a = max(lo, center - 0.125 * span)
            b = min(hi, center + 0.125 * span)
        y = float(rng.uniform(lo, hi))
        try:
            f1 = float(oracle(float(a), y))
            f2 = float(oracle(float(b), y))
            g1 = float(oracle(y, float(a)))
            g2 = float(oracle(y, float(b)))
        except Exception:
            continue

        if all(np.isfinite(v) and lo <= v <= hi for v in (f1, f2)):
            total += 1
            passed += int(f2 > f1)
        if all(np.isfinite(v) and lo <= v <= hi for v in (g1, g2)):
            total += 1
            passed += int(g2 > g1)

    return float(passed / max(total, 1))


def _estimate_repeat_noise_p95(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    probes: int,
    seed: int,
) -> float:
    """Estimate observation noise from repeated measurements at identical inputs.

    The returned value is the 95th percentile absolute repeat difference,
    normalized by the domain span. It is an empirical scale estimate only; no
    Gaussian noise model is required by the verifier.
    """
    rng = np.random.default_rng(seed)
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    differences = []

    attempts = 0
    while len(differences) < int(probes) and attempts < 20 * int(probes):
        x, y = rng.uniform(lo, hi, size=2)
        attempts += 1
        try:
            a = float(oracle(float(x), float(y)))
            b = float(oracle(float(x), float(y)))
        except Exception:
            continue
        if all(np.isfinite(v) and lo <= v <= hi for v in (a, b)):
            differences.append(abs(a - b) / span)

    if not differences:
        return 0.0
    return float(np.quantile(differences, 0.95))


def _empirical_bisymmetry_p95(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    probes: int,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    lo, hi = map(float, domain)
    span = max(hi - lo, 1e-12)
    residuals = []

    for _ in range(int(probes)):
        x, y, z, w = rng.uniform(lo, hi, size=4)
        try:
            xy = float(oracle(float(x), float(y)))
            zw = float(oracle(float(z), float(w)))
            xz = float(oracle(float(x), float(z)))
            yw = float(oracle(float(y), float(w)))
            if not all(
                np.isfinite(v) and lo <= v <= hi
                for v in (xy, zw, xz, yw)
            ):
                continue
            left = float(oracle(xy, zw))
            right = float(oracle(xz, yw))
        except Exception:
            continue
        if all(
            np.isfinite(v) and lo <= v <= hi
            for v in (left, right)
        ):
            residuals.append(abs(left - right) / span)

    if not residuals:
        return float("inf")
    return float(np.quantile(residuals, 0.95))


def verify_representation_hypotheses(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    theory: EquationalTheory,
    *,
    probes: int = 60,
    seed: int = 0,
    monotonicity_threshold: float = 0.95,
    bisymmetry_tolerance: float = 0.012,
) -> RepresentationEvidence:
    """Empirically verify the extra hypotheses needed before theorem routing.

    The shallow equational miner is deliberately not treated as sufficient
    evidence for a representation theorem. Associative-generator routing also
    requires strong sampled monotonicity. Quasi-arithmetic-mean routing requires
    sampled monotonicity plus the bisymmetry identity, which rules out smooth
    symmetric/idempotent decoys that merely resemble means.
    """
    repeat_noise = _estimate_repeat_noise_p95(
        oracle,
        domain,
        probes=max(16, probes // 3),
        seed=seed + 10,
    )
    # A bisymmetry comparison composes multiple noisy oracle calls. Under a
    # first-order propagation model its residual noise scale is larger than a
    # direct repeat difference. The 1.8 multiplier is a conservative
    # propagation allowance; the original fixed tolerance remains a floor.
    effective_bisymmetry_tolerance = max(
        float(bisymmetry_tolerance),
        1.8 * float(repeat_noise),
    )

    monotonicity = _empirical_monotonicity_rate(
        oracle,
        domain,
        probes=probes,
        seed=seed,
    )
    bisymmetry = None
    verified = "unresolved"
    passed = False

    if theory.family == "additive_generator_candidate":
        passed = monotonicity >= monotonicity_threshold
        if passed:
            verified = "additive_generator"
    elif theory.family == "quasi_arithmetic_mean_candidate":
        bisymmetry = _empirical_bisymmetry_p95(
            oracle,
            domain,
            probes=probes,
            seed=seed + 1,
        )
        passed = (
            monotonicity >= monotonicity_threshold
            and bisymmetry <= effective_bisymmetry_tolerance
        )
        if passed:
            verified = "quasi_arithmetic_mean"
    elif theory.family == "commutative_semilattice":
        passed = True
        verified = "commutative_semilattice"

    return RepresentationEvidence(
        candidate_family=theory.family,
        verified_family=verified,
        monotonicity_rate=float(monotonicity),
        bisymmetry_p95=(
            None if bisymmetry is None else float(bisymmetry)
        ),
        repeat_noise_p95=float(repeat_noise),
        effective_bisymmetry_tolerance=float(
            effective_bisymmetry_tolerance
        ),
        probes=int(probes),
        passed=bool(passed),
    )


def verified_representation_coefficient(
    evidence: RepresentationEvidence,
) -> float | None:
    if evidence.verified_family == "additive_generator":
        return 1.0
    if evidence.verified_family == "quasi_arithmetic_mean":
        return 0.5
    return None


def representation_coefficient(theory: EquationalTheory) -> float | None:
    """Infer the latent affine coefficient from the mined identities.

    Associative non-idempotent commutative operations use the additive-generator
    form g(F)=g(x)+g(y). For a commutative idempotent mean, substituting x=y
    into g(F)=c(g(x)+g(y)) forces c=1/2.
    """
    if theory.family == "additive_generator_candidate":
        return 1.0
    if theory.family == "quasi_arithmetic_mean_candidate":
        return 0.5
    return None


def _valid_observation(
    oracle: Callable[[float, float], float],
    x: float,
    y: float,
    domain: tuple[float, float],
):
    try:
        z = float(oracle(float(x), float(y)))
    except Exception:
        return None
    if not np.isfinite(z) or not (domain[0] <= z <= domain[1]):
        return None
    return z


def random_operation_samples(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    *,
    count: int,
    seed: int,
):
    rng = np.random.default_rng(seed)
    lo, hi = map(float, domain)
    rows = []
    while len(rows) < int(count):
        x, y = rng.uniform(lo, hi, size=2)
        z = _valid_observation(oracle, x, y, domain)
        if z is not None:
            rows.append((float(x), float(y), float(z)))
    return np.asarray(rows, dtype=float)


def active_coordinate_samples(
    oracle: Callable[[float, float], float],
    domain: tuple[float, float],
    coefficient: float,
    *,
    budget: int = 20,
    initial: int = 8,
    seed: int = 0,
    n_knots: int = 31,
    smoothness: float = 3.0,
    candidate_pool: int = 180,
):
    """Choose experiments by information gain about the latent coordinate.

    For the current linearized coordinate constraints, a candidate row a has
    one-step Gaussian information gain proportional to log(1+a^T C a), where C
    is the current coefficient covariance. We therefore rank candidate
    experiments by a^T C a rather than by output-prediction variance.
    """
    rng = np.random.default_rng(seed)
    samples = random_operation_samples(
        oracle, domain, count=int(initial), seed=int(seed)
    )
    lo, hi = map(float, domain)

    while len(samples) < int(budget):
        knots, generator, A, regularizer = _coordinate_system(
            samples,
            domain,
            float(coefficient),
            n_knots=n_knots,
            smoothness=smoothness,
        )
        covariance = np.linalg.pinv(
            A.T @ A + regularizer + 1e-8 * np.eye(len(knots))
        )
        model = CoordinateModel(knots, generator, float(coefficient))

        proposals = []
        for _ in range(int(candidate_pool)):
            x, y = rng.uniform(lo, hi, size=2)
            z_pred = float(model.predict(x, y))
            if not (lo <= z_pred <= hi):
                continue
            row = (
                _interp_weights([z_pred], knots)[0]
                - coefficient * _interp_weights([x], knots)[0]
                - coefficient * _interp_weights([y], knots)[0]
            )
            score = float(row @ covariance @ row)
            proposals.append((score, float(x), float(y)))

        proposals.sort(reverse=True)
        observation = None
        for _, x, y in proposals[: max(25, len(proposals))]:
            z = _valid_observation(oracle, x, y, domain)
            if z is not None:
                observation = (x, y, z)
                break

        if observation is None:
            extra = random_operation_samples(
                oracle,
                domain,
                count=1,
                seed=int(rng.integers(0, 2**31 - 1)),
            )[0]
            observation = tuple(float(v) for v in extra)

        samples = np.vstack([samples, np.asarray(observation, dtype=float)])

    return samples
