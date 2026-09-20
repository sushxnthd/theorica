from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
from .environments.tasks import make_task, TASKS
from .agents.baselines import UniformAgent, RandomAgent
from .agents.falsification import FalsificationFirstAgent
from .evaluation.metrics import evaluate_run

AGENTS={
    "uniform":UniformAgent,
    "random":RandomAgent,
    "falsification":FalsificationFirstAgent,
}

def run_once(agent_name,task,seed=0,budget=30):
    env=make_task(task,seed)
    agent=AGENTS[agent_name]()
    run=agent.run(env,budget=budget)
    metrics=evaluate_run(env,run,budget=budget)
    return run,metrics

def run_suite(seeds=20,budget=30,tasks=None,agents=None):
    tasks=tasks or TASKS
    agents=agents or list(AGENTS)
    rows=[]
    for task in tasks:
        for seed in range(seeds):
            for agent in agents:
                _,m=run_once(agent,task,seed,budget)
                rows.append(m)
    return rows

def summarize(rows):
    groups=defaultdict(list)
    for r in rows:
        groups[(r["task"],r["agent"])].append(r)
    out=[]
    for (task,agent),rs in sorted(groups.items()):
        out.append({
            "task":task,
            "agent":agent,
            "runs":len(rs),
            "discovery_rate":sum(r["discovery_success"] for r in rs)/len(rs),
            "mean_nrmse":sum(r["nrmse"] for r in rs)/len(rs),
            "mean_experiments":sum(r["experiments_used"] for r in rs)/len(rs),
            "mean_prototype_score":sum(r["prototype_score"] for r in rs)/len(rs),
        })
    return out

def save_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2),encoding="utf-8")
