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

## Cross-role flags (for the group, not Role 1 deliverables)
| Date | From | To | Item |
|---|---|---|---|
| 2026-06-24 | R1 | Role 2 | Confirmed closed-form corrections (factor `c` in 25/26, large-FCL flat term, eq-24 factor-2) |
| 2026-06-24 | R1 | Role 3 | Carbon-sign-across-distributions starter (`exploratory_cross_role/verify_correlation.py`) |
| 2026-06-24 | R1 | Role 4 | Small-FCL boundary `K*_M=K°_R` / regime stitching; contract-proof generalization starter |
