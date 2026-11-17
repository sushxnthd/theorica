# Canonical policy-signature boundary result

## Result

The relabeling-invariant canonical policy-tree signature separates the
non-isomorphic `P0` and `P2` obstruction systems even though their scalar
optima, sorted middle-root profiles, and exposure antichains agree. All four
preregistered comparisons are unequal.

| Exact policy | P0 cost / nodes | P2 cost / nodes | Signature equal? |
|---|---:|---:|---:|
| Unrestricted | 51 / 1,103 | 51 / 1,133 | No |
| Forced middle root 1 | 51 / 1,103 | 51 / 1,133 | No |
| Forced middle root 2 | 51 / 1,103 | 51 / 1,133 | No |
| Forced middle root 3 | 52 / 1,254 | 52 / 1,298 | No |

All eight trees have depth 11. For the three cost-51 comparisons, the first
canonical difference occurs after the erasure child and three ordinary-child
steps: the `P0` state has two ordinary response branches and the corresponding
`P2` state has three. For the cost-52 root, the first difference is immediate:
the sorted truthful cell-size vector has length two for `P0` and three for
`P2`.

This is an executable boundary missed by scalar cost and terminal exposure
geometry: the systems require different internal response branching under the
repository's exact deterministic optimum. It does not claim that every optimal
policy differs, nor that this signature is a complete reachable-state
bisimulation invariant.

## Holdout discipline

No new reserved family or cost case was opened. The experiment used only the
already-opened `P0/P2` case at costs `(2,9,3)`, so all 18 remaining reserved
cases stay sealed.

## Verification

- Complete canonical policy encodings are stored in deterministic gzip form.
- Eight policy hashes, replayed costs, node counts, and depths were checked by
  a zero-production-import auditor.
- Four first-difference witnesses were independently reconstructed.
- The compressed evidence digest is independently checked.
- The verifier and auditor are deterministic and are covered by the full
  repository validation reported with the evidence commit.

## Bounded claim

The result proves separation for the deterministic exact policies selected by
the frozen solver tie-breaking rule. A complete theorem about the set of all
optimal policies requires the next experiment to construct a set-valued
reachable-state bisimulation quotient rather than a single selected tree.

