import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "verify_qary_ternary_minimal_obstruction_cost_cone.py"
SPEC = importlib.util.spec_from_file_location("ternary_cost_cone", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FACES = MODULE.FACES
HOLDOUTS = MODULE.HOLDOUTS
NEW_FACE = MODULE.NEW_FACE
predicted = MODULE.predicted


def test_preregistered_counterexample_activates_new_face():
    assert predicted((1, 3, 1)) == (18, 17, 18)


def test_new_face_is_not_redundant_with_binary_faces():
    assert NEW_FACE not in FACES
    assert max(sum(a * b for a, b in zip(face, (1, 3, 1))) for face in FACES) == 17


def test_holdouts_are_fixed_with_one_preregistered_overlap():
    assert len(HOLDOUTS) == 12
    assert sum(max(costs) <= 4 for costs in HOLDOUTS) == 1
    assert (1, 4, 2) in HOLDOUTS
