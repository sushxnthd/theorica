# Componentwise proof route falsified

## Outcome

The frozen symbolic proof obligation failed exactly one of the six target
faces. An exhaustive finite-state adversary recursion over 178,964 states
found the maximal componentwise transcript guarantees

```text
(1,5,1), (2,3,4), (2,4,3), (3,3,3), (4,2,1).
```

The proposed face `(3,4,1)` is absent. Therefore the six-face formula cannot
be proved by assigning every face a single transcript whose level-query count
is componentwise unavoidable.

## Exact countercertificate

A separate constructive search found a valid middle-first decision tree for
which none of 414 terminal transcripts dominates `(3,4,1)`. Its 32 distinct
leaf exposure vectors have five Pareto maxima:

```text
(2,3,4), (2,4,3), (2,5,1), (3,3,3), (4,3,1).
```

The avoidance search required 403 states. It is a direct counterexample to
the frozen lower-bound obligation, not a timeout or failure to find a proof.

At witness costs `(79,79,1)`, the avoidance tree, the target face, and the
production exact solver all have cost 554. The mechanism is a branch tradeoff:

```text
(3,4,1) = 1/2 (2,5,1) + 1/2 (4,3,1).
```

Consequently at least one of the two tradeoff transcripts costs at least the
target face, even though neither transcript componentwise dominates it. The
face is a convex-hull support certificate, not a scalar transcript
certificate.

## Independent verification

A standard-library-only implementation independently reconstructed the five
maximal guarantees, confirmed that `(3,4,1)` alone is missing, checked the
avoidance exposure set, and imported zero `theorica` modules.

## Reformed kernel

The next proof attempt must propagate adversarial **menus** of exposure
vectors and certify their convex hulls, rather than propagating one guaranteed
vector at a time. The exact target is to show that every middle-first policy
admits an adversarial exposure menu whose downward convex hull contains all
six target faces. This change is forced by the countercertificate.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_three_level_middle_first_componentwise.py
python scripts/audit_qary_three_level_middle_first_componentwise.py
pytest -q
```

Machine-readable evidence is under
`results/qary_three_level_middle_first_proof/`.

## Claim boundary

This result falsifies one proof architecture; it does not falsify the
six-face numerical formula. The formula still has exact agreement on 88
tested middle-first cost triples. A universal theorem now requires the
set-valued convex-hull adversary argument plus a universal feasible-policy
upper bound.
