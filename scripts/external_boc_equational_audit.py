from __future__ import annotations

"""External Binary Operation Completion audit for THEORICA.

This script evaluates THEORICA-style generic equational mining on binary
operations published in the Binary Operation Completion (BOC) literature.

Operation definitions follow Appendix B of:
Dongsung Huh, "Discovering Group Structures via Unitary Representation
Learning", ICLR 2025, which in turn adopts tasks from Power et al. (2022).

The benchmark is deliberately hostile:
- ground-truth identities are computed exhaustively from the full operation
  table and are not used by the generic miner;
- the miner receives only black-box operation calls on 32 random assignments;
- a much cheaper RoughSpec-style named-template tester is included to show
  that generic equation discovery is not query-efficient when the identity
  family is already known.

The partial modular-division task is excluded because b=0 is outside its stated
domain, so it is not a total binary operation on one finite set.
"""

import itertools
import json
from pathlib import Path

import numpy as np


IDENTITIES = (
    "commutativity",
    "associativity",
    "idempotence",
    "left_self_distributivity",
    "right_self_distributivity",
    "left_alternative",
    "right_alternative",
    "flexibility",
)


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
    """Total operations from the Power/Huh BOC panel."""
    p = 97
    tables = {
        "add": _mod_table(lambda a, b: a + b, p),
        "sub": _mod_table(lambda a, b: a - b, p),
        "cond": _mod_table(
            lambda a, b: (
                a * _mod_inverse(b, p)
                if b % 2 == 1
                else a - b
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


def exhaustive_identity_truth(table: np.ndarray) -> dict[str, bool]:
    """Compute identity truth on the complete finite operation table."""
    n = len(table)
    commutative = bool(np.array_equal(table, table.T))
    idempotent = bool(all(int(table[x, x]) == x for x in range(n)))

    associativity = True
    left_sd = True
    right_sd = True
    for x in range(n):
        for y in range(n):
            xy = int(table[x, y])
            for z in range(n):
                yz = int(table[y, z])
                xz = int(table[x, z])
                if int(table[xy, z]) != int(table[x, yz]):
                    associativity = False
                if int(table[x, yz]) != int(table[xy, xz]):
                    left_sd = False
                if int(table[xy, z]) != int(table[xz, yz]):
                    right_sd = False
            if not (associativity or left_sd or right_sd):
                # All triple identities have already been falsified.
                break
        if not (associativity or left_sd or right_sd):
            break

    left_alt = True
    right_alt = True
    flexible = True
    for x in range(n):
        xx = int(table[x, x])
        for y in range(n):
            yy = int(table[y, y])
            xy = int(table[x, y])
            yx = int(table[y, x])
            left_alt &= int(table[x, xy]) == int(table[xx, y])
            right_alt &= int(table[xy, y]) == int(table[x, yy])
            flexible &= int(table[xy, x]) == int(table[x, yx])

    return {
        "commutativity": commutative,
        "associativity": associativity,
        "idempotence": idempotent,
        "left_self_distributivity": left_sd,
        "right_self_distributivity": right_sd,
        "left_alternative": left_alt,
        "right_alternative": right_alt,
        "flexibility": flexible,
    }


def _var(name: str):
    return ("v", name)


def _op(left, right):
    return ("F", left, right)


def enumerate_terms(max_operations: int = 3):
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
    return terms, by_count


def _eval_term(term, assignment, table, cache):
    if term in cache:
        return cache[term]
    if term[0] == "v":
        value = int(assignment[term[1]])
    else:
        left = _eval_term(term[1], assignment, table, cache)
        right = _eval_term(term[2], assignment, table, cache)
        value = int(table[left, right])
    cache[term] = value
    return value


TARGET_TERMS = {
    "commutativity": (_op(_var("x"), _var("y")), _op(_var("y"), _var("x"))),
    "associativity": (
        _op(_op(_var("x"), _var("y")), _var("z")),
        _op(_var("x"), _op(_var("y"), _var("z"))),
    ),
    "idempotence": (_op(_var("x"), _var("x")), _var("x")),
    "left_self_distributivity": (
        _op(_var("x"), _op(_var("y"), _var("z"))),
        _op(_op(_var("x"), _var("y")), _op(_var("x"), _var("z"))),
    ),
    "right_self_distributivity": (
        _op(_op(_var("x"), _var("y")), _var("z")),
        _op(_op(_var("x"), _var("z")), _op(_var("y"), _var("z"))),
    ),
    "left_alternative": (
        _op(_var("x"), _op(_var("x"), _var("y"))),
        _op(_op(_var("x"), _var("x")), _var("y")),
    ),
    "right_alternative": (
        _op(_op(_var("x"), _var("y")), _var("y")),
        _op(_var("x"), _op(_var("y"), _var("y"))),
    ),
    "flexibility": (
        _op(_op(_var("x"), _var("y")), _var("x")),
        _op(_var("x"), _op(_var("y"), _var("x"))),
    ),
}


def generic_equational_miner(
    table: np.ndarray,
    *,
    assignments: int = 32,
    seed: int = 20260925,
    max_operations: int = 3,
):
    """Mine equalities over the full bounded term language."""
    terms, by_count = enumerate_terms(max_operations)
    rng = np.random.default_rng(seed)
    signatures = {term: [] for term in terms}
    n = len(table)

    for _ in range(assignments):
        assignment = {
            "x": int(rng.integers(0, n)),
            "y": int(rng.integers(0, n)),
            "z": int(rng.integers(0, n)),
        }
        cache = {}
        for term in terms:
            signatures[term].append(_eval_term(term, assignment, table, cache))

    signatures = {term: tuple(values) for term, values in signatures.items()}
    predictions = {
        name: signatures[left] == signatures[right]
        for name, (left, right) in TARGET_TERMS.items()
    }

    compound_terms = len(terms) - 3
    oracle_calls = assignments * compound_terms
    return predictions, {
        "assignments": assignments,
        "max_operations": max_operations,
        "term_count": len(terms),
        "term_count_by_operation_count": {
            str(k): len(v) for k, v in by_count.items()
        },
        "oracle_calls": oracle_calls,
    }


def template_identity_tester(
    table: np.ndarray,
    *,
    assignments: int = 8,
    seed: int = 0,
):
    """Cheap named-template falsification baseline.

    This intentionally receives the identity names/templates in advance, unlike
    the generic miner. It is analogous in spirit to template-based theory
    exploration such as RoughSpec. Each identity stops as soon as one sampled
    counterexample is observed.
    """
    rng = np.random.default_rng(seed)
    n = len(table)
    predicted = {}
    calls = 0

    for name in IDENTITIES:
        holds = True
        for _ in range(assignments):
            x, y, z = map(int, rng.integers(0, n, size=3))
            if name == "commutativity":
                left, right = table[x, y], table[y, x]
                calls += 2
            elif name == "associativity":
                xy, yz = table[x, y], table[y, z]
                left, right = table[int(xy), z], table[x, int(yz)]
                calls += 4
            elif name == "idempotence":
                left, right = table[x, x], x
                calls += 1
            elif name == "left_self_distributivity":
                yz, xy, xz = table[y, z], table[x, y], table[x, z]
                left, right = table[x, int(yz)], table[int(xy), int(xz)]
                calls += 5
            elif name == "right_self_distributivity":
                xy, xz, yz = table[x, y], table[x, z], table[y, z]
                left, right = table[int(xy), z], table[int(xz), int(yz)]
                calls += 5
            elif name == "left_alternative":
                xy, xx = table[x, y], table[x, x]
                left, right = table[x, int(xy)], table[int(xx), y]
                calls += 4
            elif name == "right_alternative":
                xy, yy = table[x, y], table[y, y]
                left, right = table[int(xy), y], table[x, int(yy)]
                calls += 4
            else:  # flexibility
                xy, yx = table[x, y], table[y, x]
                left, right = table[int(xy), x], table[x, int(yx)]
                calls += 4

            if int(left) != int(right):
                holds = False
                break
        predicted[name] = holds

    return predicted, calls


def run():
    tables = published_boc_tables()
    truths = {
        name: exhaustive_identity_truth(table)
        for name, table in tables.items()
    }
    records = []
    total_correct = 0

    for task_index, (name, table) in enumerate(tables.items()):
        truth = truths[name]
        prediction, miner_meta = generic_equational_miner(
            table,
            assignments=32,
            seed=20260925 + task_index,
            max_operations=3,
        )
        correct = sum(
            bool(prediction[key]) == bool(truth[key]) for key in IDENTITIES
        )
        total_correct += correct
        records.append(
            {
                "task": name,
                "size": int(len(table)),
                "truth": truth,
                "generic_miner_prediction": prediction,
                "identity_labels_correct": int(correct),
                "identity_labels_total": len(IDENTITIES),
                "generic_miner_oracle_calls": miner_meta["oracle_calls"],
            }
        )

    # Hostile template baseline: 100 independent seeds.
    template_seed_records = []
    for repeat in range(100):
        correct = 0
        calls = 0
        for task_index, (name, table) in enumerate(tables.items()):
            truth = truths[name]
            prediction, task_calls = template_identity_tester(
                table,
                assignments=8,
                seed=100000 + 1000 * repeat + task_index,
            )
            calls += task_calls
            correct += sum(
                bool(prediction[key]) == bool(truth[key])
                for key in IDENTITIES
            )
        template_seed_records.append(
            {
                "repeat": repeat,
                "correct": int(correct),
                "total": len(tables) * len(IDENTITIES),
                "mean_calls_per_task": float(calls / len(tables)),
            }
        )

    miner_calls = records[0]["generic_miner_oracle_calls"]
    summary = {
        "external_tasks": len(tables),
        "identity_labels": len(tables) * len(IDENTITIES),
        "generic_miner_correct": int(total_correct),
        "generic_miner_accuracy": float(
            total_correct / (len(tables) * len(IDENTITIES))
        ),
        "generic_miner_calls_per_task": int(miner_calls),
        "generic_miner_term_count": 471,
        "template_baseline_repeats": 100,
        "template_baseline_perfect_repeats": int(
            sum(
                row["correct"] == row["total"]
                for row in template_seed_records
            )
        ),
        "template_baseline_mean_calls_per_task": float(
            np.mean(
                [row["mean_calls_per_task"] for row in template_seed_records]
            )
        ),
        "template_baseline_max_calls_per_task": float(
            np.max(
                [row["mean_calls_per_task"] for row in template_seed_records]
            )
        ),
        "division_task_excluded": (
            "Published div task omits b=0 and is therefore not a total binary "
            "operation on a single finite carrier."
        ),
    }

    payload = {
        "experiment": "External BOC equational-structure falsification audit",
        "date": "2026-09-25",
        "source_benchmark": (
            "Binary Operation Completion tasks in Huh, ICLR 2025 Appendix B, "
            "adopted from Power et al. 2022"
        ),
        "identity_panel": list(IDENTITIES),
        "summary": summary,
        "records": records,
        "template_seed_records": template_seed_records,
    }
    Path("results/external_boc_equational_audit.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    assert summary["generic_miner_correct"] == summary["identity_labels"]
    assert summary["template_baseline_perfect_repeats"] == 100
    assert records[
        [r["task"] for r in records].index("S5_conj")
    ]["generic_miner_prediction"]["left_self_distributivity"]
    assert summary["template_baseline_mean_calls_per_task"] < (
        summary["generic_miner_calls_per_task"] / 100
    )


if __name__ == "__main__":
    run()
