#!/usr/bin/env python3
"""Independent standard-library audit; does not import THEORICA production code."""
import argparse, hashlib, json, math
from fractions import Fraction
from itertools import combinations


def unrank(n,k,r):
    out=[]; start=0
    for remaining in range(k,0,-1):
        for x in range(start,n):
            count=math.comb(n-x-1,remaining-1)
            if r<count:
                out.append(x); start=x+1; break
            r-=count
    return tuple(out)


def comps(total,n,prefix=()):
    if n==1:
        yield prefix+(total,); return
    for x in range(total+1): yield from comps(total-x,n-1,prefix+(x,))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--primary",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    with open(a.primary,encoding="utf-8") as f: primary=json.load(f)
    ids=subs=priors=witnesses=0; digest=hashlib.sha256()
    for n in range(2,9):
        for k in range(1,n+1):
            value=Fraction(k,n); ids+=1
            expected=list(combinations(range(n),k))
            got=[unrank(n,k,r) for r in range(math.comb(n,k))]
            assert got==expected; subs+=len(got); digest.update(repr((n,k,got)).encode())
            inclusion=[Fraction(math.comb(n-1,k-1),math.comb(n,k)) for _ in range(n)]
            assert inclusion==[value]*n
            for total in range(1,10):
                for weights in comps(total,n):
                    p=[Fraction(x,total) for x in weights]
                    assert sum(x*y for x,y in zip(p,inclusion))==value; priors+=1
            if k<n:
                eps=Fraction(1,4*n)
                for S in expected:
                    mass=sum((Fraction(1,n)-eps/k) for _ in S)
                    assert mass==value-eps; witnesses+=1
    expected={"identity_checks":ids,"subset_checks":subs,"rational_prior_checks":priors,
              "strict_witness_checks":witnesses,"enumeration_digest":digest.hexdigest()}
    for key,val in expected.items(): assert primary[key]==val,(key,primary[key],val)
    result={"status":"pass","independent":True,**expected}
    with open(a.output,"w",encoding="utf-8") as f: json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__": main()
