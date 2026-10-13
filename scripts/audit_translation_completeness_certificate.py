#!/usr/bin/env python3
"""Independent constructive audit of the completeness-certificate theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    failures = []
    cases = 0
    for n in range(2, args.max_n + 1):
        identity = list(range(n))
        for mask in range(1 << n) if n <= 16 else (0, 1, (1 << (n - 2)) - 1):
            queried = {index for index in range(n) if mask & (1 << index)}
            if len(queried) > n - 2:
                continue
            unqueried = [index for index in range(n) if index not in queried]
            first, second = unqueried[:2]
            adversary = identity.copy()
            adversary[first], adversary[second] = adversary[second], adversary[first]
            cases += 1
            if adversary == identity or any(adversary[index] != identity[index] for index in queried):
                failures.append({"n": n, "queried": sorted(queried)})
        for missing in range(n):
            observed_outputs = {identity[index] for index in range(n) if index != missing}
            forced = set(range(n)) - observed_outputs
            cases += 1
            if forced != {identity[missing]}:
                failures.append({"n": n, "missing": missing, "forced": sorted(forced)})
    payload = {
        "schema": "theorica.translation-completeness-certificate-audit.v1",
        "method": "constructive_transposition_and_forced_last_image",
        "max_n": args.max_n,
        "cases": cases,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
