# A1 Integration & Consistency Check

This document certifies that the four A1 role deliverables form **one coherent,
mutually consistent body of work** — shared notation, shared closed forms, no
contradictions, and every numerical claim reproducible. Run `bash run_all.sh`.

## 1. Reproducibility (all suites green)
| Role | Check | Result |
|---|---|---|
| Role 1 | `verify_exact.py` — 15 analytical formulas vs finite differences of Π | **15/15**, 6–16 digits |
| Role 2 | `pytest` — solver vs closed forms / FOCs / knife-edge / sweep | **36 passed** |
| Role 3 | `run_all_experiments.py` — Prop-1, carbon map, §5.3, Role-1 stress test | **reproduces** (CSVs + figures) |
| Role 4 | `pytest tests/` — FOCs, Prop 1, small-FCL, regimes, Assumption 1 | **17 passed** |

## 2. Shared notation (identical across roles)
Residual demand `x̃ = D̃ − K_R·S̃` on `[−K_R, D̄]`, CDF `F(x;K_R)`, density `f`,
`F_{K_R}=∂F/∂K_R ≥ 0`. Margins `R` (FCL), `c` (fossil), `p` (retail), `β`
(blackout). Capital `C_R, C_F, C_M`. Assumption 1: `R>c+C_M`, `R<c+C_F+C_M`,
`β+p>c+C_F`, `β+p>R`. All four roles use these symbols identically.

## 3. Shared closed forms (derived in Role 1, re-used downstream)
These are derived and machine-verified in Role 1 and used verbatim by Role 4
(`role4/regimes.py`, `role4/proposition1.py`) and tested by Role 3:

| Object | Closed form | Origin | Re-used / tested |
|---|---|---|---|
| Adoption threshold | `C̄_M = (R−c)·φ°`, `φ°=(β+p−c−C_F)/(β+p−c)` | R1 eq (27) | R4 Prop 1, R3 |
| Knife-edge bracket | `eq24 = 2·∂Π/∂K_R = 2(C_R†−C_R)` | R1 Prop (knife-edge) | R4 reconcile.py (matches R2 constant) |
| With-FCL renewable bound | `C_R† = ½[c+(R−C_M−c)²/(R−c)+(R−c−C_F−C_M)²/(β+p−R)]` | R1 Prop (C_R†) | R4 regimes.py |
| No-FCL renewable bound | `C_R° = C_F²/2(β+p−c)` | R1 Prop (C_R†) | R4 regimes.py |
| Small-FCL threshold | `C̄_M^b = C̄_M + c·q°`, `q°=F(0;K_R°)` | R1 regime prop / R4 eq 62 | R4 small_fcl.py |
| Threshold ordering | `C_M^fc < C̄_M < C̄_M^b` | R1 + R4 | R4 test_regimes |

*Consistency:* Role 4's `THEORY_HARDENING.md` and `role4/regimes.py` reproduce
these formulas character-for-character; Role 4's `reconcile.py` confirms
`eq24_constant = 2(C_R†−C_R)` against Role 2's independently-coded constant.

## 4. Cross-validation (each result checked by ≥2 roles)
- **`K_R* > K_R°`** (capacity-substitution channel): *proved* in R1 (Thm 1,
  homotopy+cofactor), *re-derived* from the eq-15 FOC in R4, *confirmed
  numerically* in R3 (**32/32** scenarios, `role1_capacity_substitution.csv`).
- **Distribution-free profit & blackout** (Prop 1 (i),(ii)): *proved* R1/R4,
  *confirmed* R3 (**16/16** whenever `C_M<C̄_M`).
- **Utilization effect positive, distribution-free**: *proved* R1 (Term II of
  eq 17), *confirmed* R3 (every scenario).
- **Carbon falls only for small `C_R` / right-skew**: *predicted* by R1's
  threshold theorem (`C_R<C_R†`, large-cost anchor `Δ→−U_0<0`), *found* by R3
  (carbon down 2/32, all low-`C_R`), *explained* by R4's buildout crossover
  `K_R^cross` (reconciles R1 theory with R2's early "never falls" numerics).
- **Eqs 25/26 corrections** (factor `c`; large-FCL flat term; eq-24 = `2×`grad):
  *found* by R1, *independently confirmed* by R2's solver.

## 5. Shared open item (flagged identically by all roles — no overclaim)
The general-`F` **net-carbon Step 3** is conditional: proven for the
uniform/power-law family and signed by Role 1's shift-ratio condition, but the
fully general "carbon falls" is the paper's conditional "may." R1
(`RESPONSE_TO_REFEREES.md`), R3 ("boundary region"), and R4 ("GAP FLAGGED … Step 3
is not [airtight], by design") all state this in the same terms. This is the
single largest target for the next round (see `NEXT_ROLES_A1.pdf`).

## 6. No contradictions found
A line-by-line reconciliation surfaced **zero** numerical or notational
conflicts between roles. The one apparent tension — R1 "carbon can fall" vs R2
"never falls in the sweep" — is resolved in R4 §"reconciliation": R2's sweep sat
above the buildout crossover, where the utilization effect dominates; R1's
reduction obtains below `C_R†` where `K_R*` is unbounded. Both are correct.

## 7. Harness output (this run)
```
── role1 verify_exact
  ✓ role1 verify_exact
== Role 2: solver test suite ==
── role2 pytest
  ✓ role2 pytest
== Role 3: comparative-statics experiments ==
── role3 experiments
  ✓ role3 experiments
== Role 4: theory-hardening test suite ==
── role4 pytest
  ✓ role4 pytest

== SUMMARY: 4 passed, 0 failed ==
ALL A1 DELIVERABLES REPRODUCE.
```
