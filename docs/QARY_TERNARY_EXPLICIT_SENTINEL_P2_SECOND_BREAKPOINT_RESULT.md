# P2 has a proved second breakpoint at leaf cost 23

## Prospective result

Every frozen source and unseen-family prediction passed.

| leaf cost | exact value | unique optimal group | root children |
| ---: | ---: | ---: | --- |
| 22 | 37 | 0 | `[33,33,33]` |
| 23 | 38 | 0 | `[34,34,33]` |

Thus `c=23` is the first integer increase after the four-way collision at
`c=11`.  The root action follows the predicted local envelope

`4 + max(11+c,33) = max(37,15+c)`

at both frozen endpoints.

## Bounded exact law

Earlier exact enumeration established `V=4+3c` at every positive integer
`1<=c<=10`, and the frozen collision established `V(11)=37`.  The new exact
endpoint gives `V(22)=37`.  Because increasing a query cost cannot decrease a
finite minimax value, monotonicity forces

`V(c)=37` for every integer `11<=c<=22`.

The next exact endpoint is `V(23)=38`.  Therefore the explicit-sentinel P2
witness now has the proved bounded chamber law

- `V=4+3c` for positive integers `1<=c<=10`;
- `V=37` for integers `11<=c<=22`;
- `V=38` at `c=23`.

This is an executable planning boundary: use the low-cost root/leaf family
through 10, recognize the collision at 11, retain the root policy through 22,
and recalibrate at 23.

## Unseen-family transport

The all-coordinate `0<->1` image had not been opened at these endpoints.  It
matched both values, unique root optima, child multisets, and all search counts.
Each solve used 20,085 states, 15,794 actions, and 95 compatibility states.
The edge-checked isomorphism fixed root group 0, so the covariance theorem
survives this new-family boundary test.

## Independent audit

The zero-production-import audit reconstructed all four root minima, exact
lower/upper-bound equalities, unique optima, transported child multisets, and
search-count equalities.  It independently joined the prior `c=1..10` evidence
to the `c=11` and new `c=22,23` endpoints and applied the monotonicity closure.

## Limits

The theorem is bounded to this P2 witness, its explicit outside token, fixed
`(a,b)=(4,11)`, positive integer leaf costs through 23, and coordinatewise
alphabet transport.  It does not establish the value for real-valued costs,
integers above 23, arbitrary word families, incomplete query libraries, or
other cost vectors.

## Reproducibility

- Frozen protocol commit: `2ffcba2913b19eaa19c5bcaaad0d22019b7dc599`.
- Exact result SHA-256: `bebaf756e0101f5b502290e54f3d7315fcaa480f355973a8aef091005e0fd65c`.
- Independent audit SHA-256: `896bceefc8da08515302c7c7491c928679f585e3aacd8d19405721ce3be08675`.
- Targeted verifier/audit test: 1 passed.
- Full regression: 334 passed.
- Ruff: passed.
