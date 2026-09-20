from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Callable, Dict, Any, Optional
import math, random

@dataclass
class FaultConfig:
    gaussian_noise_sd: float = 0.0
    heteroscedastic_noise: float = 0.0
    sensor_bias: float = 0.0
    sensor_gain: float = 1.0
    actuator_bias: float = 0.0
    actuator_scale: float = 1.0
    drift_per_measurement: float = 0.0
    additive_drift_per_measurement: float = 0.0
    outlier_probability: float = 0.0
    outlier_scale: float = 0.0
    saturation_low: Optional[float] = None
    saturation_high: Optional[float] = None
    hidden_time_sine_amplitude: float = 0.0
    hidden_time_sine_period: float = 17.0

@dataclass
class Observation:
    experiment_index: int
    x_commanded: float
    y: float
    saturated: bool
    repeated_setting: bool

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LabEnvironment:
    """One-dimensional controllable laboratory with hidden physics and hidden instrument faults."""
    def __init__(self, name: str, x_min: float, x_max: float, truth_name: str,
                 truth_fn: Callable[[float], float], faults: FaultConfig, seed: int = 0,
                 metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.truth_name = truth_name
        self.truth_fn = truth_fn
        self.faults = faults
        self.rng = random.Random(seed)
        self.seed = seed
        self.n = 0
        self._last_x = None
        self.metadata = metadata or {}

    def reset(self):
        self.rng = random.Random(self.seed)
        self.n = 0
        self._last_x = None

    def run_experiment(self, x_commanded: float) -> Observation:
        if not self.x_min <= x_commanded <= self.x_max:
            raise ValueError(f"x outside [{self.x_min}, {self.x_max}]")
        self.n += 1
        x_actual = self.faults.actuator_scale * x_commanded + self.faults.actuator_bias
        y_clean = self.truth_fn(x_actual)
        y = self.faults.sensor_gain * y_clean + self.faults.sensor_bias
        y *= 1.0 + self.faults.drift_per_measurement * (self.n - 1)
        y += self.faults.additive_drift_per_measurement * (self.n - 1)
        if self.faults.hidden_time_sine_amplitude:
            phase = 2 * math.pi * (self.n - 1) / self.faults.hidden_time_sine_period
            y += self.faults.hidden_time_sine_amplitude * math.sin(phase)
        sd = self.faults.gaussian_noise_sd + self.faults.heteroscedastic_noise * abs(y_clean)
        if sd:
            y += self.rng.gauss(0.0, sd)
        if self.rng.random() < self.faults.outlier_probability:
            y += self.rng.choice([-1.0, 1.0]) * self.faults.outlier_scale
        saturated = False
        if self.faults.saturation_low is not None and y < self.faults.saturation_low:
            y = self.faults.saturation_low
            saturated = True
        if self.faults.saturation_high is not None and y > self.faults.saturation_high:
            y = self.faults.saturation_high
            saturated = True
        repeated = self._last_x is not None and abs(self._last_x - x_commanded) < 1e-12
        self._last_x = float(x_commanded)
        return Observation(self.n, float(x_commanded), float(y), saturated, repeated)

    def noiseless_truth(self, x: float) -> float:
        return float(self.truth_fn(x))

    def public_spec(self) -> Dict[str, Any]:
        return {"name": self.name, "x_min": self.x_min, "x_max": self.x_max}
