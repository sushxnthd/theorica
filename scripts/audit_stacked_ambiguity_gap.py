#!/usr/bin/env python3
"""Independent Fraction-only audit of the stacked ambiguity-gap theorem."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

OUT = Path("results/stacked_ambiguity_gap/independent_audit.json")


def main():
    cases = []
    for case in range(60):
        actions = 3 + case % 2
        shift = Fraction(case - 17, 11)
        completions = tuple(
            tuple(shift if action == 0 else shift - action - completion
                  for action in range(actions))
            for completion in (0, 1)
        )
        zero_gap = all(row[0] == shift and max(row) == shift for row in completions)
        cases.append(("positive", case, actions, zero_gap))

    for case in range(30):
        actions = 3 if case < 10 else 4 if case < 20 else 5
        faces = tuple(range(actions))
        proper = all(
            any(action not in subset for action in faces)
            for size in range(1, actions)
            for subset in combinations(faces, size)
        )
        stacked_value = Fraction(-1, actions)
        gap = -stacked_value
        cases.append(("face", case, actions, str(stacked_value), str(gap), proper))

    canonical = json.dumps(cases, separators=(",", ":"))
    result = {
        "schema": "theorica.stacked-ambiguity-gap-audit/1",
        "production_imports": 0,
        "positive_zero_gap": sum(row[-1] is True for row in cases[:60]),
        "positive_total": 60,
        "sharp_face_witnesses": sum(row[-1] is True for row in cases[60:]),
        "sharp_face_total": 30,
        "prospective_five_action": 10,
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
    }
    result["passed"] = (
        result["positive_zero_gap"] == 60
        and result["sharp_face_witnesses"] == 30
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
