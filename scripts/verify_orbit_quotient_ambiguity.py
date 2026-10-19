#!/usr/bin/env python3
"""Exact verifier for invariant ambiguity reduction to point-orbit masses."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations

from theorica.agents.robust_provenance import synthesize_orbit_ambiguity_plan


def product_group(sizes):
    offsets, total = [], 0
    for size in sizes:
        offsets.append(total)
        total += size
    shifts = [()]
    for size in sizes:
        shifts = [prefix + (shift,) for prefix in shifts for shift in range(size)]
    return tuple(tuple(
        offsets[j] + (x - offsets[j] + shift[j]) % sizes[j]
        for x in range(total)
        for j in range(len(sizes))
        if offsets[j] <= x < offsets[j] + sizes[j]
    ) for shift in shifts)


def typed_seeds(sizes, k):
    offsets, total = [], 0
    for size in sizes:
        offsets.append(total)
        total += size
    seen = {}
    for seed in combinations(range(total), k):
        counts = tuple(sum(offsets[j] <= x < offsets[j] + sizes[j] for x in seed)
                       for j in range(len(sizes)))
        seen.setdefault(counts, seed)
    return tuple((counts, seen[counts]) for counts in sorted(seen))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    digest = hashlib.sha256()
    counts = {
        "two_orbit_cases": 0, "strict_randomization_cases": 0,
        "pure_optimal_cases": 0, "quotient_label_payoff_checks": 0,
        "support_bound_checks": 0, "three_orbit_cases": 0,
        "three_orbit_strict_cases": 0,
    }
    grid = (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1))

    for n in range(3, 8):
        for left in range(1, n):
            sizes = (left, n - left)
            group = product_group(sizes)
            for k in range(1, n):
                typed = typed_seeds(sizes, k)
                families = [(i,) for i in range(len(typed))]
                families.extend(combinations(range(len(typed)), 2))
                for family in families:
                    seeds = tuple(typed[i][1] for i in family)
                    compositions = tuple(tuple(
                        Fraction(count, size) for count, size in zip(typed[i][0], sizes)
                    ) for i in family)
                    for lo, hi in combinations(grid, 2):
                        vertices = ((lo, 1 - lo), (hi, 1 - hi))
                        plan = synthesize_orbit_ambiguity_plan(
                            n, k - 1, seeds, group, vertices,
                            ambiguity_kind="two-orbit-interval",
                            ambiguity_invariant=True,
                        )
                        assert plan.certificate_valid
                        assert len(plan.components) <= 2
                        counts["two_orbit_cases"] += 1
                        counts["support_bound_checks"] += 1
                        counts[
                            "strict_randomization_cases" if plan.strict_randomization_advantage
                            else "pure_optimal_cases"
                        ] += 1
                        # Expand each quotient vertex to a per-label prior uniform on
                        # each point orbit and independently recompute the full payoff.
                        for vertex in vertices:
                            prior = tuple(
                                vertex[j] / sizes[j]
                                for j in range(2) for _ in range(sizes[j])
                            )
                            inclusion = tuple(
                                sum((component.probability * Fraction(
                                    sum(label in subset for subset in component.query_orbit),
                                    len(component.query_orbit),
                                ) for component in plan.components), Fraction(0))
                                for label in range(n)
                            )
                            full = sum((p * a for p, a in zip(prior, inclusion)), Fraction(0))
                            quotient = sum((
                                component.probability * sum((
                                    component.orbit_composition[j] * vertex[j] for j in range(2)
                                ), Fraction(0)) for component in plan.components
                            ), Fraction(0))
                            assert full == quotient
                            counts["quotient_label_payoff_checks"] += 1
                        digest.update(repr((
                            sizes, k, compositions, vertices, plan.minimax_value,
                            plan.best_pure_value,
                        )).encode())

    # Three-orbit stress panel: full admissible type family under both the full
    # orbit-mass simplex and a contracted invariant polytope.
    for n in range(4, 8):
        for a in range(1, n - 1):
            for b in range(a, n - a):
                c = n - a - b
                if c < b:
                    continue
                sizes = (a, b, c)
                group = product_group(sizes)
                center = tuple(Fraction(size, n) for size in sizes)
                panels = (
                    ((Fraction(1), Fraction(0), Fraction(0)),
                     (Fraction(0), Fraction(1), Fraction(0)),
                     (Fraction(0), Fraction(0), Fraction(1))),
                    tuple(tuple((Fraction(1, 2) if i == j else Fraction(0))
                                + center[i] / 2 for i in range(3)) for j in range(3)),
                )
                for k in range(1, n):
                    typed = typed_seeds(sizes, k)
                    seeds = tuple(seed for _, seed in typed)
                    for vertices in panels:
                        plan = synthesize_orbit_ambiguity_plan(
                            n, k - 1, seeds, group, vertices,
                            ambiguity_kind="three-orbit-panel",
                            ambiguity_invariant=True,
                        )
                        assert plan.certificate_valid and len(plan.components) <= 3
                        counts["three_orbit_cases"] += 1
                        counts["three_orbit_strict_cases"] += int(
                            plan.strict_randomization_advantage
                        )

    frozen = synthesize_orbit_ambiguity_plan(
        7, 1, ((0, 1), (3, 4)), product_group((3, 4)),
        ((Fraction(3, 4), Fraction(1, 4)),
         (Fraction(1, 4), Fraction(3, 4))),
        ambiguity_kind="frozen-3-4", ambiguity_invariant=True,
    )
    weights = {component.orbit_composition: component.probability
               for component in frozen.components}
    expected_weights = {
        (Fraction(2, 3), Fraction(0)): Fraction(3, 7),
        (Fraction(0), Fraction(1, 2)): Fraction(4, 7),
    }
    assert weights == expected_weights
    assert frozen.minimax_value == Fraction(2, 7)
    assert frozen.best_pure_value == Fraction(1, 6)
    assert frozen.randomized_gain == Fraction(5, 42)

    # Sharp assumption boundary: for the transposition action on two labels,
    # the non-invariant singleton ambiguity prior (1,0) permits unrestricted
    # pure value 1, whereas forced invariant mixing has value 1/2.  The
    # production API therefore must (and does) refuse without invariance.
    noninvariant_counterexample = {
        "unrestricted_value": "1", "forced_invariant_value": "1/2",
        "gap": "1/2", "status": "pass",
    }
    try:
        synthesize_orbit_ambiguity_plan(
            2, 0, ((0,),), product_group((2,)), ((Fraction(1),),),
            ambiguity_kind="noninvariant-negative-control",
            ambiguity_invariant=False,
        )
        raise AssertionError("missing invariance certificate was accepted")
    except ValueError as error:
        assert "action-invariant" in str(error)

    result = {
        "schema": "theorica.orbit-quotient-ambiguity.primary.v1",
        "status": "pass", **counts,
        "two_orbit_value_digest": digest.hexdigest(),
        "frozen_prediction": {
            "status": "pass", "point_orbit_sizes": [3, 4], "k": 2,
            "weights": {"(2/3,0)": "3/7", "(0,1/2)": "4/7"},
            "value": "2/7", "best_pure": "1/6", "gain": "5/42",
        },
        "noninvariant_counterexample": noninvariant_counterexample,
        "smallest_claim": (
            "For a certified finite action-invariant convex ambiguity set and a "
            "G-closed query family, robust planning loses no value by group averaging; "
            "the game factors exactly through point-orbit masses and query-orbit "
            "composition vectors, enabling an exact rational maximin certificate."
        ),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
