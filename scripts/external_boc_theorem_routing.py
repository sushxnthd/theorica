from __future__ import annotations

"""External end-to-end theorem-routing audit on published BOC operations.

The operations come from the Binary Operation Completion task panel printed in
Appendix B of Huh (ICLR 2025), following Power et al. (2022).

THEORICA is not told which tasks are groups. For every task it:

1. generically mines shallow equational identities from black-box calls;
2. routes only if associativity is empirically supported;
3. searches for and validates a two-sided identity;
4. actively acquires right-regular generator actions;
5. reconstructs the entire operation table from the learned representation;
6. abstains when the group route cannot be certified.

Ground truth is used only after discovery, for evaluation.

This is an external falsification benchmark, not a claim of sample-efficiency
superiority. Huh's HyperCube-SE reports substantially stronger group-only BOC
sample efficiency when the representation bias is supplied in advance.
"""

import itertools
import json
from collections import deque
from pathlib import Path

import numpy as np


class TableOracle:
    def __init__(self, table: np.ndarray):
        self.table = np.asarray(table, dtype=np.int64)
        self.calls = 0

    def __call__(self, a: int, b: int) -> int:
        self.calls += 1
        return int(self.table[int(a), int(b)])


def _mod_inverse(x: int, p: int = 97) -> int:
    return pow(int(x), p - 2, p)


def _mod_table(fn, p: int = 97) -> np.ndarray:
    table = np.empty((p, p), dtype=np.int64)
    for a in range(p):
        for b in range(p):
            table[a, b] = int(fn(a, b)) % p
    return table


def _permutation_table(fn, size: int = 5) -> np.ndarray:
    permutations = list(itertools.permutations(range(size)))
    index = {perm: i for i, perm in enumerate(permutations)}

    def compose(a, b):
        return tuple(a[b[i]] for i in range(size))

    def inverse(a):
        out = [0] * size
        for i, value in enumerate(a):
            out[value] = i
        return tuple(out)

    table = np.empty((len(permutations), len(permutations)), dtype=np.int64)
    for i, a in enumerate(permutations):
        for j, b in enumerate(permutations):
            table[i, j] = index[fn(a, b, compose, inverse)]
    return table


def published_boc_tables() -> dict[str, np.ndarray]:
    p = 97
    tables = {
        "add": _mod_table(lambda a, b: a + b, p),
        "sub": _mod_table(lambda a, b: a - b, p),
        "cond": _mod_table(
            lambda a, b: (
                a * _mod_inverse(b, p) if b % 2 == 1 else a - b
            ),
            p,
        ),
        "quad1": _mod_table(lambda a, b: a**2 + b**2, p),
        "quad2": _mod_table(lambda a, b: a**2 + a * b + b**2, p),
        "quad3": _mod_table(lambda a, b: a**2 + a * b + b**2 + a, p),
        "cube1": _mod_table(lambda a, b: a**3 + a * b, p),
        "cube2": _mod_table(lambda a, b: a**3 + a * b**2 + b, p),
    }

    tables["S5_comp"] = _permutation_table(
        lambda a, b, compose, inverse: compose(a, b)
    )
    tables["S5_conj"] = _permutation_table(
        lambda a, b, compose, inverse: compose(compose(a, b), inverse(a))
    )
    tables["S5_aba"] = _permutation_table(
        lambda a, b, compose, inverse: compose(compose(a, b), a)
    )
    return tables


def _var(name: str):
    return ("v", name)


def _op(left, right):
    return ("F", left, right)


def enumerate_terms(max_operations: int = 2):
    variables = [_var("x"), _var("y"), _var("z")]
    by_count = {0: variables}
    terms = list(variables)
    for count in range(1, max_operations + 1):
        generated = {}
        for left_count in range(count):
            right_count = count - 1 - left_count
            for left in by_count[left_count]:
                for right in by_count[right_count]:
                    term = _op(left, right)
                    generated[repr(term)] = term
        by_count[count] = list(generated.values())
        terms.extend(by_count[count])
    return terms


def _eval_term(term, assignment, oracle: TableOracle, cache):
    if term in cache:
        return cache[term]
    if term[0] == "v":
        value = int(assignment[term[1]])
    else:
        left = _eval_term(term[1], assignment, oracle, cache)
        right = _eval_term(term[2], assignment, oracle, cache)
        value = oracle(left, right)
    cache[term] = value
    return value


COMM = (_op(_var("x"), _var("y")), _op(_var("y"), _var("x")))
ASSOC = (
    _op(_op(_var("x"), _var("y")), _var("z")),
    _op(_var("x"), _op(_var("y"), _var("z"))),
)
IDEM = (_op(_var("x"), _var("x")), _var("x"))


def generic_structure_probe(
    oracle: TableOracle,
    n: int,
    *,
    assignments: int = 12,
    seed: int,
):
    terms = enumerate_terms(max_operations=2)
    rng = np.random.default_rng(seed)
    signatures = {term: [] for term in terms}

    for _ in range(assignments):
        assignment = {
            "x": int(rng.integers(0, n)),
            "y": int(rng.integers(0, n)),
            "z": int(rng.integers(0, n)),
        }
        cache = {}
        for term in terms:
            signatures[term].append(
                _eval_term(term, assignment, oracle, cache)
            )

    signatures = {
        term: tuple(values) for term, values in signatures.items()
    }

    def equal(pair):
        left, right = pair
        return signatures[left] == signatures[right]

    return {
        "commutative": bool(equal(COMM)),
        "associative": bool(equal(ASSOC)),
        "idempotent": bool(equal(IDEM)),
        "assignments": int(assignments),
        "term_count": int(len(terms)),
    }


def find_two_sided_identity(
    oracle: TableOracle,
    n: int,
    *,
    seed: int,
    validation_probes: int = 16,
):
    rng = np.random.default_rng(seed)
    anchor = int(rng.integers(0, n))

    candidates = []
    for candidate in range(n):
        if (
            oracle(anchor, candidate) == anchor
            and oracle(candidate, anchor) == anchor
        ):
            candidates.append(candidate)

    for candidate in candidates:
        valid = True
        probes = list(
            map(int, rng.integers(0, n, size=validation_probes))
        )
        probes.extend([0, n - 1, anchor, candidate])
        for x in probes:
            if (
                oracle(x, candidate) != x
                or oracle(candidate, x) != x
            ):
                valid = False
                break
        if valid:
            return int(candidate)
    return None


def _inverse_permutation(action: np.ndarray) -> np.ndarray | None:
    n = len(action)
    if sorted(map(int, action)) != list(range(n)):
        return None
    inv = np.empty(n, dtype=np.int64)
    for x, y in enumerate(action):
        inv[int(y)] = int(x)
    return inv


def closure_words(
    n: int,
    identity: int,
    actions: list[np.ndarray],
):
    """Return a word for every reached element under right actions/inverses."""
    generators = []
    for index, action in enumerate(actions):
        inverse = _inverse_permutation(action)
        if inverse is None:
            return None, None
        generators.append((index, 1, action))
        generators.append((index, -1, inverse))

    words = {int(identity): tuple()}
    queue = deque([int(identity)])

    while queue:
        x = queue.popleft()
        base = words[x]
        for index, sign, action in generators:
            y = int(action[x])
            if y not in words:
                words[y] = base + ((index, sign),)
                queue.append(y)
    return words, generators


def reconstruct_from_actions(
    n: int,
    words: dict[int, tuple],
    actions: list[np.ndarray],
) -> np.ndarray:
    inverses = []
    for action in actions:
        inv = _inverse_permutation(action)
        if inv is None:
            raise RuntimeError("non-bijective learned action")
        inverses.append(inv)

    table = np.empty((n, n), dtype=np.int64)
    for a in range(n):
        for b in range(n):
            value = int(a)
            for index, sign in words[b]:
                if sign == 1:
                    value = int(actions[index][value])
                else:
                    value = int(inverses[index][value])
            table[a, b] = value
    return table


def acquire_group_representation(
    oracle: TableOracle,
    n: int,
    *,
    seed: int,
    max_generators: int = 10,
):
    """Actively acquire a right-regular representation if possible."""
    rng = np.random.default_rng(seed)
    identity = find_two_sided_identity(
        oracle, n, seed=seed + 1, validation_probes=16
    )
    if identity is None:
        return {
            "accepted": False,
            "reason": "no_validated_identity",
            "identity": None,
            "generator_count": 0,
            "coverage": 0,
            "reconstruction": None,
        }

    actions: list[np.ndarray] = []
    generator_elements: list[int] = []
    words = {int(identity): tuple()}

    for _ in range(max_generators):
        if len(words) == n:
            break

        unseen = [x for x in range(n) if x not in words]
        if not unseen:
            break
        g = int(rng.choice(unseen))

        action = np.asarray(
            [oracle(x, g) for x in range(n)], dtype=np.int64
        )
        if _inverse_permutation(action) is None:
            return {
                "accepted": False,
                "reason": "non_bijective_right_action",
                "identity": int(identity),
                "generator_count": len(actions),
                "coverage": len(words),
                "reconstruction": None,
            }

        actions.append(action)
        generator_elements.append(g)
        words, _ = closure_words(n, identity, actions)
        if words is None:
            return {
                "accepted": False,
                "reason": "invalid_action",
                "identity": int(identity),
                "generator_count": len(actions),
                "coverage": 0,
                "reconstruction": None,
            }

    if len(words) != n:
        return {
            "accepted": False,
            "reason": "carrier_not_generated",
            "identity": int(identity),
            "generator_count": len(actions),
            "coverage": len(words),
            "reconstruction": None,
        }

    reconstruction = reconstruct_from_actions(n, words, actions)
    return {
        "accepted": True,
        "reason": "group_representation_recovered",
        "identity": int(identity),
        "generator_count": len(actions),
        "generator_elements": generator_elements,
        "coverage": len(words),
        "reconstruction": reconstruction,
    }


def run():
    tables = published_boc_tables()
    expected_group = {"add", "S5_comp"}
    repeats = 100
    records = []

    for repeat in range(repeats):
        for task_index, (task, table) in enumerate(tables.items()):
            oracle = TableOracle(table)
            seed = 20260925 + 10000 * repeat + task_index

            structure = generic_structure_probe(
                oracle,
                len(table),
                assignments=12,
                seed=seed,
            )
            mining_calls = int(oracle.calls)

            group_result = None
            if structure["associative"]:
                group_result = acquire_group_representation(
                    oracle,
                    len(table),
                    seed=seed + 500000,
                    max_generators=10,
                )

            accepted = bool(
                group_result is not None and group_result["accepted"]
            )
            expected = task in expected_group
            exact = False
            generators = 0
            if accepted:
                generators = int(group_result["generator_count"])
                exact = bool(
                    np.array_equal(
                        group_result["reconstruction"],
                        table,
                    )
                )

            records.append(
                {
                    "repeat": repeat,
                    "task": task,
                    "carrier_size": int(len(table)),
                    "expected_group": expected,
                    "structure": structure,
                    "route_accepted": accepted,
                    "route_correct": accepted == expected,
                    "exact_reconstruction": exact,
                    "mining_calls": mining_calls,
                    "total_oracle_calls": int(oracle.calls),
                    "representation_calls": int(
                        oracle.calls - mining_calls
                    ),
                    "generator_count": generators,
                    "group_route_reason": (
                        None
                        if group_result is None
                        else group_result["reason"]
                    ),
                }
            )

    positives = [r for r in records if r["expected_group"]]
    negatives = [r for r in records if not r["expected_group"]]

    task_summaries = {}
    for task, table in tables.items():
        rows = [r for r in records if r["task"] == task]
        calls = np.asarray(
            [r["total_oracle_calls"] for r in rows], dtype=float
        )
        task_summaries[task] = {
            "carrier_size": int(len(table)),
            "full_table_entries": int(len(table) ** 2),
            "route_accuracy": float(
                np.mean([r["route_correct"] for r in rows])
            ),
            "acceptance_rate": float(
                np.mean([r["route_accepted"] for r in rows])
            ),
            "exact_reconstruction_rate": float(
                np.mean(
                    [
                        r["exact_reconstruction"]
                        for r in rows
                        if r["expected_group"]
                    ]
                )
                if task in expected_group
                else 0.0
            ),
            "mean_total_oracle_calls": float(np.mean(calls)),
            "median_total_oracle_calls": float(np.median(calls)),
            "min_total_oracle_calls": int(np.min(calls)),
            "max_total_oracle_calls": int(np.max(calls)),
            "mean_fraction_of_full_table": float(
                np.mean(calls) / (len(table) ** 2)
            ),
            "mean_generator_count": float(
                np.mean([r["generator_count"] for r in rows])
            ),
        }

    summary = {
        "external_tasks": len(tables),
        "repeats": repeats,
        "task_repeat_cases": len(records),
        "route_decisions_correct": int(
            sum(r["route_correct"] for r in records)
        ),
        "positive_group_cases": len(positives),
        "negative_nongroup_cases": len(negatives),
        "positive_routes_accepted": int(
            sum(r["route_accepted"] for r in positives)
        ),
        "negative_routes_abstained": int(
            sum(not r["route_accepted"] for r in negatives)
        ),
        "exact_group_reconstructions": int(
            sum(r["exact_reconstruction"] for r in positives)
        ),
        "fixed_generic_mining_calls": int(
            records[0]["mining_calls"]
        ),
        "expected_group_tasks": sorted(expected_group),
        "task_summaries": task_summaries,
        "claim_boundary": (
            "External end-to-end transfer of structure discovery -> group "
            "theorem routing -> right-regular representation acquisition -> "
            "exact table reconstruction. Not a sample-efficiency superiority "
            "claim; specialized methods such as HyperCube-SE receive a group "
            "representation bias in advance and report stronger group-only "
            "sample efficiency."
        ),
    }

    payload = {
        "experiment": (
            "THEORICA external BOC theorem-routing and representation audit"
        ),
        "date": "2026-09-25",
        "source_benchmark": (
            "Binary Operation Completion operations in Huh, ICLR 2025 "
            "Appendix B, following Power et al. 2022"
        ),
        "summary": summary,
        "records": records,
    }
    Path("results/external_boc_theorem_routing.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    assert summary["route_decisions_correct"] == len(records)
    assert summary["positive_routes_accepted"] == len(positives)
    assert summary["negative_routes_abstained"] == len(negatives)
    assert summary["exact_group_reconstructions"] == len(positives)
    assert (
        summary["task_summaries"]["add"]["mean_fraction_of_full_table"]
        < 0.12
    )
    assert (
        summary["task_summaries"]["S5_comp"]["mean_fraction_of_full_table"]
        < 0.12
    )


if __name__ == "__main__":
    run()
