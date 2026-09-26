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

### Sharp correction theorem

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

### Reconstruction bound

If `r` exact seed translations generate `G`, each remaining translation lies in `G`, and each remaining queried row suffers at most `e` adversarial corruptions, any `R` with `d_R(G)≥2e+1` gives exact full-table recovery with
```
Q = nr + (n-r)|R|.
```

If seed rows may also suffer at most `e` corruptions, repeating each seed entry `2e+1` times and majority decoding yields the sufficient end-to-end bound
```
Q_robust = nr(2e+1) + (n-r)|R|.
```

### Certify or abstain

Accept a received signature only when exactly one `g∈G` lies within radius `e`. Otherwise abstain/acquire more evidence. Under the assumptions above, every accepted decode is exact.

## Novelty boundary

Permutation groups as error-correcting codes are prior art (Bailey, 2006/2009). Query-efficient black-box operation-table reconstruction is also prior art (Zumbrägel, Maze & Rosenthal, 2008). The priority claim to investigate is the combined formulation for **active unknown-operation reconstruction through a discovered translation group**, including the sharp corruption threshold, robust-base query parameter, and certify-or-abstain reconstruction guarantee.

Do not describe the underlying coding lemma as new.
