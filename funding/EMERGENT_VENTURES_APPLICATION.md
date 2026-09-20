# Emergent Ventures Application Draft — THEORICA

## Project
**THEORICA — Autonomous Experimental Science**

## One-sentence description
THEORICA is an open research system testing whether an AI scientist can construct quantitative theories, choose informative causal interventions, and ultimately transfer from simulation into a real laboratory without human guidance.

## Why this matters
AI systems can already answer scientific questions and write code, but experimental science requires a harder loop: decide what to measure, distinguish competing explanations, detect when an instrument is untrustworthy, revise theories, and make predictions that survive observations the system has never seen.

If autonomous scientific agents are going to become useful research collaborators, they need to be evaluated on that loop rather than only on benchmark questions or optimization tasks.

## What exists today
This is not an idea-stage application.

### Native Active-Causal-Discovery-Bench
On ACDB's exact canonical 48-instance paper seed panel, THEORICA obtained:
- directed F1: **0.704**, versus **0.709** for ACDB's official PC-greedy baseline;
- interventions: **2.06**, versus **2.54**;
- ACDB efficiency: **0.824**, versus **0.730**.

THEORICA did not beat PC-greedy in graph accuracy and had worse DAG SHD. The useful result is the intervention-efficiency trade-off. The reduction in interventions was supported by a paired bootstrap CI of **[0.229, 0.750] fewer interventions/instance** and one-sided Wilcoxon **p=0.000536**.

The official PC-greedy values reproduced ACDB's published per-level results to rounding, providing a protocol check.

### Native DiscoverPhysics
A separate generic policy received raw experiment trajectories, spent exactly 15 experiments, froze a discovered force map, and was evaluated by DiscoverPhysics' native hidden-trajectory evaluator.

It passed the native trajectory threshold on:
- gravity,
- Yukawa,
- fractional gravity,
- extra dimensions,

and failed Coulomb.

That is **4/5 trajectory-axis passes on a deliberately limited compatible panel**, not an official leaderboard result. The Coulomb failure remains public.

### Open research record
THEORICA's public repository also contains:
- an earlier frozen hypothesis that failed;
- the resulting methodological pivot;
- compositional symbolic theory synthesis;
- multivariate theory construction;
- exact third-party package pins;
- raw/replayable benchmark workflows;
- explicit claim boundaries;
- a preregistered physical protocol written before official hardware data exist.

Repository:
https://github.com/sushxnthd/theorica

## The next experiment
The next question cannot be resolved in simulation:

> Does a scientific agent developed and frozen in software still behave scientifically when the apparatus has real sensor noise, drift, calibration uncertainty, backlash, saturation and hardware failure?

The first physical benchmark is **Rig 001**, a low-cost automated optics experiment.

The agent will control an unknown physical response through a narrow tool API, select its own measurements, construct a predictive theory, and then lose tool access before a randomized hidden physical holdout is collected.

The primary criterion is preregistered:
- physical holdout NRMSE <= 0.10;
- zero human intervention after START;
- zero hidden-validation leakage;
- all raw tool calls and detector samples retained.

A negative transfer result will be published too.

## Why funding is necessary
I am building THEORICA under a hard **zero-personal-spend** rule.

That rule is intentional. If the software evidence is not compelling enough to earn a small grant, sponsor, collaborator or in-kind laboratory access, I do not want to manufacture the appearance of traction by personally purchasing increasingly expensive equipment.

Funding therefore unlocks the first piece of evidence that cannot be generated for free: contact with a physical laboratory.

## Amount requested
**₹50,000**

The grant would fund:
- Rig 001 components and mechanical parts;
- redundant sensors/electronics so hardware failure does not invalidate the study;
- basic calibration/metrology materials;
- documentation and shipping/assembly contingencies.

The minimum viable single-rig build is approximately ₹25,000. Any unused funds would be retained for replicated physical trials or returned/handled according to grant requirements.

## What success looks like
Within the first funded phase:

1. build and characterize Rig 001;
2. freeze the agent and apparatus calibration;
3. execute the preregistered autonomous trials;
4. release raw traces, hardware documentation and analysis;
5. publish the positive or negative sim-to-real result;
6. invite independent laboratories to reproduce it.

If the transfer succeeds, the next step is a multi-domain physical benchmark rather than a one-off optics demonstration.

## Why me
I am pursuing this independently while still in high school. The strongest evidence of seriousness is not the size of the codebase; it is that the project has already discarded attractive claims when frozen evaluation contradicted them.

THEORICA began with the belief that a sophisticated active experiment policy would beat classical experimental design. It did not. External tasks then showed the deeper limitation was the hypothesis language itself. That failure led to compositional theory synthesis, native causal evaluation, and now native unfamiliar-physics evaluation.

I want to keep following the evidence even when it makes the project less convenient to pitch.

## Why Emergent Ventures
The project is a small, unusually leveraged bet: a modest physical-science grant tests a question that could matter far beyond one student project.

If autonomous AI scientists are going to be trusted in real laboratories, the field needs cheap, reproducible tests of whether they can survive imperfect instruments and unknown physical systems.

THEORICA is an attempt to make that test concrete.
