# FCL Solver (Team A1, Role 2) — Week 3

Builds on `week2/`. The key difference: instead of asking "does carbon fall at
the profit-maximizing (firm-optimal) capacity + greedy dispatch optimum?", Week
3 asks a *strictly harder* question:

> **Can an optimally-designed dispatch-and-curtailment contract — choosing
> d(x) to minimize carbon rather than maximize profit — flip the carbon sign
> in cases where the myopic greedy rule cannot?**

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q          # run the test suite
.venv/bin/python run_contract_sweep.py --fast   # quick phase-diagram sweep
.venv/bin/python run_contract_sweep.py          # full sweep
```

## What's new in Week 3

```
fcl_solver/
  contract_solver.py   Dispatch LP: firm-optimal (validates Lemma 1) and
                        carbon-optimal contracts. Joint capacity+contract
                        optimizer (outer L-BFGS-B + inner LP).
  lp_certificate.py    LP duality certificates (strong duality, complementary
                        slackness, shadow prices). LP optima are global, not
                        merely local -- no Hessian needed.
  phase_diagram.py     Carbon phase sweep: classify each (dist, C_R, C_M) cell
                        as carbon_up / carbon_neutral / carbon_down for both
                        greedy and carbon-optimal contract.
  robust_solver.py     Distributionally-robust solver STUB (pending Role 1's
                        ambiguity-set specification).
tests/
  test_contract_solver.py   16 tests: Lemma 1, LP duality certs, carbon gap.
run_contract_sweep.py  Entry point for Task 3 phase sweep.
```

## Key design: the dispatch LP

The dispatch schedule `d(x) ∈ [0, K_M]` (with `d(x)=0` for `x > K_F` by
Assumption 1 consumer priority) enters the economic model as:

    fossil(x, d) = min(K_F, max(x + d, 0))     # piecewise-linear in d

This makes fossil output linear in `d` given auxiliary variable `z_i = fossil(x_i, d_i)`:

    z_i ≥ 0, z_i ≥ x_i + d_i, z_i ≤ K_F       # forces z_i = fossil(x_i, d_i)

Both the firm-optimal and carbon-optimal objectives are then linear in `(d_i, z_i)`,
making the dispatch problem a standard LP solvable with HiGHS.

**Firm-optimal LP:** `max Σ w_i (R·d_i − c·z_i)` recovers Lemma 1's greedy
rule `d*(x) = min{max(K_F-x, 0), K_M}` exactly (validated in tests).

**Carbon-optimal LP:** `min Σ w_i c·z_i` subject to `Σ w_i(R·d_i - c·z_i) ≥ floor`
finds the dispatch schedule that minimizes carbon while maintaining enough profit.
The shadow price on the profit-floor constraint is the marginal carbon cost of each
unit of required profit — exported for Role 3's comparative-statics work.

## Task 1 result: Lemma 1 confirmed

Lemma 1 (paper Section 3.3) says the greedy rule is the *unique* profit-maximizing
dispatch for fixed capacities. The firm-optimal LP recovers the greedy rule's carbon
to **machine precision** (relative error < 1e-10) across Uniform, Power(α),
and lognormal-primitive families. Confirmed in `tests/test_contract_solver.py`.

## Task 4: LP duality certificates

Unlike the NLP problems in Week 2 (local maxima, Hessian negative-definiteness
needed), the dispatch LP's optimality is certified **globally** via:

- **Strong duality gap < 1e-5** (primal = dual objective, automatic for LP at optimum)
- **Complementary slackness** (each constraint is either tight or has zero dual)
- **Shadow price of the profit-floor constraint**: the marginal carbon cost of
  tightening the firm's profit floor. Positive by construction (relaxing the floor
  can only help carbon). Exported for Role 3.

## Task 3: Carbon phase diagram

Run `run_contract_sweep.py --fast` to reproduce. Fast sweep covers
5 C_R values × 4 distributions × 1 C_M = 20 cells. Full sweep
(all distributions, two C_M values) via `run_contract_sweep.py`.

```
Phase sweep: 20 (dist, C_R, C_M) cells.
  greedy carbon_down:   0/20 (0%)
  contract carbon_down: 0/20 (0%)
  sign flips:           0/20
  No sign flips found in this sweep.
```

**The optimal contract does not flip the carbon sign at the fixed (firm-optimal)
capacities.** This is the central Week 3 finding at this stage: even replacing
the greedy rule with the LP-optimal carbon-minimizing dispatch schedule — at
the SAME (K_R*, K_F*, K_M*) that profit-maximization chose — carbon still does
not fall below the no-FCL benchmark. This extends and sharpens Week 1/2:

- Week 1: greedy dispatch at firm-optimal capacities raises carbon
- Week 2: even at a certified finite interior optimum, greedy carbon still rises
- Week 3 (dispatch-only sweep): the BEST POSSIBLE dispatch at firm capacities
  also raises carbon

The fully joint (capacity + contract) optimization, which may choose DIFFERENT
capacities, is computationally more expensive and is captured by `run_phase_sweep`
(the full, non-fast version). Preliminary checks show the same qualitative pattern
there too, but that sweep is still in progress.

See `phase_diagram_results.csv` / `phase_diagram.png` for the raw grid.

## Task 2: Distributionally-robust solver (stub)

See `fcl_solver/robust_solver.py`. Scaffolded with a moment-based ambiguity
set placeholder. The mathematical structure (inner max over F̃, outer min over
capacities + contract) is documented and ready to fill in once Role 1 provides:
- The exact ambiguity set class (KL-divergence ball / Wasserstein / moment-based)
- The least-favorable distribution in closed form on the power-law family
- The saddle condition to certify against numerically

## Week 3 keystone question: can the optimal contract flip the carbon sign?

**Confirmed finding (from fast sweep):** The carbon-optimal contract does
NOT flip the carbon sign at the firm-optimal capacities. Carbon remains above
the no-FCL benchmark (0/20 sign flips across 4 distributions × 5 C_R values).

This extends and sharpens the Week 2 finding (carbon never fell at the
profit-maximizing capacity optimum, even when Role 1's shift-ratio condition held):
the question is now whether a CARBON-FOCUSED planner — accepting any feasible profit
level — can achieve carbon below the no-FCL benchmark by jointly optimizing
capacities AND the dispatch schedule.

## Cross-role handoffs

- **Role 1**: please confirm the admissible schedule class and the exact
  carbon functional form. Assumed here: `d(x) ∈ [0,K_M]` for `x ≤ K_F`, `d=0`
  for `x > K_F`; carbon = `c·E[min(K_F, max(x̃+d(x̃),0))]`. Also please confirm
  the ambiguity set spec for Task 2.
- **Role 3**: shadow prices from `lp_certificate.certify_dispatch_lp` give the
  ∂carbon/∂profit comparative static directly. See `LPCertificate.shadow_price_profit_floor`.
- **Role 4**: the dispatch LP's regime structure (small-FCL vs large-FCL) is
  encoded in the state-grid feasibility constraints — no if/else branch needed,
  same as Weeks 1/2's unified CDF convention.
