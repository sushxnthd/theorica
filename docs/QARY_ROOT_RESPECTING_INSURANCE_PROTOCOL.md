# Frozen protocol: arbitrary-depth root-respecting insurance law

Status: frozen before implementation and before prospective holdouts.
Parent commit: `1a29950f1d809b58d51c57d9b0773d0792834e46`.

## Candidate theorem

Fix `q >= 2` and depth `d >= 1`. Index `q^d` pairwise-incompatible exact
decisions by q-ary words. Expose four physical copies of every prefix query,
with positive integer level costs `c = (c_1,...,c_d)`. Allow one adversarial
substitution and one recognized erasure globally.

Restrict attention to **root-respecting policies**: at each recursive subtree,
the policy resolves the current prefix symbol using copies of that prefix query
before querying a strict descendant, then applies the same rule below.

Let `H_d`, `G_d`, and `F_d` be the exact worst-case costs with respectively no
faults, one substitution only, and one substitution plus one erasure remaining.
The candidate max-plus recurrence is

```text
H_1(c_1) = c_1
G_1(c_1) = 3 c_1
F_1(c_1) = 4 c_1

H_d(c) = c_1 + H_{d-1}(c_2,...,c_d)
G_d(c) = max(
    2 c_1 + G_{d-1}(c_2,...,c_d),
    3 c_1 + H_{d-1}(c_2,...,c_d),
)
F_d(c) = max(
    2 c_1 + F_{d-1}(c_2,...,c_d),
    3 c_1 + G_{d-1}(c_2,...,c_d),
    4 c_1 + H_{d-1}(c_2,...,c_d),
).
```

Equivalently, `F_d` is the maximum dot product against exactly `d(d+1)/2`
adversarial path-count vectors of two forms:

```text
(2^r, 4, 1^(d-r-1))
(2^r, 3, 2^s, 3, 1^(d-r-s-2))
```

for `0 <= r <= d-1` in the first family and `r,s >= 0`,
`r+s <= d-2` in the second. Here exponent notation means repetition.

The prediction is independent of `q`. The vectors have a direct fault-budget
interpretation: `2` means both faults remain hidden, `3` marks exposure of one
fault, `4` marks joint exposure at one level, and `1` means both budgets are
already exhausted.

## Opened calibration

- At depth two, the three recurrence faces are exactly the already proved
  unrestricted law `(2,4)`, `(3,3)`, `(4,1)`.
- At depth three, the recurrence generates six of the seven already proved
  unrestricted faces. The exceptional unrestricted face `(0,4,2)` is an
  ancestor-bypass policy and therefore lies outside the root-respecting class.
- Full exact depth-four binary enumeration completed for uniform costs with
  cost `10`, and for leaf-dominant costs `(1,1,1,20)` with cost `86` and active
  path `(2,2,2,4)`; both match the recurrence.
- Full exact depth-four binary enumeration for `(20,1,1,1)`, `(1,20,1,1)`, and
  `(1,1,20,1)` exceeded a 240-second cap. These negative computational results
  remain unresolved and are not counted as evidence.

## Frozen prospective holdouts

The following root-respecting cases are frozen without opening their values:

- `(q,d,c) = (2,4,(3,1,4,2))`;
- `(3,4,(2,5,1,3))`;
- `(5,5,(1,3,2,7,1))`;
- `(2,6,(6,1,2,1,3,2))`;
- `(3,8,(1,2,3,4,5,6,7,8))`.

Every holdout must match both the recurrence and the explicit face maximum.
The face counts must be `10, 10, 15, 21, 36` respectively.

## Proof and executable obligations

Success requires:

1. an executable certificate emitting all faces, the active faces, and the
   recurrence value;
2. an independent standard-library implementation generating the two closed
   face families without importing THEORICA;
3. exact agreement on all prospective holdouts and all positive integer cost
   vectors through depth six with costs in `{1,2,3}`;
4. conservative abstention when any level has fewer than four available copies;
5. full regression, lint, deterministic rerun, and hosted workflow evidence.

Any mismatch falsifies the candidate and must be preserved.

## Bounded claim

This theorem is about the complete root-respecting policy class, not all
adaptive prefix policies. Ancestor bypass already improves the unrestricted
depth-three optimum for some costs, and unrestricted depth four remains open.
The result does not claim general weighted liar-game capacity or extend beyond
one substitution, one recognized erasure, positive integer costs, and finite
exact decision families.
