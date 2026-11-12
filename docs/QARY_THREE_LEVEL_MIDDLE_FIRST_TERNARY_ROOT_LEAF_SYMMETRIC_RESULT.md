# Ternary equal-root-leaf-cost conjecture: falsified

## Result

The frozen candidate

```text
T_3(x,y,x) = max(2x+5y, 5x+4y, 6x+3y)
```

is false. At the preregistered shared boundary `(x,y)=(1,3)`, its three
faces predict `17, 17, 15`, but exact ternary synthesis gives

```text
T_3(1,3,1) = 18.
```

This is a strict one-query-cost gap over the embedded-binary lower envelope.
It falsifies the value formula itself, not merely the proposed cone-uniform
proof architecture.

## Decisive experiment

The protocol required a policy of cost at most 17 on the ray `(1,3)` for each
of the first two cones. Exact weighted minimax synthesis instead found 17
infeasible and constructed an optimal cost-18 policy:

| Quantity | Result |
|---|---:|
| Candidate value | 17 |
| Exact ternary value | 18 |
| Strict gap | 1 |
| Exact search states | 1,360,267 |
| Worst-case depth | 11 |
| Terminal transcripts | 3,035 |
| Unique terminal exposures | 47 |

The synthesized policy's maximum weighted exposure `r + 3m + l` is 18.

## Independent audit

A separate stdlib-only implementation reconstructs all 27 ternary words and
13 prefix-query groups without importing THEORICA. It independently reports:

| Budget | Feasible? |
|---:|:---:|
| 17 | no |
| 18 | yes |

The independent solver visited 599,660 cached states. Its face computation
also reconstructs the rejected candidate values `(17,17,15)`.

## Protocol disposition

The preregistered scalar holdouts were intentionally not run. The protocol
specified that they follow cone synthesis, and the conjecture failed at the
first decisive shared-boundary ray. Continuing through the holdout list after
that failure would test a claim already known to be false and invite an
unfrozen replacement formula.

The preserved parent failure remains informative: the old unit-cost ternary
policy also costs 18 on this ray. Direct synthesis proves that this was not a
poor-policy artifact; 18 is optimal.

## Consequence

The binary six-face envelope is not sufficient for unequal-cost ternary
planning, even on the symmetric `(x,y,x)` plane. Any replacement theorem must
introduce at least one genuinely ternary lower face or another mechanism that
attains 18 at `(1,3,1)`. The next kernel should first locate that missing face
from exact exposure/support data before proposing a new global fan.

## Scope and limitations

This result is exact only for arity three, depth three, four copies, one
adversarial substitution, one recognized erasure, a middle-first initial
action, and the single weighted point `(1,3,1)`. It does not identify the full
`(x,y,x)` law, prove a neighborhood around the counterexample, or characterize
arbitrary ternary cost triples. No deployment or unrestricted-policy claim is
made.
