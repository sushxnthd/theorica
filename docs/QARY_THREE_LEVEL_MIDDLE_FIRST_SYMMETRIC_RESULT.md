# Exact symmetric-slice middle-first theorem

## Theorem

Consider the binary depth-three decision problem with four physical copies of
each prefix query, one adversarial substitution, one recognized erasure, and
the first query constrained to the middle level.  If root and middle queries
have the same positive integer cost `x` and leaf queries cost `y`, then the
exact worst-case cost is

```text
S(x,y) = max(7x+y, 6x+3y, 5x+4y).
```

Thus `(7,1)` is active for `x >= 2y`, `(6,3)` for `y <= x <= 2y`, and
`(5,4)` for `x <= y`.  Adjacent faces tie exactly at `x=2y` and `x=y`.

## Lower bound: the convex-hull mechanism becomes scalar

Identify root and middle query exposure by projecting `(r,m,l)` to
`(r+m,l)`.  An exact adversary recursion over 178,964 finite states returns
the complete maximal projected componentwise antichain

```text
(5,4), (6,3), (7,1).
```

Every middle-first policy therefore has a transcript at least as expensive
as each corresponding affine face.  In particular, the formerly missing
three-dimensional face `(3,4,1)` projects to `(7,1)`.  Its observed tradeoff
between `(2,5,1)` and `(4,3,1)` is no longer a numerical coincidence: both
vectors project to the same unavoidable exposure.

## Upper bound: three cone certificates

The exact solver synthesized policies at the two phase boundaries.  Exhaustive
terminal-tree enumeration verified each policy on both extreme rays of its
cost cone:

| Cone | Active face | Extreme rays | Certified policy costs |
|---|---:|---:|---:|
| `x >= 2y` | `(7,1)` | `(1,0)`, `(2,1)` | `7`, `15` |
| `y <= x <= 2y` | `(6,3)` | `(1,1)`, `(2,1)` | `9`, `15` |
| `x <= y` | `(5,4)` | `(0,1)`, `(1,1)` | `4`, `9` |

Linearity on a polyhedral cone then bounds every terminal transcript by the
active affine face throughout that cone.  These upper bounds match the three
adversarial lower bounds, proving exactness for every positive integer pair
`(x,y)`, not merely the opened test points.

## Prospective and independent checks

All seven frozen unseen pairs matched exactly:

```text
(79,1), (81,40), (41,40), (40,41), (1,79), (2,1), (1,1).
```

They include every open cone and both phase boundaries.  A separate
standard-library-only implementation imported zero THEORICA modules,
reconstructed the same three lower faces, independently solved all seven
conditioned games, and rechecked every extreme-ray inequality.

## Executable consequence

`certify_binary_middle_first_symmetric(x, y)` evaluates the proved law,
reports all active faces (including boundary ties), returns the projected
adversary vectors, and labels its scope `binary_middle_first_symmetric`.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_three_level_middle_first_symmetric.py
python scripts/audit_qary_three_level_middle_first_symmetric.py
pytest -q
```

Machine-readable primary and independent evidence is stored under
`results/qary_three_level_middle_first_symmetric/`.

## Limitations

This theorem requires equal root and middle costs and a middle-level first
query.  It does not prove the full three-dimensional six-face conjecture,
unrestricted root dominance, q-ary exactness, or the unresolved leaf-first
law.  The useful new mechanism is an exact quotient of exposure space; a full
proof must now cover unequal root and middle costs with genuinely set-valued
certificates rather than silently extending this projection.
