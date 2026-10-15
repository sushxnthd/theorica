import numpy as np

from theorica.agents.rack_seed_acquisition import acquire_rack_generating_rows


def hidden_cycle_rack(n: int, distinguished: int) -> np.ndarray:
    table = np.tile(np.arange(n), (n, 1))
    others = [x for x in range(n) if x != distinguished]
    cycle = {x: others[(i + 1) % len(others)] for i, x in enumerate(others)}
    for x, y in cycle.items():
        table[distinguished, x] = y
    return table


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
