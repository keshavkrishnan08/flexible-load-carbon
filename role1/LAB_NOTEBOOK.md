# Lab Notebook — Team A1, Role 1 (General Carbon Theory)

**Keeper:** Role 1 (R1).  **Opened:** 2026-06-22 (A1 Week 1 Plan).

### Notebook conventions
- **Append-only / permanent.** Entries are never erased. A wrong claim is struck
  through (`~~like this~~`) with a dated correction note, not deleted.
- **Dated, sequential.** Each entry is `EN · YYYY-MM-DD` in ISO-8601, in work
  order. Entries below were performed and logged in a working session on
  **2026-06-24** unless noted; the plan opened 2026-06-22.
- **Structured.** Each entry records objective → method → result → conclusion.
- **Traceable.** Claims cite the verifier script and digit-level agreement in
  brackets; artifacts and commits are named. New results are also recorded in
  `CONTRIBUTIONS.md`.
- **Signed.** Each entry ends `— R1`.

**Role 1 mandate (A1 Week 1 Plan).** General Carbon Theory — four tasks:
(1) re-derive eqs 25/26 as ground truth; (2) generalize the net carbon-reduction
result (the general condition where capacity-substitution beats utilization);
(3) prove `K*_R > K°_R` in general; (4) draft result + gap memo.

> **Scope correction (2026-06-24).** Entries E1–E6 (+E10) are the Role 1
> deliverable. Entries E8–E9 were built under a broader "general contracting"
> framing and overlap Role 3 / Role 4; they were **quarantined** to
> `exploratory_cross_role/` and are *not* the Role 1 deliverable. The earlier
> notebook header ("General Contracting Theory") was corrected to "General Carbon
> Theory" on this date.

**Scope guards (hard walls).** Do **not** enter:
- **A2** — empirical calibration, real-data magnitudes, grid-type illustrations.
- **B1** — reliability, blackout-vs-emission tradeoff, welfare, social-vs-private
  optimum, corrective pricing.
- **B2** — flexibility continuum, AI/storage, multi-grid, price exogeneity, dynamics.
Anything touching those is logged as "dropped (out of scope)".

> **Scope note (post-review).** The Role 1 deliverable is the *General Carbon
> Theory* — entries **E1–E6** (`role1_carbon_theory.tex` + `gap_memo.md`).
> Entries **E8–E10** (optimal-contract, correlation comparative static, robust /
> detail-free) were built under a broader "general contracting" framing; on
> re-reading the A1 Week 1 Plan they overlap **Role 3** (carbon sign across
> distributions) and **Role 4** (core-proof generalization, regimes), so they have
> been **quarantined** to `exploratory_cross_role/` and are *not* counted as the
> Role 1 deliverable. They remain logged here for provenance.

---

## E1 · 2026-06-24 · Ground truth: re-derive the uniform closed forms
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

## E2 · 2026-06-24 · The capacity channel `K*_R > K°_R`, general
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

## E3 · 2026-06-24 · Net carbon: exact condition + sufficient conditions + C_R†
- Exact net-fossil identity (Prop, = paper Prop 4) by integration by parts:
  `E[fossil*]`, `E[fossil°]` in terms of conditional means at the cutoffs ⇒
  inequality **(C)**, decomposed into utilization (distribution-free) vs
  capacity-substitution.
- Sufficient distributional conditions (concave/convex density) — uniform is the
  boundary.
- `C_R†` made explicit for power-law: `C_R† = ½[c+(R−C_M−c)²/(R−c)+(R−c−C_F−C_M)²/(β+p−R)]`,
  with no-FCL threshold `C_R° = C_F²/2(β+p−c)`; proved `C_R°<C_R†` (window where
  FCL drives carbon→0 but `K°_R` finite). **Verified** [inline]: 0.040 < 0.344.

## E4 · 2026-06-24 · Adversarial exactness audit (the catch)
Built `verify_exact.py`: every analytical formula vs finite differences of the
profit integral. **15/15 PASS** to 6–16 digits — BUT it caught a real defect:
- **Theorem 1 sign typo.** The cofactor coefficient was written `(β+p−R)`; the
  algebra gives `(R−β−p)`. Magnitude and conclusion were already right and
  numerically confirmed; only the intermediate coefficient/label was wrong. Fixed.
  *(Lesson: write the FD audit before trusting any hand-derived cofactor.)*

## E5 · 2026-06-24 · Hardening Theorem 1 (two more real issues)
Regime-crossing scan [`validate_regime_crossing.py`]:
- The homotopy path **crosses regimes**: small-FCL near `C̄_M` (`K*_M→0`),
  large-FCL below. Old proof only derived the cofactor for large-FCL. Confirmed
  `dK*_R/dC_M<0` in **both** regimes (−4.28,−2.76,−2.19 small; −5.21,−21,−108
  large); restated the proof to use the general cofactor across the crossing.
- **Honest Hessian claim.** Dropped an unverified "diagonal-dominance everywhere"
  sentence (it was false near the knife-edge). Verified `H≺0` by eigenvalues on
  the interior path; it degenerates only as `K*_R→∞` (knife-edge), where
  `K*_R>K°_R` is immediate anyway.

## E6 · 2026-06-24 · Closed the four open points (per request "fix these")
1. Submodularity → reframed as non-obstruction (homotopy is complete under
   Regularity).
2. Endogenous-capacity feedback → new **distribution-free cutoffs Lemma**
   (verified `=5/9, 17/18` to 1e-9 on Beta(2,2)) + Theorem 1 ⇒ condition (C) is a
   *complete* characterization, no term dropped.
3. `C_R†` explicit (E3).
4. Regimes → ordering `C_M^fc < C̄_M < C̄_M^b` proved (gap `C_F(β+p−R)/(β+p−c)`,
   verified 0.48); triple win across all adoption regions.

## E7 · 2026-06-24 · DROPPED: carbon-tax / welfare (out of scope)
Explored emissions vs a carbon tax τ (effective fossil cost `c+τ`) looking for a
"carbon-tax backfire" result [`explore_carbontax.py`]. Found the threshold
`C̄_M(τ)` decreasing and the adoption boundary `τ̄`. **Dropped on scope review:**
social-vs-private optimum and corrective pricing are **B1**, not A1. No part of
this entered the paper. *(Kept the script in scratch only.)*

## E8 · 2026-06-24 · Extension I: the optimal contract, general F
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

## E9 · 2026-06-24 · Extension I: N&S emission + correlation comparative static
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

## E10 · 2026-06-24 · Extension II: robust & detail-free contracting (the hard frontier)
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

## E11 · 2026-06-24 · Capstone (in-scope): distribution-free reading of the carbon effect
New section in `role1_carbon_theory.tex` — strictly General Carbon Theory:
- **Two-moment sufficient statistic.** From the exact identity (E3), the carbon
  saving `Δ(F)` depends on `F` only through `(μ*_low, μ°_mid)` at the
  distribution-free cutoffs. **Verified** [`verify_carbon_robust.py`]: 6e-7.
- **Tight magnitude bounds.** `Δ_min = K°_F(1−φ°)−K*_F ≤ Δ ≤ Δ_max`, closed-form in
  capacities + `φ°` (distribution-free). **Verified** inside (−6.43 ≤ −2.17 ≤ 3.23).
- **Least-favorable distribution.** Within the monotone-density class, the uniform
  **minimizes** `Δ` ⇒ the closed-form condition is a worst-case carbon certificate
  over an infinite ambiguity set. **Verified** 3000/3000.
- ~~Attempted a general monotone-threshold theorem: `Δ(C_R)` non-increasing ⇒
  carbon region `[0,C_R†(F)]` for all `F`.~~ **Correction (2026-06-24):** dropped —
  numerics blow up at the unbounded-renewables knife-edge (`K*_R→∞`, values 1e5),
  so the claim is not cleanly supported. Theorem 2 stays heuristic. *(Honest.)*
— R1

## E12 · 2026-06-24 · Adversarial peer review (3 referees) + honesty revision
Subjected the paper to three independent adversarial referees: a proof-checker, a
counterexample hunter (rebuilt the model from scratch with a Gaussian copula, 70+
runs), and an overclaim auditor (ran all 5 scripts vs cited numbers).
- **No genuine counterexample found** — every failure coincided with a violated
  hypothesis (sharpness confirmed). Core results (K*_R>K°_R, cutoffs, bounds,
  threshold anchor) robust.
- But several statements over-reached. **Fixed:** ~~"two-moment sufficient
  statistic"~~ → affine representation *at fixed capacities* (the means aren't a
  sufficient statistic across F — capacities & q° move with F); ~~"uniform
  least-favorable, robust certificate for every F∈U"~~ → least-favorable
  *conditional shape* (cross-F covariation open); distribution-free cutoffs Lemma
  → *large-FCL only*; ~~C_R† "for every F"~~ → general upper anchor + explicit
  power-law window (general window conjectural); Thm 1 small-FCL cofactor sentence
  cited wrong matrix entry (H_MM→H_FF); Prop-regime "a fortiori in (I)" dropped
  (backwards); "machine precision"→"6–16 digits"; MV "{1,5,9}"→{1,4,5} large-FCL;
  −108→−92.1; "all four closed"→three+one crossover open.
- Full point-by-point in `RESPONSE_TO_REFEREES.md`. No theorem retracted; two
  downgraded to honest conditional form, one rescoped. PDF 11pp.
— R1

## E13 · 2026-06-25 · Self-audit: sign defect in Thm 6/7 proofs (referees missed it)
Re-auditing for "make it perfect," caught a genuine sign error the 3 referees did
not: Thm 6 / Thm 7 prose stated `∂Δ/∂μ*_low = +C_M/(R−c) > 0`. From eq:suff it is
`−C_M/(R−c) < 0` (a larger μ*_low raises E[fossil*], lowering Δ). Verified
numerically: −0.5556 = −C_M/(R−c). The **bounds and conclusions were correct** (they
used the right directions); only the stated partial sign was wrong, making the proof
prose internally contradictory ("increasing … minimized by largest"). → Fixed both
proofs (Δ decreasing in μ*_low, increasing in μ°_mid); added a tilt check to
`verify_carbon_robust.py` confirming uniform minimizes Δ over U (Δ vs tilt
s=[0,.2,.5,1,2,4]: −1.69,−0.64,+0.59,+1.67,+2.36,+2.71 → min at s=0). PDF 11pp.

Also reviewed team updates: Role-3 (now complete, validates K*_R>K°_R 32/32, carbon
rare at low-C_R — confirms my threshold thm) and Role-4 (rebuilt to FCL mandate, 17
tests pass, adopts my C_R†/C_R°/C̄_M^b closed forms + eq24=2(C_R†−C_R)). Role-2 36
tests pass. main still un-integrated.
— R1

---

## A1 Week 2 (2026-06-26) — Optimal Contract and General Carbon Theory

Mandate (A1 Week 2 Plan, Role 1): five tasks — existence/uniqueness/contract
optimality; shift-ratio uniform along the homotopy; emission keystone for general
F; connectedness of the carbon-reduction set; sharp channel condition + tight
bounds. Deliverable: `role1_week2_theory.tex` (+pdf), verified `verify_week2.py`.
Scope guards unchanged (no A2/B1/B2). Nothing outside Role 1.

## E14 · 2026-06-26 · Existence, uniqueness, contract optimality (Thm 1)
Goal: prove the program has a unique interior optimum and `d*` is the unique
dispatch, without assuming concavity (Π is submodular in (K_R,K_F)).
- **Dispatch:** per-state payoff is affine with strictly positive slopes
  `β+p−c` and `R−c`; strict `R>c` pins `d*(x)=min{(K_F−x)_+,K_M}` uniquely.
- **Existence:** Π continuous + coercive (each own-partial `<0` for large own
  capacity), Weierstrass on a compact box.
- **Uniqueness (recursive triangle):** cutoffs pin `K_F(K_R)=F^{-1}(φ2)`,
  `a(K_R)=F^{-1}(φ1)` (strict-mono inverse); the (K_F,K_M) Hessian block is
  **unconditionally** ND, `det M=(R−c)f(a)(β+p−R)f(K_F)>0`; uniqueness of K_R
  reduces to the **scalar** Schur condition `Ψ'(K_R)<0`, which also gives `H≺0`.
- **Verified** [`verify_week2.py` T1]: dispatch argmax = formula on a grid;
  coercivity; `det M` closed form; eig(M)<0; Schur<0; `Ψ(K_R)` strictly
  decreasing with unique zero = solved K_R*; eig(H)<0. Beta(2,2),Beta(2,3).
— R1

## E15 · 2026-06-26 · Shift-ratio condition uniform along the homotopy (Lemma 4)
Goal: prove the realized two-point endpoint inequality holds at every C_M from a
static hypothesis. Result: **support-wide** monotone `g=F_{K_R}/f` (for each K_R)
⇒ `g(a)≥g(K_F*)` uniformly along the whole C_M-homotopy; endpoints stay strictly
interior (cutoffs in (0,1)) and ordered (K_M*>0). This is the exact content the
Week-1 "integrate downward" step needs — the moving-window condition is *implied*
by the static one. **Verified** [T2]: 12-node homotopy, min endpoint gap ≥0 and
dK_R*/dC_M ≤0 at every node; g non-increasing on the full support for all K_R.
— R1

## E16 · 2026-06-26 · Emission keystone for general F (Thm 2 + Prop 3) — conjecture resolved NEGATIVE
Goal: close the Week-1 conjecture — does carbon fall at a finite interior
(large-FCL) optimum for a non-power-law F? **Answer: no.**
- Endogenous condition: substitute K*(C_R) into (C) — exact, proved.
- **Primitive sufficient condition:** endpoint shift-ratio (⇒ K_R*>K_R°) + a
  two-zone tail/skew bound — (a) `f(·;K_R*)` non-increasing on the FCL zone,
  (b) `f(·;K_R°)` non-decreasing on the no-FCL zone — gives a closed-form
  `Δ ≥ Δ_LB`; carbon would fall when `Δ_LB>0`. Proved + the μ-bound algebra
  verified at the representative optimum.
- **Resolution (the real result):** I set out to *exhibit* a witness and could
  not — because none exists. Two independent vectorized searches (ws2, ws3) plus a
  precise adaptive-quad scan in `verify_week2.py` (T3) over Beta scale-mixtures
  (demand skew α, supply mean E[S]∈{.5,…,.8}, full C_R×C_M grids) return **Δ<0 at
  every large-FCL interior optimum** (max Δ ≈ −1.4 < 0 (least-negative observed; all scanned negative)). So the sufficient bound never certifies a fall (`Δ_LB ≯ 0`) at any large-FCL
  interior optimum, and realized `Δ<0` throughout.
- **Mechanism (why it's structural, not a search miss):** under the model's
  dispatch, FCL on renewable-surplus states is fossil-served — the *verified*
  flat term `(K_M*−K_R*)` in `E[fossil*]=∫_{-K_M}^{a}(1−F)`. A finite program adds
  fossil at rate ~K_M* while the channel subtracts only at the renewable-shift
  rate; utilization wins at every finite interior optimum. Carbon falls **only**
  at the cheap-renewable corner `K_R*→∞` (Week-1 Thm 4(ii) window, a corner) and,
  numerically, small-FCL (Role 4). Consistent with Week-1's hedge and Role-3's
  "carbon rare at low C_R."
- **Honesty note:** the task asked to exhibit a positive witness; the math says no
  large-FCL interior optimum reduces carbon. I report the truth and do NOT fabricate a Δ>0 point. The
  keystone's value is converting a vague conjecture into a sharp falsifiable
  inequality — falsified in the carbon-rising direction. **Verified** [T3].
— R1

## E17 · 2026-06-26 · Connectedness of {C_R : Δ≥0} (Thm 3)
Goal: single-interval carbon-reduction set. Bounded above (Week-1 anchor
`Δ→−U₀`), non-empty (E16), and **single interval** under the
monotone-renewable-shadow-value condition stated as a **strict down-crossing**
`Δ'(C_R)<0` at every zero; convexity by an IVT contradiction (a re-crossing
upward would need `Δ'≥0` at a zero). **Verified** [T4]: C_R sweep has exactly one
sign change (+→−), Δ non-increasing where Δ≥0, Δ<0 at the largest C_R.
— R1

## E18 · 2026-06-26 · Sharp channel condition + tight bounds (Thm 4, Thm 5)
Goal: the N&S channel condition and tightness of the magnitude bounds.
- **Sharp condition:** `K_R*>K_R° ⇔ ∫_{C_M}^{C̄_M} λ dt >0` (FTC), with
  `λ ∝ f f [g(a)−g(K_F*)]`. Pointwise-monotone g makes `λ≥0` ⇒ **sufficient**;
  a sign-mixed integrand with positive integral shows it is **not necessary**.
  (The realized reversed-channel counterexample is Role 3's.)
- **Tight bounds:** `Δ_min ≤ Δ ≤ Δ_max` attained by degenerate conditional laws
  concentrating at the interval endpoints; checked `Δ(a,0)=Δ_min`,
  `Δ(−K_R,K_F°)=Δ_max` exactly, realized Δ strictly inside. **Verified** [T5].
— R1

## E19 · 2026-06-26 · Deep re-audit of T3 (mechanism fix + both regimes) — negative confirmed
Prompted to re-examine the T3 negative finding. Built a **direct state-by-state
fossil simulator** with explicit renewable-surplus absorption (FCL served from
surplus first). Two findings:
- **Mechanism correction.** My E16 prose ("FCL on surplus draws fossil; flat term
  = fossil added") was WRONG. The direct simulator with surplus absorption equals
  the closed form `∫_{-K_M}^{a}(1−F)` to 7 digits (6.1833 both). So the formula
  already credits surplus absorption. The correct mechanism is the **irreducible
  floor** `(K_M−K_R)_+`: max surplus in any state is `≤K_R`, so a large-FCL
  program (`K_M>K_R`) can't be fully surplus-powered — it burns ≥`K_M−K_R` fossil
  at deepest surplus. Floor vanishes iff `K_M≤K_R` (small-FCL).
- **Both regimes checked → still negative.** Searched small-FCL interior optima
  (profit-maximization, robust to the FOC-solve instability at small `C_R`).
  Result: Δ≤0 there too, for a *different* reason — small-FCL is optimal only at
  small `C_R`, where the **no-FCL** grid already drives `K_F°→0`
  (`E[fossil°]→0`), leaving nothing to save; the channel even *reverses*
  (`K_R*≤K_R°`, FCL's flexibility lets you build slightly fewer renewables).
  Representative: `CR=0.10` → no-FCL `(K_R°,K_F°)=(14.4,0.0)`, with-FCL
  `(14.0,1.6,2.1)`, Δ=−0.21.
- **Conclusion (sharper than E16).** Carbon falls at **no** finite interior
  optimum — large-FCL (floor) nor small-FCL (baseline already decarbonized) —
  only at the cheap-renewable corner `K_R*→∞`. This is *consistent* with Role-3's
  "carbon rare at low C_R." Did NOT fabricate a positive witness; reported the
  true two-regime negative. → Rewrote Prop 3 (now Prop "no finite interior
  optimum reduces carbon"), fixed the abstract + mechanism, added direct-simulator
  + floor + small-C_R checks to `verify_week2.py`.
— R1

## E20 · 2026-06-26 · Hardening pass: T3 made rigorous, conditions primitivized, scope tightened
Second hostile-referee pass flagged T3 as a scan dressed as a theorem, plus
condition/scope issues. Closed them (no math errors — honesty/rigor):
- **T3 → real results.** (1) **Floor lemma** (PROVED): `E[fossil*] ≥ K_F*(1−φ1)`
  and `≥ K_M*−K_R*` from the cutoffs. (2) **Irreducibility theorem** (PROVED):
  Δ is affine in the two conditional means, which the distribution-free cutoffs do
  NOT pin ⇒ *no* cutoff-only inequality can sign Δ — so Week-1's conjecture has no
  distribution-free proof (a genuine obstruction, not lack of effort). (3) Residual
  question = sign of the cutoff-computable **uniform-shape benchmark Δ0** + a tilt;
  numerically **Δ0<0 (max −1.17)** and Δ<0 (max −1.4) at every scanned interior
  optimum, the tilt reinforcing. This replaces "scan+conjecture" with
  "proved floor + proved impossibility + numerical residual with a negative
  benchmark." Verified [`verify_week2.py` T3: floor, Δ0<0].
- **Scope (G2).** Excised all affirmative small-FCL claims from the deliverable;
  small-FCL is Role 4's regime, stated as out-of-scope (one pointer), not a Role-1
  conjecture. Everything stays in the large-FCL mandate.
- **Conditions (G3).** Noted shift-ratio (gmono) and two-zone are primitive
  conditions on F (+ a fully-primitive max-zone version). Schur: added primitive
  content (renewable marginal value strictly decreasing along the locus; power-law
  is the exact `Ψ'≡0` boundary). MRSV/T4: anchored on the EXACT power-law interval
  `S=[0,C_R†]` (Week-1 closed forms, no condition needed); MRSV honestly scoped as
  the general-F packaging (≈ its own conclusion; σ*>σ° and C¹-ness left open).
- Abstract rewritten to "four proved + one (T3) = floor+impossibility proved,
  residual numerical." PDF 9pp.
— R1

## E21 · 2026-06-27 · "Make it perfect": close the open items (C¹, T4, T3 framing)
Pushed the three remaining open items as far as they go in-scope.
- **C¹-ness CLOSED.** Corollary: under Condition Schur (H≺0), the equilibrium map
  C_R↦(K_R*,K_F*,K_M*) and (K_R°,K_F°) are C¹ by IFT, so Δ is C¹ on the large-FCL
  interior. Removes the "C¹ we don't close" caveat (only the large↔small-FCL
  crossing stays Role 4). Verified: K_R*(C_R) FD-derivative finite & smoothly
  varying.
- **T4 restructured.** Made the EXACT power-law interval S=[0,C_R†] the PROVED
  theorem (i)+(ii), unconditional, with strict-fall core (C_R°,C_R†) distinguished
  from the Δ=0 flat. MRSV/(iii) demoted to an optional general-F extension, vacuous
  in the scanned family.
- **σ*>σ° gloss was FALSE — corrected.** The suite caught it: σ*=0.297 < σ°=0.425.
  So the MRSV "shadow-value ordering" economic justification is wrong (no-FCL
  renewables carry the larger marginal fossil impact). Removed the false claim;
  MRSV is now stated as a bare hypothesis, openly not derivable, and MOOT (the
  power-law result needs it not). Suite now documents σ*<σ° as the honest fact.
- **T3 framing sharpened.** Prop irreducible (proved: capacities+cutoffs don't
  determine sign(Δ); the range [Δmin,Δmax]=[-6.43,+3.23] straddles 0, verified) is
  the structural resolution; the family-wide Δ<0 is a conjecture BY NECESSITY (the
  impossibility forbids a distribution-free proof), backed by >250 cells (offline
  ws2/ws3 + in-suite scan), Δ0<0 everywhere. Disclosed Δ_LB ≡ Δ0.
- Third hostile-referee pass ("qualified yes") items all fixed. PDF 10pp.
— R1

## E22 · 2026-06-30 · 4th + 5th referee passes — 5 real defects fixed, then math re-derived clean
**4th pass (hostile MS referee)** found genuine errors (not nitpicks); all fixed,
no headline claim changed.
- **M1 dispatch lemma was WRONG.** Feasible set `s+d<=K_F` banned renewable surplus
  from powering the FCL, contradicting `d*=min{(K_F-x)_+,K_M}` on surplus states x<0
  (d* can exceed K_F) and the surplus-first absorption the floor uses. Rewrote with
  `d<=(K_F-x)_+`, payoff `R*d - c*(d-(-x)_+)_+`; two-segment slopes => unique. Suite
  T1a now uses KM=8>KF=5 so d*>K_F is exercised.
- **M2** "submodular => not concave" is false (submodular can be ND). Replaced with
  the real reason: concavity lapses on the power-law knife-edge (Psi'=0, flat).
- **M3** at FIXED q°, Dmax must carry (1-q°); old Dmax dropped it. Fixed; now attained
  EXACTLY (3.0573=3.0573). Straddle [-6.43,+3.06], still straddles 0.
- **M4** existence "gradient inward on faces" never used R<c+CF+CM. Replaced with
  ray-coercivity: N(g)=(R-c)min(1,g)-g*CF-CM<0 for all g>0 IFF R<c+CF+CM. Suite checks
  N<0 and that it flips when violated.
- **M5** added in-file Lemma deriving cofactor identity via Cramer; triple-verified
  [H^-1]_(KR,KM) = cof/detH = FD to 1.4e-4. Affine rep re-attributed to eq:fos.
- Minors: defined U_0; removed false "det H->0 / improper" hedge; fixed placeholder
  cites; Delta0=-1.09. Commit 4162f04.

**5th pass (pure-math re-derivation, every identity from scratch):** ALL 10 items
CORRECT — gradients, block Hessian, cofactor (Cramer index + sign), N(gamma)
coercivity, keystone bound, D0=Delta_LB, floor, q°-fixed tight bounds, det M limit,
all numbers consistent. **Zero genuine errors.** Only 2 cosmetic wording fixes
(keystone coefficient phrasing; lambda-continuity rests on |detH|=|detM*Psi'|) —
both applied. Suite 61/61, PDF 11pp.
— R1

---

## Verification ledger
| Date | Claim | Script | Result |
|---|---|---|---|
| 2026-06-24 | Uniform closed forms eqs 25/26 | `verify.py` | ≤6e-10 |
| 2026-06-24 | Knife-edge MV constant; = eq 24 | `verify.py`, `verify_exact.py` | 4e-10 |
| 2026-06-24 | All 15 analytical formulas vs FD of Π | `verify_exact.py` | **15/15**, 6–16 digits |
| 2026-06-24 | `K*_R>K°_R`, shift-ratio sign-law | `validate_capacity_channel.py` | holds, 4 families |
| 2026-06-24 | Regime crossing + `H≺0` | `validate_regime_crossing.py` | both regimes; eig<0 interior |
| 2026-06-24 | Sufficient stat + bounds + least-favorable | `verify_carbon_robust.py` | 6e-7; inside; 3000/3000 |
| 2026-06-24 | Optimal contract `d*` (quarantined) | `exploratory_cross_role/verify_contract.py` | 0/4000, 0/21,600 |
| 2026-06-24 | Correlation carbon-sign (quarantined→Role 3) | `exploratory_cross_role/verify_correlation.py` | monotone, sign-flips |
| 2026-06-26 | **A1 Week 2** — all five tasks (T1–T5) vs quadrature of Π | `verify_week2.py` | **49/49 PASS** |
| 2026-06-26 | Recursive-triangular uniqueness: det M closed form, Schur<0, H≺0, unique Ψ zero | `verify_week2.py` T1 | exact (≤1e-15) |
| 2026-06-26 | Emission conjecture resolved NEGATIVE: Δ<0 at every large-FCL interior optimum | `verify_week2.py` T3 + offline ws2/ws3 (244 cells) | max Δ≈−1.40<0 |
| 2026-06-26 | Corner non-emptiness C_R°<C_R†; FTC path-integral = ΔK_R; bounds tight | `verify_week2.py` T4,T5 | 4.21≈4.13; Δmin/Δmax attained |

## Open problems / handoffs
- **Theorem 2 (general `C_R†` existence)** — still heuristic ("the two curves
  cross") for arbitrary `F`; explicit only for power-law. *(A1, future.)*
- **Correlation `K*_R` levels** — need a stabler solver for the joint-corr model to
  get a clean `dK*_R/dρ` curve (the carbon-sign result is already clean). *(A1 /
  numerical methods.)*
- Small-FCL boundary `K*_M=K°_R`, full regime stitching → **not A1** (regimes).
- Building the shared `d*(x)`/`k*` solver for the group is A1 task (4) — partially
  served by the verifiers here; a packaged solver is the next deliverable.
