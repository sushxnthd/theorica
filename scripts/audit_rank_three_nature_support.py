"""Independent Fraction-only audit; imports no THEORICA production code."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "rank_three_nature_support"
CASES = OUT_DIR / "cases.json"
OUT = OUT_DIR / "independent_audit.json"


def barycenter(points, weights):
    return tuple(
        sum((weights[index] * point[axis]
             for index, point in enumerate(points)), Fraction(0))
        for axis in range(3)
    )


def audit_dense(case):
    points = tuple(tuple(Fraction(value) for value in point)
                   for point in case["points"])
    dense = tuple(Fraction(value) for value in case["dense"])
    compressed = tuple(Fraction(value) for value in case["compressed"])
    return (
        len(points) == len(dense) == len(compressed)
        and sum(dense, Fraction(0)) == sum(compressed, Fraction(0)) == 1
        and all(weight > 0 for weight in dense)
        and all(weight >= 0 for weight in compressed)
        and sum(weight > 0 for weight in compressed) <= 4
        and barycenter(points, dense) == barycenter(points, compressed)
        and case["passed"] is True
    )


def audit_holdout(case):
    components = tuple(
        tuple(tuple(Fraction(value) for value in action)
              for action in component)
        for component in case["components"]
    )
    nature = tuple(Fraction(value) for value in case["nature"])
    value = Fraction(case["value"])
    dual_value = sum(
        max(
            sum((nature[scenario] * action[scenario]
                 for scenario in range(len(nature))), Fraction(0))
            for action in component
        )
        for component in components
    )
    return (
        sum(nature, Fraction(0)) == 1
        and all(weight >= 0 for weight in nature)
        and sum(weight > 0 for weight in nature) <= 4
        and dual_value == value
        and case["passed"] is True
    )


def main():
    payload = json.loads(CASES.read_text())
    dense_results = [audit_dense(case)
                     for case in payload["dense_interventions"]]
    holdout_results = [audit_holdout(case)
                       for case in payload["holdouts"]]
    tight = payload["tightness"]
    tight_passed = (
        tight["passed"] is True
        and tight["value"] == "1/4"
        and tight["support"] == 4
        and tight["uniform"] is True
    )
    canonical = json.dumps({
        "dense": dense_results,
        "holdouts": holdout_results,
        "tight": tight_passed,
    }, sort_keys=True, separators=(",", ":"))
    report = {
        "schema": "rank-three-nature-support-independent-audit-v1",
        "fraction_only": True,
        "production_imports": False,
        "dense_cases": len(dense_results),
        "dense_passed": sum(dense_results),
        "holdout_cases": len(holdout_results),
        "holdouts_passed": sum(holdout_results),
        "tightness_passed": tight_passed,
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(dense_results) and all(holdout_results) and tight_passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
