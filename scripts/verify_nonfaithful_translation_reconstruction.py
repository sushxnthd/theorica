#!/usr/bin/env python3
"""Exhaust the sharp common-base reconstruction boundary through n=4."""
from __future__ import annotations

import argparse,hashlib,itertools,json,math,sys
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from theorica.agents.translation_action import discover_translation_action_representation

Perm=tuple[int,...]

def compose(a:Perm,b:Perm)->Perm: return tuple(a[b[i]] for i in range(len(a)))
def inverse(a:Perm)->Perm:
    out=[0]*len(a)
    for i,v in enumerate(a): out[v]=i
    return tuple(out)

@lru_cache(None)
def closure(generators:tuple[Perm,...])->tuple[Perm,...]:
    n=len(generators[0]); ident=tuple(range(n)); moves=tuple(dict.fromkeys(generators+tuple(inverse(g) for g in generators)))
    seen={ident}; stack=[ident]
    while stack:
        cur=stack.pop()
        for move in moves:
            nxt=compose(move,cur)
            if nxt not in seen: seen.add(nxt); stack.append(nxt)
    return tuple(sorted(seen))

@lru_cache(None)
def group_data(realized:tuple[Perm,...])->tuple[tuple[Perm,...],tuple[Perm,...],tuple[int,...]]:
    realized=tuple(sorted(set(realized))); group=closure(realized); n=len(realized[0]); generating=None
    for size in range(1,len(realized)+1):
        for subset in itertools.combinations(realized,size):
            if closure(tuple(sorted(subset)))==group: generating=subset; break
        if generating is not None: break
    assert generating is not None
    base=None
    for size in range(n+1):
        for points in itertools.combinations(range(n),size):
            signatures={tuple(g[p] for p in points) for g in group}
            if len(signatures)==len(group): base=points; break
        if base is not None: break
    assert base is not None
    return group,tuple(generating),tuple(base)

def reconstruct(rows:tuple[Perm,...],group:tuple[Perm,...],base:tuple[int,...])->tuple[Perm,...]:
    index={tuple(g[p] for p in base):g for g in group}
    return tuple(index[tuple(row[p] for p in base)] for row in rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--max-n",type=int,default=4); a=ap.parse_args()
    by_n={}; failures=[]; smallest=None
    for n in range(1,a.max_n+1):
        perms=tuple(itertools.permutations(range(n))); total=faithful=nonfaithful=0; query_sum=0; max_fraction=0.0
        for rows in itertools.product(perms,repeat=n):
            total+=1; is_faithful=len(set(rows))==n; faithful+=is_faithful; nonfaithful+=not is_faithful
            group,gens,base=group_data(tuple(sorted(set(rows))))
            recovered=reconstruct(rows,group,base)
            if recovered!=rows and len(failures)<10: failures.append({"n":n,"rows":rows,"base":base})
            generator_indices=[]; remaining=list(gens)
            for i,row in enumerate(rows):
                if row in remaining: generator_indices.append(i); remaining.remove(row)
            r=len(generator_indices); queries=r*n+(n-r)*len(base); query_sum+=queries; max_fraction=max(max_fraction,queries/(n*n))
            if not is_faithful and smallest is None:
                table=[list(row) for row in rows]
                current=discover_translation_action_representation(lambda x,y,t=table:t[x][y],n,seed=0,max_generator_rows=n,validation_queries=n*n)
                if not current.accepted and recovered==rows:
                    smallest={"n":n,"table":table,"group_size":len(group),"base":list(base),"generator_rows":generator_indices,
                              "conditional_queries":queries,"current_reason":current.reason}
        by_n[str(n)]={"operations":total,"faithful":faithful,"nonfaithful":nonfaithful,"reconstruction_failures":sum(1 for f in failures if f["n"]==n),
                      "mean_conditional_queries":query_sum/total,"max_table_fraction":max_fraction}
    expected=sum(math.factorial(n)**n for n in range(1,a.max_n+1))
    gates={"complete_count":sum(v["operations"] for v in by_n.values())==expected,"zero_failures":not failures,
           "minimal_n2":smallest is not None and smallest["n"]==2,"nonfaithful_covered":all(v["nonfaithful"]==0 or v["reconstruction_failures"]==0 for v in by_n.values())}
    payload={"schema":"theorica.nonfaithful-translation-boundary.v1","classification":"EXACT_ENUMERATION","max_n":a.max_n,"expected_operations":expected,
             "by_n":by_n,"smallest_current_learner_counterexample":smallest,"failures":failures,"gates":gates,"status":"PASS" if all(gates.values()) else "FAIL"}
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":")).encode(); payload["canonical_sha256"]=hashlib.sha256(canonical).hexdigest()
    a.output.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n"); print(json.dumps({"status":payload["status"],"gates":gates,"by_n":by_n,"smallest":smallest,"canonical_sha256":payload["canonical_sha256"]},indent=2))

if __name__=="__main__": main()
