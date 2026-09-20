from __future__ import annotations
import json, math, sys
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent / "external" / "Active-Causal-Discovery-Bench"
sys.path.insert(0, str(ROOT / "src"))
from causal_discovery import (
    GraphSubmission,
    build_benchmark_instance,
    make_v1_config,
    sample_interventional_data,
    score_submission,
)

LEVELS = {
    0: dict(d=4, k=3, n_obs=50, n_int=25, noise_var=0.5, budget_slack=2),
    1: dict(d=6, k=6, n_obs=50, n_int=25, noise_var=1.0, budget_slack=2),
    2: dict(d=8, k=9, n_obs=50, n_int=25, noise_var=1.0, budget_slack=2),
    3: dict(d=10, k=12, n_obs=50, n_int=25, noise_var=1.0, budget_slack=2),
    4: dict(d=12, k=14, n_obs=50, n_int=25, noise_var=1.0, budget_slack=2),
    5: dict(d=14, k=16, n_obs=50, n_int=25, noise_var=1.0, budget_slack=2),
}

def partial_corr_pvalue(X, i, j, cond):
    if not cond:
        r, p = stats.pearsonr(X[:, i], X[:, j])
        return float(r), float(p)
    Z = np.column_stack([np.ones(len(X)), X[:, list(cond)]])
    bi, *_ = np.linalg.lstsq(Z, X[:, i], rcond=None)
    bj, *_ = np.linalg.lstsq(Z, X[:, j], rcond=None)
    ri, rj = X[:, i] - Z @ bi, X[:, j] - Z @ bj
    r = np.clip(np.corrcoef(ri, rj)[0, 1], -.999999, .999999)
    df = max(len(X) - len(cond) - 2, 1)
    t = abs(r) * np.sqrt(df / (1 - r*r))
    return float(r), float(2 * stats.t.sf(t, df))

def pc_skeleton(X, alpha=.03, max_cond=2):
    d = X.shape[1]
    adj = {i: set(j for j in range(d) if j != i) for i in range(d)}
    sep = {}
    for l in range(max_cond + 1):
        for i in range(d):
            for j in list(adj[i]):
                if j <= i:
                    continue
                nbr = list(adj[i] - {j})
                if len(nbr) < l:
                    continue
                for cond in combinations(nbr, l):
                    _, p = partial_corr_pvalue(X, i, j, cond)
                    if p > alpha:
                        adj[i].discard(j)
                        adj[j].discard(i)
                        sep[(i, j)] = sep[(j, i)] = set(cond)
                        break
    return adj, sep

def orient_vstructures(adj, sep):
    directed = set()
    und = {tuple(sorted((i,j))) for i in adj for j in adj[i] if i < j}
    d = len(adj)
    for z in range(d):
        ns = list(adj[z])
        for x, y in combinations(ns, 2):
            if y in adj[x]:
                continue
            if z not in sep.get((x, y), set()):
                for a in (x, y):
                    e = tuple(sorted((a, z)))
                    if e in und:
                        und.remove(e)
                        directed.add((a, z))
    return directed, und

def would_cycle(directed, src, dst):
    graph = {}
    for a, b in directed:
        graph.setdefault(a, []).append(b)
    stack, seen = [dst], set()
    while stack:
        u = stack.pop()
        if u == src:
            return True
        if u in seen:
            continue
        seen.add(u)
        stack += graph.get(u, [])
    return False

def orient_edge(directed, und, a, b, src, dst):
    e = tuple(sorted((a,b)))
    if e in und and not would_cycle(directed, src, dst):
        und.remove(e)
        directed.add((src, dst))
        return True
    return False

def meek_close(directed, und, d):
    changed = True
    while changed:
        changed = False
        for b, c in list(und):
            for src, dst in ((b,c),(c,b)):
                for a in [u for u,v in directed if v == src]:
                    adjacent = tuple(sorted((a,dst))) in und or (a,dst) in directed or (dst,a) in directed
                    if not adjacent and orient_edge(directed, und, src, dst, src, dst):
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
        if changed:
            continue
        for a, b in list(und):
            for src, dst in ((a,b),(b,a)):
                if any((c,dst) in directed for s,c in directed if s == src):
                    if orient_edge(directed, und, src, dst, src, dst):
                        changed = True
                        break
            if changed:
                break
    return directed, und

def choose_target(und, d, rng, used, policy):
    candidates = [i for i in range(d) if i not in used]
    if not candidates:
        return None
    if policy == "random":
        return int(rng.choice(candidates))
    degree = {i: sum(i in e for e in und) for i in candidates}
    return max(candidates, key=lambda i: (degree[i], -i))

def run_policy(instance, seed, policy):
    X = np.asarray(instance.observational_data, dtype=float)
    d = instance.config.d
    n_obs = len(X)
    n_int = instance.config.n_int
    rng = np.random.default_rng(seed ^ (0xBADC0DE if policy == "greedy" else 0xBADF00D))
    adj, sep = pc_skeleton(X, .03, 2)
    directed, und = orient_vstructures(adj, sep)
    directed, und = meek_close(directed, und, d)
    obs_mean = X.mean(0)
    obs_sd = X.std(0, ddof=1)
    used = []
    for _ in range(instance.intervention_budget):
        target = choose_target(und, d, rng, set(used), policy)
        if target is None:
            break
        used.append(target)
        Xi = sample_interventional_data(instance.scm, target, 3.0, n_int, rng)
        mu, sd = Xi.mean(0), Xi.std(0, ddof=1)
        for pair in list(und):
            if target not in pair:
                continue
            other = pair[1] if pair[0] == target else pair[0]
            se = math.sqrt(obs_sd[other]**2 / n_obs + sd[other]**2 / n_int) + 1e-9
            z = abs(mu[other] - obs_mean[other]) / se
            und.remove(pair)
            if z > 2.2:
                directed.add((target, other))
            else:
                directed.add((other, target))
        directed, und = meek_close(directed, und, d)
        if not und:
            break

    clean = set()
    for a, b in sorted(directed):
        if not would_cycle(clean, a, b):
            clean.add((a, b))
    submission = GraphSubmission.from_edges(
        num_nodes=d,
        directed_edges=clean,
        undirected_edges=und,
        interventions_used=len(used),
    )
    score = score_submission(instance, submission)
    return {
        "directed_f1": score.directed_f1,
        "skeleton_f1": score.skeleton_f1,
        "dag_shd": score.dag_shd,
        "efficiency": score.efficiency,
        "interventions_used": len(used),
        "optimal_interventions": score.optimal_interventions,
        "remaining_undirected": len(und),
    }

def accepted_seeds(level_id, cfg, n=8):
    source = np.random.default_rng(2026092000 + level_id)
    out = []
    while len(out) < n:
        seed = int(source.integers(1, 2_147_483_647))
        try:
            build_benchmark_instance(cfg, np.random.default_rng(seed))
        except RuntimeError:
            continue
        out.append(seed)
    return out

def paired_stats(rows):
    g=np.array([r["directed_f1"] for r in rows if r["policy"]=="greedy"],float)
    q=np.array([r["directed_f1"] for r in rows if r["policy"]=="random"],float)
    d=g-q
    rng=np.random.default_rng(20260920)
    sims=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(20000)])
    return {
        "mean_delta":float(d.mean()),
        "bootstrap_95_ci":[float(np.quantile(sims,.025)),float(np.quantile(sims,.975))],
        "wilcoxon_one_sided_p":float(stats.wilcoxon(d,alternative="greater").pvalue),
        "wins":int(np.sum(d>0)),"ties":int(np.sum(d==0)),"losses":int(np.sum(d<0)),
    }

def main():
    rows = []
    for level, spec in LEVELS.items():
        cfg = make_v1_config(**spec)
        seeds = accepted_seeds(level, cfg, 8)
        for seed in seeds:
            instance = build_benchmark_instance(cfg, np.random.default_rng(seed))
            for policy in ("greedy", "random"):
                score = run_policy(instance, seed, policy)
                rows.append({"level": level, "seed": seed, "policy": policy, **score})
                print(level, seed, policy, score, flush=True)

    def mean(policy, key):
        vals = [r[key] for r in rows if r["policy"] == policy]
        return float(np.mean(vals))

    summary = {
        "benchmark": "Active-Causal-Discovery-Bench native package/API",
        "n_instances": 48,
        "methods": {
            p: {k: mean(p, k) for k in ["directed_f1","skeleton_f1","dag_shd","efficiency","interventions_used"]}
            for p in ("greedy","random")
        },
        "paired": paired_stats(rows),
        "rows": rows,
    }
    Path("native_acdb_results.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"},indent=2))

if __name__ == "__main__":
    main()
