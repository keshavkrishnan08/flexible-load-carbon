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
                          and a Primitive (D,S)-based family for genuine
                          non-self-similar distributions (Task 2).
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
  sweep.py                Task 4 parameter sweep + the main written-up
                          finding (see below).
tests/                    36 pytest cases, organized by what they check
                          (gradients, closed forms, knife-edge, Prop 1,
                          sweep regression).
run_sweep.py              Entry point for the sweep; writes
                          sweep_results.csv and sweep_carbon_heatmap.png.
```

Run everything: `.venv/bin/python -m pytest tests/ -v` (36 passed, ~95s).
Run the sweep: `.venv/bin/python run_sweep.py`.

## What's confirmed (Task 1)

eqs 7, 9, 12, 13, 15, 18-24 were independently re-derived by hand (not
just transcribed from the OCR'd PDF) and match the general numerical
solver to floating-point precision. Two corrections to `newContext.md`'s
notes, found in the process:

- **eq. 25/26 are "carbon / c"**, i.e. expected fossil *output* (MWh), not
  emissions — confirmed by re-deriving both from scratch and finding they
  match the solver only after multiplying by `c`. The paper's own phrase
  "proportional to" already hints at this; the OCR just obscured the `c`.
- **A genuine bug caught before it shipped**: my first version of the
  with-FCL carbon closed form reused Appendix G's *small*-FCL formula
  (eq. 76) for what is actually Section 4.3's *large*-FCL eq. 26 — they
  look structurally similar but the integral clips differently once
  `K_M > K_R`. Fixed and cross-checked three independent ways (direct
  quadrature, a from-scratch re-derivation, and a separate re-typing of
  the literal printed eq. 26) — see `closed_form_uniform.py`'s docstrings.
- **eq. 24 is exactly 2x a direct profit-gradient calculation**, not 1x —
  a benign bookkeeping difference (doesn't flip the sign, which is all
  eq. 24 is used for). See `test_knife_edge.py`.

## What's confirmed across distribution families (Task 2/3)

Proposition 1 parts (i) profit-higher and (ii) blackout-lower hold for
**every** distribution family tested (uniform, Power with alpha=0.5/2.0,
and a Primitive D−K_R·S construction with smooth Beta marginals) whenever
`C_M < C_bar_M`. This is the paper's distribution-free claim, and it held
in every case tried — see `tests/test_proposition1.py`.

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
   FOC signal, not a literal attainable point — and once `K_M` is also
   free, the same unboundedness extends to `K_F` and `K_M` together, not
   just `K_R` (see `test_with_fcl_profit_is_globally_unbounded_under_uniform`).
2. Given that, we swept (`C_R`, a realistic cap on buildable renewable
   capacity, and distribution shape) and asked the well-posed version of
   the question: does FCL, optimized subject to that cap, ever emit less
   carbon than the (always well-posed) no-FCL benchmark?
3. **Across 150 cells in the main sweep (10 `C_R` values x 5 capacity caps
   x 3 distributions) plus 60 more cells across 4 different `R/c/C_F/C_M`
   combinations — 210 cells total — carbon improved in zero of them.**
   Profit and reliability improved in literally every cell, exactly as
   guaranteed. See `fcl_solver/sweep.py`'s module docstring for the full
   writeup, `sweep_results.csv` / `sweep_carbon_heatmap.png` for the raw
   grid, and `tests/test_sweep.py` for a fast regression check of this
   result.

This doesn't mean carbon improvement is impossible in general — only that
across a fairly wide, deliberate search we couldn't find it within the
model's economically valid domain, which is exactly the kind of "flag fast
when numbers and theory disagree" result Role 2 is supposed to surface.
Worth raising with Role 1 / the team before leaning on the carbon-reduction
claim further.
