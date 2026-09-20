from __future__ import annotations
import numpy as np
from .benchmark import pc_skeleton,orient_vstructures,meek_close,graph_scores

class ActiveCausalScientist:
    def __init__(self,alpha=.03,max_cond=2,policy='greedy'):
        self.alpha=alpha;self.max_cond=max_cond;self.policy=policy
    def choose_target(self,und,d,rng,used):
        candidates=[i for i in range(d) if i not in used]
        if not candidates:return None
        if self.policy=='random':return int(rng.choice(candidates))
        deg={i:sum(i in e for e in und) for i in candidates}; return max(candidates,key=lambda i:(deg[i],-i))
    def run(self,world,n_obs=50,n_int=25,budget=3,seed=0):
        rng=np.random.default_rng(seed); X=world.sample(n_obs,rng)
        adj,sep=pc_skeleton(X,self.alpha,self.max_cond); directed,und=orient_vstructures(adj,sep); directed,und=meek_close(directed,und,world.d)
        used=[]; logs=[]; obs_mean=X.mean(0); obs_sd=X.std(0,ddof=1)
        for step in range(budget):
            t=self.choose_target(und,world.d,rng,set(used))
            if t is None:break
            used.append(t); value=3.0; Xi=world.sample(n_int,rng,(t,value)); mu=Xi.mean(0); sd=Xi.std(0,ddof=1)
            oriented=[]
            for pair in list(und):
                if t not in pair:continue
                other=pair[1] if pair[0]==t else pair[0]
                se=np.sqrt(obs_sd[other]**2/n_obs+sd[other]**2/n_int)+1e-9
                z=abs(mu[other]-obs_mean[other])/se
                if z>2.2:
                    und.remove(pair); directed.add((t,other)); oriented.append((t,other,z))
                else:
                    und.remove(pair); directed.add((other,t)); oriented.append((other,t,z))
            directed,und=meek_close(directed,und,world.d)
            logs.append({'target':t,'oriented':oriented,'remaining_undirected':len(und)})
            if not und:break
        scores=graph_scores(directed,und,world.edges); scores.update({'interventions_used':len(used),'remaining_undirected':len(und),'targets':used,'logs':logs})
        return scores
