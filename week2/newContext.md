# CONTEXT.md — Team A1, Role 2 (Solver & Numerical Validation)

## Who / what
- ASSIP research project. I am **Role 2** on **Team A1** (team of 4).
- We are stress-testing an analytical model about whether Bitcoin mining / flexible
  computing loads (FCLs) can *reduce* carbon emissions by financing renewable capacity.
- Role 2 job: build a numerical **solver** that reproduces the paper's hand-solved
  closed forms, then generalize it. I am the team's "fact-checker for the math."

## Which paper (read this carefully)
The current Week 1 plan targets the **FCL paper**:
"Flexible Computing Loads, Electricity Grid Resilience, and Carbon Emission
Reduction: A Tale of Bitcoin Mining and AI Training" (file: FCL_Carbon_Paper.pdf).

> There is also an EARLIER, simpler "cost-minimization" paper (one variable k,
> Section 3.5, eqs 11-13/48/60). That paper is NOT this week's target — it is
> background only. All Role 2 references below are to the FCL paper.


## The FCL model in plain terms
- Residual demand `x̃ = D̃ − K_R·S̃` (regular demand minus renewable output), with
  CDF `F(x; K_R)` on support `[−K_R, D̄]`. Higher `K_R` shifts mass toward surplus.
- The utility chooses THREE capacities simultaneously:
  - `K_R` renewable capacity (cost `C_R`/unit),
  - `K_F` fossil backup capacity (cost `C_F`/unit, variable/carbon cost `c`/unit),
  - `K_M` FCL/mining capacity (ASIC cost `C_M`/unit).
- `R` = mining revenue per MWh, `p` = retail price, `β` = blackout penalty (VOLL).
- FCL dispatch: mining runs on spare capacity and is curtailed at peak.
- Triple win claim: if `C_M < C̄_M`, introducing FCL raises profit, lowers blackout,
  and can lower carbon. `C̄_M = (R−c)(β+p−c−C_F)/(β+p−c)`.

## My Role 2 tasks (verbatim from the A1 Week 1 Plan)
1. **Build a solver that matches the closed-form benchmarks.** Code the joint
   capacity problem in Section 4 (profit **eq 10**, FOCs **eqs 12, 13, 15**); test
   against the uniform closed-forms in **eqs 25 and 26** until they match to the decimal.
2. **Open it to any residual-demand distribution.** Generalize the input `F(x; K_R)`
   so it outputs `K*_R, K*_F, K*_M`, blackout probability, and carbon for any distribution.
3. **Validate Role 1's draft.** Run the candidate general condition across a few
   distribution families; flag fast when numbers and theory disagree.
4. **Map where the result holds vs breaks.** Sweep parameters; chart which regions
   keep carbon down (rough is fine).

## Key equations to target (FCL paper — verified against the PDF)
- **Eq 10 (profit, large-FCL regime K_M>K_R):**
  `Π = p·E[D̃] + R∫_{K_F−K_M}^{K_F} F(x;K_R)dx − c·(K_F − ∫_{K_F−K_M}^{−K_R} F dx)`
  `    − (β+p)∫_{K_F}^{D̄}(1−F)dx − C_F·K_F − C_R·K_R − C_M·K_M`
  (Equivalent primitive form, valid both regimes — fossil cost = c·E[fossil],
  with E[fossil] = ∫_{−K_M}^{K_F−K_M}(1−F)dx per Remark 2.)
- **Eq 12 (FCL FOC):**     `F(K_F − K_M; K_R) = C_M / (R − c)`
- **Eq 13 (fossil FOC):**  `F(K_F; K_R) = (β + p − c − C_F − C_M) / (β + p − R)`
- **Eq 15 (renewable FOC, envelope thm):**
  `R∫_{K_F−K_M}^{K_F} ∂F/∂K_R dx + c∫_{−K_R}^{K_F−K_M} ∂F/∂K_R dx`
  `  + (β+p)∫_{K_F}^{D̄} ∂F/∂K_R dx = C_R`
- **Uniform closed forms** (F(x;K_R) = (x+K_R)/(D̄+K_R) on [−K_R, D̄]):
  - **Eq 22:** `K*_F − K*_M = D̄ − [(R−C_M−c)/(R−c)]·(D̄+K*_R)`
  - **Eq 23:** `K*_F = D̄ + [(R−c−C_F−C_M)/(β+p−R)]·(D̄+K*_R)`
  - **Eq 24 (knife-edge for K*_R):** sign of
    `(R−c)[(R−C_M−c)/(R−c)]² + c + (β+p−R)[(R−c−C_F−C_M)/(β+p−R)]² − 2C_R`
    determines K*_R = +∞ (positive) / arbitrary (zero) / 0 (negative).
    → IMPORTANT: under the uniform distribution K*_R is a CORNER (∞ or 0), never a
      nice interior value. The numeric optimizer hitting the bound or sitting at 0 is
      CORRECT, not a bug. For an interior-K*_R test, use a non-uniform distribution.
  - **Eq 25 (carbon WITHOUT FCL, uniform):** messy closed form in C_R, C_F, c, β, p, D̄.
    READ FROM PDF — my transcription is unreliable. Structure: ∝ D̄ × (expression).
  - **Eq 26 (carbon WITH FCL, uniform):**
    `∝ D̄ + [(R−c−C_F−C_M)/(β+p−R)]·(D̄+K*_R) − ½·(C_M/(R−c))²·(D̄+K*_R)`
  - Result: (26) < (25) when C_R is small enough (then eq 24 positive, K*_R = ∞,
    fossil → 0, carbon → 0).
> Claude Code: read Section 4 (eqs 10–26), Appendix B.1 (Prop 1 proof), and the
> Section 4.3 carbon part directly from FCL_Carbon_Paper.pdf and confirm/correct all
> of the above, especially eq 25. TRUST THE PAPER over these notes.

## What "validate" means
- Numerical optimum must satisfy FOCs 12, 13, 15 and reproduce the uniform closed
  forms (22, 23, 26) to the decimal. Match the carbon comparison (26) vs (25).
- Confirm Proposition 1 qualitatively: with C_M < C̄_M, FCL (i) raises profit,
  (ii) lowers blackout, (iii) can lower carbon in the right parameter range.

## How I want Claude Code to work
- **Explain changes before making them.** I'm a student and must understand every
  line — being able to explain the code is the actual assignment. Don't silently
  rewrite large chunks.
- Build incrementally: confirm FOCs/closed forms one at a time; add eq 25/26 carbon
  checks; then a non-uniform distribution; then the parameter sweep.
- Write validation as real `pytest` tests asserting numeric == closed-form to a tol.
- If a PDF equation conflicts with my notes, trust the PDF and tell me.

## Files in this folder
- `FCL_Carbon_Paper.pdf` — THE paper to build against. (Add it here so Claude Code
  can read it directly.)
- `CONTEXT.md` — this file.
