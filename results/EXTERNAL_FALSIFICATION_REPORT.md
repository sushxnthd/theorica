# External Falsification Audit: THEORICA Equational-Theory Discovery

**Audit date:** 25 September 2026  
**Purpose:** attempt to falsify the claim that THEORICA's current
experiment -> equational theory -> theorem routing -> representation-aware
experiment loop is a field-level methodological contribution.

This document is intentionally adversarial. It records prior art that invalidates
narrower novelty claims, stronger published baselines, an external benchmark,
and the remaining claim after those attacks.

## Executive verdict

The external audit **kills several broad novelty claims**:

1. Discovering algebraic equations from samples is not new.
2. Testing associativity/group axioms efficiently is not new.
3. Recovering algebraic structure from partially observed operation tables is not
   new.
4. Learning latent algebraic representations is not new.
5. Active experiment selection for symbolic/model discovery is not new.
6. Fitting additive/quasi-arithmetic generators is not new.

The narrower integration hypothesis survived the priority search:

> **An autonomous experimental system mines empirical equations from an
> initially unknown black-box operation, uses the discovered equational
> structure to decide which representation theorem is applicable, verifies
> additional theorem premises with abstention, learns the theorem-induced latent
> representation, and then changes its subsequent experiment-design objective to
> maximize information in that representation.**

Two separate broad literature searches did not identify an exact predecessor
implementing that full chain. This is **evidence of a plausible integration
novelty, not proof of priority**.

The external benchmark also shows that THEORICA's generic equation miner
transfers beyond self-generated continuous worlds, but it is dramatically less
query-efficient than a named-template tester. Therefore query efficiency of
generic identity mining is explicitly **not** a supported novelty claim.

## 1. Priority search: claims that did not survive

### 1.1 Sample-to-equation discovery predates THEORICA by decades

Barzdin & Barzdin, *Rapid Constructions of Algebraic Axioms From Samples*
(Theoretical Computer Science, 1991), explicitly studies reliable algebraic
axioms inferred from samples and gives an effective enumeration algorithm.

QuickSpec (Claessen, Smallbone & Hughes, 2010) generates terms and uses random
testing to conjecture equational specifications. RoughSpec (Einarsdottir,
Smallbone & Johansson, 2020) adds templates for laws such as associativity and
distributivity. Speculate and related theory-exploration systems extend this
line further.

**Consequence:** THEORICA's bounded generic term-equivalence miner is not, by
itself, a new research idea.

### 1.2 Query-efficient identity/property testing is established

Rajagopalan & Schulman developed randomized subcubic/near-quadratic identity
verification, including associativity. Later work studies testing whether an
operation is close to a group and more efficient verification of group tables.
Recent work continues to improve algorithms for associativity, distributivity,
groups, rings, and Abelian-group property testing.

**Consequence:** THEORICA must not claim novelty for testing algebraic premises
with few oracle calls.

### 1.3 Black-box operation recovery is established

Zumbragel, Maze & Rosenthal (2008) study recovery of operation tables of black
box groups and rings from chosen pair queries and give substantially subquadratic
query results under algebraic assumptions.

**Consequence:** active querying of an unknown operation table is not new.

### 1.4 Active learning in group-structured environments is established

Bartok, Szepesvari & Zilles (2008) study agents that actively learn deterministic
group-structured environments by experimentation with generators.

**Consequence:** combining algebraic structure and active interaction is not new
in the broad sense.

### 1.5 Strong differentiable algebraic-structure discovery already exists

Huh, *Discovering Group Structures via Unitary Representation Learning*
(ICLR 2025), introduces HyperCube, a representation-theoretic tensor
factorization for Binary Operation Completion. It recovers finite group
operations and learned unitary representations from partial observations, with
strong sample efficiency. Follow-up work strengthens its theoretical footing.

Dang-Nhu, Annabi & Argentieri (ICLR 2026) also show unsupervised discovery of
symmetry group decompositions from an embodied agent's interaction data.

**Consequence:** "automatic algebraic representation discovery" is not a
defensible field-first claim for THEORICA.

### 1.6 Generator fitting and theorem mathematics are established

Aczel-type representation results for continuous associative operations and
Kolmogorov-Nagumo/quasi-arithmetic mean characterizations are classical.
Functional Networks and aggregation-function regression use these structures
for learning, including generator fitting when the representation family is
specified.

**Consequence:** THEORICA does not claim the representation theorems or latent
generator estimators as new.

### 1.7 Active symbolic/scientific model discovery is established

QUOSR, Bayesian experimental design for symbolic discovery, active symbolic
regression, active Koopman learning, and closed-loop AI-scientist systems all
choose measurements to improve model discovery.

**Consequence:** active experiment selection alone is not new.

## 2. What the priority search did *not* find

The first dedicated literature review covered continuous black-box operation
learning, functional equations, aggregation functions, theory exploration,
symbolic regression, active design, and theorem-guided discovery.

A second hostile search expanded the scope to **139 papers**, including older
sample-to-axiom work, black-box groups and rings, group property testing,
operation-table completion, active group-environment learning, inductive
equational logic programming, 2025-2026 group-discovery work, and automated
scientific agents.

Neither search surfaced a system that demonstrates all of:

1. start from an operation whose algebraic family is not supplied;
2. infer candidate equations from observations rather than only test one
   prespecified property;
3. use those equations to select among mathematical representation theorems;
4. verify the additional premises of the selected theorem and abstain when they
   fail;
5. estimate the theorem-induced latent representation; and
6. choose subsequent experiments specifically to reduce uncertainty in that
   representation.

This negative search result does not establish priority. Older literature can be
missed, terminology differs across fields, and some relevant sources lack
machine-readable full text.

## 3. External benchmark: published Binary Operation Completion tasks

To remove the self-authored-world objection, we constructed an external audit
from the operation definitions in Appendix B of Huh (ICLR 2025), adopted from
Power et al. (2022).

The audit includes 11 total binary operations:

- modular addition;
- modular subtraction;
- conditional division/subtraction;
- three quadratic operations;
- two cubic operations;
- S5 composition;
- S5 conjugation;
- S5 `aba`.

The published division task is excluded because `b=0` is outside its stated
domain, so it is not a total binary operation on one carrier.

For each task we computed full-table ground truth for eight identities:

- commutativity;
- associativity;
- idempotence;
- left self-distributivity;
- right self-distributivity;
- left alternativity;
- right alternativity;
- flexibility.

### Generic mining result

The generic miner enumerates **471** terms over `x,y,z` with at most three
applications of the unknown operation. It receives 32 random assignments and
does not receive the eight identity templates as its search space.

| Metric | Result |
|---|---:|
| Published external tasks | 11 |
| Identity truth labels | 88 |
| Correct labels | **88/88** |
| Accuracy | **100%** |
| Operation calls per task | **14,976** |

Notably, on the published S5 conjugation operation it discovers:

- idempotence;
- left self-distributivity;
- flexibility;

while rejecting associativity and the other tested laws. The
left-self-distributive structure is characteristic of conjugation-style
operations and was not manually injected as the expected family.

Clean external workflow:
https://github.com/sushxnthd/theorica/actions/runs/36124350169

Artifact:
https://github.com/sushxnthd/theorica/actions/runs/36124350169/artifacts/10859250890

### Hostile named-template baseline

We also supplied a cheaper tester with the eight identity templates **in
advance**, analogous in spirit to template-guided theory exploration. Each
property stops on the first sampled counterexample.

Across 100 independent repeats:

| Metric | Result |
|---|---:|
| Repeats with all 88 labels correct | **100/100** |
| Mean calls per external task | **65.58** |
| Maximum repeat-average calls/task | **67.27** |
| Generic-miner calls/task | 14,976 |

Thus the template tester uses roughly **228x fewer calls** on this panel.

This is an important negative result. Generic equational discovery transfers to
external tasks, but if the scientist already knows which identities matter,
generic enumeration is profoundly inefficient.

## 4. Strong published baseline: clean-room HyperCube reproduction

HyperCube is the strongest directly relevant published method we identified for
finite algebraic operation completion.

We implemented the architecture and regularizer printed in Appendix A of the
ICLR 2025 paper in a fresh script. This is **not official HyperCube code**.
The implementation follows the printed tensor product, regularizer,
initialization, full-batch SGD settings, and epsilon=0.1 small-task setting, but
uses fixed epsilon for 500 steps rather than the paper's adaptive epsilon
scheduler.

Each result below averages ten independent 60%-training splits/initializations.

| External BOC task | H-regularized | L2 | Unregularized |
|---|---:|---:|---:|
| C6 addition | **1.000** | 0.300 | 0.129 |
| C6 subtraction | **1.000** | 0.464 | 0.107 |
| C6 squared addition | **0.893** | 0.707 | 0.286 |
| S3 composition | **1.000** | 0.893 | 0.150 |

The exact paper reports recovery of these small operations and uses an epsilon
scheduler, so the 0.893 squared-addition result is recorded as a limitation of
our minimal clean-room replication, not as a contradiction of the paper.

Clean workflow:
https://github.com/sushxnthd/theorica/actions/runs/36124253425

Artifact:
https://github.com/sushxnthd/theorica/actions/runs/36124253425/artifacts/10859660793

### What HyperCube falsifies

HyperCube demonstrates that a representation-specific algebraic inductive bias
can recover operation tables far more directly than THEORICA's generic
equational search.

THEORICA therefore cannot claim:

- first automatic algebraic-structure discovery from partial operations;
- first learned group representation from operation data;
- first strong sample-efficient Binary Operation Completion method;
- superiority to representation-specific methods on their native problem.

The proposed distinction is that HyperCube commits to a group-representation
inductive bias before observing the data, whereas THEORICA's target methodology
uses observed equations to decide which representation family to invoke.

## 5. Independent reproduction/review status

A genuinely independent researcher review cannot be manufactured by the
project author or by an AI acting for the project.

What was completed instead:

- two separate literature-search agents were given hostile, self-contained
  novelty-audit goals;
- a third-party published baseline was reimplemented from the paper rather than
  from THEORICA code;
- both external experiments were rerun from clean GitHub Actions environments
  and preserved as artifacts;
- negative findings are retained publicly.

This improves independence of **execution and literature search**, but it is not
equivalent to independent human peer review.

The correct next external step is to give the reproduction bundle to researchers
who were not involved in THEORICA and ask them specifically to find a
predecessor, break the benchmark, or reproduce the results.

## 6. Final claim after falsification

### Claims rejected by this audit

- "THEORICA invented algebraic axiom discovery from samples."
- "THEORICA invented equational theory exploration."
- "THEORICA invented efficient identity testing."
- "THEORICA invented black-box operation recovery."
- "THEORICA invented group-structure representation learning."
- "THEORICA invented active scientific/symbolic experiment design."
- "THEORICA's generic miner is query-efficient."

### Claim that survived the audit

The strongest remaining hypothesis is:

> **Empirically discovered equational structure can act as a model-class routing
> layer for autonomous experimentation: a scientist can discover candidate laws
> of composition, use them to choose and falsify the premises of a representation
> theorem, then perform subsequent experiment design in the theorem-induced
> latent representation rather than in the raw observation space.**

The existing internal frozen studies support the full loop on continuous
synthetic operations. The new external BOC audit supports transfer of the
equational-discovery stage to published operations.

### What remains unproven

The full loop has **not yet been demonstrated end-to-end on a third-party
benchmark**. The external BOC audit validates structure discovery, while the
published HyperCube comparison validates that strong specialized alternatives
exist. This is the main remaining scientific weakness.

Therefore, after hostile external falsification, the correct status is:

**plausibly novel integrated methodology with reproducible external component
validation, but not yet a proven field-level breakthrough.**

A field-level claim should wait for an external benchmark where THEORICA must
discover the structure, route itself to the representation, and use that
representation to outperform representation-agnostic active baselines without
being told the algebraic family in advance.


## 7. External end-to-end routing on published BOC operations

The first external audit validated only the equation-mining stage. We therefore
froze a second experiment that evaluates the **full surviving loop** on the same
published Binary Operation Completion task family.

For every task THEORICA receives only black-box pair queries. It is not told
which operations are groups.

The procedure:

1. generically evaluates 66 terms over x,y,z with at most two uses of F;
2. infers whether associativity is empirically supported from the term
   signatures;
3. only for associative candidates, searches for and validates a two-sided
   identity;
4. actively acquires right-multiplication actions for generators;
5. checks that the learned actions are bijections;
6. constructs words for the entire carrier under learned generator actions and
   their inverses;
7. reconstructs the complete multiplication table **without further table
   queries**;
8. otherwise abstains.

Ground truth is consulted only after discovery for scoring.

The frozen clean run used **100 repetitions of all 11 external tasks**.

| Metric | Result |
|---|---:|
| Task/repeat cases | **1,100** |
| Correct route decisions | **1,100/1,100** |
| True-group cases | 200 |
| True-group cases accepted | **200/200** |
| Non-group cases | 900 |
| Non-group cases abstained | **900/900** |
| Exact full-table reconstructions | **200/200 accepted cases** |
| Fixed generic-mining cost | 756 oracle calls/task |

For modular addition on 97 elements, complete reconstruction used **991**
oracle calls on every run, equal to **10.53%** of the 9,409-entry table.

For S5 composition on 120 elements, complete reconstruction used mean
**1,221.8** calls (median **1,157**, range **1,157–1,397**), equal to
**8.48%** of the 14,400-entry table on average. The learned right-regular
representation used 2.54 generators on average.

Clean workflow:
https://github.com/sushxnthd/theorica/actions/runs/36125334978

Artifact:
https://github.com/sushxnthd/theorica/actions/runs/36125334978/artifacts/10858793652

### Hostile comparison with HyperCube-SE

This end-to-end result closes the earlier external-validation gap, but it does
**not** establish sample-efficiency superiority. Huh (ICLR 2025) reports that
HyperCube-SE requires approximately **5%** of the operation table to attain
perfect test accuracy on group operations when the group-representation bias is
built into the model in advance. THEORICA's total costs here are approximately
8.5–10.5% of the full table because they include the cost of first deciding
whether the group representation is appropriate.

That distinction is the scientific point being tested, not a leaderboard win:
HyperCube-SE is a stronger specialized learner once the useful algebraic bias is
chosen; THEORICA pays extra measurements to infer whether that bias should be
used at all.

### Revised external status

The statement in the previous section that the full loop had not yet been
demonstrated on a third-party benchmark is superseded by this frozen run.

The externally supported claim is now:

> On the published BOC operation family, a generic empirical equation-mining
> stage can route previously unlabeled tasks into or away from a group
> representation, and on routed group tasks a representation-directed
> acquisition procedure can exactly reconstruct the hidden operation while
> abstaining on the tested non-group operations.

This materially strengthens the integration hypothesis. It still does **not**
prove field-first priority, universal algebraic routing, or superiority to
specialized algebraic learners.
