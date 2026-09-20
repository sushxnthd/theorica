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

CANONICAL={
0:{1276453582,27998312,931551983,974369856,1539978433,868078822,452641024,963592850},
1:{1257633785,1100146725,1910407594,746528573,1175759265,1982942393,1449442515,1479720101},
2:{823847298,834246677,32015887,716908331,1426457537,684342303,1207468583,1612783012},
3:{1329552115,160719912,362855691,589330817,1877150515,370845052,976218778,1286035187},
4:{518645330,511033471,1198956094,154587426,1368642322,1163629188,1332933138,1231061499},
5:{1526642568,1170708238,385840006,32447648,1017236502,1717602974,480184089,2015902496}}

def accepted_seeds(level,cfg,n,base,forbidden=frozenset()):
    rng=np.random.default_rng(base+level);out=[]
    while len(out)<n:
        seed=int(rng.integers(1,2_147_483_647))
        if seed in forbidden:continue
        try:build_benchmark_instance(cfg,np.random.default_rng(seed))
        except (RuntimeError,ValueError):continue
        out.append(seed)
    return out

def run_cascade(instance,runtime_seed):
    env=BenchmarkEnv(instance,np.random.default_rng(runtime_seed))
    X=np.asarray(env.observe(),float)
    cg=pc(X,alpha=.05,indep_test="fisherz",show_progress=False,verbose=False)
    directed,und=parse_causallearn_endpoint_matrix(cg.G.graph)
    directed=set(directed);und=set(und);directed,und=meek_close(directed,und,instance.config.d)
    policy=CascadeAwareInterventionPolicy();used=[]
    while und and env.remaining_budget>0:
        target=policy.choose_target(directed,und,X,set(used))
        if target is None:break
        used.append(target)
        Xi=np.asarray(env.intervene(var=target,value=policy.intervention_value(X,target)),float)
        directed,und=orient_after_intervention(directed,und,target,X,Xi)
    clean=set()
    for e in sorted(directed):
        if not would_cycle(clean,*e):clean.add(e)
    sub=GraphSubmission.from_edges(num_nodes=instance.config.d,directed_edges=clean,undirected_edges=und,interventions_used=len(used))
    out=env.submit_graph(sub);return out.submission,score_submission(instance,out.submission)

def sdct(s,sub):
    return {"directed_f1":float(s.directed_f1),"skeleton_f1":float(s.skeleton_f1),"dag_shd":float(s.dag_shd),"efficiency":float(s.efficiency),"interventions_used":int(sub.interventions_used)}

def paired(rows,key,higher=True):
    a=np.array([r["cascade"][key] for r in rows],float);b=np.array([r["pc_greedy"][key] for r in rows],float)
    d=(a-b) if higher else (b-a)
    rng=np.random.default_rng(20261031+len(key)); sims=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(20000)])
    try:p=float(stats.wilcoxon(d,alternative="greater").pvalue)
    except Exception:p=None
    return {"cascade":float(a.mean()),"pc_greedy":float(b.mean()),"improvement_positive_is_cascade_better":float(d.mean()),
      "bootstrap_95_ci":[float(np.quantile(sims,.025)),float(np.quantile(sims,.975))],"wilcoxon_one_sided_p":p,
      "wins":int(np.sum(d>0)),"ties":int(np.sum(d==0)),"losses":int(np.sum(d<0))}

def main():
    rows=[]; seed_map={}
    for level,spec in LEVELS.items():
        cfg=make_v1_config(**spec)
        dev=set(accepted_seeds(level,cfg,12,2026092100,CANONICAL[level]))
        forbidden=CANONICAL[level]|dev
        seeds=accepted_seeds(level,cfg,20,2026103100,forbidden)
        assert not (set(seeds)&forbidden)
        seed_map[str(level)]=seeds
        for seed in seeds:
            rt=int(seed*10000+level*101+7);inst=build_benchmark_instance(cfg,np.random.default_rng(seed))
            a_sub,a=run_cascade(inst,rt);b_sub,b=run_pc_greedy_active(inst,rt,.05)
            row={"level":level,"seed":seed,"runtime_seed":rt,"cascade":sdct(a,a_sub),"pc_greedy":sdct(b,b_sub)}
            rows.append(row);print(json.dumps(row),flush=True)
    summary={
      "split":"FROZEN_UNTOUCHED_HOLDOUT",
      "instances":len(rows),
      "method_frozen_since_commit":"bbe5b0971c71faf8481c18aeda3194a91a2e92da",
      "seed_generator":"base 2026103100 + level; 20 accepted seeds/level; excludes canonical and development seeds",
      "directed_f1":paired(rows,"directed_f1",True),
      "skeleton_f1":paired(rows,"skeleton_f1",True),
      "dag_shd":paired(rows,"dag_shd",False),
      "efficiency":paired(rows,"efficiency",True),
      "interventions_used":paired(rows,"interventions_used",False),
      "seed_map":seed_map,"rows":rows,
      "claim_boundary":"Method was frozen after the 72-world development split and before generating/observing these 120 holdout instances."
    }
    Path("results/frozen").mkdir(parents=True,exist_ok=True)
    Path("results/frozen/cascade_policy_holdout.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k not in {"rows","seed_map"}},indent=2))
if __name__=="__main__":main()
