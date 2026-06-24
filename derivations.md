# CONTEXT.md — Team A1, Role 4 (Miner-Side Theory & Demand-Response Inducement)

## Who / what
- ASSIP research project. I am **Role 4** on **Team A1** (team of 4).
- We are stress-testing an analytical model about whether Bitcoin mining /
  flexible computing loads can *reduce* carbon emissions by financing
  renewable capacity.
- Role 4 job: nail the **miner-side foundation** the rest of the paper leans
  on — prove the regulator can induce any mining quantity by price, prove
  the revenue-exogeneity result that turns the utility's profit problem into
  a cost-min problem, and work out what changes when the grid only serves
  some of the miners. Then confirm all of it numerically.

## Which paper (read this carefully)
My tasks target the **old Bitcoin-mining paper**:
"Bitcoin Mining (and maybe AI training) for Carbon Emission Reduction"
(Li, Ren, Bellos; file: `Bitcoin_Mining_for_Carbon_Emission_Reduction.txt`,
the authored Feb 28 2026 draft).

> Note: Role 2 switched to the newer **FCL paper** because *its* tasks
> (joint K_R/K_F/K_M capacities) live there. Mine do NOT: the FCL paper
> abstracts the miner side into a reduced-form dispatch rule and does not
> contain eqs 9–10 or Appendix A's 61–68. The miner oligopoly micro-
> foundation only exists in this old paper, so Role 4 stays on it.

## The model in plain terms
- `n` symmetric Bitcoin miners compete for a fixed dollar block reward `R`,
  paying electricity price `P`. The regulator sets `P` (a demand-response
  program); the utility builds renewable capacity `k` and serves all demand.
- Mining is special: it can be dialed up/down instantly with no penalty, so
  it can soak up renewable surplus and be curtailed at peak — acting as a
  shock absorber that finances renewables and substitutes fossil backup.

## My Role 4 tasks (verbatim from the A1 Week 1 Plan)
1. **Prove price induces any mining quantity.** Section 3.4.1 (eqs 9–10)
   gives `d = (n−1)/n · R/P`; prove the regulator can set `P` to hit any
   target `d` in the oligopoly case and pin the conditions.
2. **Prove the revenue-exogeneity result.** Show why `P·d` is independent of
   the utility's decisions, which is what collapses profit-max into the
   cost-min problem in Section 3.5, and where it breaks.
3. **Push the partial-grid case.** Extend Appendix A (eqs 61–68, the `m > n`
   limit) to see how inducement and exogeneity change and whether the main
   result survives.
4. **Sim the induced demand and the partial-grid limit.** Quick numerical
   check to confirm the algebra.

## Key equations to target (verified against the .txt)
- **Eq 9 (miner i):** `max R d_i/(d_i + Σ_{j≠i} d_j) − d_i P`.
- **Eq 10 (equilibrium):** `d = (1 − 1/n) R / P`; inducement `P = (1−1/n)R/d`.
- **Exogeneity:** `P d = (1 − 1/n) R` (constant ⇒ profit-max = cost-min).
- **Eq 65 (partial-grid total):** `Σ_{M∪N} d = (m+n−1)R/(nP+mPo)`.
- **Eq 68 (partial-grid in-grid):**
  `d = n(m+n−1)R[mPo−(m−1)P]/(nP+mPo)²`.
- **Small-grid limit (`m≫n`):** `d → (nR/Po)(1−P/Po)`,
  `Pd → nR(P/Po)(1−P/Po)` — concave, peak `nR/4` at `P=Po/2`;
  `d ≥ 0` iff `P ≤ Po`; usable inducement capped at `nR/(2Po)`.
- **Eq 69 (adapted DR program):** clip surplus mining at `nR/(2Po)`.

## What "validate" means
- The closed forms (eq 10, eq 68) must match an independent best-response /
  FOC-system solve to the decimal.
- `P·d` must be numerically constant in the full grid and provably non-
  constant in the partial grid.
- The small-grid limit, the `nR/4` revenue peak, and the `P ≤ Po` /
  `nR/(2Po)` bounds must all check out.

## How I want Claude Code to work
- **Explain changes before making them.** I'm a student and must understand
  every line — being able to explain the code is the actual assignment.
  Don't silently rewrite large chunks.
- Re-derive each equation by hand from the .txt; don't just transcribe.
  Trust the paper over my notes and tell me about any discrepancy.
- Build incrementally: oligopoly (Tasks 1–2) → partial grid (Task 3) →
  sims/figures (Task 4). Write validation as real `pytest` tests.

## Files in this folder
- `Bitcoin_Mining_for_Carbon_Emission_Reduction.txt` — THE paper, with
  equations intact (the project markdown had them blanked out).
- `miner_demand/` — the package. `tests/` — the checks. `derivations.md` —
  the proofs. `run_sims.py` — figures + emissions probe. `README.md` — the
  writeup of what's confirmed and what to sync with Role 1.

---

## UPDATE — Theory Hardening and Regimes (the updated Role 4 task)

Dhruv asked me to take the **updated Role 4 task**: "Theory Hardening and
Regimes" on the **FCL paper** (not the old Bitcoin paper). Motivation: Keshav's
theoretical model (Role 1) and the numerical model (Role 2) **disagree** on
carbon — Role 1 proves carbon falls; Role 2 found it never does across 210
scenarios and that the model wants infinite capacity (Assumption 1).

My job (per Role 1's handoff): stitch the small-FCL / interior / full-coverage
regimes into one map, confirm the Hessian/boundedness conditions that feed
Assumption 1, resolve the small-FCL boundary `K*_M = K°_R`, and reconcile the
two models. Deliverable: `regimes/` (+ vendored Role 2 solver as backend),
`REGIME_HARDENING.md`, `run_regime_analysis.py`.

Resolution: the with-FCL program is unbounded in `K_R` exactly when
`C_R < C_R† = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`, which is the
carbon-reduction window. Assumption 1 alone doesn't give a finite optimum;
`C_R ≥ C_R†` is the missing condition. Carbon falls only once buildout exceeds
a crossover `K_R^cross` — below it Role 2 is right (utilization effect), above
it Role 1 is right (capacity channel). Both verified against Role 2's solver.
