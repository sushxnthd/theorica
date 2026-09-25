from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid

from theorica.agents.equational_discovery import (
    EquationalTheoryMiner,
    query_efficient_theorem_route,
    verify_representation_hypotheses,
)


class NoisyOracle:
    def __init__(self, clean, domain, seed, noise_fraction):
        self.clean=clean
        self.domain=tuple(map(float,domain))
        self.rng=np.random.default_rng(seed)
        self.noise_fraction=float(noise_fraction)
    def __call__(self,x,y):
        z=float(self.clean(float(x),float(y)))
        if not np.isfinite(z): return z
        span=self.domain[1]-self.domain[0]
        return z+float(self.rng.normal(0.0,self.noise_fraction*span))


class CountingOracle:
    def __init__(self,oracle):
        self.oracle=oracle; self.calls=0
    def __call__(self,x,y):
        self.calls+=1
        return self.oracle(x,y)


def make_world(seed):
    rng=np.random.default_rng(seed)
    domain=(-0.8,0.8)
    grid=np.linspace(*domain,4001)
    for _ in range(100):
        b=float(rng.uniform(-1.0,1.0)); c=float(rng.uniform(-0.5,1.5))
        den=1+b*grid+c*grid**2
        if np.min(den)>0.25: break
    num=1+float(rng.uniform(-0.4,0.4))*grid+float(rng.uniform(0,1))*grid**2
    if np.min(num)<=0.2: num=1+0.5*grid**2
    deriv=num/den
    g=cumulative_trapezoid(deriv,grid,initial=0.0)
    g-=np.interp(0.0,grid,g)
    def add(x,y):
        t=np.interp(x,grid,g)+np.interp(y,grid,g)
        if t<g[0] or t>g[-1]: return np.nan
        return float(np.interp(t,g,grid))
    def mean(x,y):
        t=.5*(np.interp(x,grid,g)+np.interp(y,grid,g))
        return float(np.interp(t,g,grid))
    return domain,add,mean


def control(seed):
    domain=(-0.8,0.8)
    mode=seed%3
    if mode==0: return domain,lambda x,y:.35*(x+y)+.15*x*y
    if mode==1: return domain,lambda x,y:.45*x+.15*y+.10*x*y
    return domain,lambda x,y:.45*np.sin(x+y)


def decoy(seed):
    domain=(-0.8,0.8); rng=np.random.default_rng(seed)
    e1=float(rng.choice([-.10,-.05,.05,.10]))
    e2=float(rng.choice([.35,.40]))
    return domain,lambda x,y:.5*(x+y)+e1*(x-y)**2+e2*(x-y)**2*(x+y)


def cases():
    out=[]
    for i in range(25):
        d,a,_=make_world(1000+i)
        _,_,m=make_world(1100+i)
        out += [
            ("additive_generator",d,a,11000+i),
            ("quasi_arithmetic_mean",d,m,12000+i),
            ("commutative_semilattice",d,max if i%2==0 else min,13000+i),
        ]
        dc,fc=control(1200+i); out.append(("unresolved",dc,fc,14000+i))
        dd,fd=decoy(1300+i); out.append(("unresolved",dd,fd,15000+i))
    return out


def broad_call_count(clean,domain,seed,noise):
    counter=CountingOracle(NoisyOracle(clean,domain,seed,noise))
    miner=EquationalTheoryMiner(max_operations=2,p95_tolerance=.02,min_common_fraction=.20)
    theory=miner.mine(counter,domain,assignments=20,seed=seed+1)
    _=verify_representation_hypotheses(counter,domain,theory,probes=60,seed=seed+2)
    return counter.calls


def run():
    # Oracle-call totals include repeated measurements and every nested
    # composition required by theorem-premise tests.
    rows=[]
    all_cases=cases()
    for ni,noise in enumerate((0.001,0.003)):
        for expected,domain,clean,seed in all_cases:
            route=query_efficient_theorem_route(
                NoisyOracle(clean,domain,seed+100000*ni,noise),
                domain,seed=seed+200000*ni,probes=8,
            )
            rows.append({
                "noise":noise,"expected":expected,"predicted":route.verified_family,
                "correct":expected==route.verified_family,
                "calls":route.oracle_calls,
                "repeat_noise_p95":route.repeat_noise_p95,
                "comm_p95":route.commutativity_p95,
                "idem_p95":route.idempotence_p95,
                "assoc_p95":route.associativity_p95,
                "bisym_p95":route.bisymmetry_p95,
                "monotonicity":route.monotonicity_rate,
            })
    summaries=[]
    for noise in (0.001,0.003):
        r=[x for x in rows if x["noise"]==noise]
        summaries.append({
            "noise":noise,
            "n":len(r),
            "correct":sum(x["correct"] for x in r),
            "median_calls":float(np.median([x["calls"] for x in r])),
            "p90_calls":float(np.quantile([x["calls"] for x in r],.9)),
            "max_calls":max(x["calls"] for x in r),
            "errors":[x for x in r if not x["correct"]],
        })
    broad=[]
    for j,(expected,domain,clean,seed) in enumerate(all_cases[:10]):
        broad.append(broad_call_count(clean,domain,seed+900000,.001))
    summary={
        "router":summaries,
        "broad_miner_reference_n":len(broad),
        "broad_miner_reference_median_calls":float(np.median(broad)),
        "broad_miner_reference_min_calls":min(broad),
        "broad_miner_reference_max_calls":max(broad),
    }
    Path("results/query_efficient_router_dev.json").write_text(
        json.dumps({"summary":summary,"rows":rows},indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps(summary,indent=2))
    assert all(s["correct"]>=120 for s in summaries)
    assert all(s["median_calls"]<140 for s in summaries)
    assert summary["broad_miner_reference_median_calls"] > 5*max(s["median_calls"] for s in summaries)


if __name__=="__main__":
    run()
