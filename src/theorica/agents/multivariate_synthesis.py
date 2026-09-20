from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import math
import numpy as np
import sympy as sp


@dataclass(frozen=True)
class MVTerm:
    expression: str
    fn: Callable[[np.ndarray], np.ndarray]
    complexity: int


@dataclass
class MVTheory:
    expression: str
    bic: float
    rss: float
    complexity: int
    terms: list[str]
    coefficients: list[float]
    intercept: float
    predict_fn: Callable[[np.ndarray], np.ndarray]

    def predict(self, X):
        return np.asarray(self.predict_fn(np.asarray(X, dtype=float)), dtype=float)

    def sympy(self):
        try:
            return sp.sympify(self.expression.replace('abs(', 'Abs('))
        except Exception:
            return None


def _safe(fn, X):
    try:
        v=np.asarray(fn(X), dtype=float)
        if v.ndim==0: v=np.full(X.shape[0], float(v))
        if v.shape!=(X.shape[0],) or np.any(~np.isfinite(v)): return None
        return np.clip(v,-1e12,1e12)
    except Exception:
        return None


def _fmt(v):
    if abs(v-round(v))<2e-8: return str(int(round(v)))
    return f"{v:.9g}"


class MultivariateTheorySynthesizer:
    """Bounded open-ended symbolic synthesis over 1-3 variables.

    Complete target equations are never stored. The grammar creates monomials,
    interactions, nonlinear transforms, and selected binary compositions. Sparse
    linear combinations are selected with BIC + structural complexity.
    """
    def __init__(self,max_degree=6,max_terms=8,complexity_weight=0.04,trial_width=48):
        self.max_degree=max_degree; self.max_terms=max_terms
        self.complexity_weight=complexity_weight; self.trial_width=trial_width

    def generate_terms(self,n_vars:int):
        names=['x','y','z'][:n_vars]
        terms=[]; seen=set()
        def add(expr,fn,c):
            if expr in seen:return
            seen.add(expr); terms.append(MVTerm(expr,fn,c))
        atoms=[]
        for j,name in enumerate(names):
            for p in range(1,self.max_degree+1):
                expr=name if p==1 else f"{name}**{p}"
                fn=lambda X,j=j,p=p: X[:,j]**p
                add(expr,fn,p); atoms.append((expr,fn,p,j,p))
        max_inter=min(4,self.max_degree)
        if n_vars>=2:
            for px in range(1,max_inter+1):
                for py in range(1,max_inter+1-px):
                    if px+py>max_inter: continue
                    expr=("x" if px==1 else f"x**{px}")+"*"+("y" if py==1 else f"y**{py}")
                    add(expr,lambda X,px=px,py=py:(X[:,0]**px)*(X[:,1]**py),px+py+1)
        inner=[]
        for j,name in enumerate(names):
            for p in (1,2):
                expr=name if p==1 else f"{name}**{p}"
                fn=lambda X,j=j,p=p:X[:,j]**p
                inner.append((expr,fn,p))
            if self.max_degree>=3:
                inner.append((f"({name}+{name}**2)",lambda X,j=j:X[:,j]+X[:,j]**2,4))
        if n_vars>=2:
            inner += [
                ("(x+y)",lambda X:X[:,0]+X[:,1],3),
                ("(x-y)",lambda X:X[:,0]-X[:,1],3),
                ("(x*y)",lambda X:X[:,0]*X[:,1],3),
            ]
        trig=[]
        for expr,fn,c in inner:
            for nm,op in [('sin',np.sin),('cos',np.cos)]:
                e=f"{nm}({expr})"; f=lambda X,fn=fn,op=op:op(fn(X)); add(e,f,c+2); trig.append((e,f,c+2))
            add(f"log(1+abs({expr}))",lambda X,fn=fn:np.log1p(np.abs(fn(X))),c+3)
            add(f"sqrt(abs({expr}))",lambda X,fn=fn:np.sqrt(np.abs(fn(X))),c+3)
        for i,(e1,f1,c1) in enumerate(trig):
            for e2,f2,c2 in trig[i+1:]:
                if c1+c2<=11:
                    add(f"({e1})*({e2})",lambda X,f1=f1,f2=f2:f1(X)*f2(X),c1+c2+1)
        if n_vars>=2:
            add("x**y",lambda X:np.power(np.clip(X[:,0],1e-9,None),np.clip(X[:,1],-8,8)),6)
            add("y**x",lambda X:np.power(np.clip(X[:,1],1e-9,None),np.clip(X[:,0],-8,8)),6)
        return terms

    def fit(self,X,y):
        X=np.asarray(X,float); y=np.asarray(y,float)
        if X.ndim==1:X=X[:,None]
        if len(y)<max(7,X.shape[1]+4): raise ValueError('not enough observations')
        terms=self.generate_terms(X.shape[1]); usable=[]; vals=[]
        for t in terms:
            v=_safe(t.fn,X)
            if v is not None and np.std(v)>1e-12:
                usable.append(t); vals.append(v)
        A=np.column_stack(vals); means=A.mean(0); stds=np.maximum(A.std(0),1e-12); Z=(A-means)/stds
        candidates=[]
        def assemble(inds,beta,rss):
            struct=sum(usable[i].complexity for i in inds); k=len(inds)+1
            bic=len(y)*math.log(max(rss,1e-24)/len(y))+k*math.log(len(y))+self.complexity_weight*struct
            ts=[usable[i] for i in inds]; coeff=[float(v) for v in beta[:-1]]; intercept=float(beta[-1])
            def pred(Q,ts=tuple(ts),coeff=tuple(coeff),intercept=intercept):
                Q=np.asarray(Q,float); Q=Q[:,None] if Q.ndim==1 else Q
                out=np.full(Q.shape[0],intercept)
                for a,t in zip(coeff,ts):
                    v=_safe(t.fn,Q)
                    if v is None:return np.full(Q.shape[0],np.nan)
                    out += a*v
                return out
            pieces=[f"({_fmt(a)})*({t.expression})" for a,t in zip(coeff,ts) if abs(a)>1e-10]
            if abs(intercept)>1e-10 or not pieces: pieces.append(f"({_fmt(intercept)})")
            return MVTheory(' + '.join(pieces),float(bic),float(rss),struct+len(inds),[t.expression for t in ts],coeff,intercept,pred)
        names=['x','y','z'][:X.shape[1]]; idx={t.expression:i for i,t in enumerate(usable)}
        poly_exprs=[]
        if X.shape[1]==1:
            poly_exprs=[["x" if p==1 else f"x**{p}" for p in range(1,d+1)] for d in range(1,min(self.max_degree,len(y)-2)+1)]
        elif X.shape[1]==2:
            for d in range(1,min(4,self.max_degree)+1):
                es=[]
                for px in range(d+1):
                    for py in range(d+1-px):
                        if px+py==0 or px+py>d:continue
                        if px and py:
                            ex=("x" if px==1 else f"x**{px}")+"*"+("y" if py==1 else f"y**{py}")
                        elif px: ex="x" if px==1 else f"x**{px}"
                        else: ex="y" if py==1 else f"y**{py}"
                        if ex in idx:es.append(ex)
                poly_exprs.append(es)
        for es in poly_exprs:
            if not es or not all(e in idx for e in es):continue
            inds=[idx[e] for e in es]
            if len(inds)>=len(y)-1:continue
            D=np.column_stack([A[:,inds],np.ones(len(y))]); beta,*_=np.linalg.lstsq(D,y,rcond=None); rss=np.sum((y-D@beta)**2)
            candidates.append(assemble(inds,beta,max(float(rss),1e-24)))
        simple=[i for i,t in enumerate(usable) if t.complexity<=5]
        for a_pos,i in enumerate(simple):
            for j in simple[a_pos+1:]:
                if usable[i].complexity+usable[j].complexity>9: continue
                inds=[i,j]
                D=np.column_stack([A[:,inds],np.ones(len(y))])
                beta,*_=np.linalg.lstsq(D,y,rcond=None); rss=max(float(np.sum((y-D@beta)**2)),1e-24)
                candidates.append(assemble(inds,beta,rss))
        selected=[]; pred=np.full(len(y),np.mean(y)); max_terms=min(self.max_terms,len(y)-2)
        for _ in range(max_terms):
            r=y-pred; corr=np.abs(Z.T@r)
            if selected:corr[np.array(selected)]=-np.inf
            order=np.argsort(corr)[::-1][:self.trial_width]
            best=None
            for j in order:
                if not np.isfinite(corr[j]):continue
                inds=selected+[int(j)]; D=np.column_stack([A[:,inds],np.ones(len(y))]); beta,*_=np.linalg.lstsq(D,y,rcond=None); rss=max(float(np.sum((y-D@beta)**2)),1e-24)
                structural=sum(usable[i].complexity for i in inds)
                bic=len(y)*math.log(rss/len(y))+(len(inds)+1)*math.log(len(y))+self.complexity_weight*structural
                if best is None or bic<best[0]:best=(bic,int(j))
            if best is None:break
            selected.append(best[1]); D=np.column_stack([A[:,selected],np.ones(len(y))]); beta,*_=np.linalg.lstsq(D,y,rcond=None); pred=D@beta; rss=max(float(np.sum((y-pred)**2)),1e-24)
            candidates.append(assemble(selected.copy(),beta,rss))
        candidates=sorted(candidates,key=lambda t:t.bic)
        return candidates[0],candidates


def normalized_rmse(pred,truth):
    pred=np.asarray(pred,float); truth=np.asarray(truth,float)
    span=np.quantile(truth,.95)-np.quantile(truth,.05)
    return float(np.sqrt(np.mean((pred-truth)**2))/max(span,1e-12))


def exact_equivalent(expr_a:str,expr_b:str,variables=('x','y','z')):
    syms={v:sp.Symbol(v, positive=True if v in ('x','y') else None) for v in variables}
    try:
        a=sp.sympify(expr_a,locals=syms); b=sp.sympify(expr_b,locals=syms)
        return bool(sp.simplify(a-b)==0)
    except Exception:return False
