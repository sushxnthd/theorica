# THEORICA

**Autonomous Experimental Science**

THEORICA studies whether AI agents can form theories, choose causal interventions, and ultimately conduct real experiments rather than only answer scientific questions.

The project investigates three linked capabilities:

1. **Theory formation** - construct predictive symbolic laws beyond a fixed menu.
2. **Causal experimentation** - choose interventions that resolve hidden causal structure.
3. **Reality-Gap evaluation** - test whether a scientist developed in simulation transfers to unfamiliar physical apparatus under noise, drift, calibration error and failures.

## What happened scientifically

The project did not progress by one uninterrupted positive result. A frozen v0.2 evaluation falsified the hypothesis that our adaptive sampling heuristic reliably beats a strong uniform experimental design. External equations then exposed a different bottleneck: a fixed hypothesis language prevents discovery outside the menu. v0.3 replaced that menu with bounded compositional symbolic synthesis; v0.4 added multivariate theory construction and active causal discovery.

Current software evidence includes:
- fixed-menu Nguyen recovery: **2/8**;
- compositional Nguyen development recovery: **8/8**;
- frozen constant-perturbed transfer: **5/5**;
- multivariate synthesis: **70/70 runs below 0.01 NRMSE** on the included task suite;
- frozen 72-world causal holdout: directed F1 **0.588 vs 0.519** for random intervention targeting, while using **1.57 vs 2.06 interventions** on average;
- native ACDB package evaluation: **directed F1 0.647 vs 0.599** for paired random targeting across 48 independently generated official-configuration instances, while using **1.83 vs 2.90 interventions** on average.

These numbers have different evidence levels. Read `docs/CLAIM_BOUNDARIES.md` before citing them.

## Reproduce

```bash
python -m pip install -e .
pytest -q
```

See `NATIVE_ACDB_RESULT.md`, `docs/CLAIM_BOUNDARIES.md`, and the accompanying preprint source.

## Physical phase

The physical phase is preregistered before hardware data collection. The intended first experiment freezes the agent before connecting it to an automated optics rig. Human intervention after START invalidates the official run.
