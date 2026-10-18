#!/usr/bin/env python3
"""Exact verifier for the orbit-balanced minimax compression theorem."""
import argparse, hashlib, json, math
from fractions import Fraction
from itertools import combinations

from theorica.agents.robust_provenance import (
    sample_orbit_balanced_plan,
    synthesize_orbit_balanced_plan,
)


def cyclic_group(n):
    return tuple(tuple((i+s)%n for i in range(n)) for s in range(n))


def dihedral_group(n):
    return tuple(sorted({tuple((s+i)%n for i in range(n)) for s in range(n)} |
                        {tuple((s-i)%n for i in range(n)) for s in range(n)}))


def product_cyclic_group(a,b):
    return tuple(tuple(((i+s)%a if i<a else a+(i-a+t)%b) for i in range(a+b))
                 for s in range(a) for t in range(b))


def check_family(name,n,group,digest):
    plans=balanced=unbalanced=incidence=stabilizer_checks=0
    for k in range(1,n+1):
        target=Fraction(k,n)
        for seed in combinations(range(n),k):
            plan=synthesize_orbit_balanced_plan(
                n,k-1,seed,group,ambiguity_kind=name,uniform_prior_in_set=True,
            )
            assert plan.certificate_valid
            direct=tuple(Fraction(sum(x in block for block in plan.query_orbit),len(plan.query_orbit)) for x in range(n))
            assert plan.inclusion_probabilities==direct
            expected_ratios=tuple(Fraction(sum(x in seed for x in orbit),len(orbit)) for orbit in plan.point_orbits)
            assert plan.orbit_balance_ratios==expected_ratios
            assert plan.balanced==(all(value==target for value in expected_ratios))
            assert plan.full_simplex_value==min(direct)==min(expected_ratios)
            assert (plan.universal_minimax_value==target)==plan.balanced
            stabilizer=sum(tuple(sorted(g[x] for x in seed))==seed for g in group)
            assert len(group)==len(plan.query_orbit)*stabilizer
            plans+=1; incidence+=n; stabilizer_checks+=1
            balanced+=int(plan.balanced); unbalanced+=int(not plan.balanced)
            digest.update(repr((name,n,k,seed,plan.point_orbits,plan.query_orbit,direct,plan.balanced)).encode())
    return plans,balanced,unbalanced,incidence,stabilizer_checks


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); a=ap.parse_args()
    digest=hashlib.sha256(); totals={"plans":0,"balanced":0,"unbalanced":0,"incidence_checks":0,"stabilizer_checks":0}
    families=0
    for n in range(2,11):
        values=check_family(f"cyclic-{n}",n,cyclic_group(n),digest); families+=1
        for key,value in zip(totals,values): totals[key]+=value
    for n in range(3,10):
        values=check_family(f"dihedral-{n}",n,dihedral_group(n),digest); families+=1
        for key,value in zip(totals,values): totals[key]+=value
    for total in range(2,10):
        for left in range(1,total):
            right=total-left
            values=check_family(f"product-{left}-{right}",total,product_cyclic_group(left,right),digest); families+=1
            for key,value in zip(totals,values): totals[key]+=value

    compression=[]
    sampler_checks=0
    for n in range(5,13):
        for k in range(2,n-1):
            group=cyclic_group(n); seed=tuple(range(k))
            plan=synthesize_orbit_balanced_plan(n,k-1,seed,group,ambiguity_kind="cyclic-interval",uniform_prior_in_set=True)
            assert plan.balanced and len(plan.query_orbit)==n
            assert len(plan.query_orbit)<math.comb(n,k)
            first=sample_orbit_balanced_plan(plan,f"seed-{n}-{k}")
            second=sample_orbit_balanced_plan(plan,f"seed-{n}-{k}")
            assert first==second and first.covered_labels in plan.query_orbit
            sampler_checks+=1
            compression.append({"n":n,"k":k,"full_support":math.comb(n,k),"orbit_support":len(plan.query_orbit),
                                "compression":Fraction(math.comb(n,k),len(plan.query_orbit)).__str__()})

    result={"status":"pass","theorem":"orbit-balanced minimax compression iff point-orbit ratios equal k/n",
            "action_families":families,**totals,"sampler_checks":sampler_checks,
            "compression_examples":compression,"enumeration_digest":digest.hexdigest(),
            "smallest_claim":"Uniform randomization over one finite-group query orbit has point-orbit inclusion |S∩O_j|/|O_j|; it preserves the universal k/n uniform-containing-ambiguity minimax guarantee iff every point-orbit ratio equals k/n, while the full-simplex value of an unbalanced orbit is their minimum."}
    with open(a.output,"w",encoding="utf-8") as f: json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
