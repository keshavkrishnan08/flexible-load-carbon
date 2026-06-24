# Role 1 — General Carbon Theory

Deliverables for **Team A1, Role 1 (General Carbon Theory)**, per the A1 Week 1
Plan. Builds on `FCL_Carbon_Paper.pdf` (§3 model, §4 baseline analysis, App. B.1,
Prop. 4, footnote 6).

## Role 1 tasks (A1 Week 1 Plan) → status
| Task | Where | Status |
|---|---|---|
| Re-derive the closed-form case (eqs 25, 26) as ground truth | `role1_carbon_theory.tex` §2 | ✅ verified ≤6e-10 |
| Generalize the net carbon-reduction result — the general condition where capacity-substitution beats utilization | §3–4 (condition C, shift ratio) | ✅ |
| Prove the capacity comparison `K*_R > K°_R` in general (from the eq-15 shadow value) | §3 (Theorem 1) | ✅ |
| Draft result + gap memo by Friday | `gap_memo.md` | ✅ |

## Contents (the Role 1 deliverable)
| File | What it is |
|---|---|
| `role1_carbon_theory.tex` (+ `.pdf`) | The Role 1 result document. Compile with `pdflatex`. |
| `gap_memo.md` | One-page memo: the general condition + where the fully general proof resists. |
| `verify_exact.py` | **Adversarial exactness suite** — every analytical formula vs finite-differences of the profit integral. 15/15 PASS to 6–16 digits. |
| `verify.py` | Closed-form (eqs 25/26) + knife-edge + capacity-channel validation. |
| `validate_capacity_channel.py` | Shift-ratio sign-law sweep across Beta families (`K*_R>K°_R`). |
| `validate_regime_crossing.py` | Regime-crossing + Hessian-definiteness scan. |
| `LAB_NOTEBOOK.md` | Chronological research log (entries E1–E10; E8–E10 are the quarantined cross-role work). |
| `exploratory_cross_role/` | **Out-of-scope** material (optimal-contract / mechanism / robustness / correlation-charting). NOT part of the Role 1 deliverable — candidate handoffs to Role 3 / Role 4. See its README. |

## Headline results (Role 1)
1. **Uniform ground truth re-derived** (eqs 18–26) and verified to machine
   precision; knife-edge structure proved for the whole power-law family; eq 24
   shown to equal `2·∂Π/∂K_R` (sign-correct).
2. **Capacity-substitution channel, general** — `K*_R > K°_R` for any
   distribution whose **shift ratio** `g(x)=F_{K_R}/f` is non-increasing across
   the FCL dispatch window. Proof by homotopy in `C_M` + Hessian-cofactor sign.
   Power-law satisfies it for every α (⇒ footnote 6).
3. **Net-carbon condition (C)** — exact inequality, decomposed into a
   distribution-free utilization effect and a capacity-substitution effect whose
   sign is the channel above. Sufficient condition: shift-ratio + `C_R` small ⇒
   carbon strictly falls for all `C_M < C̄_M`.

## The four open points — all closed (see `gap_memo.md`)
1. **Submodularity** is not an obstruction — homotopy+cofactor proof is complete
   under a Regularity condition (`H≺0`, verified by eigenvalues; lapses only at
   the knife-edge where `K*_R=∞>K°_R` is immediate).
2. **Endogenous-capacity feedback** — comparison probabilities are
   distribution-free (Lemma 3) and the one level effect is signed by Theorem 1,
   so (C)+Theorem 1 is a *complete* characterization.
3. **`C_R†` explicit** for the power-law family:
   `C_R† = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`.
4. **Regimes ordered** — `C_M^fc < C̄_M < C̄_M^b`. (Full small-FCL/regime stitching
   is Role 4.)

All backed by `verify_exact.py` (15/15 PASS).

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
