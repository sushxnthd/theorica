#!/usr/bin/env python3
"""Independent formula-and-transcript audit; imports no primary verifier."""
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path

def perm(n,hidden,direction):
    domain=[x for x in range(n) if x!=hidden]
    nxt={}
    for i,x in enumerate(domain):
        nxt[x]=domain[(i+direction)%len(domain)]
    nxt[hidden]=hidden
    return nxt

def grow(n,hidden,pair,p):
    reached=set(pair)
    for _ in range(n+1):
        old=set(reached)
        for x in old:
            for y in old:
                reached.add(p[y] if x==hidden else y)
        if reached==old: return reached
    raise AssertionError("closure did not stabilize")

def canon(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-n",type=int,default=64)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); checked=0; failures=[]
    for n in range(3,a.max_n+1):
        observed=[]
        for hidden in range(n):
            p=perm(n,hidden,1)
            # A cycle has no off-diagonal fixed points, so a row probe is an
            # equality test for the hidden label.
            order=list(reversed(range(n))); used=0; answer=None
            for row in order[:-1]:
                used+=1; col=(row-1)%n
                value=p[col] if row==hidden else col
                if value!=col: answer=row; break
            if answer is None: answer=order[-1]
            other=0 if answer!=0 else 1
            if answer!=hidden or len(grow(n,hidden,{answer,other},p))!=n:
                failures.append([n,hidden,answer,used])
            observed.append(used); checked+=1
        target=Fraction(n+1,2)-Fraction(1,n)
        if sum(map(Fraction,observed))/n!=target or max(observed)!=n-1:
            failures.append(["aggregate",n,observed])
        # Information lower bound: q off-diagonal identity answers mention at
        # most q rows; for q<n-1 at least two hidden labels remain compatible.
        for q in range(n-1):
            remaining=n-q
            if remaining<2: failures.append(["ambiguity",n,q,remaining])
            checked+=1
    payload={"schema":"theorica.partial-cell-hidden-generator.audit.v1",
             "max_n":a.max_n,"checks":checked,"failures":failures,
             "status":"PASS" if not failures else "FAIL"}
    payload["canonical_sha256"]=canon(payload)
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload,indent=2))
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
