# Regime Stitching, Hardening, and Reconciliation: Role 4 Week 3 (Team A1)

Against the **FCL paper** (`FCL_Carbon_Paper.txt`, §3-4, Appendix B.1, Appendix
G) and **Role 1's pushed contract/robust theory**
(`role1/exploratory_cross_role/role1_contract_theory.tex`,
`role1_robust_contract.tex`), which Role 1 hands to Role 4. This is the **Week 3**
Role 4 deliverable; it builds on Week 1 (`THEORY_HARDENING.md`) and Week 2
(`MECHANISM_REGIMES.md`) and is organized by the four Week 3 bullets. Every
analytical claim is backed by a check in `tests/` (run `pytest tests/ -q`) and,
where it is a comparison, by Role 2's solver, vendored unchanged in
`role4/fcl_backend/`. Notation as before: residual demand `x = D − K_R·S` on
`[−K_R, D̄]`; capacities `K_R, K_F, K_M`; margins `R, c, p, β`; capital costs
`C_R, C_F, C_M`; `φ° = (β+p−c−C_F)/(β+p−c)`.

Week 3 is **purely additive**: four new modules (`regime_stitch.py`,
`hardening.py`, `regime_phase.py`, `reconcile_week3.py`), four matching test
files, and `run_analysis_week3.py`. Weeks 1-2 are untouched. Week-3 suite: **24
passing**; with Weeks 1-2 in place the full suite is **66** (17 + 25 + 24).

---

## Bullet 1: Carry the contract and characterization across regimes (`role4/regime_stitch.py`)

**The regime boundary.** Residual demand lives on `[−K_R, D̄]`, so `F(x;K_R)=0`
for `x ≤ −K_R`. The FCL program is *small* when `K_M < K_R` (`−K_M` strictly
inside the support, `F(−K_M)>0`) and *large* when `K_M ≥ K_R` (`−K_M ≤ −K_R`,
`F(−K_M)=0`). The boundary is exactly **`K_M = K_R`**.

**Claim (what stitches, and where it kinks).**

- **The contract `d*` is regime-free.** `d*(x)=min{(K_F−x)_+, K_M}` (Role 1
  Thm 1 / paper eq 3) never branches on the regime; it is the same continuous,
  1-Lipschitz, non-increasing, piecewise-linear schedule in both. *(Confirmed
  pointwise on grids straddling the boundary,
  `test_regime_stitch::test_contract_is_regime_free`.)*
- **The carbon functional `E[fossil](K_M)=∫_{−K_M}^{K_F−K_M}(1−F)dx` is `C¹`
  across `K_M=K_R`.** It is a single integral with continuously moving limits;
  the backend computes it from the *extended* CDF with no regime branch (see
  `role4/fcl_backend/model.py`), so any discontinuity would have to live in the
  capacity *solution*, not the functional. *(Two-sided finite difference at the
  boundary: value jump `9.9e−5`, derivative jump `<1e−2`;
  `::test_carbon_functional_C1_across_boundary`.)*
- **The `K_M` marginal value is `C⁰` but kinks (`C¹` fails).** The large- and
  small-FCL marginal values are
  > `MV_L(K_M) = (R−c)F(K_F−K_M) − C_M`, &nbsp;&nbsp;
  > `MV_S(K_M) = (R−c)F(K_F−K_M) + c·F(−K_M) − C_M`.

  They agree at `K_M=K_R` because the extra pure-renewable-surplus term
  `c·F(−K_M) → c·F(−K_R) = 0` there
  (`::test_marginal_value_continuous_at_boundary`). Their `K_M`-derivatives
  differ by the density at the support floor:
  > `MV_S'(K_R⁻) − MV_L'(K_R⁺) = −c·f(−K_R;K_R) = −c/(D̄+K_R)` (uniform),

  a kink in `MV = ∂Π/∂K_M`. Hence **profit `Π` is `C¹` across the boundary but
  not `C²`**: `∂²Π/∂K_M²` jumps by exactly `c·f(−K_R)` as the surplus term
  switches on. *(Numerical jump `0.0071` = closed form `c/(D̄+K_R)=0.0071`;
  `::test_profit_is_C1_not_C2_kink_located`.)*

**The takeaway (locate and explain).** The two Week-3 shared objects, the
contract and the carbon functional, **stitch continuously**; the *only*
non-smoothness is a corner in the FOC surface at `K_M=K_R`, where the small-FCL
surplus term turns on. Because the value and the carbon functional are
continuous, the optimum `K_M*(C_M)` itself passes from large- to small-FCL
**continuously** through the Week-2 crossover `C_M^cross` (locus `K_M*=K_R°`), so
carbon does not jump when the program changes regime *(smooth `K_M*(C_M)`,
crossing `K_R°`; `::test_optimum_varies_continuously_through_crossover`)*. Worked
instance: kink magnitude `c/(D̄+K_R) = 0.0071` at `K_R=K_R°=41.42`.

---

## Bullet 2: Harden the optimality and robust proofs (`role4/hardening.py`)

Four pieces of measure-theoretic scaffolding, each with the hypothesis it
certifies, and Assumption 1 stress-tested against each.

**(A) Existence of the optimal capacities (Weierstrass).** Role 1's ex-ante
theorem asserts a maximizer exists because Assumption 1 confines the optimum to a
compact box and `Π` is continuous. We make the box explicit, `K_F ≤ D̄` (A2),
`K_M ≤ D̄+K_R`, `K_R ≤ K_R^hi`: and verify the backend optimum lies strictly
inside it. **But the `K_R` face is finite only when `C_R ≥ C_R†`**; on the carbon
window `C_R < C_R†` the box is non-compact (Week-1 corner-at-infinity) and
Weierstrass does not apply. So **Assumption 1 alone is *not* sufficient for
existence**, it needs `C_R ≥ C_R†`. *(`::test_box_compact_iff_C_R_ge_C_R_dagger`,
`::test_assumption1_alone_insufficient_for_existence`.)*

**(B) Measurability / existence of the optimal schedule.** The statewise
integrand `φ_x(δ)` is Carathéodory (continuous in `δ`, measurable in `x`); its
argmax correspondence is measurable and admits the explicit **continuous**
selection `d*(x)=min{(K_F−x)_+, K_M}`, which is a fortiori Borel-measurable. We
certify continuity, the 1-Lipschitz modulus, and uniqueness of the served-load
maximizer (`φ_x` strictly increasing to the feasibility cap). This grounds Role
1's Thm 1 in measure theory rather than a pointwise assertion.
*(`::test_optimal_schedule_measurable_and_lipschitz`.)*

**(C) IC/IR constraint qualification (screening, Week-2 Bullet 4).** Single
crossing `C_{dθ}=−d<0` plus a monotone hazard give: local IC + the envelope
`u'(θ)=ψ(d(θ))` characterize incentives; the relaxed solution has `d^SB(θ)`
**non-decreasing**, which restores every omitted *global* IC constraint; and IR
binds only at the bottom type. The active set `{IR at θ_lo, monotonicity}` is
qualified, so the first-order/envelope program is exact. *(monotone `d^SB`, IR at
bottom, rent `≥0` rising; `::test_screening_constraint_qualification`.)*

**(D) Sion minimax for the ambiguity set `U`.** The robust carbon problem is
`max_{K∈box} min_{F∈U} Δ(K,F)`. We verify Sion's hypotheses for `U` (Role 1's
monotone-density shape class): `U` is **convex** (a convex combination of
non-increasing densities is non-increasing); `Δ` is **linear in `F`** through the
two conditional means (Role 1's saving equation), hence quasi-convex and
quasi-concave; and the capacity set is the **compact box of (A)**: again only
when `C_R ≥ C_R†`. Then min-max = max-min, both attained at the least-favorable
**uniform** (Role 1 Thm robust). We confirm the saddle numerically where the box
is compact; **on the carbon window the minimax is ill-posed** (non-compact `K_R`)
recorded, not silently passed. *(`::test_ambiguity_set_convex_and_Delta_linear`,
`::test_minimax_saddle_where_box_compact`, `::test_minimax_ill_posed_on_carbon_window`.)*

**Assumption-1 verdict.** Existence and the minimax saddle need *more* than
Assumption 1, both additionally require `C_R ≥ C_R†` (the Week-1
corner-at-infinity). Measurability and the screening CQ follow from Assumption
1's `R>c` core. This is the honest hardening result: the robust machinery is
well-posed **exactly where the with-FCL program is bounded**.

---

## Bullet 3: The stitched carbon phase diagram over the full cost plane (`role4/regime_phase.py`)

In the `(C_M, C_R)` cost plane at fixed `(R,c,C_F,β,p,D̄)`, three analytic curves
partition the plane (figure: `phase_full.png`):

- **Carbon boundary** `C_R = C_R†(C_M) = ½[c + (R−C_M−c)²/(R−c) +
  (R−c−C_F−C_M)²/(β+p−R)]`, carbon **down** below, **up** above (within Role
  1's shape class `U`).
- **Regime-form line** `C_M = C_M^cross`: where the contract's `K_M`-FOC
  switches between the large-FCL (eq 12) and small-FCL (eq 61) forms; i.e. where
  the **optimal contract changes form**.
- **Adoption edge** `C_M = C̄_M^b`.

**The stitch (the Bullet-3 theorem).** `C_R†(C_M)` is **one analytic curve**,
defined by the *same* closed form on both sides of `C_M^cross`, because it is the
with-FCL boundedness threshold read off the interior FOCs, it does not know the
small/large split (which changes only the *form* of the `K_M`-FOC, not the carbon
functional's value, `C¹` by Bullet 1). Consequently:

1. the carbon-**down** region `{C_R < C_R†(C_M)}` is a single **connected** set,
   the subgraph of a continuous function, that **spans both FCL regimes** and
   does not fracture at `C_M^cross`;
2. its boundary is **smooth across `C_M^cross`** (an explicit quadratic, no kink
   in the phase boundary even though the FOC surface kinks, Bullet 1); and
3. the regime line crosses the carbon boundary **once**, transversally, at
   `(C_M^cross, C_R†(C_M^cross)) = (0.354, 0.771)`.

*(`::test_boundary_smooth_across_regime_line`,
`::test_carbon_down_region_connected_spans_both_regimes`,
`::test_regime_line_crosses_boundary_once`.)*

**Global shape (a corrected observation).** `C_R†(C_M)` is **convex** in `C_M`
(curvature `1/(R−c)+1/(β+p−R)>0`), *not* monotone: its minimum sits at
`C_M = C̄_M`. So the carbon-down window in `C_R` is **narrowest exactly at the
adoption threshold `C̄_M`** and widens on either side, connectedness holds
regardless of the non-monotonicity. The curve ordering is
`C_M^fc < C_M^cross < C̄_M < C̄_M^b` (`0.000 < 0.354 < 0.500 < 0.793`): the
regime-form line sits inside the interior/large-FCL adoption band
(`::test_curve_ordering`).

---

## Bullet 4: Reconcile the team (`role4/reconcile_week3.py`)

Cross-check the three **shared objects** the Week-3 plan names, each against Role
1's pushed formalization and Role 2's vendored backend.

| Shared object | Role 4 (regime-stitched) vs | Result |
|---|---|---|
| **Contract `d*`** | Role 1 Thm 1 / eq 3 / backend `dispatch`, pointwise across both regimes | identical, dev `0.0e0` (`::test_contract_matches_backend_across_regimes`) |
| **Carbon functional `E[fossil]`** | Role 2 backend quadrature, both regimes | rel error `2.2e−9` (`::test_carbon_functional_matches_backend`) |
| **Robust optimum** | Role 1 least-favorable = uniform; Role 4 Sion saddle | saddle + uniform least-favorable **where `C_R ≥ C_R†`**; ill-posed on the window (flagged) (`::test_robust_optimum_consistent_or_flagged`) |

The contract and carbon functional agree across regimes **because** of Bullet 1
(carbon functional `C¹`, phase boundary smooth), the reconciliation records that
dependency (`::test_reconcile_all_available_checks_consistent`).

**Divergences flagged before the integrated paper** (`::test_divergences_flagged`):

- **The robust *capacity* problem is ill-posed on the carbon window** `C_R < C_R†`
  the very window where carbon falls. There `K_R` runs to the
  corner-at-infinity (Week 1), so no finite saddle exists; the robust certificate
  must be read at **fixed capacities** (Role 1's framing) or restricted to
  `C_R ≥ C_R†`. This is the central tension Role 4 surfaces.
- **The general-`F` Step-3 net-carbon sign remains conditional** (proven for
  uniform/power-law; Role 1's shift ratio gives the capacity channel, not the
  full net sign), unchanged by design.
- **Roles 2 & 3 Week-3 outputs are not yet pushed** (optimal-contract & DRO
  solvers, characterization sweep, comparative statics), so cross-checks against
  them are deferred, verified here against Role 1's pushed exploratory theory
  and Role 2's vendored backend, exactly as Week 2 did. A full Week-3
  `INTEGRATION.md` pass should follow once they land.

---

## What Week 3 closes, and what remains

- **Closed.** The contract and carbon functional are carried across the
  small-/large-FCL boundary with a continuous stitch and a *located, quantified*
  kink (`c/(D̄+K_R)`); the optimality/robust proofs are given measure-theoretic
  footing (existence, measurability, IC/IR CQ, Sion saddle) with each
  hypothesis verified; the carbon phase diagram is stitched into one connected
  both-regime region with a smooth boundary; the shared objects reconcile against
  Role 1 and the backend.
- **The hardening headline.** Existence and the robust minimax are well-posed
  **iff `C_R ≥ C_R†`**: Assumption 1 alone is insufficient, the same
  corner-at-infinity Week 1 found, now shown to govern the *robust* problem too.
- **Awaiting the others' Week-3 pushes** (not yet verifiable): Role 1's
  optimal-vs-carbon-optimal contract flip and DRO closed forms on the power-law
  family; Role 2's optimal-contract and DRO solvers; Role 3's characterization
  and contract comparative statics + robustness certificate. The Week-3
  reconciliation is complete against what is pushed.
- **Still conditional (unchanged, by design):** the general-`F` net-carbon
  Step 3.
