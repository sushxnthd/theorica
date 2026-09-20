# External Replication & Collaboration Challenge

THEORICA is seeking **independent attempts to break, reproduce, or physically validate** the current results.

## Reproduce

### 1. Native ACDB
Run the pinned workflow:

`.github/workflows/native_acdb_replay.yml`

The published replay reproduces the native-package aggregate result exactly.

### 2. DiscoverPhysics
Run:

`.github/workflows/native_discoverphysics_forcemap.yml`

The adapter is deliberately generic: it receives simulator trajectories, spends a fixed 15-experiment budget, estimates a radial force map and scaling exponents, then freezes before native held-out trajectory evaluation.

## Ways to falsify the project

Useful negative results are welcome. In particular:

- find untouched scientific worlds where the symbolic grammar fails;
- construct causal instances where ambiguity-targeted intervention is systematically worse than random or classical design;
- test robustness to observation noise and instrument faults;
- identify leakage, benchmark contamination, or incorrect claim boundaries;
- reproduce results on a different machine/environment.

## Physical collaboration

The largest unresolved question is sim-to-real transfer. We are looking for a university/school/research lab willing to provide **in-kind access** to basic motorized optics/electronics or host Rig 001. No paid service is requested.

The physical protocol is preregistered in:

`docs/SIM_TO_REAL_PREREGISTRATION.md`

## Reporting

Please open an issue with:
- exact commit SHA;
- environment;
- commands;
- raw outputs;
- whether the result reproduced or failed;
- any deviations from the protocol.

A credible failure is as valuable as a replication.
