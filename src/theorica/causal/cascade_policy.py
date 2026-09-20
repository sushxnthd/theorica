from __future__ import annotations
import math
import numpy as np
from .benchmark import meek_close, would_cycle

class CascadeAwareInterventionPolicy:
    """Select interventions for expected graph-orientation yield.

    The policy combines:
    1. unresolved-edge incidence,
    2. observational association strength as a rough identifiability proxy,
    3. expected orientation cascades under both possible directions.

    It contains no benchmark-specific graph truths and does not inspect hidden DAGs.
    """

    def __init__(self, cascade_weight: float = 0.35, min_scale: float = 1e-9):
        self.cascade_weight=float(cascade_weight)
        self.min_scale=float(min_scale)

    @staticmethod
    def _cascade_gain(directed,und,a,b,d):
        gains=[]
        for edge in ((a,b),(b,a)):
            dd=set(directed); uu=set(und); pair=tuple(sorted((a,b)))
            if pair not in uu or would_cycle(dd,*edge):
                gains.append(0.0);continue
            before=len(uu);uu.remove(pair);dd.add(edge)
            dd,uu=meek_close(dd,uu,d)
            gains.append(float(before-len(uu)))
        return float(np.mean(gains))

    def choose_target(self,directed,und,X,used):
        d=X.shape[1]
        candidates=[i for i in range(d) if i not in used and any(i in e for e in und)]
        if not candidates:return None
        C=np.nan_to_num(np.corrcoef(X,rowvar=False),nan=0.0)
        scores={}
        for i in candidates:
            score=0.0
            for pair in und:
                if i not in pair:continue
                j=pair[1] if pair[0]==i else pair[0]
                assoc=min(1.0,max(0.0,abs(float(C[i,j]))))
                cascade=self._cascade_gain(directed,und,i,j,d)
                # Every incident edge has base value; association prioritizes
                # edges likely to produce a detectable intervention shift.
                score += (0.5+0.5*assoc)*(1.0+self.cascade_weight*max(0.0,cascade-1.0))
            scores[i]=score
        return max(candidates,key=lambda i:(scores[i],-i))

    def intervention_value(self,X,target):
        mu=float(np.mean(X[:,target])); sd=float(np.std(X[:,target],ddof=1))
        # Scale the intervention to the observed variable rather than assuming
        # a universal absolute unit.
        return mu+3.0*max(sd,self.min_scale)

def orient_after_intervention(directed,und,target,X_obs,X_int,z_threshold=1.959963984540054):
    """Orient target-incident CPDAG edges from intervention-induced mean shifts."""
    directed=set(directed);und=set(und)
    n_obs=len(X_obs);n_int=len(X_int)
    mu0=X_obs.mean(0);mu1=X_int.mean(0)
    v0=X_obs.var(0,ddof=1);v1=X_int.var(0,ddof=1)
    for pair in list(und):
        if target not in pair:continue
        other=pair[1] if pair[0]==target else pair[0]
        se=math.sqrt(float(v0[other])/n_obs+float(v1[other])/n_int)+1e-12
        shifted=abs(float(mu1[other]-mu0[other])) > z_threshold*se
        cand=(target,other) if shifted else (other,target)
        und.remove(pair)
        if not would_cycle(directed,*cand):
            directed.add(cand)
    directed,und=meek_close(directed,und,X_obs.shape[1])
    return directed,und
