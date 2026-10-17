#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

from theorica.agents.robust_provenance import deterministic_tv_frontier, robust_provenance_frontier


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    counts={'prior_vectors':0,'frontier_cases':0,'deterministic_subset_checks':0,'randomized_lp_cases':0,'uniform_separations':0}
    failures=[]; witnesses=[]
    radii=(Fraction(0),Fraction(1,20),Fraction(1,10),Fraction(1,4))
    for n in range(3,8):
        for weights in product(range(1,4),repeat=n):
            counts['prior_vectors']+=1
            total=sum(weights)
            for q in range(n):
                k=q+1
                nominal=max(Fraction(sum(weights[i] for i in subset),total) for subset in combinations(range(n),k))
                counts['deterministic_subset_checks']+=sum(1 for _ in combinations(range(n),k))
                for delta in radii:
                    observed=deterministic_tv_frontier(weights,q,delta)
                    expected=Fraction(1) if k==n else max(Fraction(0),nominal-delta)
                    if observed!=expected: failures.append({'weights':weights,'q':q,'delta':str(delta)})
                    # LP check on a fixed asymmetric control per dimension;
                    # deterministic enumeration remains exhaustive.
                    if weights == (3,) + (1,) * (n - 1):
                        frontier=robust_provenance_frontier(weights,q,delta)
                        counts['randomized_lp_cases']+=1
                        if frontier.randomized_value+1e-8<float(observed): failures.append({'minimax_below_deterministic':weights,'q':q,'delta':str(delta)})
                    counts['frontier_cases']+=1
        uniform=(1,)*n
        for q in range(n-1):
            frontier=robust_provenance_frontier(uniform,q,Fraction(1,10))
            expected=(q+1)/n
            if abs(frontier.randomized_value-expected)>1e-8 or frontier.deterministic_plan_minimax:
                failures.append({'uniform':n,'q':q})
            else:
                counts['uniform_separations']+=1
                if len(witnesses)<8: witnesses.append({'n':n,'q':q,'deterministic':str(frontier.deterministic_value),'randomized':frontier.randomized_value})
    payload={'schema':'theorica.robust-provenance-query-frontier.v1','theorems':{
      'deterministic':'D*=1 for q=n-1; otherwise max(0,sum_top_(q+1)(p)-delta)',
      'randomized':'R*(p,delta,q)=min_{TV(pi,p)<=delta} sum_top_(q+1)(pi)',
      'separation':'for uniform p and delta>0, R*=(q+1)/n>D* when D* is positive'},
      'counts':counts,'failures':failures,'witnesses':witnesses,'status':'PASS' if not failures else 'FAIL'}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'))
    payload['canonical_sha256']=hashlib.sha256(raw.encode()).hexdigest()
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:payload[k] for k in ('status','counts','witnesses','canonical_sha256')},indent=2))
    if failures: raise SystemExit(1)

if __name__=='__main__': main()

