#!/usr/bin/env python3
"""Exact verifier for partial-cell localization in hidden-generator racks."""
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path

def cycle(n,z,reverse=False):
    xs=[i for i in range(n) if i!=z]
    if reverse: xs=list(reversed(xs))
    p=list(range(n))
    for a,b in zip(xs,xs[1:]+xs[:1]): p[a]=b
    return tuple(p)

def op(n,z,p,x,y):
    return p[y] if x==z else y

def closure(n,z,p,seeds):
    """Exact operation closure specialized to the one-active-row family."""
    seen=set(seeds)
    if z not in seen:
        return seen
    # Only left multiplication by z is nonidentity, so operation closure is
    # exactly the union of p-orbits of the current elements.
    frontier=list(seen)
    while frontier:
        value=p[frontier.pop()]
        if value not in seen:
            seen.add(value)
            frontier.append(value)
    return seen

def structural_rack_check(n,z,p):
    if p[z]!=z or set(p)!=set(range(n)): return False
    outside=[x for x in range(n) if x!=z]
    if any(p[x]==x for x in outside): return False
    orbit=[]; x=outside[0]
    while x not in orbit:
        orbit.append(x); x=p[x]
    if set(orbit)!=set(outside) or x!=outside[0]: return False
    # Translation assignment is constant on both p-orbits; conjugating id by p
    # is id and conjugating p by itself is p.
    return True

def explicit_rack_check(n,z,p):
    return all(op(n,z,p,x,op(n,z,p,y,w)) ==
               op(n,z,p,op(n,z,p,x,y),op(n,z,p,x,w))
               for x in range(n) for y in range(n) for w in range(n))

def canonical(payload):
    raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-n",type=int,default=64)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    counts={"family_members":0,"explicit_rack_checks":0,"seed_checks":0,
            "scan_cases":0,"lower_bound_witnesses":0,"expectation_checks":0}
    failures=[]; per_n=[]
    for n in range(3,a.max_n+1):
        costs=[]
        for reverse in (False,True):
            for z in range(n):
                p=cycle(n,z,reverse); counts["family_members"]+=1
                if not structural_rack_check(n,z,p):
                    failures.append(["rack_structure",n,z,reverse])
                if n<=12:
                    counts["explicit_rack_checks"]+=1
                    if not explicit_rack_check(n,z,p):
                        failures.append(["rack_explicit",n,z,reverse])
                singleton=max(len(closure(n,z,p,{x})) for x in range(n))
                if singleton>=n:
                    failures.append(["rank_one",n,z,reverse])
                for other in range(n):
                    if other==z: continue
                    counts["seed_checks"]+=1
                    if len(closure(n,z,p,{z,other}))!=n:
                        failures.append(["rank_two",n,z,reverse,other])
                order=list(range(n)); q=0; found=None
                for row in order[:-1]:
                    col=(row+1)%n
                    q+=1
                    if op(n,z,p,row,col)!=col:
                        found=row; break
                if found is None: found=order[-1]
                counts["scan_cases"]+=1; costs.append(q)
                other=(found+1)%n
                if found!=z or len(closure(n,z,p,{found,other}))!=n:
                    failures.append(["scan",n,z,reverse,found,q])
        # Two orientations duplicate costs; use one orientation for expectation.
        one=costs[:n]
        expected=sum(Fraction(x,1) for x in one)/n
        formula=Fraction(n+1,2)-Fraction(1,n)
        counts["expectation_checks"]+=1
        if expected!=formula:
            failures.append(["expectation",n,str(expected),str(formula)])
        if max(one)!=n-1:
            failures.append(["worst_case",n,max(one),n-1])
        # Every q<n-1 all-identity transcript leaves >=2 unprobed rows.
        for q in range(n-1):
            queried=list(range(q)); candidates=list(range(q,n))
            z1,z2=candidates[:2]
            for z in (z1,z2):
                p=cycle(n,z,False)
                if any(op(n,z,p,row,(row+1)%n)!=(row+1)%n for row in queried):
                    failures.append(["witness",n,q,z])
            counts["lower_bound_witnesses"]+=1
        per_n.append({"n":n,"worst_case":max(one),
                      "expected_numerator":expected.numerator,
                      "expected_denominator":expected.denominator})
    payload={"schema":"theorica.partial-cell-hidden-generator.v1",
             "protocol_commit":"1bce1288ad1b4d59c96d3d363c12b1f42dd91249",
             "max_n":a.max_n,"counts":counts,"failures":failures,
             "status":"PASS" if not failures else "FAIL","per_n":per_n}
    payload["canonical_sha256"]=canonical(payload)
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:payload[k] for k in ("status","counts","canonical_sha256")},indent=2))
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
