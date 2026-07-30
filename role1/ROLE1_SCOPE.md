# Role 1 — Scope of Claims

What Role 1 asserts, under exactly what hypotheses, and what it does not assert. Written so
a referee, a coauthor, or a future version of us can tell in one pass which statements carry
weight and which do not.

## Model scope: which variant Role 1 solves

Role 1 solves the **utility-operated** configuration: the utility captures the computing
margin `R`, pays hardware cost `C_M`, and `K_M` is chosen by utility optimization. The key
condition is `(R−c)F(K_F−K_M) + c·F(−K_M) = C_M`.

This is **not** the paper's main model. The Guide (Appendix A.1) settles the main line as
**third-party miners at tariff p**: entry by free entry, `(R−p)F(K_F−K_M) = C_M`, margin
`R−p` for miners and `p−c` for the utility — the *double margin*, which Role 1's setup does
not contain.

Role 1's variant is nonetheless load-bearing, not a curiosity: §5.2 proves the deregulated
competitive equilibrium decentralizes to exactly this integrated-planner benchmark at
`P_r = R`, `P_cap = β+p`. So Role 1 characterizes the object the decentralization theorem is
stated against.

**Every sharpness statement differs between the two configurations**, and all of Role 1's
capacity-and-carbon results have now been re-derived with `R−p`/`p−c` (below, and claim 10):
the two cutoffs, the decoupling, and the exact `Φ` coefficient. The only object still in a
different margin is §5.3's deregulated prices-vs-quantities (`R−c−τ`), which is a distinct
market structure by design, not a pending re-derivation.

### Which margin appears where, and why (read before objecting to "three margins")

A referee will notice that the three Role-1 sections use three different margins. They are
not inconsistent; each is the correct margin for its section's market structure. But the
deliverables did not say so, so this table is the reconciliation:

| Section | Market structure | Margin | Why |
|---|---|---|---|
| Theory (Weeks 2–4): φ₁, φ₂, Φ, `thm:classify`, `thm:decarb` | Utility-operated: utility runs the FCL, captures `R`, pays `c` | **`R−c`** | The utility's own computing margin. `φ₁=C_M/(R−c)`, Φ coefficient `C_M/(R−c)`. |
| Calibration (§7): break-even `P*`, entry threshold `C̄_M` | Third-party miner entry at tariff `p` | **`R−p`** | The *entry* question is a miner's, and a miner earns `R`, pays tariff `p`. `C̄_M=(R−p)φ°` is the miner's entry margin, not the utility's. |
| §5.3 prices-vs-quantities | Deregulated competitive market with a per-MWh tax `τ` | **`R−c−τ`** | Competitive dispatch nets the tax off the surplus margin; `τ̄=R−c` is the greening threshold. |

So the three margins track three market structures, linked by §5.2's decentralization
theorem (the deregulated equilibrium decentralizes the utility-operated planner at `P_r=R`).
**Update (this is now done — cutoffs AND the carbon coefficient).** The *entire*
capacity-and-carbon theory has been re-derived in the paper's main double-margin model — see
`role1_double_margin.tex` and `verify_double_margin.py` (**9/9 PASS**, claim 10 below):
- both distribution-free cutoffs carry over — miner `φ₁=C_M/(R−p)`, fossil
  `φ°_dm=(β+p−c−C_F)/β` (same numerator, denominator `β` because the utility internalizes
  miner entry and the coupling term cancels);
- the fossil and FCL cutoffs **decouple** (`C_M` enters only `φ₁`) — a result the
  utility-operated model hides;
- the **exact carbon coefficient** transfers: `Φ_dm` is the utility-operated `Φ` verbatim with
  the single substitution `C_M/(R−c) → C_M/(R−p)`; verified `Δ=Φ_dm` to 2e-4 at the DM
  equilibrium (`Φ_dm=−2.3749` vs `Δ=−2.3752`). Not just the sign — the full closed form.

The only section still in a different margin is §5.3's prices-vs-quantities, which is
**deliberately** the deregulated market (`R−c−τ`), a distinct structure, not an inconsistency.
So the theory now lives natively in the main model, and the margin table below is the map.

## Claims, with their hypotheses

| # | Claim | Hypotheses | Status |
|---|---|---|---|
| 1 | Distribution-free cutoffs `φ₁=C_M/(R−c)`, `φ₂`, `φ°=(β+p−c−C_F)/(β+p−c)` | Assumption 1, interior optimum | **Proved.** Independently re-derived. `φ°` is a newsvendor critical fractile. |
| 2 | Existence and uniqueness via recursive-triangular FOC structure | Assumption 1, regularity, reduced SOC (Condition Schur) | **Proved.** The strongest block; residuals at 1e-16, Hessian and Schur complement negative definite. Condition Schur is checkable, not derived from primitives. |
| 3 | `Δ = Φ(F)`, so carbon falls iff `Φ>0` | **`K_M* ≥ K_R*` (large-FCL)** | **Proved on that regime.** The hypothesis is essential: outside it Φ can carry the wrong sign (at `C_R=0.34`, Φ=+1.905 vs true Δ=−0.135). Not an ad-hoc patch — see "One regime boundary" below. |
| 4 | Per-mean decisiveness (sharp iff, margins `D_ℓ`, `D_m`) | Interior optimum with `Δ<0` | **Proved**, gated on two explicit scalar margins, both verified at the representative optimum. |
| 5 | Surplus contract is fossil-minimizing | None | **Proved**, but it is a lemma and near-definitional. Also stated in the Guide (§4, §5.3) before Role 1 wrote it. |
| 6 | Surplus contract raises `K_R` and lowers carbon | Adoption + single-peakedness | **Proved.** One added positive term in the `K_R` FOC. Crowded by prior work; defense is scope, not conclusion. |
| 7 | Frontier identity `C(τ)−C(0)=Φ_ft(1−Λ)`; surplus-only carbon-optimal | **Condition M** (`K_R'≤0≤K_F'`) — *sufficient, not necessary, and false at interior optima* | Identity is definitional. The ranking is **proved under Condition M**. But Condition M **fails** where `K_R` is genuinely interior: `K_R` *rises* with τ (1.753→2.655) and `Λ∈[0.139,0.218]>0`. The earlier "verified numerically" was degenerate — `K_R` was pinned at the barrier, so `K_R'=0` trivially. The **conclusion** (`Λ<1`, surplus-only carbon-optimal) survives. |
| 8 | §5.3: allocation equivalence, boundary selection, revenue divergence, long-run strict ranking | Deregulated setting; `τ̄=R−c` | **Proved.** The newest and least pre-empted work. |
| 9 | Calibration: break-even separability; `C̄_M` insensitivity | None | **Proved**, and reproduces the Guide's coefficients (2533.0, 6181.9) and every table cell. |
| 10 | **Double-margin cutoffs** `φ₁=C_M/(R−p)`, `φ°_dm=(β+p−c−C_F)/β`; cutoffs decouple; **exact carbon coefficient** `Φ_dm` (utility-operated `Φ` with `C_M/(R−c)→C_M/(R−p)`) | Third-party miner entry (the paper's *main* model); interior optimum | **Proved and verified** (`verify_double_margin.py` **9/9**: cutoffs exact to 1e-16 / 1e-4; `Δ=Φ_dm` to 2e-4). The whole capacity-and-carbon theory now lives in the main model. Decoupling (`C_M` only in `φ₁`) is new. |
| 11 | **Φ certifies a carbon *increase*** on its whole valid domain | Large-FCL; the naive rule | **Established** (`prop:alwaysup`). At every large-FCL optimum solved, `Δ<0`, `Δ∈[−3.249,−1.208]` bounded from zero. The "classification" is honestly a certification of backfire; decarbonization is a small-FCL corner (`Δ>0` first at `C_R=0.05`, `K_M≪K_R`). Turns the "empty branch" objection into the result. |
| 12 | **Storage** dominates the FCL as a carbon tech, but the dispatch gap is storage-invariant (survives rivalry); FCL is higher-*value* iff `R>c+η[φ°_dm·c+(1−φ°_dm)(β+p)]` | Static expected-flow storage | **Proved and verified** (`verify_storage.py` **6/6**). Concedes the carbon point, shows the dispatch results survive (gap invariant to `K_S`; robust to rivalry, +2.129→+2.116), and the value verdict is robust — higher tariff `p` pushes it *toward* the load. |

## One regime boundary, two results

The large-FCL condition `K_M ≥ K_R` is not a patch bolted onto the carbon theorem to make
the algebra close. It is the model's single regime boundary, and it governs the Week-1
knife-edge too.

Along the uniform/power-law locus, the marginal value of renewable capacity is

| `K_R` | 1 | 4 | 8 |
|---|---|---|---|
| MV | 0.344444 | 0.344444 | **0.317438** |
| `K_M` | 4.278 | 5.444 | 7.000 |
| `K_M ≥ K_R`? | yes | yes | **no** |
| `F(−K_M)` | 0 | 0 | **0.0556** |

The knife-edge holds exactly at the two large-FCL points and fails at the small-FCL one.
Verified across three distributions (α = 1.0, 0.5, 2.0): spread on large-FCL is 4e-09,
8e-08, 2e-10; departure at small-FCL is 2.7e-02, 1.2e-01, 1.5e-03. It does not degrade
gracefully near the boundary — it holds on one side and breaks on the other.

Same mechanism both times. Every sharp result here needs the load deep enough to absorb the
whole renewable surplus, `F(−K_M)=0`, so the fossil integral's lower limit is the support
endpoint rather than an interior point. When that fails an extra `K_M·F(−K_M)` term appears:
it breaks the integration by parts behind `Φ`, and it breaks the cancellation behind `MV`.

So the honest reading of Role 1 is that its sharp results are results **about the
surplus-absorbing regime**, stated as such — not general claims carrying a caveat.

Both halves are asserted in `verify_exact.py`: the knife-edge is checked to hold across
large-FCL points *and* checked to genuinely break at the small-FCL point, so neither the
result nor its boundary can rot silently.

## Withdrawn

**The carbon phase diagram / boundary `{Φ=0}` and Condition S.** Withdrawn. Every cell in
which the supporting sweep reported `Φ>0` lies in the small-FCL regime, where the identity of
claim 3 does not hold; true Δ computed by quadrature is negative in all of them. `{Φ=0}`
separates nothing observed. Condition S is vacuous as stated.

**The Week-2 impossibility, as a theorem.** Not established. The LP construction over the
equilibrium polytope shows the sign is identified at some capacity vectors and the linear
relaxation straddles at others, but at the straddling vector tested every positive-Δ law
fails the second-order condition — it is a saddle, not an equilibrium. Treat as open.

## Known-not-ours

- The **direction** of the naive-rule carbon effect is Knittel–Senga–Wang (NBER 34065) and
  Holland–Mansur (2008). Role 1 contributes the exact analytic boundary, not the sign.
- The **surplus contract** appears in the Guide before Role 1 formalized it.

## The "only if" branch

Searched, not merely untested. Over a 60-point `(C_R, C_M, R)` grid, 16 solved equilibria:
large-FCL `Δ∈[−3.249,−1.208]`, small-FCL `Δ∈[−1.573,−0.049]`, **zero with `Δ>0`**. On the
regime where Φ is valid, Δ is bounded away from zero. Evidence, not proof — 24 of 60 points
failed to converge, and absence of a witness is not emptiness.

## Out of scope for Role 1

| Item | Owner |
|---|---|
| Calibration inputs — especially `p`, which EIA-861 rebuilds at $66–90/MWh vs the assumed $50, moving `C̄_M=(R−p)φ°` one-for-one | A2 |
| Regulatory lag; the (RR) result is a post-reset comparative static (filing-to-order 189–325 days) | B3 / A2 |
| §4 Case A's ambiguous condition — the Guide says it "requires solving the constrained system" | B1 |
| Welfare benchmark (Appendix A) | B1 |
| `P_r ∈ [c,R]` selection in §5.2; exactness holds only at `P_r=R` | B3 |
| `R(A)` dilution fixed point; `K_M^SP < K_M^NE < K_M*` | B3 |
| Storage competing for the same surplus — ~~the first question a referee asks~~ now ADDRESSED (claim 12, `role1_storage.tex`); the full *dynamic* state-of-charge program remains | B2 |
| Carbon leakage / relocation; counterfactual is grid-local "no load" | B2 / B1 |

## Numerical-layer status

Role 1's harness: B1/B2/B4 fixed (a crash laundered into a PASS, a PASS printed beside
falsifying data, a hardcoded `True`); regime guard added so the large-FCL Φ raises rather
than returning a wrong-signed value.

Since then: **B6** — the knife-edge flag was computed, printed, and discarded; asserting it
exposed the regime boundary above. **M6** — the Φ=Δ agreement was claimed at `~1e-9`; the
measured, quadrature-limited figure is `~3e-8`, now stated. **M9** — a "✓" was printed
unconditionally beside FOC residuals; it is now conditional. **M13** — bare `fsolve` returned
its last iterate whatever happened, so downstream checks could run on a non-solution; all
call sites now go through `_fsolve_checked`, which treats the residual as ground truth (not
`ier`), polishes stalls (restart, then Levenberg-Marquardt), and raises only if no solver
reaches tolerance. It caught a genuine boundary non-solution at `C_M=0.30` (`K_F`≈`Dbar`).
**M3** — the cited 244-cell sweep ran offline and its script is not in this repo; the lab
notebook now says so, and the reproducible evidence is the 60-point grid above.

**Tolerance vs accuracy floor.** `verify.py` evaluates FOC residuals through a ScaleMix
(`ns=601` scale nodes) + `limit=60` quad. For skewed densities (`D~Beta(1,3)`) the `gR`
residual floors at ~`1.4e-5`, *flat across quad subdivisions* — the floor is the mixture
discretization, not the integrator. Demanding `rtol=1e-8` there asks for accuracy the script
does not have, so `solve_with`/`solve_no` in `verify.py` accept at `1e-5` (the genuine floor);
the equilibrium is independently confirmed by `validate_capacity_channel.py`, which reaches
the same `dK_R/dC_M` via analytic `intFKR`. `verify_exact` (`1e-9..1e-16`) and
`validate_regime_crossing` (`ns=1500`, `1e-16`) genuinely hit `1e-8` and keep it.

**The Week-4 Condition-M sweep was worse than "evaluated at an artificial cap."** The
renewable barrier bound in every cell, so `K_R'(τ)=0` held trivially and Condition M was
never actually tested. Rerun at a genuine interior optimum, it **fails** — see claim 7. The
sweep now guards its own non-degeneracy: it asserts `K_R` is interior before drawing any
conclusion, and it *reports* Condition M rather than asserting it, since asserting it would
only ever pass at a barrier. What it asserts is the conclusion, `Λ<1`.

**Week-3 Theorem 1's cap** turned out to be a different animal from Condition M, and better.
`K_R` does sit at the cap in most families (profit is still rising at `K_R=14` for symmetric,
left-skew, and high-`C_F`), so the reported *magnitude* is a property of the constraint set.
But the *sign* is not: swept over five families x five caps from 1.5x to 20x `K_R°`, the
carbon saving is positive in all 25 cells. Both facts are now asserted — the second
deliberately, as a ceiling on what may be quoted. The left-skew family alone ranges
`+0.0019` to `+5.98` across caps, a factor of 3000, so **no magnitude from that sweep belongs
in the paper**. Profit is also genuinely non-concave in `K_R` for left-skew (two sign changes
of `∂Π/∂K_R` over `[2,14]`), so "the" optimum needs a stated selection rule.

**A verification defect that mimicked a theorem failure.** The carbon integral masked a fixed
grid, so a limit moving between nodes changed nothing until it crossed one, then jumped
(~5e-3). Consequence: on a fine sweep `e(K_R)` *increased* on 60/100 steps — reading as a
direct refutation of the monotone-fossil lemma — and the left-skew carbon saving came out
negative (−3e-4). Both were artifacts, 3–15x smaller than the jump that caused them. With
endpoints made exact: 0/100 increases, saving positive. The lemma's own test ran at step 0.5,
250x coarser than the artifact, so it could never have caught it; it now runs at step 0.02.
The lesson generalizes: **a verification grid coarser than its own noise floor reports success
whether or not the result is true.**

**Frontier saturation.** The budget family saturates once `d_τ` is limited by `K_M` rather
than `τ` (between τ=5 and τ=15 here), so monotonicity in τ is strict only while the budget
binds. The old "strictly increasing" assertion passed only because the pinned barrier kept
the sweep away from saturation.
