import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_p2_root_action_collision_and_handoff():
    result = json.loads(
        (ROOT / "results/qary_ternary_p2_root_action_transition/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_p2_root_action_transition/audit.json").read_text()
    )

    endpoints = {row["leaf_cost"]: row for row in result["endpoints"]}
    assert endpoints[11]["exact"]["exact_lower_bound"] == 37
    assert endpoints[11]["observed_optimal_groups"] == [0, 3]
    assert endpoints[11]["clean_group3_action"]["child_values"] == [26, 22, 22]
    assert endpoints[12]["exact"]["exact_lower_bound"] == 37
    assert endpoints[12]["observed_optimal_groups"] == [0]
    assert endpoints[12]["root_group0_action"]["child_values"] == [27, 27, 33]
    assert result["remaining_reserved_cases"] == 8
    assert result["summary"]["prediction_supported"] is True
    assert audit["passed"] is True
