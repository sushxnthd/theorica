# Divergence-Agnostic Uniform-Ambiguity Minimax Law

Status: **exact system theorem passed; historical novelty not claimed**

## Smallest supported claim

Let there be \(n\) candidate labels and let a depth-\(q\) query plan cover
\(k=q+1\) labels (queried labels plus the terminal guess). Let
\(\mathcal U\subseteq\Delta_n\) be any certified ambiguity set that contains
the uniform prior \(u=(1/n,\ldots,1/n)\). Then

\[
\max_{\mu\ \mathrm{over}\ k\mathrm{-subsets}}
\min_{\pi\in\mathcal U}
\mathbb E_{S\sim\mu}[\pi(S)]
=\frac{k}{n}.
\]

Uniform randomization over all \(k\)-subsets is minimax. A deterministic
plan is strictly dominated exactly when its certified worst-case covered
mass is less than \(k/n\).

This is stronger than the preceding total-variation-only result: it needs
no convexity, divergence formula, radius, or permutation closure—only the
machine-checkable membership fact \(u\in\mathcal U\).

## Proof

For any randomized plan, write \(a_i=\Pr(i\in S)\). Because every realized
set has size \(k\), \(0\le a_i\le1\) and \(\sum_i a_i=k\). Nature may choose
\(u\), so

\[
\min_{\pi\in\mathcal U}\pi^\top a\le u^\top a
=\frac1n\sum_i a_i=\frac{k}{n}.
\]

Under the uniform distribution on \(k\)-subsets,
\(a_i=\binom{n-1}{k-1}/\binom nk=k/n\) for every label. Therefore every
\(\pi\in\Delta_n\) gives

\[
\pi^\top a=\frac{k}{n}\sum_i\pi_i=\frac{k}{n}.
\]

The upper and lower bounds coincide. For a deterministic subset \(S\), the
robust value is \(\inf_{\pi\in\mathcal U}\pi(S)\); comparison with \(k/n\)
gives the iff strict-domination test.

If \(0<k<n\) and \(\mathcal U\) contains a nontrivial neighborhood of
uniform, every deterministic subset is strictly dominated: transfer an
arbitrarily small mass \(\varepsilon\) from \(S\) to its complement. This
covers positive-radius balls around uniform for TV, forward/reverse KL,
chi-square, squared Hellinger, and Jensen-Shannon divergences. Full coverage
\(k=n\) correctly remains value one with no strict gain.

## Exact verification

- 35 \((n,k)\) theorem identities for \(2\le n\le8\)
- 501 exact subset-unranking checks
- 318,195 exact rational-prior payoff checks
- 494 constructive strict-domination witnesses
- six divergence families evaluated on finite positive witnesses
- 14 focused production tests
- byte-identical primary rerun
- independent standard-library checker with the same canonical digest:
  \`683c7c5af8c3ea6f2ff903e43637bb98bd6789555b7be0d1199610e683eaac82\`
- exact workflow, general CI, prior robust-frontier workflow, prior synthesis
  workflow, and inherited rack-closure workflow all passed on the corrected head

The initial missing-test-dependency failure and two API/test mismatches remain
in workflow history. They were fixed in follow-up commits rather than erased.

## SCIENCE ledger

The TV-specific uniform result is a special case of a simpler structural law:
the adversary's possession of the uniform prior fixes the minimax value, while
the balanced inclusion vector makes the randomized plan prior-invariant. The
exact strictness boundary is robust deterministic mass below \(k/n\).

## CONSEQUENCE ledger

THEORICA now has a fail-closed, compact planner:

1. require a certificate that uniform belongs to the ambiguity set;
2. return the exact rational value \(k/n\);
3. sample an exactly uniform \(k\)-subset through rejection-safe, seed-bound
   rank unranking;
4. emit an executable query order and terminal guess;
5. compare any certified deterministic robust value against \(k/n\).

This removes construction and storage of the explicit \(\binom nk\)-component
LP mixture. The certificate uses \(O(n)\) metadata, and execution selects
\(O(k)\) labels.

## Priority audit

The broad ingredients are established: randomized minimax decision rules are
classical, and phi-divergence robust optimization explicitly covers
chi-square, Hellinger, and KL ambiguity sets. Relevant primary/author sources:

- Ben-Tal et al., *Robust Solutions of Optimization Problems Affected by
  Uncertain Probabilities*, Management Science 59(2), 2013:
  https://optimization-online.org/2011/06/3076/
- Duanmu, Roy, and Schrittesser, *Statistical minimax theorems via nonstandard
  analysis*, 2022: https://arxiv.org/abs/2212.13250
- Guan, Liang, and Ma, *Random Distributionally Robust Optimization under
  Phi-divergence*, 2025: https://arxiv.org/abs/2506.23839

Accordingly, this branch does **not** claim a new general minimax theorem or
new phi-divergence theory. Its defensible contribution is the exact
certified-family reduction, sharp deterministic domination gate, and scalable
executable reasoning contract inside THEORICA.

## Limits

- The result says nothing when uniform membership is uncertified.
- It optimizes the current equal-value identification objective; unequal query
  costs, label utilities, or nonuniform terminal rewards change the game.
- A small state description does not make sampling or downstream queries free.
- The finite verification supports the implementation; the all-\(n\) statement
  rests on the proof above.
