# Frozen protocol: non-isomorphic ternary scalar boundary

## Question

The first two minimal ternary obstructions are policy-equivalent under a
level-coloured partition-hypergraph isomorphism.  The third obstruction,
`P2={(2,1,0),(2,2,0)}`, is separated from them by stable colour
multiplicities.  This experiment opens exactly one remaining prospective case,
`P2` at level costs `(2,9,3)`, to determine what non-isomorphism changes.

## Frozen prediction and three-way classification

The prediction is that `P2` retains scalar optimum `51` but has a different
exact middle-root profile from the isomorphic `P0/P1` orbit.  The result will
be classified without post-hoc relabelling:

1. **scalar boundary:** the unrestricted exact optimum differs from `51`;
2. **root-policy boundary:** the optimum is `51`, but the sorted vector of
   exact costs conditioned on each of the three logical middle queries differs;
3. **unresolved finer boundary:** both scalar and conditioned-cost profiles
   agree, requiring a stronger policy invariant in the next experiment.

The deterministic canonical policy exposure antichain for each conditioned
root is recorded as secondary evidence, but equality of one canonical
antichain is not claimed to enumerate all optimal policies.

## Exact procedure

- Synthesize unrestricted exact policies for `P0` and `P2`.
- For each logical middle query, restrict only the first physical query to one
  of its four copies; later queries remain unrestricted.  Compute the exact
  conditioned optimum and canonical exposure antichain.
- Compare sorted conditioned-cost profiles, so arbitrary names of middle
  queries cannot manufacture a difference.
- A zero-THEORICA-import dynamic program independently proves feasibility at
  each reported optimum and infeasibility one unit below, unrestricted and for
  all six conditioned cases.
- Re-run artifacts byte-for-byte and execute the complete regression suite.

No other reserved cost case may be opened.  A mismatch between production and
independent boundaries falsifies the result and is preserved.

