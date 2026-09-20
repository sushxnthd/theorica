from __future__ import annotations
import numpy as np
from ..agents.symbolic_synthesis import CompositionalTheorySynthesizer

def evaluate_theory_run(env, run, holdout_n: int = 601):
    obs = run.observations
    synth = CompositionalTheorySynthesizer()
    theory, candidates = synth.fit(
        [o["x_commanded"] for o in obs], [o["y"] for o in obs]
    )
    grid = np.linspace(env.x_min, env.x_max, holdout_n)
    truth = np.array([env.noiseless_truth(float(x)) for x in grid], dtype=float)
    pred = theory.predict(grid)
    if np.any(~np.isfinite(pred)):
        rmse = float("inf")
        nrmse = float("inf")
    else:
        rmse = float(np.sqrt(np.mean((pred - truth) ** 2)))
        span = max(float(np.quantile(truth, .95) - np.quantile(truth, .05)), 1e-9)
        nrmse = rmse / span
    return {
        "task": env.name,
        "agent": run.agent,
        "seed": run.seed,
        "selected_model": "compositional_symbolic",
        "expression": theory.expression,
        "nrmse": nrmse,
        "rmse": rmse,
        "discovery_success": bool(nrmse < .08),
        "high_precision_success": bool(nrmse < .01),
        "experiments_used": len(obs),
        "candidate_count": len(candidates),
        "theory_complexity": theory.complexity,
    }
