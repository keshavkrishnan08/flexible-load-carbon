# Role 1 — General Carbon Theory

Deliverables for Team A1, Week 1. Builds on `FCL_Carbon_Paper.pdf`
(§3 model, §4 baseline analysis, App. B.1, Prop. 4, footnote 6).

## Contents
| File | What it is |
|---|---|
| `role1_carbon_theory.tex` | Main result document (Management-Science-grade theory). Compile with `pdflatex`. |
| `role1_contract_theory.tex` | **Extension I** — the optimal demand-response *contract*: existence/uniqueness/characterization (general F), N&S emission condition, the demand–supply correlation comparative static, and the regulator–utility mechanism. |
| `role1_robust_contract.tex` | **Extension II** — distributionally *robust* (least-favorable = uniform ⇒ closed-form worst-case certificate) and *detail-free* (prior-independent, Wilson-doctrine) contracting. |
| `LAB_NOTEBOOK.md` | Chronological research log: derivations, the sign-error catch, test-bug catches, dropped directions (carbon-tax = B1), verification ledger, open problems. |
| `gap_memo.md` | One-page memo: the general condition + where the fully general proof resists. |
| `verify_exact.py` | **Adversarial exactness suite** — every analytical formula vs finite-differences of the profit integral. 15/15 PASS to 6–16 digits. |
| `verify.py` | Closed-form + capacity-channel validation (no closed forms assumed). |
| `validate_capacity_channel.py` | Fast shift-ratio sign-law sweep across Beta families. |
| `validate_regime_crossing.py` | Regime-crossing + Hessian-definiteness scan. |
| `verify_contract.py` | Optimal-contract optimality: 0/4000 pointwise, 0/21,600 feasible policies beat d*. |
| `verify_correlation.py` | Correlation comparative static: carbon margin monotone in corr(D,S), sign-flips at zero. |

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

## The four open points — all closed (see `gap_memo.md`)
1. **Submodularity** is not an obstruction — homotopy+cofactor proof is complete
   under a checkable Regularity condition (diagonal dominance).
2. **Endogenous-capacity feedback** — comparison probabilities are
   distribution-free (Lemma 3) and the one level effect is signed by Theorem 1,
   so (C)+Theorem 1 is a *complete* characterization.
3. **`C_R†` is explicit** for the power-law family:
   `C_R† = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`.
4. **Regimes unified** — `C_M^fc < C̄_M < C̄_M^b`, triple win across all adoption
   regions. Sole residual (the exact `K*_M=K°_R` boundary) → Role 4.

All backed by `verify_exact.py` (15/15 PASS).

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

## Contracting extension (strictly A1 domain)
`role1_contract_theory.tex` places the *contract itself* on general footing — the
A1 mandate ("existence + full characterization of the optimal demand-response
contract d*(x) under general distributions; N&S emission condition; correlation
comparative static; principal-agent mechanism"):
1. **Optimal contract, general F.** The unique optimal demand-response contract is
   the renewable-first threshold rule `d*(x)=min{(K_F−x)_+, K_M}` — proven optimal
   over the *full* space of state-contingent policies, any distribution
   (0/21,600 feasible policies beat it numerically).
2. **N&S emission condition.** Carbon falls *iff* condition (C). Emission
   reduction is **not generic** — it needs real regularity (settles the mandate's
   "mild vs restrictive" question: mild-but-real).
3. **Correlation comparative static.** The shift ratio `g(x)=F_{K_R}/f = E[S|x̃=x]`
   is the conditional renewable factor; carbon falls **iff demand and renewable
   supply are sufficiently negatively correlated**. Decoupling: `K*_R>K°_R`
   *always*, but only negative association turns it into carbon reduction.
   Verified — net carbon saving monotone in corr(D,S), sign-flips at zero.
4. **Regulator–utility mechanism.** The price-based program implements d* as the
   agent's unique best response iff `R>c` (observable) and `β+p>R`; induced
   computing demand pinned by the distribution-free cutoff `C_M/(R−c)`.

Scope guard: no overlap with A2 (calibration), B1 (reliability/welfare/social-vs-
private pricing), or B2 (flexibility continuum/storage/multi-grid).
