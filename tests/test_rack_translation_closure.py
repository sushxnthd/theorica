import numpy as np

from theorica.agents.translation_certificate import (
    reconstruct_rack_from_generating_rows,
)


def dihedral_quandle(order: int) -> np.ndarray:
    return np.asarray(
        [[(2 * x - y) % order for y in range(order)] for x in range(order)],
        dtype=np.int64,
    )


def test_two_rows_reconstruct_odd_dihedral_quandle_exactly():
    table = dihedral_quandle(7)
    result = reconstruct_rack_from_generating_rows(
        lambda x, y: int(table[x, y]), 7, [0, 1]
    )
    assert result.accepted
    assert result.oracle_calls == 14
    assert result.derived_rows == 5
    assert np.array_equal(result.reconstructed_table, table)


def test_non_generating_seed_abstains_without_extra_queries():
    table = dihedral_quandle(7)
    result = reconstruct_rack_from_generating_rows(
        lambda x, y: int(table[x, y]), 7, [0]
    )
    assert not result.accepted
    assert result.reason == "seed_rows_do_not_generate_carrier"
    assert result.oracle_calls == 7


def test_non_bijective_seed_rejected():
    table = np.zeros((3, 3), dtype=np.int64)
    result = reconstruct_rack_from_generating_rows(
        lambda x, y: int(table[x, y]), 3, [0]
    )
    assert not result.accepted
    assert result.reason == "non_bijective_seed_translation"
