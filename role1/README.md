# Role 1: General Carbon Theory

Deliverables for **Team A1, Role 1 (General Carbon Theory)**, per the A1 Week 1
Plan. Builds on `FCL_Carbon_Paper.pdf` (§3 model, §4 baseline analysis, App. B.1,
Prop. 4, footnote 6).

## Role 1 tasks (A1 Week 1 Plan) → status
| Task | Where | Status |
|---|---|---|
| Re-derive the closed-form case (eqs 25, 26) as ground truth | `role1_carbon_theory.tex` §2 | ✅ verified ≤6e-10 |
| Generalize the net carbon-reduction result, the general condition where capacity-substitution beats utilization | §3-4 (condition C, shift ratio) | ✅ |
| Prove the capacity comparison `K*_R > K°_R` in general (from the eq-15 shadow value) | §3 (Theorem 1) | ✅ |
| Draft result + gap memo by Friday | `gap_memo.md` | ✅ |

## Role 1 tasks (A1 Week 2 Plan) → status
| Task | Where | Status |
|---|---|---|
| Existence, uniqueness, contract optimality (recursive-triangular FOC; unique dispatch via strict `R>c`) | `role1_week2_theory.tex` §2 (Thm 1) | ✅ |
| Shift-ratio condition uniform along the `C_M`-homotopy | §3 (Lemma 4) | ✅ |
| Emission keystone for general `F`: **floor lemma** (proved) + **irreducibility theorem** (proved: the carbon sign is not cutoff-decidable, so the Week-1 conjecture has no distribution-free proof) + numerical residual (uniform-shape benchmark Δ₀<0 and Δ<0 at every scanned large-FCL interior optimum). Carbon falls only at the cheap-renewable corner. Small-FCL is Role 4 (out of scope) | §4 (Thm 2, Lemma 4, Props 2-3) | ✅ |
| Connectedness of the carbon-reduction set `{C_R: Δ≥0}` (bounded, non-empty, single interval) | §5 (Thm 3) | ✅ |
| Sharp N&S channel condition (path integral) + tight two-sided bounds | §6 (Thm 4, Thm 5) | ✅ |

All Week 2 identities checked in `verify_week2.py` against quadrature of the
profit integral.

## Contents (the Role 1 deliverable)
| File | What it is |
|---|---|
| `role1_carbon_theory.tex` (+ `.pdf`) | The Role 1 result document. Compile with `pdflatex`. |
| `gap_memo.md` | One-page memo: the general condition + where the fully general proof resists. |
| `verify_exact.py` | **Adversarial exactness suite**: every analytical formula vs finite-differences of the profit integral. 15/15 PASS to 6-16 digits. |
| `verify.py` | Closed-form (eqs 25/26) + knife-edge + capacity-channel validation. |
| `validate_capacity_channel.py` | Shift-ratio sign-law sweep across Beta families (`K*_R>K°_R`). |
| `validate_regime_crossing.py` | Regime-crossing + Hessian-definiteness scan. |
| `verify_carbon_robust.py` | Sufficient statistic + magnitude bounds + least-favorable distribution (§"distribution-free reading"). |
| `LAB_NOTEBOOK.md` | Dated, append-only research log (ISO-8601 entries E1-E11; conventions at top). |
| `RESPONSE_TO_REFEREES.md` | Point-by-point response to a 3-referee adversarial review; what was fixed/downgraded/defended. |
| `CONTRIBUTIONS.md` | Append-only contributions ledger (one row per result/fix/decision, with commit). |
| `exploratory_cross_role/` | **Out-of-scope** material (optimal-contract / mechanism / robustness / correlation-charting). NOT part of the Role 1 deliverable, candidate handoffs to Role 3 / Role 4. See its README. |

## Headline results (Role 1): post-referee, honestly calibrated
1. **Uniform ground truth re-derived** (eqs 18-26), verified vs quadrature to
   6e-10 (FOCs ≤1e-15); knife-edge proved for the power-law family (constant MV on
   the *large-FCL* portion of the locus); eq 24 = `2·∂Π/∂K_R` (sign-correct).
2. **Capacity-substitution channel, general**: `K*_R > K°_R` for any distribution
   satisfying **two** conditions: shift-ratio `g(x)=F_{K_R}/f` non-increasing,
   plus interior regularity. Proof by homotopy in `C_M` + Hessian-cofactor sign.
   Power-law satisfies the shift-ratio condition for every α. *(3 referees found no
   counterexample, incl. a from-scratch copula rebuild at corr +0.95.)*
3. **Net-carbon condition (C)**: exact inequality; distribution-free utilization
   effect vs sign-controlled capacity-substitution effect.
4. **Distribution-free reading** (capstone, stated at *fixed equilibrium
   capacities*): the carbon change is **affine in two conditional means**, sits
   inside **closed-form magnitude bounds** from cutoff data, and the **uniform is
   the least-favorable conditional shape** within the monotone class. *Honest
   scope:* these are fixed-capacity statements; the cross-distribution
   "robust certificate over every F∈U" is **not** closed (capacities co-vary with
   F), flagged open.
5. **Viability threshold `C_R†`**: general large-cost anchor (`Δ→−U₀<0`, every F)
   + explicit power-law window; general-F nonempty window conjectural.

## Status of the open points (see `gap_memo.md`, `RESPONSE_TO_REFEREES.md`)
- **Submodularity**: closed (homotopy+cofactor under Regularity `H≺0`).
- **Endogenous-capacity feedback**: closed *at fixed capacities*; cross-F
  covariation signed in direction, not fully closed.
- **`C_R†`**: general upper anchor proven; explicit power-law window; general
  window conjectural.
- **Regimes**: ordering `C_M^fc < C̄_M < C̄_M^b` proven; small-FCL region (I) +
  crossover `K*_M=K°_R` → Role 4.

Exact-algebra core backed by `verify_exact.py` (15/15, 6-16 digits). The paper now
claims exactly what it proves; full referee response in `RESPONSE_TO_REFEREES.md`.

## Reproduce
```bash
pip install --break-system-packages numpy scipy
python3 verify_exact.py     # 15/15 exactness audit
python3 verify.py           # closed forms + knife-edge + capacity channel
pdflatex role1_carbon_theory.tex
```

## Cross-role notes
- Confirms **Role 2**'s closed-form corrections (factor `c` in 25/26, large-FCL
  flat term, eq-24 factor-2). Their solver is the validation backend.
- **Role 3** (Comparative Statics) owns the carbon-sign-across-distributions
  mapping; a starter (`verify_correlation.py`) is in `exploratory_cross_role/`.
- **Role 4** (Theory Hardening) owns the small-FCL / regime stitching and the
  core-proof generalization; a starter contract write-up is in
  `exploratory_cross_role/`.
