from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
ACDB=ROOT/"external"/"Active-Causal-Discovery-Bench"
sys.path.insert(0,str(ACDB))
sys.path.insert(0,str(ACDB/"src"))

from causal_discovery import BenchmarkEnv, GraphSubmission, build_benchmark_instance, make_v1_config, score_submission
from run_ladder import run_pc_greedy_active
from theorica.causal.benchmark import pc_skeleton, orient_vstructures, meek_close, would_cycle

LEVELS={
 0:dict(d=4,k=3,n_obs=50,n_int=25,noise_var=.5,budget_slack=2),
 1:dict(d=6,k=6,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
 2:dict(d=8,k=9,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
 3:dict(d=10,k=12,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
 4:dict(d=12,k=14,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
 5:dict(d=14,k=16,n_obs=50,n_int=25,noise_var=1.,budget_slack=2),
}
SEEDS={
 0:[1276453582,27998312,931551983,974369856,1539978433,868078822,452641024,963592850],
 1:[1257633785,1100146725,1910407594,746528573,1175759265,1982942393,1449442515,1479720101],
 2:[823847298,834246677,32015887,716908331,1426457537,684342303,1207468583,1612783012],
 3:[1329552115,160719912,362855691,589330817,1877150515,370845052,976218778,1286035187],
 4:[518645330,511033471,1198956094,154587426,1368642322,1163629188,1332933138,1231061499],
 5:[1526642568,1170708238,385840006,32447648,1017236502,1717602974,480184089,2015902496],
}
PUBLISHED_PC_GREEDY={0:.808333,1:.802273,2:.612693,3:.696656,4:.689550,5:.641963}

def choose_target(und,d,used):
    candidates=[i for i in range(d) if i not in used]
    if not candidates:return None
    degree={i:sum(i in e for e in und) for i in candidates}
    return max(candidates,key=lambda i:(degree[i],-i))

def run_theorica(instance,runtime_seed):
    env=BenchmarkEnv(instance,np.random.default_rng(runtime_seed))
    X=np.asarray(env.observe(),float)
    d=instance.config.d
    n_obs=len(X); n_int=instance.config.n_int
    adj,sep=pc_skeleton(X,.03,2)
    directed,und=orient_vstructures(adj,sep)
    directed,und=meek_close(directed,und,d)
    obs_mean=X.mean(0); obs_sd=X.std(0,ddof=1)
    used=[]
    while und and env.remaining_budget>0:
        target=choose_target(und,d,set(used))
        if target is None:break
        used.append(target)
        Xi=np.asarray(env.intervene(var=target,value=3.0),float)
        mu=Xi.mean(0); sd=Xi.std(0,ddof=1)
        for pair in list(und):
            if target not in pair:continue
            other=pair[1] if pair[0]==target else pair[0]
            se=math.sqrt(obs_sd[other]**2/n_obs+sd[other]**2/n_int)+1e-9
            z=abs(mu[other]-obs_mean[other])/se
            und.remove(pair)
            cand=(target,other) if z>2.2 else (other,target)
            if not would_cycle(directed,*cand):
                directed.add(cand)
        directed,und=meek_close(directed,und,d)
    clean=set()
    for a,b in sorted(directed):
        if not would_cycle(clean,a,b):clean.add((a,b))
    submission=GraphSubmission.from_edges(
        num_nodes=d,directed_edges=clean,undirected_edges=und,interventions_used=len(used)
    )
    output=env.submit_graph(submission)
    return output.submission,score_submission(instance,output.submission)

def score_dict(s):
    return {k:float(getattr(s,k)) for k in ["directed_f1","skeleton_f1","dag_shd","efficiency"]}

def bootstrap(d,seed=20260920,n=20000):
    d=np.asarray(d,float); rng=np.random.default_rng(seed)
    sims=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(n)])
    return [float(np.quantile(sims,.025)),float(np.quantile(sims,.975))]

def main():
    rows=[]
    for level,spec in LEVELS.items():
        cfg=make_v1_config(**spec)
        for seed in SEEDS[level]:
            runtime_seed=int(seed*10000+level*101+7)
            instance=build_benchmark_instance(cfg,np.random.default_rng(seed))
            th_sub,th=run_theorica(instance,runtime_seed)
            pc_sub,pc=run_pc_greedy_active(instance,runtime_seed,.05)
            row={
              "level":level,"seed":seed,"runtime_seed":runtime_seed,
              "theorica":{**score_dict(th),"interventions_used":int(th_sub.interventions_used)},
              "official_pc_greedy":{**score_dict(pc),"interventions_used":int(pc_sub.interventions_used)}
            }
            rows.append(row); print(json.dumps(row),flush=True)

    def agg(method,key):
        vals=[r[method][key] for r in rows]
        return float(np.mean(vals))
    per_level={}
    for level in LEVELS:
        rs=[r for r in rows if r["level"]==level]
        per_level[str(level)]={
          "theorica_directed_f1":float(np.mean([r["theorica"]["directed_f1"] for r in rs])),
          "official_pc_greedy_directed_f1":float(np.mean([r["official_pc_greedy"]["directed_f1"] for r in rs])),
          "published_pc_greedy_directed_f1":PUBLISHED_PC_GREEDY[level],
        }
    d=np.array([r["theorica"]["directed_f1"]-r["official_pc_greedy"]["directed_f1"] for r in rows])
    try:p=float(stats.wilcoxon(d,alternative="greater").pvalue)
    except Exception:p=None
    summary={
      "panel":"ACDB canonical full_gpt55 seed map",
      "instances":len(rows),
      "runtime_seed_rule":"seed*10000 + level*101 + 7",
      "theorica":{
        "directed_f1":agg("theorica","directed_f1"),
        "skeleton_f1":agg("theorica","skeleton_f1"),
        "dag_shd":agg("theorica","dag_shd"),
        "efficiency":agg("theorica","efficiency"),
        "interventions_used":agg("theorica","interventions_used"),
      },
      "official_pc_greedy":{
        "directed_f1":agg("official_pc_greedy","directed_f1"),
        "skeleton_f1":agg("official_pc_greedy","skeleton_f1"),
        "dag_shd":agg("official_pc_greedy","dag_shd"),
        "efficiency":agg("official_pc_greedy","efficiency"),
        "interventions_used":agg("official_pc_greedy","interventions_used"),
      },
      "paired_theorica_minus_pc_directed_f1":{
        "mean":float(d.mean()),"bootstrap_95_ci":bootstrap(d),
        "wilcoxon_one_sided_p":p,"wins":int(np.sum(d>0)),"ties":int(np.sum(d==0)),"losses":int(np.sum(d<0))
      },
      "per_level":per_level,
      "rows":rows,
      "claim_boundary":"Same canonical seed map and runtime RNG rule as ACDB full_gpt55 manifest. THEORICA was not part of the original paper panel; comparisons to published LLM rows are contextual, not an official leaderboard submission."
    }
    Path("results/native/acdb_canonical_panel.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"},indent=2))

if __name__=="__main__":main()
