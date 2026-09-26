namespace TheoricaFormal

/--
Metric-space core of adversarially robust translation decoding.

If two candidate translations are separated by more than twice the error budget,
then no received observation can lie within that budget of both candidates.

This theorem is deliberately stated for an abstract Nat-valued distance.  Hamming
distance on restricted translation signatures is the intended instantiation.
-/
theorem unique_decode_of_separation
    {α : Type}
    (dist : α → α → Nat)
    (triangle : ∀ a b c, dist a c ≤ dist a b + dist b c)
    (symm : ∀ a b, dist a b = dist b a)
    (c₁ c₂ received : α)
    (e : Nat)
    (separated : e + e < dist c₁ c₂)
    (close₁ : dist c₁ received ≤ e)
    (close₂ : dist c₂ received ≤ e) : False := by
  have received_close₂ : dist received c₂ ≤ e := by
    rw [symm received c₂]
    exact close₂
  have tri : dist c₁ c₂ ≤ dist c₁ received + dist received c₂ :=
    triangle c₁ received c₂
  have sum_bound : dist c₁ received + dist received c₂ ≤ e + e :=
    Nat.add_le_add close₁ received_close₂
  have impossible_bound : dist c₁ c₂ ≤ e + e :=
    Nat.le_trans tri sum_bound
  exact (Nat.not_lt_of_ge impossible_bound) separated

/--
Equivalent uniqueness formulation: two distinct candidates cannot both be
radius-e explanations of the same observation if every distinct candidate pair
has distance greater than 2e.
-/
theorem radius_e_explanation_unique
    {α : Type}
    (dist : α → α → Nat)
    (triangle : ∀ a b c, dist a c ≤ dist a b + dist b c)
    (symm : ∀ a b, dist a b = dist b a)
    (e : Nat)
    (pair_separated : ∀ a b, a ≠ b → e + e < dist a b)
    (a b received : α)
    (ha : dist a received ≤ e)
    (hb : dist b received ≤ e) : a = b := by
  by_contra hne
  exact unique_decode_of_separation dist triangle symm a b received e
    (pair_separated a b hne) ha hb

end TheoricaFormal
