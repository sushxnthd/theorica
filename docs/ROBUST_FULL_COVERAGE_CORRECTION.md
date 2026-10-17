# Robust provenance frontier: full-coverage correction

The frozen constructive-synthesis protocol found a boundary counterexample to
the deterministic formula reported at parent commit
`6c0fc90b22af5ead1247ce92382c881b5f3120e6`.

For `k=q+1<n`, the established argument is correct:

`D*(p,delta,q)=max(0,sum_top_k(p)-delta)`.

For `k=n`, however, the only covered-label set is the full carrier. Every
admissible prior assigns it probability one, so

`D*(p,delta,n-1)=1`.

The old formula incorrectly returned `1-delta`. For example, with
`p=(1/2,1/3,1/6)`, `delta=1/4`, and `q=2`, it returned `3/4` although every
deterministic full-coverage plan succeeds with probability one.

This failure is preserved in `results/robust_full_coverage_failure.json`. The
runtime theorem and exhaustive verifier are corrected piecewise. All earlier
strict deterministic/randomized separations use `q<n-1` and remain candidates
for confirmation; no full-coverage separation may be claimed.
