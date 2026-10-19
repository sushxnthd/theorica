#!/usr/bin/env python3
"""Exact exhaustive verifier for the sparse orbit-mixture repair law."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations

from theorica.agents.robust_provenance import (
    sample_orbit_mixture_plan,
    synthesize_orbit_mixture_plan,
)


def product_group(sizes):
    offsets = []
    total = 0
    for size in sizes:
        offsets.append(total)
        total += size
    elements = [()]
    for size in sizes:
        elements = [prefix + (shift,) for prefix in elements for shift in range(size)]
    return tuple(
        tuple(
            offsets[j] + (x - offsets[j] + shifts[j]) % sizes[j]
            for x in range(total)
            for j in range(len(sizes))
            if offsets[j] <= x < offsets[j] + sizes[j]
        )
        for shifts in elements
    )


def seeds_for_types(sizes, k):
    offsets = []
    total = 0
    for size in sizes:
        offsets.append(total)
        total += size
    result = []
    for seed in combinations(range(total), k):
        counts = tuple(sum(offsets[j] <= x < offsets[j] + sizes[j] for x in seed)
                       for j in range(len(sizes)))
        if not any(existing[0] == counts for existing in result):
            result.append((counts, seed))
    return tuple(sorted(result))


def exact_weights(points, target):
    """Independent Fraction-only search for a convex representation."""
    dimension = len(target)
    for size in range(1, min(dimension, len(points)) + 1):
        for indices in combinations(range(len(points)), size):
            if size == 1:
                if points[indices[0]] == target:
                    return indices, (Fraction(1),)
                continue
            for coordinate_rows in combinations(range(dimension), size - 1):
                matrix = [[points[index][row] for index in indices] for row in coordinate_rows]
                matrix.append([Fraction(1) for _ in indices])
                rhs = [target[row] for row in coordinate_rows] + [Fraction(1)]
                aug = [row[:] + [value] for row, value in zip(matrix, rhs)]
                singular = False
                for col in range(size):
                    pivot = next((row for row in range(col, size) if aug[row][col]), None)
                    if pivot is None:
                        singular = True
                        break
                    aug[col], aug[pivot] = aug[pivot], aug[col]
                    scale = aug[col][col]
                    aug[col] = [value / scale for value in aug[col]]
                    for row in range(size):
                        if row != col and aug[row][col]:
                            scale = aug[row][col]
                            aug[row] = [a - scale * b for a, b in zip(aug[row], aug[col])]
                if singular:
                    continue
                weights = tuple(aug[i][-1] for i in range(size))
                if not all(weight >= 0 for weight in weights):
                    continue
                if all(sum(weights[p] * points[index][row]
                           for p, index in enumerate(indices)) == target[row]
                       for row in range(dimension)):
                    return indices, weights
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    digest = hashlib.sha256()
    counts = {
        "families": 0, "admissible_families": 0, "feasible": 0,
        "infeasible": 0, "repair_witnesses": 0, "point_checks": 0,
        "support_bound_checks": 0, "sampler_checks": 0,
    }
    smallest_repair = None

    for n in range(3, 10):
        for left in range(1, n):
            sizes = (left, n - left)
            group = product_group(sizes)
            counts["families"] += 1
            for k in range(1, n):
                typed = seeds_for_types(sizes, k)
                points = tuple(tuple(Fraction(c, size) for c, size in zip(kind, sizes))
                               for kind, _ in typed)
                for mask in range(1, 1 << len(typed)):
                    chosen = tuple(i for i in range(len(typed)) if mask & (1 << i))
                    seeds = tuple(typed[i][1] for i in chosen)
                    accessible = tuple(points[i] for i in chosen)
                    target = (Fraction(k, n),) * 2
                    expected = exact_weights(accessible, target) is not None
                    plan = synthesize_orbit_mixture_plan(
                        n, k - 1, seeds, group, ambiguity_kind=f"product-{sizes}",
                        uniform_prior_in_set=True,
                    )
                    assert plan.certificate_valid and plan.feasible == expected
                    counts["admissible_families"] += 1
                    counts["feasible" if expected else "infeasible"] += 1
                    if expected:
                        assert plan.inclusion_probabilities == target * 0 + (Fraction(k, n),) * n
                        assert len(plan.components) <= plan.affine_dimension + 1 <= 2
                        counts["point_checks"] += n
                        counts["support_bound_checks"] += 1
                        individually_balanced = any(point == target for point in accessible)
                        if not individually_balanced:
                            counts["repair_witnesses"] += 1
                            witness = {
                                "n": n, "k": k, "point_orbit_sizes": list(sizes),
                                "accessible_compositions": [[str(x) for x in p] for p in accessible],
                                "weights": [str(c.probability) for c in plan.components],
                                "component_compositions": [
                                    [str(x) for x in c.orbit_composition] for c in plan.components
                                ],
                            }
                            if smallest_repair is None:
                                smallest_repair = witness
                        first = sample_orbit_mixture_plan(plan, f"{sizes}-{k}-{mask}")
                        second = sample_orbit_mixture_plan(plan, f"{sizes}-{k}-{mask}")
                        assert first == second
                        counts["sampler_checks"] += 1
                    digest.update(repr((sizes, k, accessible, expected,
                                        tuple((c.orbit_composition, c.probability)
                                              for c in plan.components))).encode())

    frozen = synthesize_orbit_mixture_plan(
        7, 1, ((0, 3), (3, 4)), product_group((3, 4)),
        ambiguity_kind="frozen-3-4-witness", uniform_prior_in_set=True,
    )
    assert frozen.feasible and frozen.inclusion_probabilities == (Fraction(2, 7),) * 7
    assert tuple(c.probability for c in frozen.components) == (Fraction(6, 7), Fraction(1, 7))
    assert all(c.orbit_composition != (Fraction(2, 7),) * 2 for c in frozen.components)

    three_orbit_cases = three_orbit_feasible = three_orbit_repairs = 0
    for n in range(4, 9):
        for a in range(1, n - 1):
            for b in range(a, n - a):
                c = n - a - b
                if c < b:
                    continue
                sizes = (a, b, c)
                group = product_group(sizes)
                for k in range(1, n):
                    typed = seeds_for_types(sizes, k)
                    points = tuple(tuple(Fraction(x, size) for x, size in zip(kind, sizes))
                                   for kind, _ in typed)
                    index_families = []
                    for support in range(1, min(3, len(typed)) + 1):
                        index_families.extend(combinations(range(len(typed)), support))
                    if len(typed) > 3:
                        index_families.append(tuple(range(len(typed))))
                    for chosen in index_families:
                        accessible = tuple(points[i] for i in chosen)
                        target = (Fraction(k, n),) * 3
                        expected = exact_weights(accessible, target) is not None
                        plan = synthesize_orbit_mixture_plan(
                            n, k - 1, tuple(typed[i][1] for i in chosen), group,
                            ambiguity_kind=f"product-{sizes}", uniform_prior_in_set=True,
                        )
                        assert plan.certificate_valid and plan.feasible == expected
                        three_orbit_cases += 1
                        if expected:
                            three_orbit_feasible += 1
                            assert plan.inclusion_probabilities == (Fraction(k, n),) * n
                            assert len(plan.components) <= plan.affine_dimension + 1 <= 3
                            if target not in accessible:
                                three_orbit_repairs += 1
                        digest.update(repr((sizes, k, accessible, expected,
                                            tuple((c.orbit_composition, c.probability)
                                                  for c in plan.components))).encode())

    result = {
        "schema": "theorica.orbit-mixture-repair.primary.v1",
        "status": "pass",
        **counts,
        "frozen_prediction": {
            "status": "pass", "point_orbit_sizes": [3, 4], "k": 2,
            "weights": ["6/7", "1/7"], "inclusion": "2/7",
        },
        "smallest_repair_witness": smallest_repair,
        "three_orbit_cases": three_orbit_cases,
        "three_orbit_feasible": three_orbit_feasible,
        "three_orbit_repairs": three_orbit_repairs,
        "enumeration_digest": digest.hexdigest(),
        "smallest_claim": (
            "For a finite action and G-closed admissible k-query family, an invariant "
            "plan attains uniform inclusion k/n iff the target orbit-composition vector "
            "lies in the convex hull of accessible query-orbit composition vectors; "
            "when feasible, at most affine_dimension+1 point-orbit mixtures suffice."
        ),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
