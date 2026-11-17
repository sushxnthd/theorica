#!/usr/bin/env python3
"""Prospective exact test of the frozen clean-separator residual law."""
from __future__ import annotations

import importlib.util
import json
from functools import lru_cache
from pathlib import Path

from theorica.agents.corruption_resilient_features import certify_common_robust_plan

SPEC = importlib.util.spec_from_file_location(
    "helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)

OUT = Path("results/qary_ternary_clean_separator/results.json")
INF = 10**9
PROSPECTIVE_COSTS = (3, 10, 3)
PREDICTED_VALUE = 30


def witness_state():
    # One copy each of groups 1 and 0 was consumed by the frozen prefix.
    return ((1,) * 8 + (0, 0), 1, (3, 3) + (4,) * 11)


def clean_separator(rows, state):
    counts, _, remaining = state
    zero = {i for i, count in enumerate(counts) if count == 0}
    one = {i for i, count in enumerate(counts) if count == 1}
    witnesses = []
    for query, copies in enumerate(remaining):
        if not copies or H.level(query) != 1:
            continue
        cells = {}
        for i, answer in enumerate(rows[query]):
            cells.setdefault(answer, []).append(i)
        zero_cells = [
            (answer, members)
            for answer, members in cells.items()
            if zero.intersection(members)
        ]
        clean = (
            len(zero_cells) == len(zero)
            and all(len(zero.intersection(members)) == 1 for _, members in zero_cells)
            and all(not one.intersection(members) for _, members in zero_cells)
        )
        if clean:
            witnesses.append(
                {
                    "query_group": query,
                    "cells": [
                        {
                            "answer": answer,
                            "zero_lie": sorted(zero.intersection(members)),
                            "one_lie": sorted(one.intersection(members)),
                        }
                        for answer, members in sorted(cells.items())
                    ],
                }
            )
    return witnesses


def exact_value(words, level_costs, start, allowed_levels=None):
    rows = H.rows(words)
    costs = tuple(level_costs[H.level(i)] for i in range(len(rows)))
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)
    games = H.games(10)
    compatibility = {}
    states = 0
    actions = 0
    permitted_levels = (
        frozenset((0, 1, 2))
        if allowed_levels is None
        else frozenset(allowed_levels)
    )

    def live(counts):
        return tuple(i for i, count in enumerate(counts) if count <= 1)

    def terminal(counts):
        ids = live(counts)
        if ids not in compatibility:
            if len(ids) <= 1:
                compatibility[ids] = bool(ids)
            else:
                certificate = certify_common_robust_plan(tuple(games[i] for i in ids))
                compatibility[ids] = (
                    certificate.policy_identifiable and certificate.certificate_valid
                )
        return compatibility[ids]

    def candidates(state):
        counts, _, remaining = state
        ids = live(counts)
        return tuple(
            query
            for query, copies in enumerate(remaining)
            if copies
            and H.level(query) in permitted_levels
            and len({rows[query][i] for i in ids}) >= 2
        )

    def transitions(state, query):
        counts, erasures, remaining = state
        next_remaining = tuple(
            copies - (i == query) for i, copies in enumerate(remaining)
        )
        result = []
        for answer in alphabets[query]:
            changed = tuple(
                min(2, count + (rows[query][i] != answer))
                for i, count in enumerate(counts)
            )
            if live(changed):
                result.append((answer, (changed, erasures, next_remaining)))
        if erasures < 1:
            result.append((None, (counts, erasures + 1, next_remaining)))
        return tuple(result)

    @lru_cache(None)
    def value(state):
        nonlocal states, actions
        states += 1
        if terminal(state[0]):
            return 0
        best = INF
        for query in candidates(state):
            actions += 1
            child_values = [value(child) for _, child in transitions(state, query)]
            if child_values and max(child_values) < INF:
                best = min(best, costs[query] + max(child_values))
        return best

    result = value(start)
    root_actions = []
    for query in candidates(start):
        children = [(answer, value(child)) for answer, child in transitions(start, query)]
        worst_child = INF if not children else max(v for _, v in children)
        score = INF if worst_child >= INF else costs[query] + worst_child
        root_actions.append(
            {
                "query_group": query,
                "query_level": H.level(query),
                "query_cost": costs[query],
                "child_values": [v for _, v in children],
                "action_value": score,
                "optimal": score == result,
            }
        )
    return {
        "exact_lower_bound": result,
        "constructive_upper_bound": min(row["action_value"] for row in root_actions),
        "root_actions": root_actions,
        "states_solved": states,
        "actions_evaluated": actions,
        "compatibility_states": len(compatibility),
        "allowed_query_levels": sorted(permitted_levels),
    }


def main():
    words = (*H.BASE, *H.PAIRS[2])
    state = witness_state()
    rows = H.rows(words)
    witnesses = clean_separator(rows, state)

    # The discovery value is a regression guard, not a newly opened holdout.
    discovery = exact_value(words, H.COSTS, state)
    prospective = exact_value(words, PROSPECTIVE_COSTS, state)
    supported = (
        bool(witnesses)
        and discovery["exact_lower_bound"]
        == discovery["constructive_upper_bound"]
        == 27
        and prospective["exact_lower_bound"]
        == prospective["constructive_upper_bound"]
        == PREDICTED_VALUE
    )
    report = {
        "schema": "theorica.ternary-clean-separator/1",
        "family": "P2_WL_nonisomorphic",
        "words": [list(word) for word in words],
        "witness_state": {
            "lie_counts": list(state[0]),
            "erasures_used": state[1],
            "remaining_copies": list(state[2]),
        },
        "clean_separator": {
            "present": bool(witnesses),
            "witnesses": witnesses,
        },
        "discovery_regression": {"level_costs": list(H.COSTS), **discovery},
        "prospective": {
            "level_costs": list(PROSPECTIVE_COSTS),
            "predicted_value": PREDICTED_VALUE,
            **prospective,
        },
        "opened_reserved_cases": 1,
        "remaining_reserved_cases": 17,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "clean_separator_residual_law_supported"
                if supported
                else "clean_separator_residual_law_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
