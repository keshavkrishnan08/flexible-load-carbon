# Role 1 — Gap Memo: the general net-carbon-reduction result

**One page on what is proved, what the general condition is, and where it resists.**

## What we set out to do
Footnote 6 and §4.3 sign the net carbon reduction only for the uniform (and, by
footnote, power-law) family. Two things had to be made general and rigorous:

1. **The channel:** renewable capacity is higher with FCL, `K*_R > K°_R`.
2. **The net sign:** the capacity-substitution effect beats the utilization
   effect.

## What is now proved (see `role1_carbon_theory.tex`)

- **Capacity channel, general (Theorem 1).** `K*_R ≥ K°_R` for **any**
  residual-demand distribution satisfying one transparent condition — the
  **shift ratio** `g(x) = F_{K_R}(x)/f(x)` is non-increasing in `x` across the
  FCL dispatch window. Proof route: implicit differentiation of the FOC system
  gives
  `dK*_R/dC_M ∝ (β+p−R)(R−c)·[F_{K_R}(K_F)f(K_F−K_M) − F_{K_R}(K_F−K_M)f(K_F)] / detH`,
  and the bracket `= f·f·[g(K_F) − g(K_F−K_M)] ≤ 0` under the condition. Since
  at `C_M = C̄_M` the system collapses to the no-FCL optimum (`K_M=0`),
  integrating `dK*_R/dC_M ≤ 0` from `C̄_M` down gives `K*_R ≥ K°_R`.
- **Power-law / footnote 6 (Corollary 1).** `g(x) = (D̄−x)/(D̄+K_R)` is affine
  and decreasing for *every* shape parameter α, so the channel holds for the
  whole family — this is exactly why footnote 6 extends.
- **Exact net-carbon inequality (Prop. 2 = paper Prop. 4), condition (C).**
  Clean decomposition: utilization effect (always `+`, distribution-free) vs.
  net-of-capacity effect (sign carried by `K*_R > K°_R`).
- **Clean sufficient condition (Theorem 2).** Shift-ratio condition + `C_R`
  small enough ⇒ carbon strictly falls for all `C_M < C̄_M`. Recovers eqs 25–26.
- **Corrections confirmed:** eqs 25/26 are fossil *output* (drop factor `c`);
  the large-FCL flat term `(K_M−K_R)` is required; eq 24 = `2·∂Π/∂K_R`
  (sign-correct, factor-2 is a grouping artifact — not a bug).

## The four open points — now closed

All four limitations of the uniform-only treatment are resolved. Every formula
below is verified to machine precision against finite differences of the profit
integral (`verify_exact.py`).

1. **Submodularity — not an obstruction.** `Π` is submodular in `(K_R, K_F)`
   (`∂²Π/∂K_R∂K_F = (R−β−p)F_{K_R}(K_F) − (R−c)F_{K_R}(K_F−K_M) ≤ 0`, verified
   to 3e-6) with increasing differences in `(K_R;K_M)` and `(K_F;K_M)`, so no
   reorder restores supermodularity and Topkis does not apply. **But it isn't
   needed:** the homotopy-in-`C_M` + signed-cofactor proof is complete under a
   stated **Regularity condition** (interior, `H ≺ 0` along the path), verified
   by eigenvalue computation. The path *crosses regimes* — small-FCL near `C̄_M`
   (where `K*_M→0`), large-FCL below — and `dK*_R/dC_M < 0` is confirmed in both
   (scan: −4.28,−2.76,−2.19 small; −5.21,−21,−108 large). Regularity lapses only
   at the knife-edge (`C_R` small, `K*_R→∞`), where `K*_R>K°_R` is immediate.
   A signed one-parameter cofactor does the comparative-statics job without a
   lattice.
2. **Endogenous-capacity feedback — no term is missing.** The comparison
   probabilities are **distribution-free** (new Lemma; `C/(R−c)` at `K_F−K_M`,
   `φ°` at `K_F°` — verified `=5/9, 17/18` to 1e-9 on a Beta mixture). The only
   surviving level effect, `K*_R > K°_R`, is signed once by Theorem 1. So
   condition (C) **+** Theorem 1 is a *complete* characterization — the feared
   second-order feedback enters only through the leftward shift that condition
   (a) already books.
3. **`C_R†` — explicit.** For the power-law family,
   `C_R† = MV = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`, and the
   no-FCL threshold is `C_R° = C_F²/(2(β+p−c))`. We prove `C_R° < C_R†` (=0.040
   vs 0.344 at the calibration), so on the nonempty window `(C_R°, C_R†)` FCL
   drives `E[fossil]→0` while `K°_R` stays finite ⇒ carbon strictly falls.
4. **Regimes — unified.** Thresholds are strictly ordered
   `C_M^fc = R−c−C_F  <  C̄_M = (R−c)φ°  <  C̄_M^b = C̄_M + cF(0;K°_R)`
   (gap `C̄_M − C_M^fc = C_F(β+p−R)/(β+p−c) > 0`, verified 0.48). Adoption iff
   `C_M < C̄_M^b`; the triple win holds across all regions — strict in
   small/large-FCL, degenerate-favorable in full coverage.

**Single residual (→ Role 4):** the exact small-FCL boundary `K*_M = K°_R`
inside region (I).

**Sharpness (→ Role 3).** The condition is tight: the cofactor bracket flips
with `g(K_F) − g(K_F−K_M)`, so `g` *increasing* (high-demand states windier than
surplus — a positive demand/supply correlation) gives `dK*_R/dC_M > 0` and
`K*_R < K°_R`. That's the precise "where the triple win breaks"; worth a
targeted numerical counterexample.

## Handoffs
- **Role 2:** validate `dK*_R/dC_M` sign-law and the `C_R†` crossing across
  distribution families (we used Beta scale-mixtures; extend the sweep).
- **Role 3:** build the counterexample with `g` increasing; map the triple-win
  region vs. the demand/supply correlation.
- **Role 4:** stitch small-FCL / interior / full-coverage into one regime map;
  confirm Hessian negative-definite conditions feed Assumption 1.
