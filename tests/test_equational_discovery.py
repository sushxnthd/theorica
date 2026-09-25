import numpy as np

from theorica.agents.equational_discovery import (
    EquationalTheoryMiner,
    active_coordinate_samples,
    enumerate_terms,
    fit_coordinate,
    representation_coefficient,
)


def test_bounded_term_language_is_generic():
    terms = enumerate_terms(max_operations=2)
    assert len(terms) == 66
    strings = {str(t) for t in terms}
    assert "F(F(x,y),z)" in strings
    assert "F(x,F(y,z))" in strings


def test_miner_distinguishes_three_structures():
    miner = EquationalTheoryMiner(p95_tolerance=1e-10)

    add = miner.mine(lambda x, y: x + y, (-0.4, 0.4), assignments=24, seed=1)
    assert add.associative and add.commutative and not add.idempotent
    assert add.family == "additive_generator_candidate"
    assert representation_coefficient(add) == 1.0

    mean = miner.mine(lambda x, y: (x + y) / 2.0, (-1.0, 1.0), assignments=24, seed=2)
    assert mean.commutative and mean.idempotent and not mean.associative
    assert mean.family == "quasi_arithmetic_mean_candidate"
    assert representation_coefficient(mean) == 0.5

    semilattice = miner.mine(max, (-1.0, 1.0), assignments=24, seed=3)
    assert semilattice.associative and semilattice.commutative and semilattice.idempotent
    assert semilattice.family == "commutative_semilattice"


def test_active_coordinate_recovers_relativistic_composition():
    F = lambda u, v: (u + v) / (1.0 + u * v)
    domain = (-0.75, 0.75)

    samples = active_coordinate_samples(
        F,
        domain,
        1.0,
        budget=20,
        initial=8,
        seed=7,
        candidate_pool=120,
    )
    assert samples.shape == (20, 3)

    model = fit_coordinate(samples, domain, 1.0)
    rng = np.random.default_rng(8)
    errors = []
    for _ in range(250):
        u, v = rng.uniform(-0.55, 0.55, size=2)
        truth = F(u, v)
        if not (domain[0] <= truth <= domain[1]):
            continue
        pred = float(model.predict(u, v))
        errors.append((pred - truth) ** 2)

    assert len(errors) > 150
    assert np.sqrt(np.mean(errors)) < 0.01
