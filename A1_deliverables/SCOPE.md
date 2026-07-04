# Workstream A1 -- Scope (and the A1/A2 boundary)

**A1: General theory and numerical methods.** The general carbon result plus the solver.
Nothing empirical, nothing welfare, nothing market-structure.

This file fixes the boundary so no A1 work drifts into A2 or the B workstreams, and so
A2 knows exactly what it inherits.

## What A1 owns

- The **general model** and its mathematical properties: existence, uniqueness, the
  recursive-triangular structure, the capacity-substitution channel.
- The **general carbon result**: conditions and signs for when a flexible load reduces
  emissions, distribution-free / shape-independent statements, the exact bounds, and the
  **optimal-contract theory** (the surplus contract, the decarbonization theorem, the
  carbon--profit *positive menu*).
- The **solver and numerical methods**: the joint-capacity/dispatch solver and the
  verification suites, run on **synthetic, theory-tied** distribution families
  (Beta scale mixtures, power-law) to check identities to machine precision.

A1's claims are **qualitative and structural**: signs, conditions, existence,
monotonicity, closed forms. A1 fixes parameters only to *illustrate* and *verify* the
theory, never to estimate a real-world number.

## What A1 does NOT do (the boundaries)

| Question | Owner |
|---|---|
| Real grid data (ERCOT dispatch, EIA generation/capacity) | **A2** |
| The **magnitude** of the effect (MWh, tCO2) at real parameters | **A2** |
| Calibration and empirical sensitivity / robustness on real params | **A2** |
| Reliability/**welfare**, blackout-**versus**-emissions trade-off, private-vs-social optimum | **B1** |
| Beyond Bitcoin: general flexible loads, storage, multi-grid | **B2** |
| Different **market structures**; large flexible-load data | **B3** |

## The A1 -> A2 handoff (what A2 inherits)

A2 takes A1's model, solver, and closed forms as **given** and grounds them in data:

- the **solver** (validated to machine precision on synthetic families) to plug real
  ERCOT/EIA inputs into;
- the **closed-form objects** to calibrate against: the cost cutoffs
  $\varphi_1,\varphi_2,\varphi^\circ$, the viability threshold $C_R^\dagger$, the
  capacity channel $K_R^*>K_R^\circ$, the exact net-carbon inequality;
- the **conditions to test empirically**: the adoption condition $C_M<R\,F(0;K_R^\circ)$,
  the surplus-contract decarbonization, the sign of the carbon effect at real parameters.

A2 produces the *magnitude* ("how many tCO2, and does the sign survive at real
parameters"); A1 produces the *structure* ("here is the sign, the condition, and the
contract that delivers it"). A2 adds no new theory; A1 makes no empirical magnitude claim.

## Self-check (current A1 deliverables)

- Week-1/2/3 theory + `verify_week*.py`: use only synthetic Beta/power-law families;
  no ERCOT/EIA, no tCO2/MWh magnitude claims, no calibration to real data. **In A1 scope.**
- The Week-3 carbon--profit frontier is a **positive** object (the menu of contracts and
  their carbon and firm profit). The **normative selection** of a point on it -- the
  welfare / private-vs-social question -- is **B1's**; A1 only characterizes the menu and
  notes reliability is *held* (a positive fact, not a blackout-vs-emissions analysis).
