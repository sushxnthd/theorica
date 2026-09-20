from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
ACDB=ROOT/"external"/"Active-Causal-Discovery-Bench"
sys.path.insert(0,str(ACDB));sys.path.insert(0,str(ACDB/"src"))
from causal_discovery import BenchmarkEnv,GraphSubmission,build_benchmark_instance,make_v1_config,parse_causallearn_endpoint_matrix,score_submission
from run_ladder import run_pc_greedy_active
from causallearn.search.ConstraintBased.PC import pc
from theorica.causal.cascade_policy import CascadeAwareInterventionPolicy,orient_after_intervention
from theorica.causal.benchmark import meek_close,would_cycle

LEVELS={
0:dict(d=4,k=3,n_obs=50,n_int=25,noise_var=.5,budget_slack=2),
1:dict(d=6,k=6,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
2:dict(d=8,k=9,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
3:dict(d=10,k=12,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
4:dict(d=12,k=14,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
5:dict(d=14,k=16,n_obs=50,n_int=25,noise_var=1.,budget_slack=2)}

def accepted_seeds(level,cfg,n=12):
    rng=np.random.default_rng(2026092100+level);out=[]
    while len(out)<n:
        seed=int(rng.integers(1,2_147_483_647))
        try:build_benchmark_instance(cfg,np.random.default_rng(seed))
        except (RuntimeError,ValueError):continue
        out.append(seed)
    return out

def run_cascade(instance,runtime_seed):
    env=BenchmarkEnv(instance,np.random.default_rng(runtime_seed))
    X=np.asarray(env.observe(),float)
    cg=pc(X,alpha=.05,indep_test="fisherz",show_progress=False,verbose=False)
    directed,und=parse_causallearn_endpoint_matrix(cg.G.graph)
    directed=set(directed);und=set(und)
    directed,und=meek_close(directed,und,instance.config.d)
    policy=CascadeAwareInterventionPolicy()
    used=[]
    while und and env.remaining_budget>0:
        target=policy.choose_target(directed,und,X,set(used))
        if target is None:break
        used.append(target);value=policy.intervention_value(X,target)
        Xi=np.asarray(env.intervene(var=target,value=value),float)
        directed,und=orient_after_intervention(directed,und,target,X,Xi)
    clean=set()
    for e in sorted(directed):
        if not would_cycle(clean,*e):clean.add(e)
    sub=GraphSubmission.from_edges(num_nodes=instance.config.d,directed_edges=clean,undirected_edges=und,interventions_used=len(used))
    out=env.submit_graph(sub);return out.submission,score_submission(instance,out.submission)

def mean(rows,method,key):return float(np.mean([r[method][key] for r in rows]))
def sdct(s,sub):return {"directed_f1":float(s.directed_f1),"dag_shd":float(s.dag_shd),"efficiency":float(s.efficiency),"interventions_used":int(sub.interventions_used)}

def main():
    rows=[]
    for level,spec in LEVELS.items():
        cfg=make_v1_config(**spec)
        for seed in accepted_seeds(level,cfg):
            rt=int(seed*10000+level*101+7);inst=build_benchmark_instance(cfg,np.random.default_rng(seed))
            a_sub,a=run_cascade(inst,rt);b_sub,b=run_pc_greedy_active(inst,rt,.05)
            row={"level":level,"seed":seed,"cascade":sdct(a,a_sub),"pc_greedy":sdct(b,b_sub)}
            rows.append(row);print(json.dumps(row),flush=True)
    d=np.array([r["cascade"]["directed_f1"]-r["pc_greedy"]["directed_f1"] for r in rows])
    rng=np.random.default_rng(20260921); sims=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(10000)])
    summary={"split":"development-only","instances":len(rows),
      "cascade":{k:mean(rows,"cascade",k) for k in ["directed_f1","dag_shd","efficiency","interventions_used"]},
      "pc_greedy":{k:mean(rows,"pc_greedy",k) for k in ["directed_f1","dag_shd","efficiency","interventions_used"]},
      "f1_delta":float(d.mean()),"f1_ci":[float(np.quantile(sims,.025)),float(np.quantile(sims,.975))],
      "claim_boundary":"Development evidence only. These seeds may influence method revisions and may not support final performance claims.","rows":rows}
    Path("results/development").mkdir(parents=True,exist_ok=True)
    Path("results/development/cascade_policy_dev.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"},indent=2))
if __name__=="__main__":main()
