import numpy as np

from theorica.agents.translation_certificate import certify_translation_group_completeness


def test_repeated_identity_rows_certify_at_sharp_bound():
    table = np.tile(np.arange(4), (4, 1))
    result = certify_translation_group_completeness(lambda x, y: int(table[x, y]), 4, [0])
    assert result.accepted
    assert result.oracle_calls == 4 + 3 * 3
    assert np.array_equal(result.reconstructed_table, table)


def test_outside_transposition_rejected():
    table = np.tile(np.arange(4), (4, 1))
    table[3, 2], table[3, 3] = table[3, 3], table[3, 2]
    result = certify_translation_group_completeness(lambda x, y: int(table[x, y]), 4, [0])
    assert not result.accepted
    assert result.reason == "incomplete_generator_group"
