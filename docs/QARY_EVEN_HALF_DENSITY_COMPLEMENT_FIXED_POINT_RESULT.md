# Complement fixed points at the half-density boundary

## Central theorem

Let `T_{q,h}` count unlabelled rooted `q`-ary suffix-trie shapes of height
`h`, including the empty and full shapes, and let `F_{q,h}` count shapes fixed
by leaf complement.  Then

`T_{q,0}=2`, `F_{q,0}=0`, and

`T_{q,h}=binom(T_{q,h-1}+q-1,q)`.

If `P=(T_{q,h-1}-F_{q,h-1})/2`, the complement involution on the child
shapes has `F_{q,h-1}` fixed points and `P` two-cycles.  A parent multiset is
fixed exactly when both members of each two-cycle have equal multiplicity.
Consequently,

`F_{q,h}=[t^q](1-t)^(-F_{q,h-1})(1-t^2)^(-P)`.

All fixed classes have half of the `q^h` leaves.  Thus no fixed class exists
when `q^h` is odd.  At even half density, if `A` is the corresponding Pólya
coefficient, complement decomposes the layer into `F_{q,h}` fixed classes and
`(A-F_{q,h})/2` two-cycles.

For a fixed class, a family and its complement have isomorphic suffix tries.
The existing explicit-sentinel quotient theorem therefore constructs a full
query-system isomorphism: exact minimax values agree for every positive
level-only cost vector, and an optimal policy transports.  This conclusion is
specific to fixed classes; it is not asserted across a non-fixed complement
pair.

## Prospectively frozen q=6 holdout

The protocol reserved `q=6,h=2,k=18` before opening the direct shape
enumerator.  The labelled layer contains

`binom(36,18)=9,075,135,300`

families, but the complete rooted-tree quotient has only 924 representatives.
Every frozen prediction passed:

- the exact orbit polynomial sums to 924 and is palindromic;
- its coefficients at sizes 15 through 21 are
  `51,55,55,58,55,55,51`;
- the half-density layer contains exactly 58 classes;
- exactly 20 classes are self-complementary;
- the other 38 classes form exactly 19 complement pairs;
- complement squared returned every canonical shape unchanged; and
- all 20 fixed shapes received an explicit involutive child-index bijection
  sending each child subtree to its complement.

The executable reduction is more than a count: the system can classify an
even half-density family, determine whether complement preserves its policy
class, and, in the fixed case, construct the policy transport rather than
resynthesizing from scratch.

## Independent verification

The primary implementation enumerated sorted six-child multisets.  A
zero-production-import audit instead enumerated weak compositions of six over
the seven possible height-one child weights.  It independently reconstructed
all 924 representatives, the 58 half-density classes, the 20 fixed classes,
the 19 two-cycles, the coefficient window, and the complement involution.

The broader theorem-side `q=4,h=3` calculation also closed exactly:

- 1,088,430 total classes;
- 60,802 half-density classes;
- 1,326 fixed classes; and
- 29,738 non-fixed complement pairs.

Primary artifact SHA-256:
`876c034162963920751df3aee8a5d9d6ec7c7e4ac62a8bb51126e54355ae3cb8`.

Audit artifact SHA-256:
`20940a80b2cb009ff21dee109a83df29ea33711cd4f0082947e4fcddb0445b2f`.

Both scripts executed successfully and all new Python files compiled in the
available environment.  The environment did not include pytest or Ruff, so
the repository-wide regression and lint claims are deferred to exact-head
hosted CI rather than inferred locally.

## Limits

The policy consequence assumes the binary cube base, a complete prefix-query
library, a separate outside sentinel, and positive level-only costs.  The
theorem does not cover incomplete query libraries, aliased outside responses,
non-level costs, or DAGs with cross-branch sharing.  Fixed orbit class means
isomorphism under a complete-tree automorphism; it does not mean a labelled
family literally equals its complement.
