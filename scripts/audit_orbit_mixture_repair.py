#!/usr/bin/env python3
"""Independent audit of the orbit-mixture artifact; no production import."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations


def types(a, b, k):
    out = []
    for x in range(max(0, k - b), min(a, k) + 1):
        out.append((Fraction(x, a), Fraction(k - x, b)))
    return tuple(out)


def feasible(points, target):
    if target in points:
        return True
    for left, right in combinations(points, 2):
        delta = left[0] - right[0]
        if delta == 0:
            continue
        weight = (target[0] - right[0]) / delta
        if 0 <= weight <= 1 and all(
            weight * left[j] + (1 - weight) * right[j] == target[j] for j in range(2)
        ):
            return True
    return False


def compositions(sizes, k):
    result = []
    def visit(index, remaining, prefix):
        if index == len(sizes) - 1:
            if 0 <= remaining <= sizes[index]:
                counts = prefix + (remaining,)
                result.append(tuple(Fraction(x, size) for x, size in zip(counts, sizes)))
            return
        for value in range(max(0, remaining - sum(sizes[index + 1:])),
                           min(sizes[index], remaining) + 1):
            visit(index + 1, remaining - value, prefix + (value,))
    visit(0, k, ())
    return tuple(sorted(result))


def feasible_three(points, target):
    if target in points:
        return True
    for left, right in combinations(points, 2):
        for coordinate in range(3):
            delta = left[coordinate] - right[coordinate]
            if delta:
                weight = (target[coordinate] - right[coordinate]) / delta
                if 0 <= weight <= 1 and all(
                    weight * left[j] + (1 - weight) * right[j] == target[j] for j in range(3)
                ):
                    return True
                break
    for p, q, r in combinations(points, 3):
        # Try each pair of coordinate equations together with sum(weights)=1.
        for rows in combinations(range(3), 2):
            matrix = [[p[row], q[row], r[row]] for row in rows]
            matrix.append([Fraction(1), Fraction(1), Fraction(1)])
            rhs = [target[row] for row in rows] + [Fraction(1)]
            aug = [row[:] + [value] for row, value in zip(matrix, rhs)]
            singular = False
            for col in range(3):
                pivot = next((row for row in range(col, 3) if aug[row][col]), None)
                if pivot is None:
                    singular = True
                    break
                aug[col], aug[pivot] = aug[pivot], aug[col]
                scale = aug[col][col]
                aug[col] = [value / scale for value in aug[col]]
                for row in range(3):
                    if row != col and aug[row][col]:
                        scale = aug[row][col]
                        aug[row] = [a - scale * b for a, b in zip(aug[row], aug[col])]
            if singular:
                continue
            weights = tuple(aug[i][-1] for i in range(3))
            if all(weight >= 0 for weight in weights) and all(
                weights[0] * p[j] + weights[1] * q[j] + weights[2] * r[j] == target[j]
                for j in range(3)
            ):
                return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    primary = json.load(open(args.primary, encoding="utf-8"))
    digest = hashlib.sha256()
    counts = {"families": 0, "admissible_families": 0, "feasible": 0,
              "infeasible": 0, "repair_witnesses": 0}
    for n in range(3, 10):
        for a in range(1, n):
            b = n - a
            counts["families"] += 1
            for k in range(1, n):
                points = types(a, b, k)
                target = (Fraction(k, n),) * 2
                for mask in range(1, 1 << len(points)):
                    accessible = tuple(points[i] for i in range(len(points)) if mask & (1 << i))
                    ok = feasible(accessible, target)
                    counts["admissible_families"] += 1
                    counts["feasible" if ok else "infeasible"] += 1
                    if ok and target not in accessible:
                        counts["repair_witnesses"] += 1
                    digest.update(repr(((a, b), k, accessible, ok)).encode())
    for key, value in counts.items():
        assert primary[key] == value, (key, primary[key], value)
    # The primary digest additionally commits production weights, so this
    # audit records its own independently derived feasibility digest.
    assert primary["status"] == "pass"
    assert primary["repair_witnesses"] > 0
    assert primary["frozen_prediction"] == {
        "status": "pass", "point_orbit_sizes": [3, 4], "k": 2,
        "weights": ["6/7", "1/7"], "inclusion": "2/7",
    }
    three_cases = three_feasible = three_repairs = 0
    for n in range(4, 9):
        for a in range(1, n - 1):
            for b in range(a, n - a):
                c = n - a - b
                if c < b:
                    continue
                sizes = (a, b, c)
                for k in range(1, n):
                    points = compositions(sizes, k)
                    families = []
                    for support in range(1, min(3, len(points)) + 1):
                        families.extend(combinations(range(len(points)), support))
                    if len(points) > 3:
                        families.append(tuple(range(len(points))))
                    target = (Fraction(k, n),) * 3
                    for chosen in families:
                        accessible = tuple(points[i] for i in chosen)
                        ok = feasible_three(accessible, target)
                        three_cases += 1
                        if ok:
                            three_feasible += 1
                            if target not in accessible:
                                three_repairs += 1
    assert primary["three_orbit_cases"] == three_cases
    assert primary["three_orbit_feasible"] == three_feasible
    assert primary["three_orbit_repairs"] == three_repairs
    result = {
        "schema": "theorica.orbit-mixture-repair.audit.v1",
        "status": "pass", "independent": True, **counts,
        "three_orbit_cases": three_cases,
        "three_orbit_feasible": three_feasible,
        "three_orbit_repairs": three_repairs,
        "feasibility_digest": digest.hexdigest(),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
