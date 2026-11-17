# P2 collision confirmed; predicted reversal falsified

## Prospective result

The frozen collision prediction passed at `c=11`, but the proposed reversal at
`c=12` failed:

| leaf cost | exact value | source optimal groups | predicted consequence |
| ---: | ---: | --- | --- |
| 11 | 37 | `[0,3,11,12]` | four-way collision confirmed |
| 12 | 37 | `[0]` | clean-middle reversal falsified |

At `c=11`, all nominated source child vectors passed exactly:

- group 0: `[22,22,33]`;
- group 3: `[26,22,22]`;
- group 11: `[26,22]`.

At `c=12`, the exact vectors are instead `[23,23,33]`, `[27,22,22]`, and
`[27,22]`.  The root action stays at 37 while the clean-middle action rises to
38 and the leaf actions to 39.  Group 0 is therefore uniquely optimal.

## Mechanism

The exploratory low-cost branch `4+3c` remains exact at diagnostic costs 9 and
10, with values 31 and 34.  It collides with the other optimal mechanisms at
37 when `c=11`.  Beyond that collision the presumed affine continuation is
wrong: downstream subproblems saturate, and the constant root branch wins.

The sentinel model therefore does **not** reverse the old handoff direction.
Instead it changes the approach to the same boundary:

- aliased P2 reaches the collision from a clean-middle-controlled plateau;
- sentinel P2 reaches it from a root/leaf three-way tie;
- both select root group 0 uniquely at `c=12`.

Across every enumerated positive integer, the sentinel advantage is positive
through `c=10` and closes at `c=11`.  This is a concrete planner consequence:
response refinement changes low-cost policies and values but the two encodings
reconverge at the high-cost policy boundary.

## Unseen-family transport

The all-coordinate `0<->2` image matched both exact endpoints and all search
counts.  Source optima `[0,3,11,12]` transport to `[0,1,4,5]` at `c=11`, and
source `[0]` transports to `[0]` at `c=12`.  Thus the covariance theorem again
survives even though the frozen numerical mechanism is partly falsified.

## Limits

The prospective claim is bounded to `c=11,12`, this P2 witness, its `0<->2`
image, explicit outside token, and fixed `(a,b)=(4,11)`.  Values at `c=9,10`
are post-falsification diagnostics.  No claim is made for real-valued costs,
larger costs, arbitrary states, or other obstruction families.

## Reproducibility

- Frozen protocol commit: `f73de0ee372bfabe50a52d1d2b19090f27c5020c`.
- Exact result SHA-256: `187995bee98160d1824ded037d4f7a2298dba39b0aa64035d83a578c738102af`.
- Independent audit SHA-256: `ba7cad15f81a69c8a11c8894ead0bc4980dc925b3df631303ebd9fe3085df787`.
- Targeted verifier/audit test: 1 passed.
- Full regression: 333 passed.
- Ruff: passed for the verifier, audit, and targeted test.
