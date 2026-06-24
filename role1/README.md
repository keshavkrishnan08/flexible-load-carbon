# Role 1 — General Carbon Theory

Deliverables for Team A1, Week 1. Builds on `FCL_Carbon_Paper.pdf`
(§3 model, §4 baseline analysis, App. B.1, Prop. 4, footnote 6).

## Contents
| File | What it is |
|---|---|
| `role1_carbon_theory.tex` | Main result document (Management-Science-grade theory). Compile with `pdflatex`. |
| `gap_memo.md` | One-page memo: the general condition + where the fully general proof resists. |
| `verify.py` | Independent numerical validation (no closed forms assumed). |

## Headline results
1. **Uniform ground truth re-derived** (eqs 18–26) and verified to machine
   precision; knife-edge structure proved for the whole power-law family; eq 24
   shown to equal `2·∂Π/∂K_R` (sign-correct).
2. **Capacity-substitution channel, general** — `K*_R > K°_R` for any
   distribution whose **shift ratio** `g(x)=F_{K_R}/f` is non-increasing across
   the FCL dispatch window. Proof by homotopy in `C_M` + Hessian-cofactor sign.
   Power-law satisfies it for every α (⇒ footnote 6).
3. **Net-carbon condition (C)** — exact inequality, decomposed into a
   distribution-free utilization effect (`+`) and a capacity-substitution effect
   whose sign is the channel above. Clean sufficient condition: shift-ratio
   condition + `C_R` small ⇒ carbon strictly falls for all `C_M < C̄_M`.

## Reproduce
```bash
pip install --break-system-packages numpy scipy
python3 verify.py          # V1 closed forms + knife-edge; V2 capacity-channel sign-law
pdflatex role1_carbon_theory.tex
```

## Cross-role notes
- Confirms **Role 2**'s closed-form corrections (factor `c` in 25/26, large-FCL
  flat term, eq-24 factor-2). Their solver is the validation backend.
- **Role 4** owns the companion Bitcoin (oligopoly) paper; the regime-stitching
  handoff (small-FCL / interior / full-coverage) is flagged in `gap_memo.md`.
