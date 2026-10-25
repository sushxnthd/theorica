#!/usr/bin/env python3
"""Independent Fraction-only replay of stacked primal-dual certificates."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

SOURCE = Path("results/stacked_ambiguity_dual/results.json")
OUT = Path("results/stacked_ambiguity_dual/independent_audit.json")


def audit_case(row):
    games = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in game)
        for game in row["games"]
    )
    action_count = row["actions"]
    policy = tuple(Fraction(value) for value in row["stacked_policy"])
    dual = tuple(
        (item["completion"], item["scenario"], Fraction(item["weight"]))
        for item in row["dual"]
    )
    stacked = Fraction(row["stacked_value"])
    common = Fraction(row["common_value"])
    gap = Fraction(row["gap"])
    primal_floor = min(
        sum(
            (policy[action] * game[action][scenario]
             for action in range(action_count)),
            Fraction(0),
        )
        for game in games
        for scenario in range(len(game[0]))
    )
    dual_payoffs = tuple(
        sum(
            (weight * games[completion][action][scenario]
             for completion, scenario, weight in dual),
            Fraction(0),
        )
        for action in range(action_count)
    )
    return (
        len(policy) == action_count
        and all(value >= 0 for value in policy)
        and sum(policy, Fraction(0)) == 1
        and all(weight > 0 for _, _, weight in dual)
        and sum((weight for _, _, weight in dual), Fraction(0)) == 1
        and len(dual) <= action_count
        and primal_floor == stacked
        and max(dual_payoffs) == stacked
        and tuple(Fraction(value) for value in row["dual_action_payoffs"])
        == dual_payoffs
        and common - stacked == gap
    )


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    exact_cases = [row for row in payload["cases"] if "games" in row]
    audited = sum(audit_case(row) for row in exact_cases)
    prospective = [
        row for row in exact_cases if row["family"] == "prospective-six-action"
    ]
    prospective_sharp = sum(
        len(row["dual"]) == 6
        and all(Fraction(item["weight"]) == Fraction(1, 6) for item in row["dual"])
        and Fraction(row["gap"]) == Fraction(1, 6)
        for row in prospective
    )
    canonical = json.dumps(exact_cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "exact_case_total": len(exact_cases),
        "exact_primal_dual_replays": audited,
        "prospective_six_action_total": len(prospective),
        "prospective_six_action_sharp": prospective_sharp,
        "primary_digest_reproduced": hashlib.sha256(canonical.encode()).hexdigest()
        == payload["summary"]["exact_case_digest"],
        "production_imports": 0,
    }
    summary["passed"] = (
        summary["exact_case_total"] == 50
        and summary["exact_primal_dual_replays"] == 50
        and summary["prospective_six_action_total"] == 10
        and summary["prospective_six_action_sharp"] == 10
        and summary["primary_digest_reproduced"]
    )
    OUT.write_text(
        json.dumps(
            {"schema": "theorica.stacked-ambiguity-dual-audit/1", "summary": summary},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
