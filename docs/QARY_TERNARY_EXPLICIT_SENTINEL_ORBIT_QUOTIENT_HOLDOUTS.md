# Frozen holdouts: complete obstruction orbit quotient

The structural protocol was published before opening either representative.
Exact representative enumeration then produced the following discovery values
at `(a,b)=(4,11)`:

| class | leaf cost | exact value | optimal groups | states / actions / compatibility |
| --- | ---: | ---: | --- | --- |
| same-middle | 1 | 6 | `[4,5,7,8,10]` | `5600 / 3532 / 49` |
| same-middle | 23 | 69 | `[10]` | `5600 / 3532 / 49` |
| different-middle | 1 | 7 | `[0,4,5,7,8,10,11]` | `20085 / 15794 / 95` |
| different-middle | 23 | 38 | `[0]` | `20085 / 15794 / 95` |

No reserved holdout value was opened to obtain these rows.

## Frozen transported predictions

The same-middle holdout `{(2,2,1),(2,2,2)}` has an edge-checked isomorphism
whose query map sends representative group 10 to 12.  Predict:

- at `c=1`: value `6`, optimal groups `[4,5,7,8,12]`;
- at `c=23`: value `69`, unique optimal group `[12]`;
- exact search counts `5600 / 3532 / 49` at both costs.

The different-middle holdout `{(2,1,2),(2,2,1)}` has an edge-checked
isomorphism fixing group 0 and sending representative groups 10 and 11 to 11
and 12.  Predict:

- at `c=1`: value `7`, optimal groups `[0,4,5,7,8,11,12]`;
- at `c=23`: value `38`, unique optimal group `[0]`;
- exact search counts `20085 / 15794 / 95` at both costs.

For every transported optimal action, predict the representative child-value
multiset after the certified response-label permutation.  Any value, policy,
child multiset, bound, or search-count mismatch falsifies the quotient claim
and must be retained.
