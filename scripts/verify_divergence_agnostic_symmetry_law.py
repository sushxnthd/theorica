#!/usr/bin/env python3
"""Exact verifier for the divergence-agnostic uniform-prior minimax law."""
import argparse, hashlib, json, math
from fractions import Fraction
from itertools import combinations, product

from theorica.agents.robust_provenance import (
    divergence_agnostic_symmetry_value,
    synthesize_uniform_ambiguity_plan,
    unrank_uniform_k_subset,
)


def compositions(total, n, prefix=()):
    if n == 1:
        yield prefix + (total,)
        return
    for x in range(total + 1):
        yield from compositions(total - x, n - 1, prefix + (x,))


def divergences(p):
    n=len(p); u=1.0/n; pf=[float(x) for x in p]
    tv=.5*sum(abs(x-u) for x in pf)
    fkl=sum(x*math.log(x/u) for x in pf if x>0)
    rkl=sum(u*math.log(u/x) for x in pf)
    chi=sum((x-u)**2/u for x in pf)
    h2=sum((math.sqrt(x)-math.sqrt(u))**2 for x in pf)
    m=[.5*(x+u) for x in pf]
    js=.5*sum(x*math.log(x/y) for x,y in zip(pf,m) if x>0)+.5*sum(u*math.log(u/y) for y in m)
    return {"tv":tv,"forward_kl":fkl,"reverse_kl":rkl,"chi_square":chi,"hellinger_squared":h2,"jensen_shannon":js}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    identity_checks=subset_checks=witness_checks=prior_checks=0
    digest=hashlib.sha256()
    divergence_max={k:0.0 for k in ("tv","forward_kl","reverse_kl","chi_square","hellinger_squared","jensen_shannon")}
    for n in range(2,9):
        for k in range(1,n+1):
            q=k-1
            value=divergence_agnostic_symmetry_value(n,q,uniform_prior_in_set=True)
            assert value==Fraction(k,n); identity_checks+=1
            plan=synthesize_uniform_ambiguity_plan(n,q,ambiguity_kind="uniform-containing",uniform_prior_in_set=True)
            assert plan.minimax_value==value and plan.covered_labels==k
            expected=list(combinations(range(n),k))
            got=[unrank_uniform_k_subset(n,k,r) for r in range(math.comb(n,k))]
            assert got==expected; subset_checks+=len(got)
            digest.update(repr((n,k,got)).encode())
            for total in range(1,10):
                for weights in compositions(total,n):
                    p=tuple(Fraction(x,total) for x in weights)
                    payoff=sum(p[i]*Fraction(k,n) for i in range(n))
                    assert payoff==value; prior_checks+=1
            if k<n:
                eps=Fraction(1,4*n)
                for S in expected:
                    s=set(S)
                    p=tuple(Fraction(1,n)-eps/k if i in s else Fraction(1,n)+eps/(n-k) for i in range(n))
                    assert sum(p)==1 and min(p)>0
                    assert sum(p[i] for i in S)==Fraction(k,n)-eps
                    ds=divergences(p)
                    assert all(math.isfinite(v) and v>0 for v in ds.values())
                    for key,val in ds.items(): divergence_max[key]=max(divergence_max[key],val)
                    witness_checks+=1
    result={"status":"pass","theorem":"uniform-in-ambiguity minimax value k/n","identity_checks":identity_checks,
            "subset_checks":subset_checks,"rational_prior_checks":prior_checks,"strict_witness_checks":witness_checks,
            "divergence_families":sorted(divergence_max),"representative_max_divergence":divergence_max,
            "enumeration_digest":digest.hexdigest(),
            "smallest_claim":"If the certified ambiguity set contains the uniform prior, uniform randomization over k-subsets is minimax with exact value k/n; a deterministic plan is strictly dominated exactly when its certified worst-case mass is below k/n."}
    with open(args.output,"w",encoding="utf-8") as f: json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__": main()
