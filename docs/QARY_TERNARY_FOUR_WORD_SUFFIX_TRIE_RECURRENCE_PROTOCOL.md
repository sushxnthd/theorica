# Frozen protocol: ternary four-word suffix-trie recurrence

## Question

Does the suffix-trie quotient remain complete when the arbitrary added family grows from three to four words, and can the quotient be generated without enumerating the family universe?

The experiment is fixed at alphabet size `q=3`, total word depth `d=4`, the existing explicit outside sentinel, and an arbitrary family of `k=4` added words sharing the sentinel prefix.  Thus the raw universe has

\[
\binom{3^3}{4}=17{,}550
\]

families.  No result from the transport run may alter the predictions below.

## Theorem prediction

Let \(\mathcal T^{(q)}_{h,k}\) be the unlabelled rooted trie shapes of height \(h\), with every leaf at height zero, \(k\) leaves, and at most \(q\) children at every internal node.  Set

\[
\mathcal T^{(q)}_{0,1}=\{()\},\qquad
\mathcal T^{(q)}_{0,k}=\varnothing\quad(k\ne1).
\]

For \(h>0\), \(\mathcal T^{(q)}_{h,k}\) is exactly the set of multisets of between one and \(\min(q,k)\) members drawn from \(\bigcup_{j\le k}\mathcal T^{(q)}_{h-1,j}\), whose leaf counts sum to \(k\).  Two added families induce isomorphic complete query systems if and only if their suffix tries have the same member of \(\mathcal T^{(q)}_{d-1,k}\).

If a shape \(T\) has \(m\) children, with multiplicities \(a_1,\ldots,a_r\) among its distinct child shapes, its labelled embedding count obeys

\[
E_q(())=1,\qquad
E_q(T)=\frac{(q)_m}{\prod_i a_i!}\prod_{C\in T}E_q(C).
\]

Therefore the eleven predicted class sizes, in canonical `repr` order, are frozen as

```
81, 2916, 243, 243, 1458, 2187, 54, 162, 2187, 6561, 1458
```

Their sum must be `17550`.  The resulting representative-solve reduction is exactly `17550 -> 11`, a factor of `1595.4545...`; the claim is the integer reduction to eleven solves, not an integral symmetry-orbit factor.

The lexicographically last family in each canonical class is frozen as:

```
211+212+221+222
122+212+221+222
202+212+221+222
121+122+221+222
121+122+212+222
022+122+221+222
212+220+221+222
122+220+221+222
112+122+212+222
022+122+212+222
122+202+212+222
```

As an unseen-alphabet corollary, the same recurrence at `q=4`, `h=3`, `k=4` must produce fourteen shapes whose embedding counts sum to

\[
\binom{4^3}{4}=635{,}376.
\]

This identity is checked symbolically; the `q=4` family universe is not enumerated.

## Decisive experiment

1. Generate the eleven predicted shapes and recursive embedding counts before classifying any family.
2. Enumerate all 17,550 ternary four-suffix families exactly once and require exact agreement with the frozen class sizes and holdouts.
3. Solve one representative per class, construct an edge-checked completion/query/cell transport to every family, and commit all family digests to deterministic global and per-class SHA-256 streams.
4. Execute each frozen holdout as a full transport, not merely a class lookup.
5. Falsify collapse by checking all 55 cross-class representative pairs for graph nonisomorphism.
6. Reconstruct all classifications, transports, holdouts, stream commitments, and recurrence counts with an independent zero-production-import audit.
7. Rerun both programs byte deterministically and run the complete test suite.

Any mismatch, transport failure, cross-class isomorphism, nondeterminism, or audit disagreement falsifies the theorem claim and is preserved as a negative result.

## Bounded consequence

Passing establishes an executable exact classifier and eleven-representative policy-transfer procedure for this fixed ternary depth-four, four-word explicit-sentinel family.  It does not establish the recurrence-to-query-system theorem for arbitrary depth, alphabet, family size, or other environment models.
