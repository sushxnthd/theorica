import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "verify_qary_ternary_obstruction_column_generation.py"
SPEC = importlib.util.spec_from_file_location("column_generation", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_prospective_cost_suffix_is_frozen():
    assert MODULE.UNOPENED_COSTS == (
        (3, 10, 3),
        (4, 11, 2),
        (5, 13, 4),
        (7, 19, 5),
        (11, 29, 7),
        (13, 34, 9),
    )


def test_known_missing_column_costs_51():
    exposures = ((1, 5, 1), (3, 3, 5), (3, 4, 3), (3, 5, 0), (4, 2, 2), (4, 3, 1), (4, 4, 0))
    assert max(sum(x * y for x, y in zip(row, (2, 9, 3))) for row in exposures) == 51
