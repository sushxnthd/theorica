# Frozen protocol: integer-ratio middle-first theorem

**Frozen before exact evaluation.**

## Candidate theorem

For every integer k >= 2 and positive integer costs x,y, predict the following exact binary middle-first laws.

Root-heavy costs (kx,x,y):

R_k(x,y) = max((4k+2)x+y, (3k+3)x+3y, (2k+3)x+4y).

Middle-heavy costs (x,kx,y):

M_k(x,y) = max((5k+1)x+y, (4k+2)x+3y, (3k+2)x+4y).

Both laws predict phase boundaries y=(k-1)x/2 and y=kx.

## Exact lower-bound criterion

Project transcript exposure (r,m,l) to (kr+m,l) for the root-heavy family and (r+km,l) for the middle-heavy family. The complete maximal adversary antichains must equal the three predicted coefficient pairs for every k >= 2. The proof must establish this parametrically, not by claiming a finite sweep as universal.

## Exact upper-bound criterion

Synthesize boundary-optimal policies that satisfy both extreme rays of each closed cone. The cone rays are (1,0) and (2,k-1), then (2,k-1) and (1,k), then (0,1) and (1,k). The proof must expose transcript vectors and reduce every ray inequality to a nonnegative affine function of k for all k >= 2. Scalar-optimal canonical tie-breaking is not sufficient.

## Prospective holdouts

Open only after this freeze: k in {3,4,7,11}; both root-heavy and middle-heavy orientations; and (x,y) in {(79,1),(2,k-1),(2,2k-1),(1,k),(1,79k)}. This gives 40 exact prospective cases including both phase boundaries and extreme regimes.

## Independent verification

A zero-THEORICA-import implementation must independently recompute the projected antichains for all four frozen k values, solve all 40 holdouts, and replay every symbolic cone inequality. Evidence must reproduce byte-for-byte, and missing prerequisites must abstain.

## Kill criteria and scope

Any antichain mismatch, holdout mismatch, negative symbolic inequality, or independent disagreement falsifies the stated family. Passing proves only the binary, four-copy, one-substitution, one-erasure, middle-first conditioned family for integer k >= 2. It does not prove arbitrary rational ratios, unrestricted first actions, higher arity, or leaf-first exactness.
