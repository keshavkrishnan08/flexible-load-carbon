# Mechanism Design and Regimes: Role 4 Week 2 (Team A1)

Against the **FCL paper** (`FCL_Carbon_Paper.txt`, Lemma 1 / §3.3, §4.1,
Appendix G, §8 / Remark 8). This is the **Week 2** Role 4 deliverable; it builds
on Week 1's `THEORY_HARDENING.md` and is organized by the four Week 2 bullets.
Each analytical claim is backed by a check in `tests/` (run `pytest tests/ -q`,
41 passing = 17 Week 1 + 24 Week 2) and, where it is a comparison, by Role 2's
solver, vendored unchanged in `role4/fcl_backend/`. Notation as in Week 1:
residual demand `x = D − K_R·S`; capacities `K_R, K_F, K_M`; margins `R, c, p, β`;
capital costs `C_R, C_F, C_M`; `φ° = (β+p−c−C_F)/(β+p−c)`.

---

## Bullet 1: A single per-MWh price implements the optimum (`role4/instrument.py`)

**Claim (the regulator's instrument-design problem).** A *single scalar* per-MWh
price `R`: not a state-contingent transfer schedule `t(x)`: uniquely
implements (i) the first-best dispatch rule `d*(x)` state by state and (ii) the
optimal capacity vector `(K_R*, K_F*, K_M*)`; and it does so **iff**

> `c < R < β + p`  (the price-richness window).

**Implementation of dispatch.** By Lemma 1 (subproblem eq 4), given any `x`,

> `d*(x) = min{ max{K_F − x, 0}, K_M }`

is the unique maximizer of the per-period payoff `R·d − c·[min{K_F,(x+d)+} −
min{K_F,x+}]` once revenue accrues only to *served* MWh `min(d,(K_F−x)+)`. The
per-MWh margin is strictly positive on the feasible region, `R` on renewable
surplus, `R−c` on gap-filling fossil, so the payoff strictly increases to the
feasibility/cap boundary; the minimal maximizer is exactly `d*`. **Confirmed**
independently of the rule by a fine grid search (`tests/test_instrument.py::
test_best_response_matches_rule_pointwise`, and `::test_flat_price_induces_eq3_
dispatch` at the solver's own capacities).

**Why a single price is rich enough** (the non-trivial part). Within each
dispatch region the principal's marginal value of an extra served MWh is
*state-independent* (`R`, then `R−c`) and the objective is linear in `d`. A flat
price therefore tracks marginal value exactly; an unrestricted state-contingent
transfer would add value only if marginal value varied *within* a region in a
way a constant could not follow, which Assumption 1 rules out. **Confirmed:** the
extra value of an optimal `t(x)` over the flat price is `0`
(`::test_state_contingent_transfer_buys_nothing`).

**The window, and Assumption 1.** Below `c` no MWh is ever served; above `β+p`
consumers are curtailed to serve FCL (the perverse A4 violation). So the
one-dimensional instrument is rich enough **iff** `R ∈ (c, β+p)`. A1 (`R>c+C_M>c`)
and A4 (`β+p>R`) place `R` strictly inside, so the baseline always admits
single-price implementation (`::test_richness_window_and_assumption1`,
`::test_richness_fails_outside_window`). Worked instance: window `(1.0, 3.0)`,
`R=2.0` interior.

**A scalar pins the 3-vector.** The capacity FOCs (eqs 12, 13, 15) are functions
of the same `R`, so sweeping the single instrument traces a *one-parameter*
capacity curve `(K_R*,K_F*,K_M*)(R)`: a scalar pins the vector, and the
attainable set under one price is a curve, not all of `R³` (the precise sense of
"rich enough"; `::test_single_scalar_pins_capacity_vector`).

**Cross-role consistency.** This bullet reproduces Role 1's already-pushed
`prop:pa` (in `role1/exploratory_cross_role/role1_contract_theory.tex`, which
Role 1's README hands off to Role 4): identical conditions `R>c`, `β+p>R`, and
the same distribution-free cutoff `C_M/(R−c) = 0.3`. The served-MWh feasibility
fix here is the same correction Role 1's `verify_contract.py` records ("cap
served load by availability `K_F−x`"), reached independently; Role 1's verifier
finds 0/21,600 feasible policies beat `d*`. Existence/uniqueness leans on Role
1's pushed `thm:contract` (`unique under H≺0`); the monotone-triangular
sharpening is Role 1's own Week-2 item, not yet pushed.

---

## Bullet 2: The unified regime theorem and the `K_M*=K_R°` crossover (`role4/unified_regime.py`)

Week 1 mapped two regime axes separately and left one open finishing item: the
small-/large-FCL boundary `K*_M = K°_R`, "located numerically … but not forced
into a general closed form." **Week 2 closes it** under the uniform family and
composes the axes into one theorem.

**The crossover, in closed form.** Solving the small-FCL FOCs (App. G eqs 61, 63)
at the renewable base `K_R = K_R°` for `(K_F*, K_M*)` and imposing `K_M* = K_R°`
gives (sympy-derived; reproduced in `run_analysis_week2.py`):

> `C_M^cross = (R−c)·[ D̄(β+p−c−C_F) + K_R°(R−c−C_F) ] / [ (D̄+K_R°)(β+p−c) ]`,

with `K_R° = D̄(√(c/Δ) − 1)`, `Δ = 2C_R − C_F²/(β+p−c)`. For `C_M < C_M^cross`
the optimal FCL program is *large* relative to the renewable base (`K_M* > K_R°`);
for `C_M > C_M^cross` it is *small*. **Confirmed:** the closed form equals the
numerically located crossover, `K_M*(C_M^cross)=K_R°` exactly, the locus sits
strictly inside the adoption region (`C_M^cross < C̄_M^b`), and the FCL-scale
label flips across it (`tests/test_unified_regime.py`). `K_R°` matches Role 2's
solver to `1e-4` (`::test_K_R_circ_matches_backend`). Worked instance:
`K_R° = 41.42`, `C_M^cross = 0.354` (closed form = numeric); at the fixture
`C_M = 0.3 < 0.354`, so **large-FCL**.

**The unified regime theorem** (`unified_theorem`). Every Assumption-1 point
carries exactly one label on each of three independent axes,

- **coverage** (in `C_M`): full-coverage `|` interior/large-FCL `|` small-FCL
  adoption `|` no adoption, ordered `C_M^fc < C̄_M < C̄_M^b`;
- **boundedness** (in `C_R`): both-finite `|` with-FCL-unbounded (the carbon
  window) `|` both-unbounded, split by `C_R° < C_R†`;
- **FCL scale** relative to the renewable base: the side of `C_M^cross`
  (`K_M* ≷ K_R°`),

and the labels are mutually consistent: the two orderings always hold,
`C_M^cross < C̄_M^b`, and the boundedness label never constrains the coverage
label. **Confirmed** on a parameter grid (`::test_unified_theorem_axes_
consistent`).

---

## Bullet 3: Necessity of Assumption 1, from pressure-test to proof (`role4/necessity.py`)

Week 1 demonstrated necessity by nudging each parameter past its boundary. Week 2
upgrades each to a **proof**: every condition's guarded quantity is an explicit
elementary function `g(s)` of the condition's *slack* `s`, strictly monotone (a
signed closed-form derivative), hitting the boundary of its validity range
*exactly* at `s = 0`. A strictly monotone function equal to the boundary at `s=0`
is valid on one side only, so `s > 0` is necessary and sufficient, for **all**
parameters, not a sampled nudge.

| Cond | Slack `s` | Guarded `g(s)` | `g(0)` | `g'` | Valid |
|---|---|---|---|---|---|
| **A1** | `R−c−C_M` | `C_M/(C_M+s)` = eq-12 RHS | `1` | `<0` | `g<1 ⇔ s>0` |
| **A2** | `c+C_F+C_M−R` | `m/(m+s)`, `m=β+p−c−C_F−C_M` = eq-13 RHS | `1` | `<0` | `g<1 ⇔ s>0` |
| **A3** | `β+p−c−C_F` | `s/(s+C_F)` = `φ°` | `0` | `>0` | `g>0 ⇔ s>0` |
| **A4** | `β+p−R` | `s` = eq-13 denom `β+p−R` | `0` | `>0` | `g>0 ⇔ s>0` |

The derivative signs are verified symbolically; each guarded value sits exactly
on its validity edge at slack 0 (`tests/test_necessity.py`).

**The relaxed regime, per condition:**

- **A1** relaxed (`R≤c+C_M`): **no-adoption** corner, `K_M*=0`. *Strictly
  necessary* for any FCL program.
- **A2** relaxed (`R≥c+C_F+C_M`): **full-coverage** corner, `K_F*≥D̄`, blackout 0
  (strict ⇒ the out-of-scope dedicated-provider case). *Necessary only for
  interiority*, relaxing yields a well-defined favorable regime, not a
  contradiction.
- **A3** relaxed (`β+p≤c+C_F`): **no-backup**, `φ°≤0`, the grid tolerates
  blackout. *Strictly necessary*.
- **A4** relaxed (`β+p≤R`): **perverse curtailment**: consumers blacked out for
  FCL; `F*` leaves `(0,1)`. *Strictly necessary*.

So `{A1, A3, A4}` are strictly necessary and `A2` is necessary only for the
interior regime, the same asymmetry Week 1 flagged, now proven
(`::test_strict_vs_interior_only_asymmetry`).

---

## Bullet 4: Second-best contract when the renewable factor is private (`role4/screening.py`)

The paper treats residual demand as observable and dispatch as self-enforcing
(Lemma 1, Remark 1), true for Bitcoin because `R` is publicly verifiable.
Section 8 / Remark 8 flag the AI-training case, where the agent's signal is
opaque. **We formalize exactly that gap:** the principal observes demand `D` but
not the renewable factor `S`, so residual demand `x = D − K_R·S` is the agent's
**private signal**.

**Model** (a faithful 1-D reduction). Type `θ = S ∈ [0,1]`, density `f`, CDF `F`,
monotone hazard (default Uniform[0,1]). In the carbon-relevant gap-filling region
the principal's gross value of dispatching `d` is the displacement margin
`(R−c)d`; the agent's private cost is `C(d,θ) = (1−θ)ψ(d)`, `ψ(d)=d²/2`, so
`C_{dθ} = −d < 0` (single crossing). Dispatch is capped at `K_M`.

> **First best:** `(R−c) = (1−θ)ψ'(d)` ⇒ `d^FB(θ) = min{(R−c)/(1−θ), K_M}`.
>
> **Second best:** `(R−c) = [(1−θ)+(1−F)/f]ψ'(d)` ⇒
> `d^SB(θ) = min{(R−c)/[(1−θ)+(1−F)/f], K_M}`.

By the envelope theorem `u'(θ)=ψ(d(θ))≥0` (rent rises in type), IR binds at the
bottom, and the virtual-surplus bracket is larger, so `d^SB(θ) ≤ d^FB(θ)` with
equality at the top (cap / inverse hazard `→0`): **no distortion at the top,
downward distortion below.** Uniform[0,1] gives the clean closed form
`d^SB(θ) = ½·d^FB(θ)` on the interior. **Confirmed:** monotone `d^SB` (IC),
no-distortion-at-top, the ½-distortion closed form, and rent `≥0` rising in type
with `E[u]>0` (`tests/test_screening.py`).

**How the information rent shifts emissions vs full information:**

- **Short run (fixed capacities): utilization effect.** Fossil drawn for FCL is
  proportional to dispatch; `d^SB ≤ d^FB`, so the carbon-*raising* utilization
  effect is **dampened**: `E[d^SB] < E[d^FB]` (`::test_utilization_effect_
  dampened`). Private info lowers short-run carbon, but only by running the
  program less, forfeiting the profit/reliability gains. Worked instance:
  `E[d^FB]=4.40 → E[d^SB]=2.55`.
- **Long run: capacity-substitution channel.** The leaked rent lowers the
  principal's captured FCL value to an effective revenue `R_eff < R`
  (`R_eff = 1.55 < 2.0`). The carbon-reduction window is `C_R < C_R†`, and
  `C_R†(R)` is increasing in the FCL revenue, so a lower `R_eff` lowers `C_R†`
  and **shrinks the window** (`C_R† = 0.79 → 0.75`;
  `::test_carbon_window_shrinks_under_private_info`). Since the carbon reduction
  came precisely from the capacity channel (Prop 1 Step 3), the rent shrinks the
  very set of renewable-cost regimes in which it operates.

> Under the uniform family `K_R` itself is a knife-edge corner that does not move
> with `R` (the project's Week-1 finding), so the capacity channel is read off
> the threshold `C_R†`, exactly as Role 1 frames it, not off an interior `K_R`.

**Headline.** Private information on the renewable factor introduces a rent wedge
`R → R_eff` that (a) distorts dispatch downward (no distortion at the top) and
(b) shrinks the carbon-reduction window, a force *against* the carbon leg of the
triple win, absent in the transparent-`R` (Bitcoin) case. This is the Section-8
contractibility distinction made precise.

---

## What Week 2 closes, and what remains

- **Closed:** the Week-1 open finishing item: the small-/large-FCL crossover
  `K_M*=K_R°` now has an explicit uniform closed form (Bullet 2), matched to the
  numeric locus. This is exactly Role 1's handed-off item ("small-FCL boundary
  `K*_M=K°_R` → Role 4").
- **Cross-role verified (against what is already pushed):** Bullet 1 matches Role
  1's pushed `prop:pa`/`thm:contract` (same conditions, same cutoff, same
  feasibility fix, first-best gap 0); `K_R°` matches Role 2's solver to 1e-4; the
  shared closed forms `φ°, C̄_M, C_R†, C_R°` are Role 1's, reused unchanged. The
  full suite is 41 passing.
- **Awaiting the others' Week-2 pushes (not yet verifiable):** Role 1's
  monotone-triangular uniqueness sharpening (Bullet 1 leans on the weaker `H≺0`
  for now), Role 2's analytic Hessian / negative-definiteness certificate, and
  Role 3's cross-distribution robust certificate + reversed-channel
  counterexample. A full Week-2 `INTEGRATION.md` pass should follow once those land.
- **Still conditional (unchanged from Week 1, by design):** the general-`F`
  net-carbon Step 3 of Proposition 1. Bullet 4's screening result is stated for
  the canonical convex-cost / monotone-hazard reduction; extending the rent-wedge
  comparison to a fully general residual `F` is the natural next target, parallel
  to the Step-3 gap.
