# Miner Demand (Team A1, Role 4)

Miner-side theory and numerical validation for *"Bitcoin Mining (and maybe
AI training) for Carbon Emission Reduction"* (Li, Ren, Bellos) — the
oligopoly mining-demand foundation (Section 3.4.1, eqs 9–10), the revenue-
exogeneity result behind the Section 3.5 duality, and the partial-grid
extension (Appendix A, eqs 61–68). Built against
`Bitcoin_Mining_for_Carbon_Emission_Reduction.txt` and `CONTEXT.md` in this
directory. Proofs are in `derivations.md`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Layout

```
miner_demand/
  oligopoly.py        Tasks 1-2. Equilibrium demand d=(1-1/n)R/P (eq.10),
                       price inducement (its inverse), the exogenous
                       revenue P*d=(1-1/n)R, and an independent
                       best-response root-find that re-derives eq.10
                       without using it.
  partial_grid.py      Task 3. The n in-grid + m out-of-grid game
                       (eqs 61-68): total demand (eq.65), in-grid demand
                       (eq.68), the m>>n limit, the nR/4 revenue peak, the
                       P<=Po and nR/(2Po) bounds, and a check that revenue
                       exogeneity BREAKS. Eq.68 is validated against an
                       independent two-price FOC-system solve.
  demand_response.py   The clean (Section 3.6.3) and adapted (eq.69)
                       demand-response programs that shape d(D,S).
  emissions.py         A numerical probe (uniform case) of whether the
                       adapted program reduces carbon vs no-mining -- the
                       "does the result survive the partial grid" question.
tests/                 29 pytest cases, organized by task (oligopoly,
                       exogeneity, partial grid, demand response/emissions).
run_sims.py            Task 4 entry point: figures + emissions sweep.
derivations.md         Lemma/Proposition statements and proofs (the
                       written theory deliverable), each cross-referenced
                       to the test that guards it.
```

Run everything: `.venv/bin/python -m pytest tests/ -q` (29 passed, ~0.1s).
Run the sims: `.venv/bin/python run_sims.py` (writes two figures, a CSV,
and a heatmap).

## What's confirmed (Tasks 1–2)

Eqs 9–10 and the exogeneity result were re-derived by hand (see
`derivations.md`, Lemma 1 / Prop. 2) and cross-checked numerically:

- **eq. 10** (`d = (1-1/n)R/P`) matches an independent best-response
  root-find — i.e. solving miner *i*'s eq.(9) FOC to a fixed point without
  ever using eq.10 — to ~1e-9 across prices.
- **Inducement is a bijection**: every target demand round-trips through
  `P* = (1-1/n)R/d*` exactly, and each miner's equilibrium profit is
  `R/n² ≥ 0` *independent of P*, so participation never binds — the
  regulator really can hit any mining quantity.
- **`P·d = (1-1/n)R` is numerically constant** across four orders of
  magnitude of `P` (derivative w.r.t. `P` is 0 to ~1e-9), which is the exact
  property that collapses the utility's profit problem into Section 3.5's
  cost-min problem.

One implementation note worth recording: naive *simultaneous* best-response
iteration diverges once `n` is large (the `-(n-1)·d_others` slope makes the
Jacobi map non-contracting). The independent validator therefore root-finds
the best-response fixed point directly (Brent) rather than iterating — same
equilibrium, but actually convergent. Caught while the first version of
`test_oligopoly` failed to converge.

## What's confirmed across the partial grid (Task 3)

`derivations.md` Prop. 3. Eq. 68 matches an independent two-price FOC-system
solve (`scipy.fsolve` on eqs 61–62) to ~1e-7; the `m≫n` limit, the `nR/4`
revenue peak at `P=Po/2`, the `d≥0 ⇔ P≤Po` cutoff, and the `nR/(2Po)` usable-
inducement cap all check out.

The headline of Task 3: **revenue exogeneity breaks in the partial grid.**
In the full grid `P·d` is flat (exogenous); once miners can leave for `Po`,
`P·d` is a concave parabola peaking at `nR/4`, so profit-max no longer equals
cost-min. `sim_revenue.png` shows the flat line vs the hump side by side.

A small discrepancy to flag: the paper calls `P·d` "approximately exogenous
if `P` is not too far from `Po`." Numerically that's safe only near the
revenue peak `Po/2`; as `P→Po` in-grid demand collapses and `P·d` varies
steeply. The "approximately exogenous" reading should be stated around
`Po/2`, not near `Po`. (Noted in `derivations.md`, Prop. 3 Remark — worth
confirming with the authors.)

## The main finding (Task 3/4): carbon doesn't fall in the cost-min probe — and the miner-side reason why

`emissions.py` asks the natural follow-up: under the bounded inducement of
the partial grid, does the adapted program (eq. 69) still cut carbon? Across
**756 parameter cells** (renewable cost, fossil cost, mining floor, supply
spread) emissions never drop below the no-mining benchmark — consistent with
what Role 2 found on the FCL side.

The Role 4 contribution is the *reason*, which is exactly Prop. 3: in the
partial grid the surplus-absorbing mining channel is **capped at `nR/(2Po)`**,
so it can't do the heavy lifting, and the only other lever — fossil-fed
mining when renewables fall short — adds emissions directly while only weakly
inducing extra capacity.

**This does not contradict the paper.** The paper's Appendix-A reduction is
derived from the grid's *profit* problem (eq. 70), not cost-minimization —
precisely because Prop. 3 shows cost-min is no longer the right object once
exogeneity breaks. So the faithful emissions test has to couple this miner-
side result to **Role 1's** regulator/profit optimization. That coupling is
the main thing to sync before anyone leans on the partial-grid carbon claim.
See `emissions_sweep.csv` / `emissions_heatmap.png` for the grid and
`tests/test_emissions.py` for the regression guard.
