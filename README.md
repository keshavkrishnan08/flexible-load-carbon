# Team A1 — Flexible Computing Loads, Grid Resilience, and Carbon Emissions

**Workstream A1: General Carbon/Contracting Theory and Numerical Methods.**
This is the integrated A1 deliverable: one general theory of when flexible
computing loads (FCLs — Bitcoin mining, AI training) reduce carbon emissions by
financing renewable capacity, with a numerical-methods backend and
cross-validation. Built on `FCL_Carbon_Paper` (§3 model, §4 baseline, App. B.1,
App. G, Prop. 4, footnote 6).

> **Scope.** A1 owns the *theory* (general distributions, the carbon condition,
> the contract, mechanism design) and the *numerical methods*. It does **not**
> cover empirical calibration with real data (A2), reliability/welfare/social-vs-
> private pricing (B1), or the flexibility continuum / storage / multi-grid /
> dynamics (B2).

## The one-paragraph result
Introducing an FCL demand-response program with capacity `K_M` changes the
utility's optimal mix `(K_R, K_F, K_M)`. Two forces act on carbon: a
distribution-free **utilization effect** (computing burns spare fossil, raising
emissions) and a **capacity-substitution effect** (FCL revenue `R>c` raises the
shadow value of renewables, so `K_R* > K_R°`, lowering emissions). Whether carbon
falls is governed by a single transparent primitive — the **shift ratio**
`g(x)=F_{K_R}/f = E[S | x̃=x]`, the conditional renewable factor — and by the
renewable cost `C_R`: carbon falls iff renewables are cheap enough (`C_R < C_R†`)
and demand–supply association is sufficiently negative (`g` non-increasing). The
adoption threshold `C̄_M=(R−c)φ°` and the bounds `C_R†, C_R°, C̄_M^b` are in closed
form; the carbon effect at fixed capacities reduces to two conditional means and
is worst-cased (within the monotone-density class) by the uniform.

## Who did what (and how it connects)
| Role | Deliverable | Connects to |
|---|---|---|
| **Role 1** — General Carbon Theory | `role1/role1_carbon_theory.tex` (11pp): the capacity-substitution channel `K_R*>K_R°` (homotopy+cofactor), the exact net-carbon condition (C), the viability threshold `C_R†`, the distribution-free reading; 15/15 machine-precision audit; 3-referee review. | Provides the closed forms (`C_R†, C_R°, C̄_M^b`, eq-24=`2(C_R†−C_R)`) used by Roles 3–4. |
| **Role 2** — Solver & Numerical Validation | `role2/fcl_solver/` (36 tests): joint-capacity solver, closed-form uniform benchmarks, FOCs, knife-edge, sweep. | The validation backend; vendored unchanged into Role 4. Confirms Role 1's eqs 25/26 and corrections. |
| **Role 3** — Comparative Statics | `role3/` : Prop-1 distribution-free checks, carbon-sign map across distributions, §5.3 timing, Role-1 stress-test. | **Empirically confirms Role 1**: `K_R*>K_R°` 32/32; carbon falls only at low `C_R`+right-skew (Role 1's threshold). |
| **Role 4** — Theory Hardening & Regimes | `role4/THEORY_HARDENING.md` (17 tests): re-verifies eqs 12/13/15 + Prop 1, completes small-FCL (eq 62), stitches regimes, pressure-tests Assumption 1. | **Uses Role 1's closed forms**; reconciles Role 1 (theory) ↔ Role 2 (numerics) via the buildout crossover. |

## How the pieces interlock (the "110% connected" map)
- **Closed forms flow Role 1 → Roles 3, 4.** `C̄_M`, `C_R†=½[c+(R−C_M−c)²/(R−c)+(R−c−C_F−C_M)²/(β+p−R)]`,
  `C_R°=C_F²/2(β+p−c)`, `C̄_M^b=C̄_M+c·q°`, and eq-24`=2(C_R†−C_R)` are derived in
  Role 1 and re-used verbatim in Role 4 (`role4/regimes.py`) and tested in Role 3.
- **Role 2's solver is the common backend.** Role 1's analytic formulas, Role 3's
  sweeps, and Role 4's checks all validate against the same quadrature solver
  (vendored into `role4/fcl_backend/` with a NOTICE).
- **Cross-validation closes the loop.** Role 1 *proves* `K_R*>K_R°`; Role 3
  *confirms* it 32/32; Role 4 *re-derives* the FOC that produces it. Role 1
  predicts carbon falls only for small `C_R`; Role 3 *finds* exactly that; Role 4
  *explains* the buildout crossover that reconciles "theory says falls / early
  numerics say never."
- **Shared honesty.** All four independently flag the same residual: the general-`F`
  net-carbon Step 3 is conditional (proven for uniform/power-law, conjectural in
  full generality). No role overclaims.

## Reproduce everything
```bash
bash run_all.sh        # runs Role 1 audit + Role 2/4 pytest + Role 3 experiments
```
See `INTEGRATION.md` for the consistency check and the combined results table,
and `A1_deliverables/A1_Week2_NextRoles.pdf (Word) and A1_deliverables/A1_integrated_paper.pdf` for the parallelized plan that takes A1 to a
Management-Science-ready submission.
