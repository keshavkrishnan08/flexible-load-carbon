# CONTEXT.md — Team A1, Role 2 (Solver & Numerical Methods), Week 3

> Session context with **Week 2 status confirmed and filled in** from the actual
> repo/test results. Read Sections 1–4 before touching code.

---

## 1. The project, in one paragraph

Team A1 (four people, ASSIP research project) is empirically and theoretically
testing whether Bitcoin mining / flexible computing loads (FCLs) can reduce
carbon emissions by financing renewable energy capacity. The primary reference
is the **FCL paper** — three capacity variables: renewable `K_R`, fossil `K_F`,
FCL/mining `K_M`, plus a blackout penalty `β`. There is also an **earlier
cost-minimization paper** (one decision variable, lowercase symbols) that is
background only — do not conflate the two. Role 2 (you) owns solver
development and numerical methods, always built against the FCL paper.

---

## 2. Where the team has been (Week 1 → Week 2 → Week 3 arc)

### Week 1 (confirmed)
Built the baseline solver, validated to machine precision against closed-form
uniform-distribution benchmarks (36 passing tests). A 150-cell parameter sweep
found profit and blackout risk improved in every cell, but **carbon never
improved in any cell (0/150)** — including the cheap-renewable corner where
the paper's theory predicts a carbon win. Root cause: the paper's carbon-reduction
proof relies on `K_R → ∞`, but the with-FCL profit problem is **unbounded**
under Assumption 1, so that optimum is unattainable in practice. This produced
a direct **contradiction** with Role 1 (who proved carbon strictly falls,
verified 3000/3000) and agreed with Role 4 (0/756).

### Week 2 (confirmed as of handoff)
Reframed the carbon question around a **finite interior optimum** instead of
the unbounded corner. Four tasks completed independently (Role 1 was not
reachable during Week 2). Key results:

**CONFIRMED: The Week 1 contradiction was NOT resolved.**

- 76-cell sweep over (C_R, sigma) for the lognormal-primitive family found
  **8 certified genuine interior optima** (bound-independent, gradient~0,
  Hessian strictly negative-definite) — and **carbon improved in 0/8 of them**.
- Headline finding: at sigma=0.6, C_R=26, Role 1's endpoint shift-ratio
  condition is genuinely TRUE (g(K_F*)=0.379 ≥ g(K_F*-K_M*)=0.368) and K_R*
  did increase — yet carbon STILL rose 71%. Locked down in
  `test_shift_ratio_condition_holding_still_does_not_save_carbon`.
- Real precision bug found and fixed in `scipy.integrate.quad` (silent
  mis-convergence at undeclared discontinuity x=-K_R, fixed via `points=`
  kwarg). Also found: analytic Hessian needs a Leibniz boundary-term
  correction that Week 1's FOC derivation correctly did NOT need.
- Tools delivered: `fcl_solver/hessian.py`, `fcl_solver/finite_optimum.py`,
  `fcl_solver/finite_optimum_sweep.py`, `TruncatedLognormal` + `lognormal_primitive()`.
- All deliverables in `week2/`, 133 tests passing.

### Week 3 (current)
Scope expanded significantly. The team is now:
- Characterizing the **optimal FCL dispatch-and-curtailment contract** (not just
  capacity levels) — can an optimally-designed schedule flip the carbon sign
  that the myopic greedy rule cannot?
- Building a **distributionally-robust** version of the capacity/contract problem.
- Drawing the full **carbon phase diagram** over the cost plane.

---

## 3. Week 3 role assignments (all four roles, for context)

### Role 1 — Optimal Contract and General Carbon Theory
Characterize the optimal FCL dispatch-and-curtailment contract; prove whether
the optimal contract can flip the carbon sign; prove the exact carbon
characterization (necessary and sufficient, with the minimal decisive statistic
identified); solve the distributionally-robust capacity rule; draw the carbon
phase diagram analytically.

### Role 2 — Solver and Numerical Methods (YOU)
See Section 4 below.

### Role 3 — Comparative Statics and Robustness
Sign the characterization and optimal-contract comparative statics; quantify
the value of robustness; map fragility.

### Role 4 — Theory Hardening and Regimes
Extend the contract and characterization across regimes; harden proofs;
regime-map new objects; reconcile the team at end of week.

---

## 4. Your Week 3 tasks (Role 2)

### Task 1 — Build the optimal-contract solver
Replace the hardcoded dispatch rule `d*(x)=min{(K_F-x)_+, K_M}` (paper eq. 3)
with the full class of admissible state-contingent schedules and solve:

1. **Dispatch LP (fixed capacities):** For given (K_R, K_F, K_M), solve an LP
   over d: x → [0,K_M] for two objectives:
   - *Firm-optimal*: maximize profit → should recover the greedy rule (validate
     Lemma 1 numerically).
   - *Carbon-optimal*: minimize carbon subject to profit ≥ floor.
2. **Joint capacity+contract solver:** Optimize over (K_R, K_F, K_M, d(·))
   jointly — outer scipy minimizer over capacities, inner LP for dispatch.
3. **Contract-carbon gap:** Compare carbon(firm-optimal joint) vs
   carbon(carbon-optimal joint) vs carbon(no-FCL benchmark).

Key math: fossil output per state x under dispatch d is
  `fossil(x, d) = min(K_F, max(x+d, 0))`
which is piecewise-linear in d → LP-tractable. The LP is:
  - Variables: d_i, z_i  (dispatch and fossil at each grid point i)
  - z_i ≥ x_i + d_i, z_i ≥ 0, z_i ≤ K_F  (z_i = fossil output)
  - d_i = 0 for x_i > K_F (consumer priority / Assumption 1: β+p > R)
  - Objective: max Σ w_i(R·d_i − c·z_i) [firm] or min Σ w_i·c·z_i s.t. profit floor [carbon]

### Task 4 — Certify the new optima
For the LP problems: LP duality gives automatic global optimality certificates.
Implement dual-variable extraction and verify:
- Strong duality (primal obj = dual obj to machine precision)
- Complementary slackness (pinpoint which constraints bind, which don't)
- Sensitivity analysis: shadow prices on the profit-floor constraint

For the joint (capacity + contract) problem: verify the outer optimizer found
a true minimum by checking first-order conditions via finite differences, and
verify the LP inner problem achieves strong duality at each capacity.

### Task 3 — Validate the characterization theorem at scale
Evaluate across a large distribution library whether the carbon-optimal contract
ever achieves lower carbon than the no-FCL benchmark ("carbon sign flip"), and
if so map the region in cost space where it does. Render the phase diagram with
three regions: carbon-up / carbon-neutral / carbon-down.

Key distributions to test: Uniform, Power(alpha) family, Beta scale-mixtures,
lognormal-primitive (from Week 2), bimodal.

### Task 2 — Distributionally-robust solver (stub until Role 1 spec arrives)
Framework: for an ambiguity set Γ of distributions around a nominal F,
the robust capacity problem is:
  min_{K_R,K_F,K_M,d(·)} max_{F̃ ∈ Γ} carbon(F̃; K, d)
  s.t. min_{F̃ ∈ Γ} profit(F̃; K, d) ≥ floor

Implement with moment-based ambiguity set as default (pending Role 1's exact
spec). Certify saddle: verify minimax ≈ maximin numerically.

Suggested implementation order: **Task 1 → Task 4 → Task 3 → Task 2**.

---

## 5. Cross-role dependencies

**You depend on Role 1 for:**
- Exact admissible schedule class for the optimal contract (assumed [0,K_M]
  for x ≤ K_F, 0 for x > K_F — matches Assumption 1 β+p > R)
- Exact carbon functional form (derived from first principles: c·E[fossil(x̃,d(x̃))])
- Ambiguity set definition for Task 2 (default: moment-based until spec arrives)
- Regularity conditions for the contract and robust problems

**Roles that depend on you:**
- Role 1: numerical validation of closed-form contract
- Role 3: solver outputs for comparative statics; Hessian/cofactors
- Role 4: regime-boundary and phase-diagram numerics for integration pass

---

## 6. How to run / work

```bash
cd week3/
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```
