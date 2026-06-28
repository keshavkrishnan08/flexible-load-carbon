# CONTEXT.md — Team A1, Role 2 (Solver & Numerical Methods), Week 2

> Briefing for a fresh Claude Code session. This file is the only context you start
> with, so read it top to bottom before touching code. It explains the project, what
> already exists from Week 1, the one finding that drives everything this week, and
> the four tasks I (Role 2) own.

---

## 0. Who I am and what this repo is

- **Project (ASSIP, Team A1):** Can Bitcoin mining / flexible computing loads (FCLs)
  reduce carbon emissions by financing renewable capacity? We empirically evaluate the
  analytical models from the FCL carbon paper.
- **My role:** Role 2 — the **solver and numerical-methods** person. I build the code
  that the theory people (Role 1, Role 3, Role 4) test their claims against.
- **Repo:** `team-a1`. **My branch:** `Role-2`. Git + GitHub authenticated via `gh`.
- **Stack:** `python3` on Mac, `scipy`, `numpy`. Existing solver is `fcl_solver.py`;
  sweep output is `sweep_results.csv`.

---

## 1. The model in one screen

The utility chooses three capacities simultaneously:

- `K_R` — renewable capacity
- `K_F` — fossil capacity
- `K_M` — FCL / mining capacity

**Residual demand** `x = D − S` (demand minus renewable supply) is random with CDF
`F(x; K_R)`, where `∂F/∂K_R > 0` (more renewables shifts residual demand down).

**Dispatch rule:** `d*(x) = min{ (K_F − x)_+ , K_M }` — mining runs on spare fossil
headroom and shuts off during scarcity (`x > K_F`).

**Objective:** profit maximization `Π` with blackout penalty `β`, retail price `p`,
fossil marginal cost `c`, fossil cap cost `C_F`, renewable cap cost `C_R`, FCL hardware
cost `C_M`, and mining revenue `R` per MWh.

**Assumption 1:** `β + p > c + C_F` and `β + p > R > c`.

**Triple-win threshold:** `C̄_M = (R − c)·φ°` with `φ° = (β + p − c − C_F)/(β + p − c)`.
When `C_M < C̄_M`, **profit and reliability improve**. Carbon is the contested third leg.

**Symbols introduced for Week 2:**
- `g(x) = F_{K_R}/f` — the **shift ratio** (how much a marginal unit of `K_R` moves the
  CDF, normalized by the density). Central to whether mining raises renewable capacity.
- **Endpoint shift-ratio condition:** `g(K_F*) ≥ g(K_F* − K_M*)`. This is the sharp
  condition for `K_R* > K_R°` (FCL raising renewable capacity vs the no-FCL benchmark `°`).
- **Carbon-reduction set:** `{ C_R : Δ(C_R) ≥ 0 }`, where `Δ` is the carbon saving.

---

## 2. Where Week 1 left off (read this carefully)

What exists on the `Role-2` branch:
- `fcl_solver.py` — joint capacity/dispatch solver built from scratch.
- 36 passing tests: closed-form validation, FOC conditions, Proposition 1 across
  distribution families, and a 150-cell parameter sweep.
- `sweep_results.csv` — output of that sweep.

**The headline Week-1 finding:** across all 150 parameter combinations, **profit
improved and blackout risk dropped in every cell, but carbon never improved in any
cell** — including the cheap-renewable corner (`C_R = 0.1`) where the paper's theory
predicts a carbon win.

**Root cause identified in Week 1:** the paper's original carbon-reduction proof leans
on `K_R → ∞`, which is unreachable because the with-FCL profit problem is unbounded
under Assumption 1. So the "carbon falls" result had no finite optimum to live at.

**The contradiction that Week 2 is built to resolve:** Role 1 proved carbon strictly
falls under their general sufficient condition (verified 3000/3000), while Role 2
(0/150) and Role 4 (0/756) independently found carbon never falls. The two sides were
never reconciled — the missing piece was whether a finite, well-defined optimum even
exists for the carbon claim to hold at.

---

## 3. The Week 2 pivot (why my tasks are shaped the way they are)

Week 2 reframes the whole carbon question around a **finite interior optimum** instead
of the `K_R → ∞` limit:

- **Role 1** now proves a *primitive sufficient condition* (the endpoint shift-ratio
  condition + a tail/skew bound) under which carbon falls **at a finite interior
  optimum**, and exhibits a concrete non-power-law `F` (e.g. truncated lognormal) that
  satisfies it. They also prove the optimum exists and is unique via a
  monotone-triangular / diagonal-dominance condition on the Hessian (not global
  concavity, which fails because `Π` is submodular in `(K_R, K_F)`).
- **My job (Role 2)** is to be the numerical backbone of that turn: validate a solver
  that handles those non-uniform distributions, *show carbon actually falls at the
  finite optimum* on a theory-tied family, and *certify the regularity* (Hessian
  negative-definiteness) that makes the optimum well-defined — then map where that
  regularity breaks.

In short: Week 1 said "carbon never falls because there's no finite optimum." Week 2
says "here is the finite optimum, here is the distribution class where it lives, now
confirm carbon falls there and prove the optimum is real." That confirmation is mine.

---

## 4. My four Week-2 tasks (Role 2)

### Task 1 — Build and validate the general solver
Implement the joint capacity/dispatch solver for `d*(x)` and `(K_R, K_F, K_M)` under
**any** residual-demand distribution `F(x; K_R)`. Validate against the benchmarks **to
machine precision**, and crucially **add at least one non-power-law `F` with a
semi-closed form** (truncated lognormal is the natural candidate, to match Role 1) so
the test set goes beyond the Week-1 uniform case.
*Deliverable:* generalized solver + new tests that pass to ~1e-12 on both the uniform
closed-forms and the new semi-closed-form distribution.

### Task 2 — Carbon-sign sweep at a finite optimum  — the keystone task
Sweep over **Role 1's primitive condition** on a **synthetic, theory-tied distribution
family** and show numerically that **carbon falls at a finite interior optimum**. This
is the one principled map that replaces the scattered Week-1 counts. This is the direct
empirical resolution of the 0/150 vs 3000/3000 contradiction, so it is the most
important single result I produce this week.
*Deliverable:* a clean sweep over the distribution family's shape parameter (and `C_R`)
showing the carbon saving `Δ ≥ 0` region at a genuine finite optimum, with the boundary
located.

### Task 3 — Analytic Hessian + negative-definiteness certificate
Derive and implement the **full analytic Hessian** and the comparative-statics cofactors,
replacing the knife-edge-noisy finite differences from Week 1. On that analytic Hessian,
**certify negative-definiteness along the interior path** for Role 1's distribution class.
*Deliverable:* analytic Hessian in code, cross-checked against finite differences, plus a
certificate (e.g. all leading principal minors / eigenvalue signs) along the optimum path.

### Task 4 — Map the boundary of the regularity region
Exhibit distributions **in the admitted class where the Hessian fails to be negative
definite**, delimiting "Condition 2" sharply and complementing Role 1's uniqueness proof.
*Deliverable:* a numerical map (parameter region) showing where regularity holds vs fails.

---

## 5. Cross-role dependencies

**I depend on Role 1 for:**
- The exact form of the **primitive sufficient condition** (endpoint shift-ratio + tail/skew
  bound) and the specific **distribution family** (likely truncated lognormal) — Task 2
  cannot be "theory-tied" without it.
- The statement of the **Hessian regularity condition** ("Condition 2") — Tasks 3 & 4
  certify and map exactly that condition.

**Roles that depend on me:**
- **Role 3** (comparative statics / robustness) needs my **analytic Hessian cofactors**
  to sign `∂(carbon effect)/∂R`, `∂/∂β`, `∂/∂p`, `∂/∂C_M`, and will hand me a
  reversed-channel counterexample `F` (where `g(K_F*) < g(K_F*−K_M*)`) to solve
  numerically.
- **Role 4** (mechanism design / regimes) shares the regime boundaries (the
  small-FCL/large-FCL crossover at `K_M* = K_R°`); my solver should be able to locate it.

**Open items to confirm before/while starting:**
- Get Role 1's chosen distribution family + the precise primitive condition.
- Confirm whether the earlier cost-minimization paper still factors in anywhere (Week 1
  flag: Role 4 had been working against that paper rather than the FCL paper).

---

## 6. How to run / work

```bash
# from repo root, on the Role-2 branch
git checkout Role-2
git pull

python3 -m pytest -q            # run the test suite (36 passing as of Week 1)
python3 fcl_solver.py           # or however the sweep entrypoint is wired
```

Prefer doing GitHub operations (PRs, merges, branch compare) on the **web UI** — terminal
output for those isn't visible to me in the way I want. Keep code changes on `Role-2`;
do **not** merge into a shared branch until the decisive cross-role carbon test has run
(Task 2 feeding a finite optimum through this canonical solver is part of that).

---

## 7. Suggested order of attack

1. **Task 1 first** — generalize the solver and lock in the non-uniform validation. Every
   other task runs on top of this, so it has to be machine-precision solid first.
2. **Task 3** — derive the analytic Hessian. Tasks 2 and 4 both need it (Task 2 needs a
   trustworthy "this is a real optimum," Task 4 maps where the Hessian fails).
3. **Task 2** — the carbon-sign sweep at the finite optimum. This is the headline; don't
   start it until the solver is validated and the Hessian confirms the optimum is real,
   or a spurious carbon-falls result will be unconvincing.
4. **Task 4** — map the regularity boundary, reusing the analytic Hessian from Task 3.

When in doubt, the question to keep answering is: *does a finite interior optimum exist
here, is it unique/regular, and does carbon fall at it?* That sentence is the whole week.
