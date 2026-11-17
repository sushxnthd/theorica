#!/usr/bin/env python3
"""Zero-production-import audit of complement fixed points."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path

SOURCE = Path("results/qary_even_half_density_complement_fixed_points/results.json")
OUT = Path("results/qary_even_half_density_complement_fixed_points/audit.json")


def weak_compositions(total: int, parts: int, prefix=()):
    if parts == 1:
        yield (*prefix, total)
        return
    for value in range(total + 1):
        yield from weak_compositions(total - value, parts - 1, (*prefix, value))


def canonical_from_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(value for value, count in enumerate(counts) for _ in range(count))


def multiset_count(n: int, r: int) -> int:
    if r == 0:
        return 1
    if n == 0:
        return 0
    return comb(n + r - 1, r)


def main() -> None:
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    q = 6
    rows = tuple(weak_compositions(q, q + 1))
    coefficients = Counter(
        sum(value * count for value, count in enumerate(row)) for row in rows
    )
    half_rows = tuple(
        row
        for row in rows
        if sum(value * count for value, count in enumerate(row)) == 18
    )
    complement = {row: tuple(reversed(row)) for row in half_rows}
    fixed = tuple(row for row in half_rows if complement[row] == row)
    pairs = tuple(row for row in half_rows if row < complement[row])
    fixed_recurrence = sum(
        multiset_count(3, j) * multiset_count(1, q - 2 * j)
        for j in range(q // 2 + 1)
    )
    fixed_shapes = sorted(canonical_from_counts(row) for row in fixed)
    reported = result["q6_h2_holdout"]
    deterministic = hashlib.sha256(
        "\n".join(
            ",".join(map(str, canonical_from_counts(row))) for row in rows
        ).encode()
    ).hexdigest()
    passed = (
        len(rows) == 924
        and sum(coefficients.values()) == 924
        and [coefficients[k] for k in range(15, 22)] == [51, 55, 55, 58, 55, 55, 51]
        and len(half_rows) == 58
        and len(fixed) == fixed_recurrence == 20
        and len(pairs) == 19
        and all(complement[complement[row]] == row for row in half_rows)
        and fixed_shapes == sorted(tuple(row) for row in reported["fixed_shapes"])
        and reported["labelled_family_count"] == comb(36, 18) == 9075135300
        and result["summary"]["overall_passed"] is True
    )
    report = {
        "schema": "theorica.even-half-density-complement-fixed-points-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "independent_method": "weak compositions of six across seven child weights",
        "orbit_representatives_reconstructed": len(rows),
        "half_density_classes_reconstructed": len(half_rows),
        "fixed_classes_reconstructed": len(fixed),
        "complement_pairs_reconstructed": len(pairs),
        "fixed_recurrence_recomputed": fixed_recurrence,
        "canonical_shape_stream_sha256": deterministic,
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
