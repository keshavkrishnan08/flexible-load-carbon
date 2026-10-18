# Response to Referees: `role1_carbon_theory.tex`

The Role 1 carbon paper was put through an adversarial peer review by **three
independent referees** (2026-06-24): a proof-checker (R1), a counterexample
hunter (R2, who rebuilt the model from scratch with a Gaussian copula and ran 70+
experiments), and an overclaim/scope auditor (R3, who ran all five verification
scripts and compared every cited number to actual output).

**Consensus verdict:** the conclusions are *true* (R2 found **no genuine
counterexample**, every failure coincided with a violated hypothesis), and the
exact-algebra core is *honestly verified*; but several **proofs and statements
over-reached** and needed repair or hedging. This document lists each finding and
the change made. All are now in the revised PDF (11 pp).

## Critical fixes (flagged FATAL/MAJOR; corroborated across referees)

1. **"Two-moment sufficient statistic" was false as stated** (R1-FATAL, R3-MAJOR).
   Δ also depends on `q°=F(0;K°_R)` and the equilibrium capacities, all
   distribution-dependent. → **Downgraded** to *"Affine representation at fixed
   capacities"* (Thm, retitled) + an explicit **Remark "Not a sufficient statistic
   across F."** Abstract reworded ("at fixed equilibrium capacities … affine in two
   conditional means").

2. **"Least-favorable = uniform, robust certificate for every F∈U" over-reached**
   (R1, R2, R3 all flagged). The proof holds the F-dependent capacities fixed while
   varying F; and the uniform residual demand is itself the knife-edge (no interior
   optimum). → **Restated** as *"Least-favorable conditional shape"* (fixed
   capacities) + new **Remark `rem:lfd`** stating plainly that the cross-F
   distribution-robust certificate is *not* closed (capacity covariation only
   signed in direction by Thm 1), and that closing it is open.

3. **Distribution-free cutoffs Lemma was large-FCL only** (R1-MAJOR). In small-FCL
   `F(−K_M)≠0`. → **Lemma 2 restated**: the no-FCL cutoff is general; the two FCL
   cutoffs are distribution-free *in the large-FCL regime*; small-FCL explicitly
   excluded. **Prop (regime map)** corrected: the distribution-free profit/blackout
   claim now covers only regions (II)-(III); region (I) deferred to Role 4.

4. **Threshold theorem `C_R†` over-claimed "for every F"** (R1, R3). Only the
   large-cost anchor is general; the strict-fall window relies on the knife-edge
   (constant renewable marginal value), proven for power-law/scale families. The
   `E[fossil*]→0` step had a loose limit-interchange and the gap `C_R°<C_R†` rested
   on non-rigorous "pointwise dominance." → **Retitled** *"Viability threshold:
   general anchor, explicit window."* Part (i) general & rigorous; part (ii) under
   the stated knife-edge hypothesis with the gap proved via the explicit constant
   marginal values (not pointwise dominance); part (iii) honest, general-F nonempty
   window marked **conjectural**. The §gap item and abstract match.

5. **Theorem 1 small-FCL cofactor cited the wrong matrix entry** (R1-MAJOR). The
   cofactor `C_{KM,KR}=H_RF·H_FM − H_RM·H_FF` contains `H_FF`, not `H_MM`. →
   **Rewritten**: the extra small-FCL term is `−c·F_{K_R}(−K_M)·H_FF ≥ 0` because
   `H_FF<0` under Assumption 1. (Conclusion unchanged; R2 confirmed it numerically.)

6. **Prop (regime map) "a fortiori in (I)" was backwards** (R1). A weaker
   utilization effect shrinks the *left* side of (C), making it harder, not easier.
   → **Removed** the "a fortiori"; region (I) carbon sign explicitly left to the
   small-FCL analysis.

## Calibration / overclaim fixes (R3)

7. **"machine precision" → "6-16 digits."** Internal inconsistency with §6 (several
   formulas at 1e-4 to 1e-7). Fixed in abstract and the uniform-lemma proof; kept
   only where ≤1e-15 actually holds (eqs 25, 45, cutoffs).

8. **MV "constant at K_R∈{1,5,9}"** mismatched the script (tests {1,4,8}, prints
   `const=False` because K_R=8 crosses to small-FCL). → Restated as constant on the
   **large-FCL portion** of the locus (verified K_R∈{1,4,5}); explicitly notes it is
   *not* constant once the locus leaves that regime.

9. **Abstract "a single condition" → "two conditions"** (shift-ratio + interior
   regularity), since Theorem 1 needs Condition 2 as well.

10. **"Sharpness … tight" → "plausibly tight."** No reversed-channel example was
    delivered (the candidate families fail to converge); even at corr +0.95 the
    equilibrium window stayed in the decreasing-g region. Explicit counterexample
    handed to Role 3.

11. **`dK_R/dC_M` last value `−108` → `−92.1`** (misquote; the true FD value, noisy
    at the knife-edge). Noted as such.

12. **"all four points closed" → "three closed; regime map ordered, one crossover
    open."** Matches the in-text deferral of the small-FCL boundary to Role 4.

13. **Razor-thin strictness** (R2, R3): for right-skewed demand the no-FCL grid also
    builds heavy renewables, so the strict fall on (C_R°,C_R†) can be `Δ→0⁺`. Noted
    in the §6 threshold bullet, with the solver-instability caveat.

## Minor (R1)

14. `K_F*≥K_F°` now justified in one line (`F(K_F*)≥φ°` for `C_M≤C̄_M`).
15. Theorem 1 integration step: added continuity (maximum theorem) + "continuous,
    a.e. nonpositive derivative ⇒ non-increasing" to license the FTC across the
    regime crossing.
16. Condition 1/2 notation `C_M∈[C_M, C̄_M]` (clash) → `C_M∈(0, C̄_M]`.

## Not changed (defended)
- Exact identities (cutoffs 5/9, 17/18; gradients; fossil decomposition; magnitude
  bounds −6.43≤−2.17≤+3.23), all three referees confirmed these are correct and
  honestly verified.
- `K_R*>K°_R` (Theorem 1 core): R2 could not break it even at corr +0.95; robust.
- Condition 2's numerical-only status and its knife-edge lapse: R3 judged it
  "explicitly and fairly hedged"; unchanged.

**Net effect:** no theorem was retracted, but two were **downgraded to their honest
conditional form** (sufficient statistic, least-favorable) and one **rescoped**
(threshold: general anchor + explicit window). The paper now claims exactly what it
proves.
