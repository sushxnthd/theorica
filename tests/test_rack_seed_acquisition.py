import numpy as np
import pytest

from theorica.agents.rack_seed_acquisition import (
    acquire_rack_generating_rows,
    locate_hidden_generator_by_cells,
    locate_hidden_generator_randomized,
)


def hidden_cycle_rack(n: int, distinguished: int) -> np.ndarray:
    table = np.tile(np.arange(n), (n, 1))
    others = [x for x in range(n) if x != distinguished]
    cycle = {x: others[(i + 1) % len(others)] for i, x in enumerate(others)}
    for x, y in cycle.items():
        table[distinguished, x] = y
    return table


def operation_closure(table: np.ndarray, seeds: tuple[int, ...]) -> set[int]:
    known = set(seeds)
    changed = True
    while changed:
        changed = False
        for x in tuple(known):
            for y in tuple(known):
                value = int(table[x, y])
                if value not in known:
                    known.add(value)
                    changed = True
    return known


def test_order_three_boundary_needs_all_rows_in_label_order():
    table = hidden_cycle_rack(3, 2)
    failed = acquire_rack_generating_rows(
        lambda x, y: int(table[x, y]), 3, max_seed_rows=2
    )
    assert not failed.accepted
    assert failed.reason == "seed_budget_exhausted"
    assert failed.seed_rows == (0, 1)
    assert failed.oracle_calls == 6

    passed = acquire_rack_generating_rows(
        lambda x, y: int(table[x, y]), 3, max_seed_rows=3
    )
    assert passed.accepted
    assert passed.seed_rows == (0, 1, 2)
    assert passed.oracle_calls == 9
    assert np.array_equal(passed.reconstruction.reconstructed_table, table)


def test_early_distinguished_row_uses_two_seeds():
    table = hidden_cycle_rack(7, 0)
    result = acquire_rack_generating_rows(
        lambda x, y: int(table[x, y]), 7, max_seed_rows=2
    )
    assert result.accepted
    assert result.seed_rows == (0, 1)
    assert result.oracle_calls == 14
    assert np.array_equal(result.reconstruction.reconstructed_table, table)


@pytest.mark.parametrize("n", range(3, 33))
def test_partial_cell_locator_exhausts_all_hidden_rows(n: int):
    for distinguished in range(n):
        table = hidden_cycle_rack(n, distinguished)
        result = locate_hidden_generator_by_cells(
            lambda x, y: int(table[x, y]),
            n,
            family_certified=True,
        )
        assert result.accepted
        assert result.distinguished_row == distinguished
        assert result.oracle_calls <= n - 1
        assert len(result.observations) == result.oracle_calls
        assert result.seed_rows[0] == distinguished
        assert result.seed_rows[1] != distinguished
        assert operation_closure(table, result.seed_rows) == set(range(n))


def test_partial_cell_locator_attains_n_minus_one_bound():
    n = 17
    table = hidden_cycle_rack(n, n - 1)
    result = locate_hidden_generator_by_cells(
        lambda x, y: int(table[x, y]),
        n,
        family_certified=True,
    )
    assert result.accepted
    assert result.reason == "hidden_generator_inferred"
    assert result.oracle_calls == n - 1


def test_partial_cell_locator_refuses_uncertified_family_without_queries():
    calls = 0

    def oracle(x: int, y: int) -> int:
        nonlocal calls
        calls += 1
        return y

    result = locate_hidden_generator_by_cells(
        oracle,
        7,
        family_certified=False,
    )
    assert not result.accepted
    assert result.reason == "family_certificate_required"
    assert result.oracle_calls == 0
    assert calls == 0


def test_partial_cell_locator_rejects_out_of_range_answer():
    result = locate_hidden_generator_by_cells(
        lambda x, y: 99,
        5,
        family_certified=True,
    )
    assert not result.accepted
    assert result.reason == "oracle_value_out_of_range"
    assert result.oracle_calls == 1


def test_randomized_locator_refuses_bounded_error_without_authorization():
    calls = 0
    def oracle(x: int, y: int) -> int:
        nonlocal calls
        calls += 1
        return y
    result = locate_hidden_generator_randomized(
        oracle, 11, family_certified=True, allow_bounded_error=False,
        minimum_success_numerator=3, minimum_success_denominator=4, rng_seed=7,
    )
    assert not result.accepted
    assert result.reason == "bounded_error_authorization_required"
    assert result.oracle_calls == 0
    assert calls == 0


def test_randomized_locator_uses_exact_confidence_budget():
    n, hidden = 11, 4
    table = hidden_cycle_rack(n, hidden)
    result = locate_hidden_generator_randomized(
        lambda x, y: int(table[x, y]), n,
        family_certified=True, allow_bounded_error=True,
        minimum_success_numerator=3, minimum_success_denominator=4, rng_seed=19,
    )
    assert result.accepted
    assert result.query_budget == 8
    assert result.oracle_calls <= 8
    assert (result.guaranteed_success_numerator, result.guaranteed_success_denominator) == (9, 11)


def test_randomized_locator_keeps_zero_error_default_exact():
    n, hidden = 13, 12
    table = hidden_cycle_rack(n, hidden)
    result = locate_hidden_generator_randomized(
        lambda x, y: int(table[x, y]), n,
        family_certified=True, allow_bounded_error=False,
        minimum_success_numerator=1, minimum_success_denominator=1, rng_seed=99,
    )
    assert result.accepted
    assert result.distinguished_row == hidden
    assert result.oracle_calls == n - 1
    assert result.reason == "hidden_generator_inferred"
    assert (result.guaranteed_success_numerator, result.guaranteed_success_denominator) == (1, 1)
