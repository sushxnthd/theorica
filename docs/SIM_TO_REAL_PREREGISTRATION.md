# THEORICA Physical Phase — Preregistration v1.0

## Status
PRE-HARDWARE. This protocol must remain frozen before any official physical benchmark data are examined.

## Primary question
Can a scientific agent developed and selected without access to the physical rig autonomously infer a predictive model of an unfamiliar real apparatus under measurement imperfections?

## Rig 001
Motorized polarization/optics apparatus with LED source, fixed polarizer, motorized analyzer, independent angular feedback, photodiode/TIA/ADC detector and append-only host logs. Exact component substitutions are allowed before freeze if they preserve the instrument API; all substitutions must be documented.

## Agent information boundary
The agent receives only:
- tool/API schema and allowed control ranges;
- current observations returned by tools;
- experiment budget;
- task statement asking for a predictive quantitative model and uncertainty.

The agent does **not** receive:
- the name “Malus' law” or target equation;
- optical-axis calibration;
- hidden validation settings;
- calibration-fit parameters;
- human hints during the run.

## Human-intervention rule
After `START`, a human may stop the run only for electrical/mechanical safety. Any adjustment, restart, hint, data deletion, manual measurement choice or selective rerun invalidates the official trial and must be logged as invalid.

## Primary endpoint
Normalized root mean squared prediction error (NRMSE) on a fresh, randomized physical holdout sweep collected after the agent submits its final predictor.

Primary success threshold for B001:
- NRMSE <= 0.10; AND
- no human intervention; AND
- no hidden-validation leakage; AND
- all raw tool calls and raw detector samples retained.

## Secondary endpoints
- number of `measure()` calls;
- predictive interval coverage and width;
- correct identification of saturation/drift/offset in faulted episodes;
- replication behavior;
- calibration actions;
- wall-clock experimental time;
- model complexity;
- run-to-run variance.

## Planned task sequence
1. B001 clean but unknown optical response.
2. B002 unknown angular zero offset.
3. B003 source-intensity generalization.
4. B004 sparse physically induced outliers.
5. B005 gradual source drift.
6. B006 detector saturation.
7. B007 composite fault condition.

## Trial counts
- Engineering calibration trials are never benchmark trials.
- After hardware/calibration freeze: minimum 5 independent official runs per agent/task.
- Task order randomized.
- Failed runs remain in analysis unless invalidated by preregistered technical-invalidity rules.

## Baselines
- uniform space-filling design with the same estimator;
- random experiment selection;
- frozen THEORICA agent;
- at least one frontier-model agent when provider access is available.

## Holdout generation
For each official run, after model submission, collect at least 24 physical holdout settings in randomized order. Include high-slope and low-transmission regions, plus unseen source settings where applicable. The agent is disconnected from tool access before holdout collection.

## Statistics
Report all run-level values. For paired comparisons use identical hidden task conditions where possible. Report mean/median, bootstrap 95% confidence intervals, and paired nonparametric tests. No post-hoc removal of difficult worlds/runs.

## Sim-to-real freeze rule
The official physical campaign references a SHA-256 manifest of:
- agent source;
- model grammar;
- causal/intervention policy;
- prompts;
- evaluation code;
- this preregistration.

Any algorithmic code change creates a new experimental version and may not be retroactively substituted into the frozen campaign.

## Publication rule
The result will be reported whether it succeeds or fails. A failure to transfer is a valid result and will not trigger threshold tuning against the same physical holdout.
