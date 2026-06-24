# Lab Notebook — Team A1, Role 1 (General Contracting Theory & Numerical Methods)

A running research log: what was attempted, what was derived, what was verified,
what broke, and what was deliberately *not* done (scope). Newest entries at the
bottom. Every analytical claim is cross-checked numerically before it enters a
`.tex`; the verifier and the digit-level agreement are noted in brackets.

**Mandate (A1).** Place the central result on rigorous, general footing:
(1) existence + full characterization of the optimal demand-response contract
`d*(x)` under general distributions, with **necessary-and-sufficient** emission
conditions; (2) prove the **correlation comparative static** and that mining
raises optimal renewable capacity `K*_R > K°_R`; (3) strengthen the
**mechanism design** (regulator-principal / utility-agent), optimality + uniqueness;
(4) document numerical methods the group can rely on.

**Scope guards (hard walls).** Do **not** enter:
- **A2** — empirical calibration, real-data magnitudes, grid-type illustrations.
- **B1** — reliability, blackout-vs-emission tradeoff, welfare, social-vs-private
  optimum, corrective pricing.
- **B2** — flexibility continuum, AI/storage, multi-grid, price exogeneity, dynamics.
Anything touching those is logged as "dropped (out of scope)".

---

## E1 — Ground truth: re-derive the uniform closed forms
Goal: reproduce paper eqs 18–26 by hand from the FOCs before generalizing.
- Re-derived no-FCL `K°_F, K°_R` (eqs 20–21) and with-FCL `K*_F, K*_F−K*_M`
  (eqs 22–23) from the cutoff FOCs under `F=(x+K_R)/(D̄+K_R)`.
- Carbon eqs 25/26: confirmed they are expected fossil **output** (the constant
  `c` is dropped); the large-FCL form needs the flat term `(K_M−K_R)` because the
  integration range protrudes below `−K_R`.
- **Verified** [`verify.py`]: eqs 25/26 match direct quadrature to ≤6e-10; the
  capacity forms satisfy the FOCs to ≤1e-15.
- **Knife-edge** proven for the whole power-law family: marginal value of `K_R`
  along the locus is constant in `K_R` ⇒ corner solution. Re-derived the
  threshold and found it equals **exactly** the printed eq-24 bracket; clarified
  eq 24 = `2·∂Π/∂K_R` (sign-correct; the factor-2 is a grouping artifact, not a
  bug — reconciles Role 2's note).

## E2 — The capacity channel `K*_R > K°_R`, general
- Computed the cross-partials of `Π`. Found the obstruction: `Π` is **submodular**
  in `(K_R,K_F)` (`∂²Π/∂K_R∂K_F ≤ 0`) but has increasing differences in each of
  `(K_R;K_M)`, `(K_F;K_M)`. No relabeling fixes both signs ⇒ Topkis does not apply
  off the shelf.
- Worked around it with a **homotopy in C_M + Hessian cofactor**: implicit-function
  differentiation gives `dK*_R/dC_M = cof_{KM,KR}(H)/det H`, whose sign reduces to
  the **shift ratio** `g(x)=F_{K_R}/f`. `g` non-increasing ⇒ `dK*_R/dC_M ≤ 0`;
  integrate from `C̄_M` (where `K*_M=0`, system = no-FCL) down ⇒ `K*_R ≥ K°_R`.
- Power-law has `g(x)=(D̄−x)/Q` (affine, decreasing) for **every** α ⇒ explains
  footnote 6 extends to the whole family.
- **Verified** [`verify.py`, `validate_capacity_channel.py`]: across Beta
  scale-mixtures (symmetric, decreasing-density, right-skewed) `K*_R>K°_R`, `g`
  decreasing, and the sign of `dK*_R/dC_M` matches the cofactor bracket.

## E3 — Net carbon: exact condition + sufficient conditions + C_R†
- Exact net-fossil identity (Prop, = paper Prop 4) by integration by parts:
  `E[fossil*]`, `E[fossil°]` in terms of conditional means at the cutoffs ⇒
  inequality **(C)**, decomposed into utilization (distribution-free) vs
  capacity-substitution.
- Sufficient distributional conditions (concave/convex density) — uniform is the
  boundary.
- `C_R†` made explicit for power-law: `C_R† = ½[c+(R−C_M−c)²/(R−c)+(R−c−C_F−C_M)²/(β+p−R)]`,
  with no-FCL threshold `C_R° = C_F²/2(β+p−c)`; proved `C_R°<C_R†` (window where
  FCL drives carbon→0 but `K°_R` finite). **Verified** [inline]: 0.040 < 0.344.

## E4 — Adversarial exactness audit (the catch)
Built `verify_exact.py`: every analytical formula vs finite differences of the
profit integral. **15/15 PASS** to 6–16 digits — BUT it caught a real defect:
- **Theorem 1 sign typo.** The cofactor coefficient was written `(β+p−R)`; the
  algebra gives `(R−β−p)`. Magnitude and conclusion were already right and
  numerically confirmed; only the intermediate coefficient/label was wrong. Fixed.
  *(Lesson: write the FD audit before trusting any hand-derived cofactor.)*

## E5 — Hardening Theorem 1 (two more real issues)
Regime-crossing scan [`validate_regime_crossing.py`]:
- The homotopy path **crosses regimes**: small-FCL near `C̄_M` (`K*_M→0`),
  large-FCL below. Old proof only derived the cofactor for large-FCL. Confirmed
  `dK*_R/dC_M<0` in **both** regimes (−4.28,−2.76,−2.19 small; −5.21,−21,−108
  large); restated the proof to use the general cofactor across the crossing.
- **Honest Hessian claim.** Dropped an unverified "diagonal-dominance everywhere"
  sentence (it was false near the knife-edge). Verified `H≺0` by eigenvalues on
  the interior path; it degenerates only as `K*_R→∞` (knife-edge), where
  `K*_R>K°_R` is immediate anyway.

## E6 — Closed the four open points (per request "fix these")
1. Submodularity → reframed as non-obstruction (homotopy is complete under
   Regularity).
2. Endogenous-capacity feedback → new **distribution-free cutoffs Lemma**
   (verified `=5/9, 17/18` to 1e-9 on Beta(2,2)) + Theorem 1 ⇒ condition (C) is a
   *complete* characterization, no term dropped.
3. `C_R†` explicit (E3).
4. Regimes → ordering `C_M^fc < C̄_M < C̄_M^b` proved (gap `C_F(β+p−R)/(β+p−c)`,
   verified 0.48); triple win across all adoption regions.

## E7 — DROPPED: carbon-tax / welfare (out of scope)
Explored emissions vs a carbon tax τ (effective fossil cost `c+τ`) looking for a
"carbon-tax backfire" result [`explore_carbontax.py`]. Found the threshold
`C̄_M(τ)` decreasing and the adoption boundary `τ̄`. **Dropped on scope review:**
social-vs-private optimum and corrective pricing are **B1**, not A1. No part of
this entered the paper. *(Kept the script in scratch only.)*

## E8 — Extension I: the optimal contract, general F
`role1_contract_theory.tex`.
- **Thm 1.** The within-period surplus `J(d)=E[φ_x(d(x))]` separates across states
  (no coupling) ⇒ statewise optimum ⇒ the unique optimal contract over the **full**
  measurable-policy space, any `F`, is the renewable-first threshold
  `d*(x)=min{(K_F−x)_+,K_M}`. Lifts paper Lemma 1 from a pointwise sub-problem to
  the whole contract space.
- **Caught two TEST bugs** (theorem was fine): (i) let dispatch exceed available
  power `K_F−x` (revenue `Rδ` rose unboundedly) — fixed by capping served load by
  availability; (ii) structured perturbations let `δ>K_M` (infeasible). After both
  fixes: **0/4000** pointwise mismatches, **0/21,600** feasible policies beat `d*`
  [`verify_contract.py`].
- **Thm 2.** Ex-ante mechanism `(d*,K*)` exists for any `F` (Weierstrass on a box
  bounded by Assumption 1), unique under `H≺0`.

## E9 — Extension I: N&S emission + correlation comparative static
- **N&S.** Carbon falls iff (C); settled the mandate's "mild vs restrictive": it is
  **not generic** — positive demand-supply association makes it fail even with
  `K*_R>K°_R`.
- **Correlation comparative static.** Proved `g(x)=F_{K_R}/f = E[S̃ | x̃=x]` — the
  shift ratio *is* the conditional renewable factor (Lemma, via the joint density).
  So: carbon falls **iff demand and renewable supply are sufficiently negatively
  correlated.** Built a joint `(D,S)` model with tunable corr
  [`verify_correlation.py`]: net carbon saving **monotone in corr and sign-flips**
  (−12.1, −12.0, −8.5, +0.2, +107 as corr → −). *Caveat logged:* the `K*_R` **level**
  numerics diverge at extreme corr (fragile nested-quadrature solver), so I claim
  only the carbon-**sign** comparative static (clean) + `K*_R>K°_R` (proven in E2).
  The **decoupling** is the headline: `K*_R>K°_R` always, but only negative
  association converts it into a carbon cut.
- **Prop 5 (mechanism).** Price program implements `d*` as the agent's unique best
  response iff `R>c` (observable) and `β+p>R`; induced demand pinned by the
  distribution-free cutoff `C_M/(R−c)`.

## E10 — Extension II: robust & detail-free contracting (the hard frontier)
`role1_robust_contract.tex`.
- **Thm R1 (least-favorable distribution).** Over the shape class `U` (monotone
  density on the two zones), the **uniform minimizes** the net carbon saving:
  `∂Δ/∂μ*_low<0`, `∂Δ/∂μ°_mid>0`, and within `U` both conditional means are
  extremized at the midpoints (uniform). So the closed-form `C_R≤C_R†` is a
  **worst-case certificate over an infinite-dimensional ambiguity set**.
  **Verified** [`verify_robust.py`]: non-increasing-density mean ≤ midpoint in
  3000/3000 (uniform extremal); `Δ` minimized at the uniform.
- **Thm R2 (detail-free / Wilson doctrine).** Because the optimal cutoffs are
  distribution-free, a single **quantile-targeting** mechanism implements the
  optimum for **every** `F` — the regulator needs no prior over demand/renewables,
  only six scalar primitives. Distribution matters for the *magnitude* of the
  saving (R1), never for *how to act*.
- **Scope re-checked** after a user flag: removed "carbon-optimal contract"
  (implied a B1 social objective) → "profit-maximizing contract whose emission
  reduction is a consequence"; renamed "reliability" → "no-FCL cutoff probability"
  to avoid B1 reading; added an explicit paragraph distinguishing **distributional**
  robustness (A1) from B2's market-structure robustness discussion.

---

## Verification ledger
| Claim | Script | Result |
|---|---|---|
| Uniform closed forms eqs 25/26 | `verify.py` | ≤6e-10 |
| Knife-edge MV constant; = eq 24 | `verify.py`, `verify_exact.py` | 4e-10 |
| All 15 analytical formulas vs FD of Π | `verify_exact.py` | **15/15**, 6–16 digits |
| `K*_R>K°_R`, shift-ratio sign-law | `validate_capacity_channel.py` | holds, 4 families |
| Regime crossing + `H≺0` | `validate_regime_crossing.py` | both regimes; eig<0 interior |
| Optimal contract `d*` optimality | `verify_contract.py` | 0/4000, 0/21,600 |
| Correlation comparative static (carbon sign) | `verify_correlation.py` | monotone, sign-flips |
| Least-favorable distribution = uniform | `verify_robust.py` | 3000/3000; min at uniform |

## Open problems / handoffs
- **Theorem 2 (general `C_R†` existence)** — still heuristic ("the two curves
  cross") for arbitrary `F`; explicit only for power-law. *(A1, future.)*
- **Correlation `K*_R` levels** — need a stabler solver for the joint-corr model to
  get a clean `dK*_R/dρ` curve (the carbon-sign result is already clean). *(A1 /
  numerical methods.)*
- Small-FCL boundary `K*_M=K°_R`, full regime stitching → **not A1** (regimes).
- Building the shared `d*(x)`/`k*` solver for the group is A1 task (4) — partially
  served by the verifiers here; a packaged solver is the next deliverable.
