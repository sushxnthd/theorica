#!/usr/bin/env python3
"""Zero-production-import audit of the complement-transporter coset law."""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from math import factorial
from pathlib import Path

SOURCE = Path("results/qary_complement_transporter_coset/results.json")
OUT = Path("results/qary_complement_transporter_coset/audit.json")


def weak_compositions(total: int, parts: int, prefix=()):
    if parts == 1:
        yield (*prefix, total)
        return
    for value in range(total + 1):
        yield from weak_compositions(total - value, parts - 1, (*prefix, value))


def shape_from_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(weight for weight, count in enumerate(counts) for _ in range(count))


def stabilizer(shape: tuple[int, ...], q: int) -> int:
    counts = Counter(shape)
    out = 1
    for weight, multiplicity in counts.items():
        out *= factorial(multiplicity)
        out *= (factorial(weight) * factorial(q - weight)) ** multiplicity
    return out


def certificate(shape: tuple[int, ...], q: int, group_order: int) -> dict:
    buckets = {
        weight: [index for index, value in enumerate(shape) if value == weight]
        for weight in range(q + 1)
    }
    root = [-1] * q
    for weight in range(q // 2):
        for left, right in zip(buckets[weight], buckets[q - weight], strict=True):
            root[left], root[right] = right, left
    for index in buckets[q // 2]:
        root[index] = index
    shifts = [(q - weight) % q for weight in shape]
    encoded = []
    image = set()
    universe = {(branch, leaf) for branch in range(q) for leaf in range(q)}
    family = {
        (branch, leaf)
        for branch, weight in enumerate(shape)
        for leaf in range(weight)
    }
    for branch in range(q):
        for leaf in range(q):
            target = (root[branch], (leaf + shifts[branch]) % q)
            encoded.append(f"{branch},{leaf}->{target[0]},{target[1]}")
            if (branch, leaf) in family:
                image.add(target)
    order = stabilizer(shape, q)
    orbit = group_order // order
    return {
        "shape": list(shape),
        "root_involution": root,
        "leaf_shifts": shifts,
        "map_sha256": hashlib.sha256("\n".join(encoded).encode()).hexdigest(),
        "stabilizer_order": order,
        "complement_transporter_count": order,
        "orbit_size": orbit,
        "orbit_times_transporters": orbit * order,
        "full_map_passed": (
            sorted(root) == list(range(q))
            and all(root[root[i]] == i for i in range(q))
            and image == universe - family
        ),
    }


def exhaustive_q2_model() -> dict:
    q = 2
    root_permutations = tuple(itertools.permutations(range(q)))
    child_permutations = tuple(itertools.permutations(range(q)))
    group = tuple(
        (root, children)
        for root in root_permutations
        for children in itertools.product(child_permutations, repeat=q)
    )
    rows = []
    for shape in ((0, 2), (1, 1)):
        family = {
            (branch, leaf)
            for branch, weight in enumerate(shape)
            for leaf in range(weight)
        }
        universe = {(branch, leaf) for branch in range(q) for leaf in range(q)}
        complement = universe - family
        stabilizers = 0
        transporters = 0
        for root, children in group:
            image = {
                (root[branch], children[branch][leaf]) for branch, leaf in family
            }
            stabilizers += image == family
            transporters += image == complement
        rows.append(
            {
                "shape": list(shape),
                "stabilizers": stabilizers,
                "transporters": transporters,
                "equal": stabilizers == transporters == stabilizer(shape, q),
            }
        )
    return {"group_elements": len(group), "fixed_classes": rows}


def main() -> None:
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    q = 10
    group_order = factorial(q) ** (q + 1)
    rows = tuple(weak_compositions(q, q + 1))
    half_rows = tuple(
        row
        for row in rows
        if sum(weight * count for weight, count in enumerate(row)) == 50
    )
    fixed_rows = tuple(
        sorted(
            (row for row in half_rows if row == tuple(reversed(row))),
            key=shape_from_counts,
        )
    )
    pair_rows = tuple(row for row in half_rows if row < tuple(reversed(row)))
    records = tuple(
        certificate(shape_from_counts(row), q, group_order) for row in fixed_rows
    )
    stream = "\n".join(
        json.dumps(record, sort_keys=True, separators=(",", ":")) for record in records
    )
    reported = result["q10_h2_holdout"]
    q2 = exhaustive_q2_model()
    passed = (
        len(rows) == 184756
        and len(half_rows) == 5448
        and len(fixed_rows) == 252
        and len(pair_rows) == 2598
        and list(records) == reported["fixed_class_records"]
        and hashlib.sha256(stream.encode()).hexdigest()
        == reported["fixed_record_stream_sha256"]
        and all(record["full_map_passed"] for record in records)
        and all(
            record["orbit_times_transporters"] == group_order for record in records
        )
        and q2["group_elements"] == 8
        and all(row["equal"] for row in q2["fixed_classes"])
        and result["summary"]["overall_passed"] is True
    )
    report = {
        "schema": "theorica.complement-transporter-coset-audit/1",
        "production_imports": 0,
        "independent_method": "weak compositions plus exhaustive q=2 tree-group action",
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "orbit_representatives_reconstructed": len(rows),
        "half_density_classes_reconstructed": len(half_rows),
        "fixed_classes_reconstructed": len(fixed_rows),
        "nonfixed_pairs_reconstructed": len(pair_rows),
        "full_involutions_reconstructed": len(records),
        "fixed_record_stream_sha256": hashlib.sha256(stream.encode()).hexdigest(),
        "small_model": q2,
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "small_model"}, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
