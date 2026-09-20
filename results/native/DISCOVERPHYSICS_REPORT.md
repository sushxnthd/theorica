# Native DiscoverPhysics trajectory evaluation

## Status

THEORICA was executed against the native DiscoverPhysics package using a **generic 15-experiment force-map identification policy**.

GitHub Actions run: `35508351675`

Pinned DiscoverPhysics commit:
`33b7fa9df96de9c35744efd181ca7e5a8dd60ad5`

The discovery adapter only accessed:
- the public experiment API;
- returned particle trajectories;
- the native trajectory evaluator after the law was frozen.

It did **not** read `true_law`, optimal explanations, explanation rubrics, or evaluator holdout trajectories during discovery.

## Protocol

Selected panel: five static, two-particle worlds sharing the same public experiment interface:
- gravity
- yukawa
- fractional
- coulomb_easy
- extra_dimensions

Each world received exactly:
- 5 source/inertia scaling probes;
- 10 radial probes;
- **15 experiments total**.

The same generic algorithm was used for every world. It estimates source/inertia exponents from scaling interventions, builds a non-parametric radial acceleration map from trajectory data, freezes it, and then predicts native held-out trajectories with its own integrator.

## Results

| World | Native mean particle MSE | Benchmark trajectory pass |
|---|---:|---:|
| gravity | **3.91e-10** | **PASS** |
| yukawa | **2.89e-05** | **PASS** |
| fractional | **3.39e-12** | **PASS** |
| coulomb_easy | 5.39e-01 | FAIL |
| extra_dimensions | **1.61e-05** | **PASS** |

[
\boxed{4/5\text{ native trajectory-evaluator passes}}
]

The benchmark's native trajectory criterion is mean particle MSE < 0.01.

The failed Coulomb result is retained. No Coulomb-specific retuning was performed before publishing this report.

## Scientifically useful recovered structure

Without being told the hidden laws, the scaling probes estimated approximately:

- gravity: (p_1^{1.000}p_2^{-1.000})
- Yukawa: (p_1^{1.000}p_2^{-1.000})
- fractional: (p_1^{1.000}p_2^{-1.000})
- Coulomb: (p_1^{1.000}p_2^{1.000})
- extra dimensions: (p_1^{1.000}p_2^{-1.000})

This demonstrates that the intervention policy can recover different parameter roles from trajectories rather than assuming one universal scaling law.

## Claim boundary

Supported:
> On a selected panel of five compatible static two-particle DiscoverPhysics worlds, a generic 15-experiment THEORICA system-identification policy passed the benchmark's native held-out trajectory criterion on four worlds.

Not supported:
- official DiscoverPhysics leaderboard placement;
- 80% overall DiscoverPhysics pass rate;
- comparison against frontier LLMs;
- explanation-score pass;
- general performance on the benchmark's multi-particle or time-varying worlds.

DiscoverPhysics' official full trial pass combines trajectory accuracy with a separate LLM-judged explanation metric. This result evaluates the native trajectory axis only.
