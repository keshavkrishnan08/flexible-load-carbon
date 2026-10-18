# FCL Solver (Team A1, Role 2)

Numerical solver and validator for the joint capacity problem in
*"Flexible Computing Loads, Electricity Grid Resilience, and Carbon
Emission Reduction"* (Section 4, Appendix G). Built against
`FCL_Carbon_Paper.pdf` and `newContext.md` in this directory.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Layout

```
fcl_solver/
  distributions.py       Residual-demand CDFs F(x;K_R): Uniform, Power(alpha),
                          a Primitive (D,S)-based family for genuine
                          non-self-similar distributions, and (Week 2)
                          TruncatedLognormal + lognormal_primitive() -- the
                          non-power-law family used to search for a finite
                          interior K*_R optimum. Also: pdf()/d2cdf_dKR2()
                          (Week 2, the Hessian's extra ingredients),
                          g_ratio() (the shift-ratio condition), and
                          quad_breakpoint() (a Week 2 quad-precision bugfix
                          shared by model.py/foc.py/hessian.py).
  model.py                Profit (eq.5/10), dispatch (eq.3), blackout
                          probability, carbon -- all via direct numerical
                          integration against the *extended* CDF, so the
                          same code handles both the large-FCL (K_M>K_R)
                          and small-FCL (K_M<=K_R, Appendix G) regimes with
                          no if/else branch.
  foc.py                  Hand-derived analytic gradients (dPi/dK_R, dK_F,
                          dK_M), cross-checked against finite-difference of
                          profit() in tests/test_gradients.py.
  closed_form_uniform.py  The paper's uniform-distribution closed forms
                          (eqs 18-26), independently re-derived (not just
                          transcribed) for Task 1's "match to the decimal."
  solver.py               scipy.optimize-based joint maximizer: solve_no_fcl
                          (2D), solve_with_fcl (3D), solve_with_fcl_given_KR
                          (2D at fixed K_R, used to sidestep K_R's
                          corner-solution behavior when testing eqs 18/19).
  proposition1.py         Reusable check_triple_win(dist, params) -> which
                          parts of Proposition 1 hold.
  sweep.py                Week 1 Task 4 parameter sweep (carbon vs C_R /
                          renewable-capacity-cap under Uniform/Power).
  hessian.py              (Week 2, Task 3) Analytic 3x3 Hessian of profit,
                          a finite-difference-of-gradient cross-check, and
                          certify_negative_definite() (Sylvester minors +
                          eigenvalues).
  finite_optimum.py       (Week 2, Task 2/3) find_finite_interior_optimum():
                          certifies a GENUINE finite interior optimum
                          (bound-independent, gradient~0, Hessian neg-def)
                          or reports exactly which check failed.
  finite_optimum_sweep.py (Week 2, Task 2+4) Sweeps (C_R, lognormal sigma),
                          classifying each cell into runaway / corner_zero /
                          saddle / optimizer_stalled / genuine_optimum.
tests/                    Organized by what they check (gradients, closed
                          forms, knife-edge, Prop 1, sweep regression,
                          Week 2: lognormal distribution, Hessian, finite
                          interior optimum, regularity boundary).
run_sweep.py              Week 1 sweep entry point; writes sweep_results.csv
                          and sweep_carbon_heatmap.png.
run_finite_optimum_sweep.py  Week 2 sweep entry point; writes
                          finite_optimum_sweep_results.csv and
                          finite_optimum_sweep_map.png.
```

Run everything: `.venv/bin/python -m pytest tests/ -v`.
Run the Week 1 sweep: `.venv/bin/python run_sweep.py`.
Run the Week 2 sweep: `.venv/bin/python run_finite_optimum_sweep.py`.

## What's confirmed (Task 1)

eqs 7, 9, 12, 13, 15, 18-24 were independently re-derived by hand (not
just transcribed from the OCR'd PDF) and match the general numerical
solver to floating-point precision. Two corrections to `newContext.md`'s
notes, found in the process:

- **eq. 25/26 are "carbon / c"**, i.e. expected fossil *output* (MWh), not
  emissions, confirmed by re-deriving both from scratch and finding they
  match the solver only after multiplying by `c`. The paper's own phrase
  "proportional to" already hints at this; the OCR just obscured the `c`.
- **A genuine bug caught before it shipped**: my first version of the
  with-FCL carbon closed form reused Appendix G's *small*-FCL formula
  (eq. 76) for what is actually Section 4.3's *large*-FCL eq. 26, they
  look structurally similar but the integral clips differently once
  `K_M > K_R`. Fixed and cross-checked three independent ways (direct
  quadrature, a from-scratch re-derivation, and a separate re-typing of
  the literal printed eq. 26), see `closed_form_uniform.py`'s docstrings.
- **eq. 24 is exactly 2x a direct profit-gradient calculation**, not 1x,
  a benign bookkeeping difference (doesn't flip the sign, which is all
  eq. 24 is used for). See `test_knife_edge.py`.

## What's confirmed across distribution families (Task 2/3)

Proposition 1 parts (i) profit-higher and (ii) blackout-lower hold for
**every** distribution family tested (uniform, Power with alpha=0.5/2.0,
and a Primitive D−K_R·S construction with smooth Beta marginals) whenever
`C_M < C_bar_M`. This is the paper's distribution-free claim, and it held
in every case tried, see `tests/test_proposition1.py`.

## The main finding (Task 3/4): carbon does not improve in our search

Part (iii) ("carbon may fall") is the one part of Proposition 1 the paper
itself only claims conditionally. Trying to reproduce its own worked
example (uniform distribution, C_R "small enough") led to the most
substantial finding of this pass:

1. **The with-FCL profit problem has no finite global maximum** under the
   uniform/power families. This traces directly back to Assumption 1
   (`R < c+C_F+C_M`): it forces eq. 23's coefficient on `(D_bar+K_R)` to
   always be negative, so the closed-form `K*_F` is *guaranteed* to cross
   zero and go negative at some finite `K_R`, for every valid parameter
   set. "`K*_R = infinity`" (eq. 24's positive case) is a one-directional
   FOC signal, not a literal attainable point, and once `K_M` is also
   free, the same unboundedness extends to `K_F` and `K_M` together, not
   just `K_R` (see `test_with_fcl_profit_is_globally_unbounded_under_uniform`).
2. Given that, we swept (`C_R`, a realistic cap on buildable renewable
   capacity, and distribution shape) and asked the well-posed version of
   the question: does FCL, optimized subject to that cap, ever emit less
   carbon than the (always well-posed) no-FCL benchmark?
3. **Across 150 cells in the main sweep (10 `C_R` values x 5 capacity caps
   x 3 distributions) plus 60 more cells across 4 different `R/c/C_F/C_M`
   combinations, 210 cells total, carbon improved in zero of them.**
   Profit and reliability improved in literally every cell, exactly as
   guaranteed. See `fcl_solver/sweep.py`'s module docstring for the full
   writeup, `sweep_results.csv` / `sweep_carbon_heatmap.png` for the raw
   grid, and `tests/test_sweep.py` for a fast regression check of this
   result.

This doesn't mean carbon improvement is impossible in general, only that
across a fairly wide, deliberate search we couldn't find it within the
model's economically valid domain, which is exactly the kind of "flag fast
when numbers and theory disagree" result Role 2 is supposed to surface.
Worth raising with Role 1 / the team before leaning on the carbon-reduction
claim further.

---

# Week 2

Week 2's reframe (`CONTEXT2.md`): Week 1 said "carbon never falls because
there's no finite optimum to evaluate it at." Week 2 asks the next
question directly, find a distribution + parameter regime where a
**finite, regular** (negative-definite Hessian) interior optimum genuinely
exists, and check whether carbon falls *there*. Role 1 was not reachable
this pass (no live "Role 1" session to message, see below), so the four
tasks below were built against CONTEXT2.md's own description of the
endpoint shift-ratio condition and the truncated-lognormal candidate,
flagged clearly wherever an assumption had to be made in their absence.

## A genuine quad-precision bug, found and fixed (foundational to everything below)

Building the analytic Hessian's finite-difference cross-check exposed a
real bug in code Week 1 had already shipped and validated: `scipy.integrate.quad`
can **silently mis-converge** near an undeclared discontinuity in the
integrand, reporting an estimated error of ~1e-15 while the *actual*
value is off by ~1e-4 to 1e-5. This never affected any Week-1 VALUE check
(the bias is far smaller than Week 1's tolerances), but it completely
corrupts a finite-difference SECOND derivative, which divides a fixed-size
bias by a small step `h`. Two related issues, both fixed in
`model.py`/`foc.py`/`hessian.py`:

1. **Undeclared breakpoint.** Every `ResidualDemand` here has F=0 exactly
   at and below `x=-K_R` (the "extended CDF" convention), for Uniform/Power
   this is a literal jump discontinuity in the density. Whenever a FIXED
   integration range (e.g. `[-K_M, K_F-K_M]`) straddles `-K_R`: which
   happens routinely, exactly in the paper's main "large-FCL" regime
   `K_R<K_M<K_F+K_R`: plain adaptive quad (QAGS) can mis-converge. Fixed
   by passing `points=[-K_R]` (switches scipy to QAGP) via the new
   `distributions.quad_breakpoint()` helper, used everywhere `model.py`/
   `foc.py`/`hessian.py` integrate against a fixed range.
2. **Subdivision cap.** Separately, the lognormal-primitive family's wider
   integrals were hitting `quad`'s 200-subdivision cap *before* reaching
   the requested tolerance (an `IntegrationWarning`, easy to miss). Raised
   `limit` to 1000 everywhere; confirmed against a brute-force trapezoid
   rule that this closes the gap (~1e-7 → ~1e-13).

A **third**, distinct issue was a genuine math gap, not a quad bug: the
analytic Hessian's `H_RR` entry (`d²Pi/dK_R²`) needs an extra Leibniz
"moving boundary" term whenever an integration range crosses `-K_R`,
because `dF/dK_R` itself (not just `F`) can be discontinuous there. This
term is identically zero for the *first*-order FOCs (which is why Week 1
never needed it), but not for the second derivative. Derived, implemented,
and cross-checked in `hessian.py`. See `tests/test_hessian.py` for both
fixes pinned down with worked examples.

## Task 1: a genuinely non-power-law distribution

Added `TruncatedLognormal` (lognormal D, truncated to `(0,D_bar]` and
renormalized) as a `D_dist` plug-in for `PrimitiveResidual`, with a
closed-form `pdf_prime` so the new `d2cdf_dKR2` (the Hessian's one new
ingredient beyond Week 1's `dcdf_dKR`) has a fully analytic path, not just
a finite-difference fallback. **Caught a second, more subtle issue while
validating this against the Hessian**: truncating the lognormal at `D_bar`
creates its own jump (the *D*-distribution's own density, not the
residual's), which propagates into a second, `D_dist`-specific kink in
`dcdf_dKR(x;K_R)` at `x=D_bar-K_R` and corrupted `H_RR` by 10-30% before
being diagnosed. Rather than deriving a second Leibniz correction term for
an arbitrary `D_dist`, fixed it by choosing `(mu,sigma)` so `f(D_bar)` is
numerically negligible (~1e-9), see `distributions.TruncatedLognormal`'s
"PARAMETER CHOICE WARNING" docstring for the full derivation and the
concrete before/after numbers. `pdf`/`dcdf_dKR`/`d2cdf_dKR2` all validated
to ~1e-9-1e-10 against independent finite differences
(`tests/test_lognormal_distribution.py`).

## Task 3: analytic Hessian + regularity certificate

`hessian.py` derives all six distinct entries by hand from `foc.py`'s
three gradients, cross-checked against a finite-difference-of-the-analytic-
gradient (tighter and far less noisy than double-differencing `profit()`
directly) across Uniform/Power/lognormal-primitive and both FCL regimes,
see `tests/test_hessian.py` (30 cases). `certify_negative_definite()`
applies two independent criteria (eigenvalues, Sylvester leading minors)
and checks they agree.

**Found and documented a genuine case where the Hessian does not exist at
all**, not just "is hard to compute": `PowerResidual(alpha<1)`'s `dF/dK_R`
diverges (not merely "is large") approaching the support edge from inside
confirmed the divergence follows the predicted `eps^(alpha-1)` power law
exactly (`tests/test_regularity_boundary.py`). Whenever `K_M>K_R` for such
a distribution, `H_RR` is not a finite number; `power_alpha_0.5` is
excluded from the Hessian cross-check tests at exactly those points, with
the reason documented rather than silently skipped.

## Task 2 (the keystone) + Task 4: a genuine finite interior optimum, and what happens there

**Finding #1, the distribution family alone does not fix Week 1's
unboundedness.** Re-running Week 1's exact `valid_params` (`C_R=8`) under
the new lognormal-primitive family: the with-FCL profit problem **still
runs away**, `K_M` keeps hitting whatever bound is given, with a gradient
that stays persistently positive (~+22) rather than shrinking toward zero,
exactly like Week 1's Uniform/Power finding. The root cause was never the
distribution's self-similarity in `K_R` per se; it's that once renewable
capacity is abundant enough to make deep curtailment near-certain, the
marginal value of FCL hardware approaches `R-C_M>0` (guaranteed positive
under Assumption 1) *regardless of distribution*, and nothing stops `K_R`
and `K_M` from growing together to keep harvesting that margin unless
`C_R` is expensive enough to outweigh it.

**Finding #2, raising `C_R` into the right window produces a genuine,
certified finite interior optimum.** For this `(R,c,C_F,C_M,beta,p)`
combination, a window of `C_R` exists (roughly 21-27) between "runs away"
(low `C_R`) and "collapses to `K_R=0`" (high `C_R`) where the optimizer
finds a point that is: bound-independent (identical result at 4x and 15x
`D_bar` bounds), a genuine FOC stationary point (`‖grad‖ < 1e-3`), and a
true local maximum (Hessian strictly negative definite, both certificate
criteria agreeing). E.g. at `C_R=25`: `K*=(25.3, 26.6, 9.2)`
(small-FCL regime, `K_M<K_R`). See `tests/test_finite_interior_optimum.py`.

**Finding #3, carbon does not fall there either.** At that exact
certified optimum: profit and blackout probability both improve over the
no-FCL benchmark (exactly as Proposition 1 parts (i)/(ii) guarantee,
distribution-free), but **carbon is higher, not lower**
(`carbon_change ≈ +204`, i.e. ~37% worse). This is the central Week 2
result: even once Week 1's main objection, no finite optimum exists, so
the question was never well-posed, is fully resolved, carbon still does
not improve in this instance.

**Finding #4, a discrepancy with the endpoint shift-ratio condition,
flagged for Role 1.** At this same optimum, `K*_R > K_R°` (renewable
capacity DID increase relative to the no-FCL benchmark), but the
endpoint shift-ratio condition `g(K_F*) >= g(K_F*-K_M*)` (using
`g(x)=F_{K_R}(x)/f(x)`, per CONTEXT2.md's definition) is **FALSE** there
(0.261 < 0.314). If the condition is meant to be necessary for
`K*_R>K_R°` (not just sufficient), this is a direct counterexample worth
reconciling against Role 1's exact theorem statement, flagged explicitly
in `tests/test_finite_interior_optimum.py` rather than smoothed over,
since Role 1 could not be reached for clarification this pass (no
addressable "Role 1" agent session was available when checked).

**The broader sweep** (`run_finite_optimum_sweep.py`, 76 cells: 19 `C_R`
values from 8 to 44 in steps of 2, x 4 lognormal `sigma` values
0.2/0.28/0.4/0.6) confirms this is not a one-off:

```
  corner_zero:      36/76 (47%)
  runaway:          32/76 (42%)
  genuine_optimum:   8/76 (11%)
  saddle:            0/76
  optimizer_stalled: 0/76

  Among 8 genuine (finite, regular, interior) optima found:
  carbon_lower in 0/8.
```

Two more findings from the full grid (see `finite_optimum_sweep_results.csv`
/ `finite_optimum_sweep_map.png` for the raw data):

- **The `genuine_optimum` window is remarkably stable across `sigma`**:
  for every one of the four `sigma` values tried, the window is exactly
  `C_R ∈ {24, 26}` at this grid resolution (i.e. roughly `(22,28)`),
  raising the lognormal's tail thickness shifts the optimum's location
  (`K_R*` grows from ~25 at `sigma=0.2` to ~39 at `sigma=0.6`) but not
  the `C_R` window where a regular interior optimum exists at all.
- **The sharpest single counterexample, at `sigma=0.6, C_R=26`**: the
  endpoint shift-ratio condition is **TRUE** here (`g(K_F*)=0.379 >=
  g(K_F*-K_M*)=0.368`), i.e. Role 1's proposed mechanism for `K_R*>K_R°`
  genuinely fires, not just incidentally, and `K_R*=38.6 > K_R°=11.3`
  exactly as the condition is meant to predict. **Carbon still rises by
  +545 (~71% worse than the no-FCL benchmark)** while profit and
  reliability both still improve. This is the one case across the whole
  sweep where the condition's own claimed mechanism is unambiguously
  active, and it still does not produce a carbon improvement, see
  `test_shift_ratio_condition_holding_still_does_not_save_carbon`.
- **No `saddle` cells were found anywhere in this grid**: for the
  lognormal-primitive family, the Hessian-regularity boundary coincides
  exactly with the `runaway`/`genuine_optimum`/`corner_zero` transitions
  found by the bound-independence check, there is no separate
  indefinite-Hessian region at this resolution. The `PowerResidual(alpha<1)`
  divergence (Task 3/4 above) remains the sharper, closed-form regularity
  failure example for this codebase.

## Summary for the team

- Tasks 1 and 3 are complete and machine-validated: the solver now handles
  a genuinely non-power-law distribution to ~1e-9-1e-10 precision, and the
  analytic Hessian + regularity certificate are ready for Role 3's
  comparative-statics work (the cofactors/eigenvalues they need are
  exposed via `hessian.hessian()` / `hessian.certify_negative_definite()`).
- Task 2's keystone question has a concrete, reproducible answer across
  **8 independently certified finite interior optima** spanning 4 lognormal
  shapes: **carbon never fell at any of them** (0/8), extending Week 1's
  finding to the well-posed case Week 2 was designed to test. The
  `sigma=0.6, C_R=26` cell is the headline result to report back to
  Role 1 first, it's the one place the shift-ratio condition's own
  mechanism is confirmed active (condition TRUE, `K_R*` did increase) and
  carbon still rose 71%, so it can't be dismissed as "the condition just
  didn't apply here." Bring this alongside the quad bugfix (it may matter
  for Role 1's or Role 4's own numerics if they independently re-derive
  any second-order quantity).
- Task 4 has two concrete, opposite-flavor regularity-boundary examples:
  `PowerResidual(alpha<1)` (the Hessian provably does not exist past a
  sharp `alpha=1` threshold, a closed-form divergence) and the
  lognormal-primitive `(C_R,sigma)` sweep (maps `runaway` /
  `genuine_optimum` / `corner_zero`; no separate `saddle` region turned up
  at this grid resolution, so the regularity boundary there coincides with
  the bound-independence transitions rather than an internal indefinite
  zone).
- **I attempted to reach "Role 1" via the team messaging system for the
  exact primitive condition, distribution family, and "Condition 2"
  statement before starting (per CONTEXT2.md's open items), no
  addressable session was available.** Everything above was built from
  CONTEXT2.md's own description; Findings #1 and #4 are the places most
  likely to need reconciling against Role 1's actual theorem once they're
  reachable.
