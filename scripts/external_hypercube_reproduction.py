from __future__ import annotations

"""Clean-room reproduction of HyperCube's small BOC experiments.

This is NOT official HyperCube code. It is a clean-room implementation of the
architecture and regularizer printed in Appendix A of:

Dongsung Huh, "Discovering Group Structures via Unitary Representation
Learning", ICLR 2025.

The paper specifies:
- T_abc = einsum('aij,bjk,cki->abc', A,B,C) / n
- the HyperCube regularizer printed below;
- N(0, 1/sqrt(n)) initialization;
- full-batch gradient descent, lr=0.5, momentum=0.5;
- epsilon=0.1 for small-scale experiments;
- 60% of the Cayley table as training data.

We intentionally use a simple fixed-epsilon 500-step protocol rather than
claiming an exact reproduction of the paper's adaptive epsilon scheduler.
The purpose is adversarial benchmarking: establish that a strong published
algebraic inductive bias transfers under a minimal clean-room implementation.
"""

import itertools
import json
import math
from pathlib import Path

import numpy as np
import torch


def small_boc_tables() -> dict[str, np.ndarray]:
    n = 6
    add = np.fromfunction(lambda a, b: (a + b) % n, (n, n), dtype=int)
    sub = np.fromfunction(lambda a, b: (a - b) % n, (n, n), dtype=int)
    sqadd = np.fromfunction(
        lambda a, b: (a**2 + b**2) % n, (n, n), dtype=int
    ).astype(np.int64)

    perms = list(itertools.permutations(range(3)))
    index = {perm: i for i, perm in enumerate(perms)}

    def compose(a, b):
        return tuple(a[b[i]] for i in range(3))

    s3 = np.empty((6, 6), dtype=np.int64)
    for i, a in enumerate(perms):
        for j, b in enumerate(perms):
            s3[i, j] = index[compose(a, b)]

    return {
        "C6_add": np.asarray(add, dtype=np.int64),
        "C6_sub": np.asarray(sub, dtype=np.int64),
        "C6_squared_add": sqadd,
        "S3_composition": s3,
    }


def hypercube_product(A, B, C):
    return torch.einsum("aij,bjk,cki->abc", A, B, C) / A.shape[0]


def hypercube_regularizer(A, B, C):
    def helper(M, N):
        MM = torch.einsum("aim,aij->mj", M, M)
        NN = torch.einsum("bjk,bmk->jm", N, N)
        return torch.einsum("mj,jm->", MM, NN)

    return (
        helper(A, B) + helper(B, C) + helper(C, A)
    ) / A.shape[0]


def train(
    table: np.ndarray,
    *,
    seed: int,
    regularizer: str,
    steps: int = 500,
    train_fraction: float = 0.60,
    epsilon: float = 0.10,
):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    n = int(len(table))

    pairs = [(a, b) for a in range(n) for b in range(n)]
    rng.shuffle(pairs)
    n_train = round(train_fraction * len(pairs))
    train_pairs = set(pairs[:n_train])
    test_pairs = [pair for pair in pairs if pair not in train_pairs]

    target = torch.zeros((n, n, n), dtype=torch.float32)
    mask = torch.zeros((n, n, 1), dtype=torch.float32)
    for a, b in train_pairs:
        target[a, b, int(table[a, b])] = 1.0
        mask[a, b, 0] = 1.0

    scale = 1.0 / math.sqrt(n)
    factors = [
        torch.nn.Parameter(torch.randn(n, n, n) * scale)
        for _ in range(3)
    ]
    optimizer = torch.optim.SGD(
        factors,
        lr=0.5,
        momentum=0.5,
    )

    for _ in range(int(steps)):
        optimizer.zero_grad()
        prediction = hypercube_product(*factors)
        loss = torch.sum(((prediction - target) * mask) ** 2)

        if regularizer == "H":
            loss = loss + epsilon * hypercube_regularizer(*factors)
        elif regularizer == "L2":
            loss = loss + epsilon * sum(
                torch.sum(factor * factor) for factor in factors
            )
        elif regularizer != "none":
            raise ValueError(regularizer)

        loss.backward()
        optimizer.step()

    with torch.no_grad():
        classes = hypercube_product(*factors).argmax(dim=2).cpu().numpy()

    train_accuracy = float(
        np.mean(
            [
                int(classes[a, b]) == int(table[a, b])
                for a, b in train_pairs
            ]
        )
    )
    test_accuracy = float(
        np.mean(
            [
                int(classes[a, b]) == int(table[a, b])
                for a, b in test_pairs
            ]
        )
    )
    return train_accuracy, test_accuracy


def run():
    tables = small_boc_tables()
    records = []

    for task, table in tables.items():
        for regularizer in ("H", "L2", "none"):
            for seed in range(10):
                train_accuracy, test_accuracy = train(
                    table,
                    seed=seed,
                    regularizer=regularizer,
                )
                records.append(
                    {
                        "task": task,
                        "regularizer": regularizer,
                        "seed": seed,
                        "train_accuracy": train_accuracy,
                        "test_accuracy": test_accuracy,
                    }
                )

    summaries = []
    for task in tables:
        for regularizer in ("H", "L2", "none"):
            rows = [
                row
                for row in records
                if row["task"] == task
                and row["regularizer"] == regularizer
            ]
            tests = np.asarray(
                [row["test_accuracy"] for row in rows], dtype=float
            )
            trains = np.asarray(
                [row["train_accuracy"] for row in rows], dtype=float
            )
            summaries.append(
                {
                    "task": task,
                    "regularizer": regularizer,
                    "train_accuracy_mean": float(np.mean(trains)),
                    "test_accuracy_mean": float(np.mean(tests)),
                    "test_accuracy_min": float(np.min(tests)),
                    "perfect_test_runs": int(np.sum(tests == 1.0)),
                    "runs": len(rows),
                }
            )

    def row(task, regularizer):
        return next(
            x
            for x in summaries
            if x["task"] == task
            and x["regularizer"] == regularizer
        )

    comparison = {
        task: {
            "H_mean_test": row(task, "H")["test_accuracy_mean"],
            "L2_mean_test": row(task, "L2")["test_accuracy_mean"],
            "unregularized_mean_test": row(task, "none")[
                "test_accuracy_mean"
            ],
        }
        for task in tables
    }

    payload = {
        "experiment": "Clean-room HyperCube small-BOC reproduction",
        "date": "2026-09-25",
        "provenance": {
            "paper": (
                "Dongsung Huh, Discovering Group Structures via Unitary "
                "Representation Learning, ICLR 2025"
            ),
            "implementation_status": (
                "clean-room implementation from Appendix A; not official code"
            ),
            "protocol_difference": (
                "fixed epsilon=0.1 for 500 steps; the paper uses an adaptive "
                "epsilon scheduler after sufficient convergence"
            ),
            "train_fraction": 0.60,
            "seeds": [0, 9],
        },
        "comparison": comparison,
        "summaries": summaries,
        "records": records,
    }

    Path("results/external_hypercube_reproduction.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(comparison, indent=2))

    # Hostile sanity gates. We demand that the structural regularizer
    # generalizes perfectly on the two true-group tasks and materially beats
    # unregularized tensor completion on every task.
    assert row("C6_add", "H")["perfect_test_runs"] == 10
    assert row("S3_composition", "H")["perfect_test_runs"] == 10
    for task in tables:
        assert (
            row(task, "H")["test_accuracy_mean"]
            > row(task, "none")["test_accuracy_mean"] + 0.20
        )


if __name__ == "__main__":
    run()
