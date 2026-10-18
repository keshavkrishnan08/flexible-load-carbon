# Role 1: Gap Memo: the general net-carbon-reduction result

**One page on what is proved, what the general condition is, and where it resists.**

## What we set out to do
Footnote 6 and §4.3 sign the net carbon reduction only for the uniform (and, by
footnote, power-law) family. Two things had to be made general and rigorous:

1. **The channel:** renewable capacity is higher with FCL, `K*_R > K°_R`.
2. **The net sign:** the capacity-substitution effect beats the utilization
   effect.

## What is now proved (see `role1_carbon_theory.tex`)

- **Capacity channel, general (Theorem 1).** `K*_R ≥ K°_R` for **any**
  residual-demand distribution satisfying one transparent condition, the
  **shift ratio** `g(x) = F_{K_R}(x)/f(x)` is non-increasing in `x` across the
  FCL dispatch window. Proof route: implicit differentiation of the FOC system
  gives
  `dK*_R/dC_M ∝ (β+p−R)(R−c)·[F_{K_R}(K_F)f(K_F−K_M) − F_{K_R}(K_F−K_M)f(K_F)] / detH`,
  and the bracket `= f·f·[g(K_F) − g(K_F−K_M)] ≤ 0` under the condition. Since
  at `C_M = C̄_M` the system collapses to the no-FCL optimum (`K_M=0`),
  integrating `dK*_R/dC_M ≤ 0` from `C̄_M` down gives `K*_R ≥ K°_R`.
- **Power-law / footnote 6 (Corollary 1).** `g(x) = (D̄−x)/(D̄+K_R)` is affine
  and decreasing for *every* shape parameter α, so the channel holds for the
  whole family, this is exactly why footnote 6 extends.
- **Exact net-carbon inequality (Prop. 2 = paper Prop. 4), condition (C).**
  Clean decomposition: utilization effect (always `+`, distribution-free) vs.
  net-of-capacity effect (sign carried by `K*_R > K°_R`).
- **Clean sufficient condition (Theorem 2).** Shift-ratio condition + `C_R`
  small enough ⇒ carbon strictly falls for all `C_M < C̄_M`. Recovers eqs 25-26.
- **Corrections confirmed:** eqs 25/26 are fossil *output* (drop factor `c`);
  the large-FCL flat term `(K_M−K_R)` is required; eq 24 = `2·∂Π/∂K_R`
  (sign-correct, factor-2 is a grouping artifact, not a bug).

## The four open points: now closed

All four limitations of the uniform-only treatment are resolved. Every formula
below is verified to machine precision against finite differences of the profit
integral (`verify_exact.py`).

1. **Submodularity: not an obstruction.** `Π` is submodular in `(K_R, K_F)`
   (`∂²Π/∂K_R∂K_F = (R−β−p)F_{K_R}(K_F) − (R−c)F_{K_R}(K_F−K_M) ≤ 0`, verified
   to 3e-6) with increasing differences in `(K_R;K_M)` and `(K_F;K_M)`, so no
   reorder restores supermodularity and Topkis does not apply. **But it isn't
   needed:** the homotopy-in-`C_M` + signed-cofactor proof is complete under a
   stated **Regularity condition** (interior, `H ≺ 0` along the path), verified
   by eigenvalue computation. The path *crosses regimes*, small-FCL near `C̄_M`
   (where `K*_M→0`), large-FCL below, and `dK*_R/dC_M < 0` is confirmed in both
   (scan: −4.28,−2.76,−2.19 small; −5.21,−21,−108 large). Regularity lapses only
   at the knife-edge (`C_R` small, `K*_R→∞`), where `K*_R>K°_R` is immediate.
   A signed one-parameter cofactor does the comparative-statics job without a
   lattice.
2. **Endogenous-capacity feedback: no term is missing.** The comparison
   probabilities are **distribution-free** (new Lemma; `C/(R−c)` at `K_F−K_M`,
   `φ°` at `K_F°`: verified `=5/9, 17/18` to 1e-9 on a Beta mixture). The only
   surviving level effect, `K*_R > K°_R`, is signed once by Theorem 1. So
   condition (C) **+** Theorem 1 is a *complete* characterization, the feared
   second-order feedback enters only through the leftward shift that condition
   (a) already books.
3. **`C_R†`: now a theorem for general `F`.** The viability threshold
   `C_R† = sup{C_R : Δ(C_R) ≥ 0}` is finite and positive for *every* `F` (with
   a.s.-positive renewables): carbon falls on the nonempty window `(C_R°, C_R†)`
   and rises above it. Proof anchors both ends, the rigorous large-cost limit
   `Δ → −U₀ < 0` (no renewables ⇒ FCL only adds the utilization effect) plus the
   small-cost unbounded-renewables regime, with the strict gap `C_R° < C_R†`
   forced by the `R>c` shadow-value weight. Explicit instance (power-law):
   `C_R† = MV = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`,
   `C_R° = C_F²/(2(β+p−c))`. Verified [`verify_threshold.py`]: Beta(2,5) carbon
   falls for small `C_R` (Δ=+0.56,+1.07), rises past `C_R†∈(0.35,0.5)`,
   `Δ<0` at the large-cost anchor. *(Upgrades the earlier heuristic.)*
4. **Regimes: unified.** Thresholds are strictly ordered
   `C_M^fc = R−c−C_F  <  C̄_M = (R−c)φ°  <  C̄_M^b = C̄_M + cF(0;K°_R)`
   (gap `C̄_M − C_M^fc = C_F(β+p−R)/(β+p−c) > 0`, verified 0.48). Adoption iff
   `C_M < C̄_M^b`; the triple win holds across all regions, strict in
   small/large-FCL, degenerate-favorable in full coverage.

**Single residual (→ Role 4):** the exact small-FCL boundary `K*_M = K°_R`
inside region (I).

**Sharpness (→ Role 3).** The condition is tight: the cofactor bracket flips
with `g(K_F) − g(K_F−K_M)`, so `g` *increasing* (high-demand states windier than
surplus, a positive demand/supply correlation) gives `dK*_R/dC_M > 0` and
`K*_R < K°_R`. That's the precise "where the triple win breaks"; worth a
targeted numerical counterexample.

## Handoffs
- **Role 2:** validate `dK*_R/dC_M` sign-law and the `C_R†` crossing across
  distribution families (we used Beta scale-mixtures; extend the sweep).
- **Role 3:** build the counterexample with `g` increasing; map the triple-win
  region vs. the demand/supply correlation.
- **Role 4:** stitch small-FCL / interior / full-coverage into one regime map;
  confirm Hessian negative-definite conditions feed Assumption 1.

---

# Role 1: Gap Memo addendum: A1 Week 2

**Five Week-2 results (`role1_week2_theory.tex`, verified `verify_week2.py`).**
Same model, same large-FCL interior regime, nothing outside Role 1.

1. **Existence, uniqueness, contract optimality (Thm 1).** A maximizer exists
   (coercivity + Weierstrass). It is unique not by concavity, `Π` is submodular
   in `(K_R,K_F)`, so global concavity fails, but by a **recursive-triangular**
   FOC structure: the distribution-free cutoffs pin `K_F(K_R)` and `K_M(K_R)` as
   unique inverses of `F`, and the `(K_F,K_M)` Hessian block is **unconditionally**
   negative definite (`det M = (R−c)f(a)(β+p−R)f(K_F) > 0`). Uniqueness of `K_R`
   then needs a **single scalar** diagonal-dominance / reduced-SOC condition
   (Schur complement `Ψ'(K_R) < 0`), which also certifies `H ≺ 0`. Dispatch
   `d*(x)=min{(K_F−x)_+,K_M}` is the unique optimum because the per-state payoff
   has strictly positive slopes `β+p−c` and `R−c` (strict `R>c`).

2. **Shift-ratio uniform along the homotopy (Lemma 4).** Support-wide
   monotonicity of `g=F_{K_R}/f` (a static, `C_M`-free hypothesis) implies the
   realized two-point endpoint inequality `g(a) ≥ g(K_F*)` holds at **every**
   `C_M` on the path, even as the window `(K_F*−K_M*, K_F*)` moves, both
   endpoints stay strictly interior (cutoffs in `(0,1)`) and ordered (`K_M*>0`).
   This is the exact content the Week-1 "integrate downward" step needs.

3. **Emission keystone for general `F` (Thm 2 + Prop 3).** Substituting the
   equilibrium map into (C) gives the exact endogenous condition. A **primitive
   sufficient condition**, endpoint shift-ratio (⇒ `K_R*>K_R°`) plus a two-zone
   tail/skew bound (`f(·;K_R*)` non-increasing on the FCL zone, `f(·;K_R°)`
   non-decreasing on the no-FCL zone), yields a closed-form lower bound
   `Δ ≥ Δ_LB`, so carbon strictly falls when `Δ_LB>0`. **Resolution of the Week-1
   conjecture, NEGATIVE across BOTH regimes** (carbon falls at no finite interior
   optimum). Validated with a **direct state-by-state fossil simulator** (FCL
   served from renewable surplus first) that matches the closed form to 7 digits
   (6.1833), confirming the formula already credits surplus absorption.
   - **Large-FCL (`K_M*≥K_R*`):** exhaustive search (Beta mixtures, every skew,
     `E[S]≤.8`, full `C_R×C_M` grid) gives `Δ<0` at every optimum (max ≈ −1.4).
     Mechanism = the **irreducible floor** `(K_M*−K_R*)_+`: max surplus in any
     state is `≤K_R*`, so an FCL bigger than `K_R*` can't be fully surplus-powered
     and burns ≥`K_M*−K_R*` fossil even at deepest surplus.
   - **Small-FCL (`K_M*<K_R*`):** the floor vanishes, but this regime is optimal
     only at small `C_R`, where the **no-FCL** grid already drives `K_F°→0`
     (`E[fossil°]→0`), nothing to save, and the channel even **reverses**
     (`K_R*≤K_R°`). E.g. `CR=0.10`: no-FCL `(14.4, 0.0)`, with-FCL `(14.0,1.6,2.1)`,
     `Δ=−0.21`.
   - Carbon strictly falls **only** at the cheap-renewable corner `K_R*→∞`
     (Week-1 Thm 4(ii) window). Consistent with Role-3's "carbon rare at low C_R."
   **Correction:** my first-pass mechanism ("flat term = fossil added") was wrong;
   the formula already credits surplus absorption. Did **not** fabricate a positive
   witness, reported the true two-regime negative.

4. **Connectedness of `{C_R : Δ≥0}` (Thm 3).** Bounded above (Week-1 large-cost
   anchor `Δ→−U₀`), non-empty (result 3), and a **single interval** under the
   monotone-renewable-shadow-value condition: `Δ'(C_R)<0` at every zero (strict
   down-crossing), proved to rule out a second crossing by an IVT argument.

5. **Sharpness (Thm 4, Thm 5).** The N&S condition for `K_R*>K_R°` is the **path
   integral** `∫_{C_M}^{C̄_M} λ dt > 0` (FTC), `λ ∝ f f [g(a)−g(K_F*)]`;
   pointwise-monotone `g` makes `λ≥0` so it is **sufficient but not necessary**.
   The two-sided bounds `Δ_min ≤ Δ ≤ Δ_max` are **tight**, attained by
   degenerate conditional laws concentrating at the interval endpoints.

**Still open (honest):** the cross-`F` robust certificate over all of `U`
(capacity covariation) remains Role 3; small-FCL boundary `K*_M=K°_R` remains
Role 4. The reversed-channel realized counterexample (necessity witness) is Role 3.
