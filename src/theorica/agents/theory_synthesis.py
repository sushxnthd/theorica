from __future__ import annotations
import numpy as np
from .common import AgentRun
from .symbolic_synthesis import CompositionalTheorySynthesizer


class TheorySynthesizingScientist:
    """Scientist that invents sparse symbolic theories from a compositional grammar."""
    name = "theory_synthesis"

    def __init__(self, *, adaptive: bool = True, name: str | None = None,
                 synthesizer: CompositionalTheorySynthesizer | None = None):
        self.adaptive = bool(adaptive)
        self.name = name or ("theory_synthesis" if adaptive else "theory_synthesis_uniform")
        self.synthesizer = synthesizer or CompositionalTheorySynthesizer()

    @staticmethod
    def _largest_gap(env, obs):
        xs = sorted({float(o["x_commanded"]) for o in obs})
        points = [env.x_min] + xs + [env.x_max]
        gap, midpoint = max(
            ((points[i + 1] - points[i], (points[i + 1] + points[i]) / 2.0) for i in range(len(points) - 1)),
            key=lambda item: item[0],
        )
        return float(midpoint)

    def _choose_discriminating(self, env, obs, candidates):
        if not self.adaptive or len(candidates) < 2:
            return self._largest_gap(env, obs)
        grid = np.linspace(env.x_min, env.x_max, 401)
        top = candidates[: min(5, len(candidates))]
        predictions = np.vstack([t.predict(grid) for t in top])
        disagreement = np.nanstd(predictions, axis=0)
        xs = np.asarray([o["x_commanded"] for o in obs], dtype=float)
        span = max(env.x_max - env.x_min, 1e-12)
        nearest = np.min(np.abs(grid[:, None] - xs[None, :]), axis=1) / span
        novelty = np.clip(nearest / 0.08, 0.05, 1.0)
        score = np.nan_to_num(disagreement, nan=0.0, posinf=0.0, neginf=0.0) * novelty
        if not np.any(score > 0):
            return self._largest_gap(env, obs)
        return float(grid[int(np.argmax(score))])

    def run(self, env, budget: int = 14):
        if budget < 6:
            raise ValueError("theory synthesis requires a budget of at least 6")
        obs = []
        initial_fractions = [0.0, 1.0, 0.5, 0.21, 0.72, 0.37]
        for fraction in initial_fractions:
            x = env.x_min + fraction * (env.x_max - env.x_min)
            obs.append(env.run_experiment(x).as_dict())
            if len(obs) >= budget:
                break

        history = []
        while len(obs) < budget:
            theory, candidates = self.synthesizer.fit(
                [o["x_commanded"] for o in obs], [o["y"] for o in obs]
            )
            history.append({"n": len(obs), "expression": theory.expression, "bic": theory.bic})
            adaptive_index = len(obs) - len(initial_fractions)
            if self.adaptive and adaptive_index % 3 != 2:
                x = self._choose_discriminating(env, obs, candidates)
            else:
                x = self._largest_gap(env, obs)
            obs.append(env.run_experiment(x).as_dict())

        theory, candidates = self.synthesizer.fit(
            [o["x_commanded"] for o in obs], [o["y"] for o in obs]
        )
        selected_params = {
            "expression": theory.expression,
            "term_expressions": theory.term_expressions,
            "coefficients": theory.coefficients,
            "intercept": theory.intercept,
            "bic": theory.bic,
            "complexity": theory.complexity,
            "candidate_count": len(candidates),
            "history": history,
        }
        weights = {f"candidate_{i}": float(np.exp(-0.5 * max(0.0, c.bic - theory.bic))) for i, c in enumerate(candidates[:6])}
        total = sum(weights.values()) or 1.0
        weights = {k: v / total for k, v in weights.items()}
        return AgentRun(
            self.name, env.name, env.seed, obs, "compositional_symbolic", selected_params,
            weights, suspected_faults=[], stopped_early=False,
        )
