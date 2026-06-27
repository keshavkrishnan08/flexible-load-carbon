# Contributions — Team A1, Role 1 (General Carbon Theory)

**Append-only.** Add one row whenever a result, fix, artifact, or scope decision
lands. Newest at the bottom. `By` = contributor (R1 = Role 1). Cite the artifact
and the commit so every line is traceable. Do not edit past rows; correct via a
new dated row.

| Date | By | Contribution | Artifact / commit |
|---|---|---|---|
| 2026-06-24 | R1 | Re-derived uniform closed forms (eqs 20–26) as ground truth; knife-edge proved for power-law family; clarified eq 24 = 2·∂Π/∂K_R | `role1_carbon_theory.tex` §2 · `15d23e5` |
| 2026-06-24 | R1 | Proved general capacity channel `K*_R > K°_R` (homotopy + Hessian cofactor; shift-ratio condition) | §3 Thm 1 · `15d23e5` |
| 2026-06-24 | R1 | Exact net-carbon inequality (C) + sufficient conditions; explicit power-law `C_R†` | §4 · `15d23e5` |
| 2026-06-24 | R1 | Gap memo (general condition + where it resists) | `gap_memo.md` · `15d23e5` |
| 2026-06-24 | R1 | Machine-precision exactness audit (15/15 vs finite differences); caught + fixed Theorem 1 sign typo | `verify_exact.py` · `c8913cf` |
| 2026-06-24 | R1 | Closed the four open points (submodularity, feedback, `C_R†`, regime ordering); distribution-free cutoffs Lemma | §1,4,6 · `c8913cf` |
| 2026-06-24 | R1 | Hardened Theorem 1: regime-crossing handled; replaced false diagonal-dominance claim with verified `H≺0` | §3 · `d6b1f02` |
| 2026-06-24 | R1 | Scope correction: quarantined out-of-scope contracting/correlation work to `exploratory_cross_role/` (candidate handoffs → Role 3 / Role 4) | `exploratory_cross_role/` · `d50efab` |
| 2026-06-24 | R1 | Capstone: two-moment sufficient statistic, tight magnitude bounds, least-favorable distribution (robust carbon certificate) | §"distribution-free reading" · `01f4843` |
| 2026-06-24 | R1 | Dropped general monotone-`C_R`-threshold claim (numerics diverge at knife-edge); Theorem 2 left honest | `LAB_NOTEBOOK.md` E11 · `01f4843` |
| 2026-06-24 | R1 | General existence theorem for the viability threshold C_R-dagger (large-cost anchor + power-law window) | role1_carbon_theory.tex Thm 4 · c761532 |
| 2026-06-24 | R1 | Adversarial peer review (3 referees); downgraded 2 overstated theorems to conditional form, rescoped threshold, fixed cofactor sentence + numbers | RESPONSE_TO_REFEREES.md · pending |
| 2026-06-25 | R1 | Self-audit caught a sign defect in Thm 6/7 proofs (referees missed it); fixed prose + verifier tilt check (bounds/conclusions were already correct) | role1_carbon_theory.tex §6 · c539cae |
| 2026-06-25 | R1 | Reviewed team updates: Role-3 (complete, validates my theory 32/32), Role-4 (rebuilt to FCL mandate, 17 tests, uses my closed forms); both consistent | (review) · n/a |
| 2026-06-26 | R1 | **A1 Week 2.** Existence + uniqueness + contract optimality via recursive-triangular FOC (unconditional (K_F,K_M) ND block + scalar Schur); unique dispatch via strict R>c | `role1_week2_theory.tex` §2 Thm 1 · pending |
| 2026-06-26 | R1 | Shift-ratio condition made uniform along the C_M-homotopy (support-wide monotone g ⇒ realized endpoint inequality at every C_M) | §3 Lemma 4 · pending |
| 2026-06-26 | R1 | Emission keystone: exact endogenous condition + sufficient bound. Resolves Week-1 conjecture NEGATIVE across BOTH regimes (no finite interior optimum reduces carbon): large-FCL blocked by the irreducible floor (K_M−K_R)_+; small-FCL blocked because at small C_R the no-FCL grid already decarbonizes (K_F°→0) and the channel reverses. Fall only at the cheap-renewable corner | §4 Thm 2 / Prop 3 · pending |
| 2026-06-26 | R1 | Re-audit: built direct state-by-state fossil simulator (surplus absorption) = closed form to 7 digits; corrected the mechanism (formula already credits absorption; the floor, not "FCL draws fossil", is the obstruction) | `verify_week2.py` T3 + LAB E19 · pending |
| 2026-06-26 | R1 | Hardening pass: T3 floor lemma (proved) + irreducibility theorem (carbon sign not cutoff-decidable ⇒ no distribution-free proof of the conjecture) + uniform-shape benchmark Δ0<0; excised small-FCL (Role 4); primitivized/anchored conditions (Schur content, power-law exact interval, MRSV scoped) | §4 + §5 · LAB E20 · pending |
| 2026-06-26 | R1 | Connectedness of {C_R:Δ≥0}: bounded + non-empty + single interval under strict-down-crossing MRSV condition | §5 Thm 3 · pending |
| 2026-06-26 | R1 | Sharp N&S channel condition as a path integral (monotone g sufficient not necessary); two-sided Δ bounds proved tight via attaining laws | §6 Thm 4/5 · pending |
| 2026-06-26 | R1 | Week-2 numerical suite vs quadrature of Π | `verify_week2.py` · pending |

## Cross-role flags (for the group, not Role 1 deliverables)
| Date | From | To | Item |
|---|---|---|---|
| 2026-06-24 | R1 | Role 2 | Confirmed closed-form corrections (factor `c` in 25/26, large-FCL flat term, eq-24 factor-2) |
| 2026-06-24 | R1 | Role 3 | Carbon-sign-across-distributions starter (`exploratory_cross_role/verify_correlation.py`) |
| 2026-06-24 | R1 | Role 4 | Small-FCL boundary `K*_M=K°_R` / regime stitching; contract-proof generalization starter |
