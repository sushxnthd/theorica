import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "verify_qary_ternary_minimal_obstruction_policy_fan.py"
SPEC = importlib.util.spec_from_file_location("ternary_policy_fan", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_unopened_holdout_suffix_is_fixed():
    assert MODULE.UNOPENED == (
        (3, 10, 3),
        (4, 11, 2),
        (5, 13, 4),
        (7, 19, 5),
        (11, 29, 7),
        (13, 34, 9),
    )


def test_pareto_reduction_removes_dominated_exposures():
    class Node:
        def __init__(self, query_index=None, children=()):
            self.query_index = query_index
            self.children = children

    leaf = Node()
    short = Node(0, ((0, leaf),))
    long = Node(0, ((0, short),))
    root = Node(4, ((0, short), (1, long)))
    assert MODULE.pareto_exposures(root) == ((2, 1, 0),)
