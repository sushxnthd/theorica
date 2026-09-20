from __future__ import annotations
import random
import numpy as np
from .common import AgentRun, final_fit

class UniformAgent:
    name="uniform"
    def run(self, env, budget=30):
        obs=[]
        for x in np.linspace(env.x_min, env.x_max, budget):
            obs.append(env.run_experiment(float(x)).as_dict())
        fit,weights=final_fit(obs)
        return AgentRun(self.name,env.name,env.seed,obs,fit.name,fit.params,weights,[],False)

class RandomAgent:
    name="random"
    def run(self, env, budget=30):
        rng=random.Random(env.seed+991)
        obs=[]
        for _ in range(budget):
            x=rng.uniform(env.x_min,env.x_max)
            obs.append(env.run_experiment(x).as_dict())
        fit,weights=final_fit(obs)
        return AgentRun(self.name,env.name,env.seed,obs,fit.name,fit.params,weights,[],False)
