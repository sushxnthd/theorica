from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from theorica.agents.representation_closure import (
    WeakAnnihilatorSynthesizer,
    AnnihilatorTheory,
)
from theorica.agents.symbolic_synthesis import (
    CompositionalTheorySynthesizer,
    SynthesizedTheory,
)


@dataclass(frozen=True)
class FalsificationStep:
    step: int
    x: float
    y: float
    explicit_prediction: float
    operator_prediction: float
    log_e_increment: float
    log_e_value: float
    rejected: bool


@dataclass
class FalsificationResult:
    mode: str
    theory: SynthesizedTheory | AnnihilatorTheory
    rejected_at: int | None
    log_e_value: float
    alpha: float
    adequacy_tolerance: float
    probes: list[FalsificationStep]

    def predict(self, xs):
        return self.theory.predict(xs)


class AnytimeRepresentationFalsifier:
    """Counterexample-guided, anytime-valid theory falsification.

    The current explicit theory f and an alternative operator theory g are frozen
    before challenge experiments. At each step, THEORICA chooses the available x
    where |f(x)-g(x)| is largest, obtains a new observation, and updates an
    e-process.

    For Gaussian sensor noise with known sigma and the composite adequacy null

        H0(x): |E[Y|x] - f(x)| <= epsilon,

    the one-step e-value is

        N(y; g(x), sigma^2)
        -------------------
        sup_{|mu-f(x)|<=epsilon} N(y; mu, sigma^2).

    Its conditional expectation is at most one for every null mean in the
    adequacy band. Products therefore form an e-process under adaptive,
    predictable experiment selection. Ville's inequality gives

        P_H0(sup_t E_t >= 1/alpha) <= alpha.

    epsilon=0 recovers the simple likelihood-ratio martingale. If g is the true
    mean in that special case, maximizing |f(x)-g(x)| maximizes the expected
    one-step log-evidence, equal to (f(x)-g(x))^2/(2 sigma^2).

    This is a statistical falsification rule for a frozen theory, not a proof
    that an entire symbolic grammar is false.
    """

    def __init__(
        self,
        *,
        alpha: float = 0.01,
        adequacy_tolerance_sigma: float = 3.0,
        adequacy_tolerance_fraction: float = 0.003,
        symbolic_trial_width: int = 200,
        operator_top_k: int = 40,
    ):
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be in (0,1)")
        self.alpha = float(alpha)
        self.adequacy_tolerance_sigma = float(adequacy_tolerance_sigma)
        self.adequacy_tolerance_fraction = float(adequacy_tolerance_fraction)
        self.symbolic_trial_width = int(symbolic_trial_width)
        self.operator = WeakAnnihilatorSynthesizer(top_k=operator_top_k)

    def _fit_frozen_pair(self, x, y, bounds):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        explicit, _ = CompositionalTheorySynthesizer(
            trial_width=self.symbolic_trial_width
        ).fit(x, y)

        qlo, qhi = np.quantile(x, [0.18, 0.82])
        inner = (x >= qlo) & (x <= qhi)
        candidate = self.operator.choose_by_forecast(
            x[inner], y[inner], x[~inner], y[~inner], bounds
        )
        if candidate is None:
            return explicit, None, None
        operator_theory = self.operator.finalize(candidate, x, y, bounds)
        return explicit, candidate, operator_theory

    @staticmethod
    def _scalar_predict(theory, x: float) -> float:
        value = np.asarray(theory.predict(np.array([x], dtype=float)), dtype=float)
        if value.size != 1 or not np.isfinite(value[0]):
            return float("nan")
        return float(value[0])

    @staticmethod
    def _log_e_increment(y, f, g, sigma, epsilon):
        if not all(np.isfinite(v) for v in (y, f, g, sigma, epsilon)):
            return float("-inf")
        if sigma <= 0:
            raise ValueError("noise sigma must be positive")
        distance_to_null_band = max(abs(y - f) - epsilon, 0.0)
        return float(
            (distance_to_null_band**2 - (y - g) ** 2) / (2.0 * sigma**2)
        )

    def run(
        self,
        xs,
        ys,
        *,
        bounds,
        probe_pool,
        observe: Callable[[float], float],
        noise_sigma: float,
        budget: int = 8,
        policy: str = "disagreement",
        random_seed: int = 0,
    ):
        x0 = np.asarray(xs, dtype=float)
        y0 = np.asarray(ys, dtype=float)
        bounds = (float(bounds[0]), float(bounds[1]))
        pool = np.unique(np.asarray(probe_pool, dtype=float))
        pool = pool[(pool >= bounds[0]) & (pool <= bounds[1])]
        if len(pool) == 0:
            raise ValueError("probe pool is empty")
        if budget < 1:
            raise ValueError("budget must be positive")

        explicit, candidate, operator_theory = self._fit_frozen_pair(
            x0, y0, bounds
        )
        if candidate is None or operator_theory is None:
            return FalsificationResult(
                mode="explicit",
                theory=explicit,
                rejected_at=None,
                log_e_value=float("-inf"),
                alpha=self.alpha,
                adequacy_tolerance=float("nan"),
                probes=[],
            )

        signal_scale = max(
            float(np.quantile(y0, 0.95) - np.quantile(y0, 0.05)),
            float(np.std(y0)),
            1e-9,
        )
        epsilon = max(
            self.adequacy_tolerance_sigma * float(noise_sigma),
            self.adequacy_tolerance_fraction * signal_scale,
        )

        f_pool = np.asarray(explicit.predict(pool), dtype=float)
        g_pool = np.asarray(operator_theory.predict(pool), dtype=float)
        valid = np.isfinite(f_pool) & np.isfinite(g_pool)
        pool = pool[valid]
        f_pool = f_pool[valid]
        g_pool = g_pool[valid]
        if len(pool) == 0:
            return FalsificationResult(
                mode="explicit",
                theory=explicit,
                rejected_at=None,
                log_e_value=float("-inf"),
                alpha=self.alpha,
                adequacy_tolerance=epsilon,
                probes=[],
            )

        rng = np.random.default_rng(random_seed)
        used = np.zeros(len(pool), dtype=bool)
        log_e = 0.0
        threshold = math.log(1.0 / self.alpha)
        steps: list[FalsificationStep] = []
        observed_x = []
        observed_y = []
        rejected_at = None

        if policy == "uniform":
            order = np.argsort(pool)
            target_positions = np.linspace(0, len(order) - 1, min(budget, len(order)))
            fixed_order = order[np.unique(np.round(target_positions).astype(int))]
            fixed_order = list(map(int, fixed_order))
        elif policy == "random":
            fixed_order = list(map(int, rng.permutation(len(pool))))
        elif policy == "disagreement":
            fixed_order = []
        else:
            raise ValueError("policy must be disagreement, uniform, or random")

        for step in range(1, min(budget, len(pool)) + 1):
            if policy == "disagreement":
                score = np.abs(f_pool - g_pool)
                score[used] = -np.inf
                idx = int(np.argmax(score))
            else:
                remaining = [idx for idx in fixed_order if not used[idx]]
                if not remaining:
                    break
                idx = int(remaining[0])

            used[idx] = True
            x = float(pool[idx])
            y = float(observe(x))
            f = float(f_pool[idx])
            g = float(g_pool[idx])
            increment = self._log_e_increment(
                y, f, g, float(noise_sigma), epsilon
            )
            if np.isfinite(increment):
                log_e += increment
            else:
                log_e = float("-inf")

            rejected = bool(log_e >= threshold)
            steps.append(
                FalsificationStep(
                    step=step,
                    x=x,
                    y=y,
                    explicit_prediction=f,
                    operator_prediction=g,
                    log_e_increment=increment,
                    log_e_value=log_e,
                    rejected=rejected,
                )
            )
            observed_x.append(x)
            observed_y.append(y)
            if rejected:
                rejected_at = step
                break

        if rejected_at is not None:
            all_x = np.concatenate([x0, np.asarray(observed_x, dtype=float)])
            all_y = np.concatenate([y0, np.asarray(observed_y, dtype=float)])
            final = self.operator.finalize(candidate, all_x, all_y, bounds)
            mode = "operator"
        else:
            all_x = np.concatenate([x0, np.asarray(observed_x, dtype=float)])
            all_y = np.concatenate([y0, np.asarray(observed_y, dtype=float)])
            final, _ = CompositionalTheorySynthesizer(
                trial_width=self.symbolic_trial_width
            ).fit(all_x, all_y)
            mode = "explicit"

        return FalsificationResult(
            mode=mode,
            theory=final,
            rejected_at=rejected_at,
            log_e_value=float(log_e),
            alpha=self.alpha,
            adequacy_tolerance=float(epsilon),
            probes=steps,
        )
