"""Independent Fraction-only audit; deliberately imports no THEORICA code."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "rank_one_scenario_quotient" / "primary.json"
OUT = ROOT / "results" / "rank_one_scenario_quotient" / "independent_audit.json"
SEED = 20261024
SIZES = (9, 13, 21, 34, 64)


def make(coordinates, groups):
    return tuple(tuple(tuple(Fraction(b) + Fraction(d) * z for z in coordinates)
                       for b, d in group) for group in groups)


def opened_cases():
    rng = random.Random(SEED - 1)
    cases = []
    hand = (
        (((0, 1), (0, -1)),),
        (((3, 0), (1, 0)),),
        (((0, 1), (0, -1)), ((2, 1), (2, -1))),
        (((1, 2), (-2, -1), (0, 0)), ((3, -2), (-1, 2))),
    )
    for count in range(3, 7):
        for ordering in range(4):
            z = [Fraction(i - count // 2) for i in range(count)]
            random.Random(SEED + 31 * count + ordering).shuffle(z)
            cases.extend(make(tuple(z), group) for group in hand)
        for _ in range(60):
            z = list(range(-count, count + 1))
            rng.shuffle(z)
            z = tuple(Fraction(value) for value in z[:count])
            groups = []
            for _component in range(2 + rng.randrange(2)):
                groups.append(tuple((rng.randrange(-4, 5), rng.randrange(-3, 4))
                                    for _action in range(2 + rng.randrange(2))))
            cases.append(make(z, tuple(groups)))
    return tuple(cases)


def holdout_cases():
    rng = random.Random(SEED)
    cases = []
    for count in SIZES:
        for _ in range(10):
            z = list(range(-2 * count, 2 * count + 1))
            rng.shuffle(z)
            z = tuple(Fraction(value) for value in z[:count])
            groups = tuple(tuple((rng.randrange(-7, 8), rng.choice((-3, -2, -1, 0, 1, 2, 3)))
                                 for _action in range(2)) for _component in range(3))
            cases.append(make(z, groups))
    return tuple(cases)


def independent_result(components):
    profiles = tuple(action for component in components for action in component)
    anchor = next((row for row in profiles if len(set(row)) > 1), None)
    if anchor is None:
        endpoints = (0, 0)
    else:
        witness = next(i for i in range(1, len(anchor)) if anchor[i] != anchor[0])
        for row in profiles:
            slope = Fraction(row[witness] - row[0], anchor[witness] - anchor[0])
            intercept = row[0] - slope * anchor[0]
            assert all(row[i] == intercept + slope * anchor[i]
                       for i in range(len(anchor)))
        endpoints = (
            min(range(len(anchor)), key=lambda i: (anchor[i], i)),
            min(range(len(anchor)), key=lambda i: (-anchor[i], i)),
        )
    actions = tuple(tuple(sum(components[t][choice[t]][s]
                              for t in range(len(components)))
                          for s in range(len(profiles[0])))
                    for choice in product(*(range(len(c)) for c in components)))
    pairs = tuple(sorted(set((row[endpoints[0]], row[endpoints[1]]) for row in actions)))
    candidates = {Fraction(0), Fraction(1)}
    for a, b in combinations(pairs, 2):
        denominator = (a[0] - a[1]) - (b[0] - b[1])
        if denominator:
            q = Fraction(b[1] - a[1], denominator)
            if 0 <= q <= 1:
                candidates.add(q)
    value = min(max(q * a + (1 - q) * b for a, b in pairs) for q in candidates)
    strict = max(min(pair) for pair in pairs) < value
    # A two-column finite game always admits an optimal agent mixture of support <=2.
    support = 2 if strict else 1
    return {
        "value": str(value), "strict": strict, "support": support,
        "scenarios": len(profiles[0]), "expanded_actions": len(actions), "passed": True,
    }


def digest(items):
    value = hashlib.sha256()
    for item in items:
        value.update((json.dumps(item, sort_keys=True) + "\n").encode())
    return value.hexdigest()


def main():
    primary = json.loads(PRIMARY.read_text())
    opened = [independent_result(case) for case in opened_cases()]
    holdouts = [independent_result(case) for case in holdout_cases()]
    checks = {
        "opened_count": len(opened) == primary["opened"]["cases"],
        "opened_digest": digest(opened) == primary["opened"]["digest"],
        "opened_classification": sum(item["strict"] for item in opened)
            == primary["opened"]["strict"],
        "holdout_count": len(holdouts) == primary["holdouts"]["cases"] == 50,
        "holdout_digest": digest(holdouts) == primary["holdouts"]["digest"],
        "holdout_sizes": sorted(set(item["scenarios"] for item in holdouts))
            == list(SIZES) == primary["holdouts"]["sizes"],
        "falsification": primary["falsification"]["false_accepts"] == 0
            and primary["falsification"]["endpoint_attack_actual"] == "1/2"
            and primary["falsification"]["endpoint_heuristic_claim"] == "1"
            and primary["falsification"]["production_rejected"],
        "scaling_arithmetic": primary["scaling"]["expanded_actions"] == 4 ** 20
            and primary["scaling"]["effective_scenarios"] == 2
            and primary["scaling"]["support"] <= 2
            and primary["scaling"]["valid"],
        "primary_passed": primary["passed"] and all(primary["checks"].values()),
    }
    result = {
        "schema": "rank-one-scenario-quotient-independent-audit-v1",
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
