# Adversarially Robust Translation Reconstruction

## Candidate contribution

This note extends THEORICA's translation-action reconstruction with an exact adversarial corruption guarantee.

Let `F:S×S→S` be an unknown finite operation and `L_x(y)=F(x,y)` its left translations. Suppose a representation-discovery stage has identified `G ≤ Sym(S)` containing the relevant `L_x`.

For `R⊆S`, define the restricted signature
```
σ_R(g) = (g(y))_{y∈R}
```
and
```
d_R(G) = min_{g≠h} d_H(σ_R(g),σ_R(h)).
```

## Theorem 1: sharp correction threshold

A translation is uniquely recoverable from its `R`-signature under any at most `e` adversarial corruptions **iff**
```
d_R(G) ≥ 2e+1.
```

Sufficiency follows from the Hamming triangle inequality. Sharpness follows by taking a minimum-distance pair and constructing a hybrid received word within radius `e` of both whenever `d_R(G)≤2e`.

Define the robust base number
```
b_e(G) = min {|R| : d_R(G) ≥ 2e+1}.
```
Then `b_0(G)` is exactly the ordinary base size.

## Theorem 2: robust table reconstruction

If `r` exact seed translations generate `G`, each remaining translation lies in `G`, and each remaining queried row suffers at most `e` adversarial corruptions, any `R` with `d_R(G)≥2e+1` gives exact full-table recovery with
```
Q = nr + (n-r)|R|.
```

If seed rows may also suffer at most `e` corruptions, repeating each seed entry `2e+1` times and majority decoding gives the sufficient end-to-end bound
```
Q_robust = nr(2e+1) + (n-r)|R|.
```

## Theorem 3: exact law for sharply k-transitive actions

Let `G` act sharply `k`-transitively on `S`, where `|S|=n` and `k<n`. For any queried coordinate set `R` of size `m≥k-1`,
```
d_R(G) = m-k+1.
```

Hence
```
b_e(G) = k+2e
```
whenever `k+2e≤n`; if `k+2e>n`, no one-shot coordinate signature can correct `e` adversarial errors.

### Proof

Two distinct elements of a sharply `k`-transitive group can agree on at most `k-1` points, so they differ on at least `m-k+1` points of `R`.

Conversely, fix any `k-1` points of `R`. Their pointwise stabilizer has size `n-k+1>1`, so choose a nonidentity element in it. It cannot fix any additional point, because then it would fix `k` distinct points and sharp `k`-transitivity would force it to be the identity. Thus it moves every other point of `R`, attaining distance exactly `m-k+1`.

Combining with Theorem 1 gives `m-k+1≥2e+1`, or `m≥k+2e`. The bound is therefore exact.

### Query-optimal corollary

If THEORICA's discovered translation group is sharply `k`-transitive, the remaining rows can be reconstructed with
```
Q = nr + (n-r)(k+2e)
```
queries whenever `k+2e≤n`.

No fixed one-shot coordinate signature using fewer than `k+2e` values per remaining row can guarantee correction against `e` adversarial errors.

Special cases:
- regular actions: `b_e=2e+1`;
- sharply 2-transitive affine actions: `b_e=2e+2`.

## Certify or abstain

Accept a received signature only when exactly one `g∈G` lies within radius `e`. Otherwise abstain/acquire more evidence. Under the theorem assumptions, every accepted decode is exact.

## Novelty boundary

Permutation groups as error-correcting codes and the minimum-distance behavior of sharply transitive groups are prior art. Query-efficient black-box operation-table reconstruction is also prior art. The priority claim to investigate is the combined formulation for **active unknown-operation reconstruction through a discovered translation group**, including the sharp corruption threshold, robust-base query parameter, query-optimal sharply-transitive corollary, and certify-or-abstain reconstruction guarantee.

A dedicated hostile literature search found the two main ingredients separately but no located work combining them into exact adversarially robust oracle reconstruction. This remains a priority-search result, not a proof that no obscure predecessor exists.

Do not describe the underlying coding lemma or sharply-transitive minimum-distance fact as new.
