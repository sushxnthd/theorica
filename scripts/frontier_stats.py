from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from scipy import stats

def bootstrap_delta(d,seed=20260920,n=20000):
    rng=np.random.default_rng(seed); d=np.asarray(d,float)
    sims=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(n)])
    return [float(np.quantile(sims,.025)),float(np.quantile(sims,.975))]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('path');args=ap.parse_args()
    p=Path(args.path);data=json.loads(p.read_text());rows=data['rows']; by={}
    for r in rows:by[(r['task_id'],r['condition'])]=r
    pairs=[]
    for task in sorted({r['task_id'] for r in rows}):
        a=by.get((task,'vanilla'));b=by.get((task,'theorica'))
        if a and b and a['score']['valid'] and b['score']['valid']:
            pairs.append((task,a['score']['nrmse'],b['score']['nrmse']))
    d=np.array([a-b for _,a,b in pairs],float)
    out={'pairs':len(pairs),'vanilla_mean_nrmse':float(np.mean([a for _,a,b in pairs])) if pairs else None,'theorica_mean_nrmse':float(np.mean([b for _,a,b in pairs])) if pairs else None,'mean_nrmse_improvement_vanilla_minus_theorica':float(d.mean()) if len(d) else None,'bootstrap_95_ci':bootstrap_delta(d) if len(d) else None,'theorica_pairwise_wins':int(np.sum(d>0)),'ties':int(np.sum(d==0)),'losses':int(np.sum(d<0))}
    if len(d):
        try: out['wilcoxon_one_sided_p']=float(stats.wilcoxon(d,alternative='greater').pvalue)
        except Exception:out['wilcoxon_one_sided_p']=None
    target=p.with_name(p.stem+'_stats.json');target.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

if __name__=='__main__':main()
