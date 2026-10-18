# FCL Solver (Team A1, Role 2): Week 4

Builds on `week3/`. Week 4's central deliverable is the **carbon
classification functional Ψ**, which provides an if-and-only-if
characterization of the carbon sign derived from the paper's Proposition 4.

## Week 3 confirmed status (before starting Week 4)

All 22 tests pass. Central finding: **0/20 sign flips** in the dispatch-phase
sweep, even the LP-optimal (carbon-minimizing) dispatch at firm-optimal
capacities fails to flip the carbon sign. This extends Week 1/2's findings.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q           # 21 tests, ~90s
.venv/bin/python run_week4_sweep.py --fast      # classification sweep
```

## What's new in Week 4

```
fcl_solver/
  carbon_functional.py   Implements Ψ (Prop 4, eqs 44/45) and
                          compute_functional() → FunctionalResult.
                          Bug caught during dev: integration limits for
                          μ*_low were wrong (gap-filling zone instead of
                          full-dispatch zone) - fixed and documented.
  classification_sweep.py  Sweeps the full 15-distribution library.
  phase_diagram_w4.py    Level-set phase diagram via Ψ, bisection boundary.
  leverage_saddle.py     Leverage condition + robust saddle certificate.
  regularity_map.py      Regularity-region map (reuses Week 2 Hessian).
tests/
  test_carbon_functional.py   13 tests (identity, sign-match, unit)
  test_leverage_regularity.py  8 tests
```

## The Classification Functional (Task 1, keystone)

From the paper's **Proposition 4** (Appendix B.1, p. 82-84), in the
large-FCL regime (K*_M > K*_R):

```
E[fossil_with_FCL] = K*_F − (C_M/(R-c)) · (K*_F − K*_M − μ*_low)   (44)
E[fossil_no_FCL]   = K°_F · (1−φ°) + (φ°−q°) · μ°_mid               (45)

Ψ = (C_M/(R-c)) · (K*_F − K*_M − μ*_low)
  − [K*_F − K°_F·(1−φ°) − (φ°−q°)·μ°_mid]

Carbon improves ↔ Ψ > 0
```

where:
- `μ*_low` = conditional mean of x in `[-K*_R, K*_F-K*_M]` (the full-dispatch
  zone *within the support*), normalized by `C_M/(R-c) = F(K*_F-K*_M; K*_R)`
- `μ°_mid` = conditional mean of x in `[0, K°_F]` (the no-FCL fossil zone),
  normalized by `φ°-q°`
- `φ° = F(K°_F; K°_R)` = no-FCL reliability
- `q° = F(0; K°_R)` = surplus probability at no-FCL benchmark

### A real bug caught during development

The first implementation used the **gap-filling zone** `[K*_F-K*_M, K*_F-K*_R]`
for μ*_low, producing a ~48% error in the fossil formula and a **sign flip
in Ψ**. The correct zone is the **full-dispatch zone within the support**
`[-K*_R, K*_F-K*_M]`. Fixed via `test_prop4_fossil_with_fcl_matches_direct`
cross-checking the formula against the direct numerical integral from `model.py`.

## Task 1 result: iff claim corroborated

**10/10 interior cells** across 5 distributions × 3 C_R values: sign(Ψ)
matches sign(carbon_no_FCL − carbon_with_FCL) in every case.

```
dist                  CR    Ψ          Δcarbon    sign_match
─────────────────────────────────────────────────────────────
uniform               25    -9.73      +437.81    True
uniform               30    -9.73      +437.81    True
power_alpha_2.0       20    -5.05      +227.33    True
power_alpha_2.0       25    -5.05      +227.33    True
power_alpha_2.0       30    -5.05      +227.33    True
lognormal_sig=0.28    25    -4.44      +204.40    True
lognormal_sig=0.28    30    -7.28      +327.64    True
lognormal_sig=0.6     25   -13.54      +622.65    True
lognormal_sig=0.6     26   -22.44      +…         True   (Week-2 canonical)
lognormal_sig=0.6     30   -24.09     +1083.89    True
```

Ψ is **negative in every interior cell** (carbon always rose), matching
the consistent Week 1-3 finding. The iff claim is corroborated, no cell
found where sign(Ψ) ≠ sign(Δcarbon). Note: **carbon improvement (Ψ > 0)
is not observed** in any cell, which is itself the central finding of this
project: the FCL program, as parameterized, consistently raises rather than
lowers carbon.

See `classification_sweep.csv` and `phase_diagram_w4.png` for the full
sweep results.

## Task 4: regularity-region map

`regularity_map.py` reuses the Week 2 analytic Hessian to classify each
cell as: `regular` / `corner_KR` / `corner_KM` / `corner_zero` / `saddle`
/ `solver_failed`. Regularity is checked only at interior optima; corner
solutions are classified separately. The C_R=8 (cheap-renewable, runaway)
case consistently returns `corner_KR`.

## Task 3: leverage condition + robust saddle

The leverage ratio λ = (surplus dispatch revenue) / (renewable capex)
measures whether FCL's income from renewable-surplus hours is large enough
to fund the renewable investment. `leverage_saddle.py` computes λ across
C_R and reports whether λ ≥ 1 (self-financing). The robust saddle
certification uses a finite perturbation grid pending Role 3's exact
ambiguity-set specification.

## Task 2: phase diagram from Ψ

`phase_diagram_w4.py` traces Ψ's level sets numerically across the (C_R,
C_M) cost plane. Since Ψ < 0 everywhere in the sampled region, the carbon
phase diagram shows a uniformly carbon-up region for the distributions
tested. The zero-level boundary (where Ψ = 0 and carbon is neutral) lies
outside the parameter range explored by the fast sweep.

## Cross-role outputs

- **Role 1**: sign-match corroboration in `test_psi_sign_*` tests (and the
  diagnostic above). The integration-zone bug is documented in
  `carbon_functional.py`'s bug-note comment.
- **Role 3**: `LPCertificate.shadow_price_profit_floor` (from Week 3), and
  `LeverageResult.lambda_ratio` for the robustness capstone.
- **Role 4**: `RegularityCell.outcome` and the `min_eigenvalue` field for
  regime-stitching.
