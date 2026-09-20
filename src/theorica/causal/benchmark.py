from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
import numpy as np
from scipy import stats

@dataclass
class CausalWorld:
    d:int; edges:set[tuple[int,int]]; weights:np.ndarray; noise:float; seed:int
    def sample(self,n,rng,intervention=None):
        X=np.zeros((n,self.d),float)
        indeg=[0]*self.d; ch=[[] for _ in range(self.d)]
        for a,b in self.edges: indeg[b]+=1; ch[a].append(b)
        q=[i for i,v in enumerate(indeg) if v==0]; order=[]
        while q:
            u=q.pop(0); order.append(u)
            for v in ch[u]:
                indeg[v]-=1
                if indeg[v]==0:q.append(v)
        ivar=-1; ival=0.0
        if intervention is not None: ivar,ival=intervention
        for j in order:
            if j==ivar: X[:,j]=ival; continue
            pa=[a for a,b in self.edges if b==j]
            mu=np.zeros(n)
            for a in pa: mu += self.weights[a,j]*X[:,a]
            X[:,j]=mu+rng.normal(0,self.noise,n)
        return X

def random_world(d,k,seed,noise=1.0):
    rng=np.random.default_rng(seed); order=list(rng.permutation(d)); poss=[(order[i],order[j]) for i in range(d) for j in range(i+1,d)]
    chosen=rng.choice(len(poss),size=k,replace=False); edges={poss[int(i)] for i in chosen}
    W=np.zeros((d,d))
    for a,b in edges:
        mag=rng.uniform(.5,2.0); W[a,b]=mag if rng.random()<.5 else -mag
    return CausalWorld(d,edges,W,noise,seed)

def partial_corr_pvalue(X,i,j,cond):
    if not cond:
        r,p=stats.pearsonr(X[:,i],X[:,j]); return float(r),float(p)
    Z=np.column_stack([np.ones(len(X)),X[:,list(cond)]])
    bi,*_=np.linalg.lstsq(Z,X[:,i],rcond=None); bj,*_=np.linalg.lstsq(Z,X[:,j],rcond=None)
    ri=X[:,i]-Z@bi; rj=X[:,j]-Z@bj
    r=np.corrcoef(ri,rj)[0,1]; r=np.clip(r,-.999999,.999999)
    df=max(len(X)-len(cond)-2,1); t=abs(r)*np.sqrt(df/(1-r*r)); p=2*stats.t.sf(t,df)
    return float(r),float(p)

def pc_skeleton(X,alpha=.03,max_cond=2):
    d=X.shape[1]; adj={i:set(j for j in range(d) if j!=i) for i in range(d)}; sep={}
    for l in range(max_cond+1):
        changed=False
        for i in range(d):
            for j in list(adj[i]):
                if j<=i: continue
                nbr=list(adj[i]-{j})
                if len(nbr)<l: continue
                for cond in combinations(nbr,l):
                    _,p=partial_corr_pvalue(X,i,j,cond)
                    if p>alpha:
                        adj[i].discard(j); adj[j].discard(i); sep[(i,j)]=sep[(j,i)]=set(cond); changed=True; break
        if not changed and l>0: pass
    return adj,sep

def orient_vstructures(adj,sep):
    directed=set(); und={tuple(sorted((i,j))) for i in adj for j in adj[i] if i<j}; d=len(adj)
    for z in range(d):
        ns=list(adj[z])
        for x,y in combinations(ns,2):
            if y in adj[x]:continue
            if z not in sep.get((x,y),set()):
                for a in (x,y):
                    e=tuple(sorted((a,z)))
                    if e in und:und.remove(e); directed.add((a,z))
    return directed,und

def would_cycle(directed,src,dst):
    graph={}
    for a,b in directed:graph.setdefault(a,[]).append(b)
    stack=[dst];seen=set()
    while stack:
        u=stack.pop()
        if u==src:return True
        if u in seen:continue
        seen.add(u);stack+=graph.get(u,[])
    return False

def orient_edge(directed,und,a,b,src,dst):
    e=tuple(sorted((a,b)))
    if e in und and not would_cycle(directed,src,dst): und.remove(e); directed.add((src,dst)); return True
    return False

def meek_close(directed,und,d):
    changed=True
    while changed:
        changed=False
        for b,c in list(und):
            for src,dst in [(b,c),(c,b)]:
                pars=[a for a,z in directed if z==src]
                for a in pars:
                    adjacent=tuple(sorted((a,dst))) in und or (a,dst) in directed or (dst,a) in directed
                    if not adjacent and orient_edge(directed,und,src,dst,src,dst):changed=True;break
                if changed:break
            if changed:break
        if changed:continue
        for a,b in list(und):
            for src,dst in [(a,b),(b,a)]:
                mids=[c for s,c in directed if s==src and (c,dst) in directed]
                if mids and orient_edge(directed,und,src,dst,src,dst):changed=True;break
            if changed:break
    return directed,und

def graph_scores(directed,und,true_edges):
    true=set(true_edges); pred=set(directed); tp=len(pred&true); fp=len(pred-true); fn=len(true-pred)
    prec=tp/(tp+fp) if tp+fp else 1.; rec=tp/(tp+fn) if tp+fn else 1.; f1=2*prec*rec/(prec+rec) if prec+rec else 0.
    ts={tuple(sorted(e)) for e in true}; ps={tuple(sorted(e)) for e in pred}|set(und); stp=len(ts&ps); sfp=len(ps-ts); sfn=len(ts-ps)
    sp=stp/(stp+sfp) if stp+sfp else 1.; sr=stp/(stp+sfn) if stp+sfn else 1.; sf1=2*sp*sr/(sp+sr) if sp+sr else 0.
    shd=0
    for pair in ts|ps:
        if pair not in ts or pair not in ps:shd+=1;continue
        a,b=pair; te=(a,b) if (a,b) in true else (b,a)
        if pair in und:shd+=1
        elif te not in pred:shd+=1
    return {'directed_f1':f1,'directed_precision':prec,'directed_recall':rec,'skeleton_f1':sf1,'dag_shd':shd}
