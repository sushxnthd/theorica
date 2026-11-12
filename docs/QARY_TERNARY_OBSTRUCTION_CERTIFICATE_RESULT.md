# Machine-checkable lower bound for the minimal ternary obstruction

## Claim

At level costs `(1,3,1)`, every two-element subset of

```text
{(2,0,0), (2,1,0), (2,2,0)}
```

added to the binary cube `{0,1}^3` has exact middle-first minimax cost 18.
The earlier exact search established the value; this experiment supplies an
explicit adversarial lower-bound object for the missing direction.

For each ten-word family, the repository now contains a content-addressed
refutation DAG at budget 17. At every nonterminal node the DAG covers every
affordable informative planner query and gives one legal observation or
recognized-erasure child that remains refuted after charging the query cost.
Budget decreases on every edge, so the object is finite and acyclic.

## Mechanism exposed

For all three allowed middle-first root queries, the certified adversary's
initial response is the distinguished outside-subtree value `0`. This keeps
the two aligned root-`2`, leaf-`0` completions coupled to the binary family.
The same absorbing-zero mechanism survives through a maximum of 12 adversarial
steps and is exactly where the extra unit over the embedded binary cost enters.

The first two obstruction pairs have the same structural root certificate;
the pair using middle symbols `1` and `2` has a second root. This reduces the
three numerical obstructions to two content-addressed adversarial types.

## Exact evidence

| Added pair | DAG nodes | DAG edges | Maximum depth | Root SHA-256 |
|---|---:|---:|---:|---|
| `(2,0,0)`, `(2,1,0)` | 6,501 | 18,351 | 12 | `a1263ddb4af6f150d1b5dad9ca72633b9134ff801b650dfa79068bfc04dcfee4` |
| `(2,0,0)`, `(2,2,0)` | 6,501 | 18,351 | 12 | `a1263ddb4af6f150d1b5dad9ca72633b9134ff801b650dfa79068bfc04dcfee4` |
| `(2,1,0)`, `(2,2,0)` | 6,498 | 18,338 | 12 | `96fcab7a2c56055ed3b68affbbe2d1608ecfdd28938b5d95dde02fa3ede92dff` |

The shared store contains 9,932 unique nodes. Its canonical JSON SHA-256 is
`9b4e860666419ec5e4504073af95337518f00295a942e96877375a9ea5f427b6`.
The repository stores that canonical JSON with deterministic gzip compression;
the independent verifier decompresses it before checking the content hash.

All three families are independently feasible at budget 18. All six controls
obtained by deleting one of the two added words are feasible at budget 17,
confirming inclusion minimality.

## Independent verification and falsification

The independent verifier imports zero THEORICA modules and makes zero optimizer
calls. It reconstructs the prefix-query rows from the ten words and checks:

- all 9,932 content hashes;
- exact coverage of every admissible planner query;
- every adversarial response and fault-state transition;
- every residual budget and query multiplicity;
- all three root states and all reachable nodes.

It rejects 3/3 preregistered corruptions: a changed child reference, a changed
root budget, and a changed root state coordinate. Thus acceptance is not a
restatement of the generator's dynamic-programming result.

## Consequence

The lower bound is now portable: an external checker can validate infeasibility
at 17 without trusting the optimizer or rerunning search. The two root hashes
also give a concrete target for an analytic compression of the adversary.

## Limitations

This certificate theorem is restricted to the three ten-word families, costs
`(1,3,1)`, arity three, depth three, four copies, one substitution, one
recognized erasure, distinguished-zero prefix semantics, and a middle-first
initial action. A finite DAG explains and verifies the lower bound but is not
yet a closed-form global ternary cost cone or a symbolic adversary valid for
arbitrary candidate families.
