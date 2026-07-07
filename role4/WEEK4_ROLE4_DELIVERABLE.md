# Role 4 Week 4 — Theory Hardening and Regimes

This is the final Role 4 Week-4 layer. It reuses the already-tested regime-stitching, hardening, phase-map, and reconciliation modules, then exposes one acceptance module: `role4/week4.py`.

## Week-4 object

Role 4 uses the stitched classifier

```text
Lambda(C_M, C_R) = C_R^dagger(C_M) - C_R
```

with the sign convention:

```text
Lambda > 0  => carbon down
Lambda = 0  => neutral boundary
Lambda < 0  => carbon up
```

The boundary is

```text
C_R^dagger(C_M) = 1/2 [ c + (R-C_M-c)^2/(R-c) + (R-c-C_F-C_M)^2/(beta+p-R) ].
```

## Bullet 1 — Extend the functional across regimes

`week4.extend_functional_across_regimes(P)` verifies that the carbon integral stitches continuously and `C^1` across the small-/large-FCL boundary `K_M=K_R`. The classifier boundary is smooth across the regime-form line `C_M^cross`; the only located discontinuity is in the profit Hessian, not the carbon functional.

## Bullet 2 — Harden the converse

`week4.harden_converse(P)` collects the measure-theoretic scaffolding required by the necessity/converse side: compact capacity box iff `C_R >= C_R^dagger`, Borel-measurable extremal dispatch schedule, IC/IR constraint qualification, convex monotone-density ambiguity set, linearity of the carbon functional in the law, and Sion saddle only when the capacity set is compact. It explicitly flags the carbon window as ill-posed for the robust capacity problem.

## Bullet 3 — Regime-map the classification

`week4.regime_map_classification(P)` returns the stitched phase diagram over the full `(C_M,C_R)` cost plane. The carbon-down region is connected, spans both small- and large-FCL regimes, and crosses the regime-form line exactly once. The ordering is

```text
C_M^fc < C_M^cross < C_M_bar < C_M_bar^b.
```

## Bullet 4 — Reconcile the team

`week4.reconcile_team(P)` checks the shared contract, carbon functional, and robust optimum against the available Role 1 theory files and Role 2 backend. The contract and carbon functional are consistent; the robust optimum is consistent where well-posed and flagged where the capacity problem is ill-posed on the carbon-reduction window.

## Run

```bash
python -m pytest -q
python run_analysis_week4.py
```

Validated locally after the Week-4 patch: `70 passed`.
