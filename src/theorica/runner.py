from __future__ import annotations
from .adapters.nguyen_source import make_nguyen
from .agents.theory_synthesis import TheorySynthesizingScientist
from .evaluation.theory_metrics import evaluate_theory_run
from .causal import random_world, ActiveCausalScientist

def run_nguyen_once(task='nguyen-5', seed=0, budget=14):
    env=make_nguyen(task,seed)
    run=TheorySynthesizingScientist().run(env,budget=budget)
    return run,evaluate_theory_run(env,run)

def run_causal_once(nodes=6, edges=6, seed=123, budget=2, policy='greedy'):
    world=random_world(nodes,edges,seed,1.0)
    return ActiveCausalScientist(policy=policy).run(world,budget=budget,seed=seed+1000)
