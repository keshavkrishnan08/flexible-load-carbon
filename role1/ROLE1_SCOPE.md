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

**Open decision for the advisor.** Every sharpness statement differs between the two
configurations. If Role 1's results are to serve the main line, cutoffs, FOCs, thresholds,
and the Φ coefficient must be re-derived with `R−p` and `p−c`. That is mechanical but not
trivial, and it has not been done.

## Claims, with their hypotheses

| # | Claim | Hypotheses | Status |
|---|---|---|---|
| 1 | Distribution-free cutoffs `φ₁=C_M/(R−c)`, `φ₂`, `φ°=(β+p−c−C_F)/(β+p−c)` | Assumption 1, interior optimum | **Proved.** Independently re-derived. `φ°` is a newsvendor critical fractile. |
| 2 | Existence and uniqueness via recursive-triangular FOC structure | Assumption 1, regularity, reduced SOC (Condition Schur) | **Proved.** The strongest block; residuals at 1e-16, Hessian and Schur complement negative definite. Condition Schur is checkable, not derived from primitives. |
| 3 | `Δ = Φ(F)`, so carbon falls iff `Φ>0` | **`K_M* ≥ K_R*` (large-FCL)** | **Proved on that regime.** The hypothesis is essential: outside it Φ can carry the wrong sign (at `C_R=0.34`, Φ=+1.905 vs true Δ=−0.135). |
| 4 | Per-mean decisiveness (sharp iff, margins `D_ℓ`, `D_m`) | Interior optimum with `Δ<0` | **Proved**, gated on two explicit scalar margins, both verified at the representative optimum. |
| 5 | Surplus contract is fossil-minimizing | None | **Proved**, but it is a lemma and near-definitional. Also stated in the Guide (§4, §5.3) before Role 1 wrote it. |
| 6 | Surplus contract raises `K_R` and lowers carbon | Adoption + single-peakedness | **Proved.** One added positive term in the `K_R` FOC. Crowded by prior work; defense is scope, not conclusion. |
| 7 | Frontier identity `C(τ)−C(0)=Φ_ft(1−Λ)`; surplus-only carbon-optimal | **Condition M** (`K_R'≤0≤K_F'`) | Identity is definitional. The ranking is **proved under Condition M**, which is verified numerically, not derived. |
| 8 | §5.3: allocation equivalence, boundary selection, revenue divergence, long-run strict ranking | Deregulated setting; `τ̄=R−c` | **Proved.** The newest and least pre-empted work. |
| 9 | Calibration: break-even separability; `C̄_M` insensitivity | None | **Proved**, and reproduces the Guide's coefficients (2533.0, 6181.9) and every table cell. |

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
| Storage competing for the same surplus — the first question a referee asks | B2 |
| Carbon leakage / relocation; counterfactual is grid-local "no load" | B2 / B1 |

## Numerical-layer status

Role 1's harness: B1/B2/B4 fixed (a crash laundered into a PASS, a PASS printed beside
falsifying data, a hardcoded `True`); regime guard added so the large-FCL Φ raises rather
than returning a wrong-signed value. Remaining known issues: Week-3 Theorem 1 and the Week-4
Condition-M sweep are evaluated at artificial caps (`Kcap`, `Dbar*0.99`), so their reported
*magnitudes* are properties of the constraint set and must not appear in the paper.
