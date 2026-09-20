from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict
from .models import fit_all

@dataclass
class AgentRun:
    agent: str
    task: str
    seed: int
    observations: List[dict]
    selected_model: str
    selected_params: Dict[str, float]
    model_weights: Dict[str, float]
    suspected_faults: List[dict] = field(default_factory=list)
    stopped_early: bool = False

    def as_dict(self):
        return asdict(self)

def final_fit(observations):
    xs=[o["x_commanded"] for o in observations]
    ys=[o["y"] for o in observations]
    fits,weights=fit_all(xs,ys)
    return fits[0],weights
