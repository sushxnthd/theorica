# INSEF 2026-27 — Judging Package

Project: **THEORICA: Query-Efficient Reconstruction of Hidden Algebraic Systems from Translation Actions**
Category: Senior — Computer Science & Engineering
Status: evidence-bounded; prospective larger-nongroup outcomes must not be quoted until formally opened.

## 20-second explanation

Suppose a hidden operation has an n×n table. Reading it directly costs n² queries. THEORICA asks whether symmetry lets us infer most cells instead. It learns selected rows as permutations, discovers the transformation system they generate, identifies unseen rows from a small set of diagnostic points, and then actively tries to falsify its own reconstruction. If a check fails, the counterexample is used to expand and repair the model.

## 2–3 minute judge pitch

A finite binary operation can be represented by an n×n table. If the operation is hidden behind a query interface, the obvious exact strategy is to read all n² cells. My question was: when the rows themselves have internal symmetry, can we reconstruct the complete table without observing most of it?

THEORICA treats each row as a transformation. When those transformations are permutations, a few observed rows can generate a larger permutation action. The algorithm finds a small base: a set of points whose images act like a fingerprint for each transformation. Instead of reading every unseen row completely, THEORICA probes enough information to identify its transformation from that action and infers the remaining cells.

But structural inference can be wrong. An earlier frozen version exposed exactly that problem. It failed 48 of 345 eligible cases, all on nonassociative loops. The discovered action was sometimes incomplete even though it agreed on the current base. I preserved those failures rather than removing them. In the repaired version, a fresh validation mismatch becomes a counterexample: THEORICA acquires the complete falsifying translation, expands the action, and retries.

On the frozen public holdout, 165 unique algebras were evaluated under three acquisition seeds. Among 345 cases satisfying the scorer-defined compact-action promise, THEORICA reconstructed 345 out of 345 exactly. It produced zero false acceptances on 150 out-of-promise controls. A same-representation random-row acquisition baseline reconstructed 342 of 345 eligible cases. On paired-exact cases, THEORICA used fewer queries with a one-sided Wilcoxon p-value of 3.31×10⁻14. On the larger finite-group holdout, it reconstructed 240 of 240 eligible cases while observing a median 10.981% of the table, compared with 13.021% for the baseline.

The claim is deliberately bounded. This is not a universal algebra learner. The evidence supports exact, query-efficient reconstruction when a hidden operation has a faithful compact translation action, with abstention outside the tested promise. The broader idea is that an unknown rule can sometimes be learned more efficiently by discovering the transformations generating it rather than treating every output as independent.

## Demo sequence

1. Start with an n×n operation table completely hidden.
2. Judge chooses a prepackaged holdout example.
3. Queried cells illuminate as THEORICA acquires translations.
4. Side panel shows cumulative query fraction, discovered translations, generated-action size, base size and validation checks.
5. Inferred cells appear in a visually distinct layer; never visually merge queried and inferred evidence.
6. Reveal the scorer truth only after the learner accepts; show exact mismatch count.
7. Replay one preserved v1.1 loop failure: validation finds a counterexample.
8. Replay v1.2 repair: acquire the falsifying translation, enlarge the action, retry, verify.
9. End on frozen result card and explicit claim boundary.

## Video storyboard (target 2:30–3:00)

**0:00–0:20 — Hook.** Hidden table animation. Voice: “An unknown operation with n possible inputs in each position has n² cells. Do we really need to observe all of them?”

**0:20–0:50 — Core idea.** Animate rows becoming permutations and a few transformations generating an action. Show a small base as diagnostic points.

**0:50–1:25 — Working demo.** Run one fixed example. Keep queried cells and inferred cells visibly different. Show exact verification only after acceptance.

**1:25–1:55 — Falsification story.** Show v1.1 failure, counterexample, missing translation, action expansion, repaired reconstruction.

**1:55–2:25 — Evidence.** Result card: 345/345 eligible exact; 0/150 false accepts; larger-group median table fraction 10.981% versus 13.021%; paired one-sided Wilcoxon p=3.31×10⁻14.

**2:25–2:45 — Boundary.** “THEORICA is not universal. The result is conditional on a faithful compact translation action, and the system abstains outside the tested promise.”

**2:45–3:00 — Close.** Return to mostly unobserved table beside exact reconstructed table: “The key shift is from reading a table to discovering the transformations that generate it.”

## Deep technical Q&A

### What exactly is a left translation?
For a binary operation F, fixing the first argument x gives the map L_x(y)=F(x,y). THEORICA treats each L_x as a transformation of the carrier. Eligible cases require these learner-side translations to be permutations.

### What is the compact-action promise?
Eligibility is scorer-defined from the hidden full table after evaluation: learner-side left translations must be permutations; x↦L_x must be faithful; the full translation group has at most 20,000 elements; and its greedy permutation base has size at most 12. The learner is not handed this eligibility label.

### What is a permutation base and why does it help?
A base is a set of carrier points whose pointwise stabilizer is trivial. Therefore a group element is uniquely identified by its images on the base. If the true translations lie in the discovered action, base images can serve as compact signatures for identifying them.

### Why does this save queries?
A full table has n² entries. Complete acquisition of r translations costs nr queries; signatures over a base of size b cost roughly nb additional probes before validation overhead. Savings occur when r+b and validation cost are substantially below n.

### Is the method guaranteed to beat n²?
No. The empirical query-efficiency claim is conditional. Validation can consume many cells, especially on tiny structures, and the method can lose its advantage when the action is not compact or the validation budget dominates.

### How do you prevent leakage from the hidden table?
The learner only sees answers to its requested operation queries. Exact reconstruction and promise eligibility are scored against the full hidden table afterward. Development/holdout separation is frozen in the challenge construction.

### Why isn't this just group recognition?
The learner receives no family label and the challenge includes groups, faithful connected quandles and nonassociative loops. The reconstruction mechanism is phrased in terms of translation actions, not group multiplication axioms. The evidence does not claim efficiency for every non-group family.

### Why compare with random-row acquisition?
It shares the same representation and reconstruction machinery but changes acquisition policy. That isolates whether adaptive structural acquisition reduces queries rather than comparing against an unrelated weak model.

### Is the baseline strong enough?
It is a controlled primary baseline, not proof of superiority to every specialized algorithm. The project must not claim dominance over methods that know the algebra family in advance. Stronger published-baseline comparison remains a claim-boundary issue.

### Why use Wilcoxon?
Query counts are paired by the same exact-reconstructed cases and need not be normally distributed. A paired rank test evaluates whether THEORICA tends to require fewer queries than the baseline without assuming Gaussian differences.

### What does p=3.31×10⁻14 mean?
Under the paired-test null, a query advantage at least this extreme would be extraordinarily unlikely. It does not measure effect size and does not prove universality; the query fractions and mean-call differences provide the practical magnitude.

### Why did v1.1 fail?
A partially generated translation group could agree with observations on the current base while still omit a true translation. That made an unseen translation appear identifiable when the structural model was incomplete.

### What changed in v1.2?
When a fresh validation query falsifies F(x,y)=h_x(y), the algorithm acquires the complete true translation L_x, expands the generated action and retries reconstruction. The corpus, split, eligibility scorer, budgets, baseline and success gates stayed fixed.

### Isn't changing the algorithm after failure overfitting?
The failure is explicitly preserved and the repair targets the diagnosed mechanism rather than deleting difficult examples. The unchanged challenge then measures whether that mechanism-level repair resolves the frozen failures. A separately preregistered prospective larger-nongroup challenge provides a cleaner future test and must remain separate until opened.

### Does 345/345 establish a theorem?
No. It is an empirical result on the frozen eligible challenge. Any theorem or conditional bound must be stated separately with its assumptions. The competition claim should never turn finite empirical success into a universal theorem.

### Why zero false accepts matters?
A reconstruction system that always guesses could look successful on favorable cases. The 150 out-of-promise controls test whether THEORICA incorrectly certifies cases outside the scorer-defined structural promise; it accepted none of them.

### Why are the quandle/loop query fractions weak?
They are small structures and the frozen 64-query validation budget often exhausts the remaining table. They establish cross-family correctness, not non-group query efficiency. Do not hide this limitation.

### What would falsify the broader hypothesis?
A prospective set of eligible larger structures where exactness fails systematically, where action discovery cannot recover missing translations, or where query use approaches/exceeds exhaustive reading would weaken the claim. Those outcomes must be reported rather than tuned away.

### What is genuinely novel here?
The defensible contribution is the specific family-agnostic reconstruction procedure and its falsification-driven action expansion, evaluated under a frozen cross-family black-box challenge. Do not claim historical priority for compact group-table representations or universal algebra reconstruction.

### Could the same idea matter outside algebra?
Potentially wherever observations are generated by a compact transformation action: the conceptual lesson is to identify reusable transformations rather than learn outputs independently. This is motivation, not experimentally validated application evidence.

## Poster/display-board plan

### Panel 1 — Problem
- Hidden n×n operation table
- Exhaustive cost: n² observations
- Research question and bounded hypothesis
- One visual contrasting queried vs inferred cells

### Panel 2 — Method
- Operation row → left translation
- observed translations → generated permutation action
- action → small base/signatures
- reconstruction → fresh validation
- counterexample → acquire missing translation → retry

### Panel 3 — Evidence
- Frozen challenge design: 165 unique holdout algebras × 3 seeds = 495 cases
- 345 eligible, 150 out-of-promise controls
- THEORICA 345/345 exact; baseline 342/345
- zero false accepts
- larger-group median table fraction 10.981% vs 13.021%
- paired Wilcoxon p=3.31×10⁻14

### Panel 4 — Scientific progression
- v1.1: 48/345 eligible failures
- diagnosis: incomplete discovered action
- targeted counterexample-driven repair
- v1.2: 345/345 on unchanged eligible challenge

### Panel 5 — Limits and reproducibility
- promise assumptions
- tiny non-group efficiency limitation
- no universal/specialized-method superiority claim
- public catalogue provenance, frozen split, seeds and scorer
- QR code to repository/demo only after final public URL is frozen

## Judge traps to avoid

- Never say “THEORICA reconstructs any algebra.”
- Never present 10.981% as the overall cross-family median; it is the larger SmallGrp holdout figure.
- Never say the tiny quandle/loop cases demonstrate query efficiency.
- Never call p-value an effect size or probability the null is true.
- Never imply the prospective larger-nongroup challenge passed before its frozen results exist.
- Never claim “first ever” without completed priority search.
- Never hide v1.1 failures; they are one of the strongest scientific parts of the project.

## Final recording checklist

- [ ] Demo visibly distinguishes queried from inferred cells.
- [ ] Every numerical card matches frozen artifacts exactly.
- [ ] No prospective number appears unless formally opened and committed.
- [ ] Screen recording is legible at 1080p.
- [ ] Narration stays under three minutes unless INSEF explicitly allows/requests longer.
- [ ] Video URL is accessible without sign-in.
- [ ] PDF and video use identical title, participant names and claims.
