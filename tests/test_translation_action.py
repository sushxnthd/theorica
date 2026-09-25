import numpy as np

from theorica.agents.translation_action import (
    discover_translation_action_representation,
)


def _table_oracle(table):
    table = np.asarray(table, dtype=np.int64)
    return lambda x, y: int(table[int(x), int(y)])


def test_recovers_cyclic_addition_without_group_label():
    n = 11
    table = np.fromfunction(
        lambda x, y: (x + y) % n, (n, n), dtype=int
    ).astype(np.int64)
    result = discover_translation_action_representation(
        _table_oracle(table),
        n,
        seed=3,
        validation_queries=24,
    )
    assert result.accepted
    assert np.array_equal(result.reconstructed_table, table)
    assert result.oracle_calls < n * n


def test_recovers_reflection_subtraction():
    n = 11
    table = np.fromfunction(
        lambda x, y: (x - y) % n, (n, n), dtype=int
    ).astype(np.int64)
    result = discover_translation_action_representation(
        _table_oracle(table),
        n,
        seed=7,
        validation_queries=24,
    )
    assert result.accepted
    assert np.array_equal(result.reconstructed_table, table)


def test_rejects_nonbijective_operation():
    n = 11
    table = np.fromfunction(
        lambda x, y: (x * y) % n, (n, n), dtype=int
    ).astype(np.int64)
    result = discover_translation_action_representation(
        _table_oracle(table),
        n,
        seed=0,
        validation_queries=24,
    )
    assert not result.accepted



def test_identity_first_row_does_not_collapse_faithfulness():
    n = 11
    table = np.fromfunction(
        lambda x, y: (x + y) % n, (n, n), dtype=int
    ).astype(np.int64)
    # Seed 23 selects x=0 first, whose left translation is the identity.
    result = discover_translation_action_representation(
        _table_oracle(table),
        n,
        seed=23,
        validation_queries=24,
    )
    assert result.accepted
    assert np.array_equal(result.reconstructed_table, table)
    assert result.queried_rows >= 2



def test_validation_counterexample_refines_public_loop():
    # Public RightQuasigroups SmallLoop(6, 9), converted to zero-based form.
    # Earlier acquisition could form a partial action group whose base
    # signatures mimicked every row, then reject when validation falsified it.
    # The falsifying row must now be acquired and the action refined.
    table = np.asarray(
        [
            [0, 1, 2, 3, 4, 5],
            [1, 0, 3, 2, 5, 4],
            [2, 4, 0, 5, 1, 3],
            [3, 5, 1, 4, 0, 2],
            [4, 2, 5, 1, 3, 0],
            [5, 3, 4, 0, 2, 1],
        ],
        dtype=np.int64,
    )
    result = discover_translation_action_representation(
        _table_oracle(table),
        len(table),
        seed=990000,
        max_generator_rows=8,
        max_group_size=20000,
        max_base_size=12,
        validation_queries=64,
    )
    assert result.accepted
    assert np.array_equal(result.reconstructed_table, table)
    assert result.queried_rows >= 2
