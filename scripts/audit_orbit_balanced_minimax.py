#!/usr/bin/env python3
"""Independent standard-library checker; does not import THEORICA production code."""
import argparse, hashlib, json
from fractions import Fraction
from itertools import combinations


def cyclic(n):
    return tuple(tuple((i+s)%n for i in range(n)) for s in range(n))


def dihedral(n):
    return tuple(sorted({tuple((s+i)%n for i in range(n)) for s in range(n)} |
                        {tuple((s-i)%n for i in range(n)) for s in range(n)}))


def product_group(a,b):
    return tuple(tuple(((i+s)%a if i<a else a+(i-a+t)%b) for i in range(a+b))
                 for s in range(a) for t in range(b))


def point_orbits(n,group):
    left=set(range(n)); out=[]
    while left:
        x=min(left); orbit=tuple(sorted({g[x] for g in group}))
        out.append(orbit); left-=set(orbit)
    return tuple(sorted(out))


def check(name,n,group,digest):
    counts=[0,0,0,0,0]; orbits=point_orbits(n,group)
    for k in range(1,n+1):
        target=Fraction(k,n)
        for seed in combinations(range(n),k):
            blocks=tuple(sorted({tuple(sorted(g[x] for x in seed)) for g in group}))
            inclusion=tuple(Fraction(sum(x in block for block in blocks),len(blocks)) for x in range(n))
            ratios=tuple(Fraction(sum(x in seed for x in orbit),len(orbit)) for orbit in orbits)
            assert all(all(inclusion[x]==ratios[j] for x in orbit) for j,orbit in enumerate(orbits))
            is_balanced=all(r==target for r in ratios)
            assert is_balanced==(len(set(inclusion))==1 and inclusion[0]==target)
            assert min(inclusion)==min(ratios)
            stabilizer=sum(tuple(sorted(g[x] for x in seed))==seed for g in group)
            assert len(group)==len(blocks)*stabilizer
            counts[0]+=1; counts[1]+=is_balanced; counts[2]+=not is_balanced; counts[3]+=n; counts[4]+=1
            digest.update(repr((name,n,k,seed,orbits,blocks,inclusion,is_balanced)).encode())
    return counts


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--primary",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    primary=json.load(open(a.primary,encoding="utf-8"))
    digest=hashlib.sha256(); totals=[0,0,0,0,0]; families=0
    cases=[]
    cases += [(f"cyclic-{n}",n,cyclic(n)) for n in range(2,11)]
    cases += [(f"dihedral-{n}",n,dihedral(n)) for n in range(3,10)]
    cases += [(f"product-{a}-{t-a}",t,product_group(a,t-a)) for t in range(2,10) for a in range(1,t)]
    for name,n,group in cases:
        values=check(name,n,group,digest); families+=1
        totals=[x+y for x,y in zip(totals,values)]
    expected={"action_families":families,"plans":totals[0],"balanced":totals[1],"unbalanced":totals[2],
              "incidence_checks":totals[3],"stabilizer_checks":totals[4],"enumeration_digest":digest.hexdigest()}
    for key,value in expected.items(): assert primary[key]==value,(key,primary[key],value)
    assert primary["status"]=="pass" and primary["unbalanced"]>0 and primary["balanced"]>0
    out={"status":"pass","independent":True,**expected}
    with open(a.output,"w",encoding="utf-8") as f: json.dump(out,f,indent=2,sort_keys=True); f.write("\n")
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
