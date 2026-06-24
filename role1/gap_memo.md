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

## Where it resists (the honest boundary)

1. **Submodularity obstruction.** `Π` is submodular in `(K_R, K_F)`
   (`∂²Π/∂K_R∂K_F = (R−β−p)F_{K_R}(K_F) − (R−c)F_{K_R}(K_F−K_M) ≤ 0`) but has
   increasing differences in `(K_R; K_M)` and `(K_F; K_M)`. The sign conflict
   means **no single reorder restores supermodularity**, so a one-line Topkis
   argument fails. The homotopy-in-`C_M` proof works but needs interiority and a
   negative-definite Hessian *along the whole path* — both verified numerically,
   not yet shown in closed form for arbitrary `F`.
2. **Endogenous-capacity feedback in (C).** Corollary 1's concave/convex
   density conditions hold the FOC-pinned cutoff probabilities fixed. A fully
   general carbon statement must also track how `K*_R, K*_F` move with the
   *shape* of `F` (a second-order feedback). Unsigned in closed form so far.
3. **`C_R†` not explicit.** Theorem 2 proves the renewable-cost threshold
   exists; closed form only for power-law (the knife-edge eq 24).
4. **Regime stitching.** Proof assumes large-FCL interior regime along the path.
   Small-FCL (App. G, wider threshold `C̄_M + cF(0;K°_R)`) and full-coverage
   (`R ≥ c+C_F+C_M`) boundaries still need a single unified statement → Role 4.
5. **Counterexample direction.** The shift-ratio condition is **sharp**: when
   `g` is *increasing* (high-demand states windier than surplus states — a
   positive demand/supply correlation), `dK*_R/dC_M > 0` and `K*_R < K°_R`, so
   the capacity channel reverses. This is the precise statement of "where the
   triple win breaks," and Role 3 should target it numerically.

## Handoffs
- **Role 2:** validate `dK*_R/dC_M` sign-law and the `C_R†` crossing across
  distribution families (we used Beta scale-mixtures; extend the sweep).
- **Role 3:** build the counterexample with `g` increasing; map the triple-win
  region vs. the demand/supply correlation.
- **Role 4:** stitch small-FCL / interior / full-coverage into one regime map;
  confirm Hessian negative-definite conditions feed Assumption 1.
