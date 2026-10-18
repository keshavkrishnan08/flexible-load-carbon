# CONTEXT.md: Team A1, Role 2 (Solver & Numerical Methods), Week 4

> Session context with **Week 3 status confirmed** from the actual repo.
> Read Sections 1-4 before touching code.

## 0. Week 3 confirmed status (as of handoff)

Week 3's 22/22 tests pass. Central finding: 0/20 sign flips in the dispatch-
phase sweep, even the LP-optimal (carbon-minimizing) dispatch at the firm-
optimal capacities fails to flip the carbon sign. This sharpens Weeks 1/2:
not only does greedy dispatch not help, but the *best possible* dispatch also
doesn't help at those capacities. The joint capacity+contract optimization
is the remaining open question.

---

## 1. The project, in one paragraph

Team A1 is testing whether Bitcoin mining / FCLs reduce carbon emissions by
financing renewable capacity. Primary reference: the FCL paper (three capacity
variables K_R, K_F, K_M). Role 2 owns solver development and numerical methods.

## 2. The Week 1-3 arc (confirmed)

- **Week 1:** 0/150 carbon improvements. Unboundedness under Assumption 1.
- **Week 2:** 0/8 at certified finite interior optima. Even when the shift-ratio
  condition genuinely held (sigma=0.6, C_R=26), carbon rose 71%.
- **Week 3:** 0/20 at firm-optimal capacities even with carbon-optimal dispatch.
  Analytic Hessian, LP duality certificates, leverage-condition stub.

## 3. Week 4: the capstone

The headline result is a closed-form **classification functional Ψ** such that:

    sign(carbon_no_FCL − carbon_with_FCL) = sign(Ψ)

This is an if-and-only-if (not just sufficient), derived from the paper's
**Proposition 4** (Appendix B.1, p. 82-84). The functional lives in the
conditional-moment space; its zero level set is the exact carbon-neutral
boundary.

## 4. Your Week 4 tasks

### Task 1: Classification-functional sweep (keystone)

The functional Ψ from Proposition 4 (large-FCL regime K*_M > K*_R):

    E[fossil_with_FCL]  = K*_F − (C_M/(R-c)) · (K*_F − K*_M − μ*_low)  (44)
    E[fossil_no_FCL]    = K°_F·(1−φ°) + (φ°−q°)·μ°_mid                 (45)

    Ψ = (C_M/(R-c))·(K*_F−K*_M−μ*_low) − [K*_F − K°_F·(1−φ°) − (φ°−q°)·μ°_mid]

    Carbon improves ↔ Ψ > 0.

where μ*_low = conditional mean of x in [−K*_R, K*_F−K*_M] (full-dispatch
zone; the code uses this correct domain), μ°_mid = conditional mean in [0, K°_F] (no-FCL fossil zone).

Sweep across the full distribution library (Uniform, Power, Beta mixtures,
bimodal, lognormal-primitive) and confirm sign(Ψ) = sign(carbon_change) in
every cell.

### Task 4: Regularity-region map

Map where (a) a genuine interior optimum exists and (b) the Hessian is
negative-definite, using the Week 2 analytic Hessian machinery reused in
regularity_map.py. Outcomes: regular / corner_KR / corner_KM / corner_zero /
saddle / solver_failed.

### Task 3: Leverage condition + robust saddle

Leverage ratio λ = (surplus dispatch revenue) / (renewable capex). Map λ
across C_R for a given distribution. Separately, certify the distributionally-
robust saddle using a finite perturbation grid (exact spec pending Role 3).

### Task 2: Phase diagram from Ψ

Trace the zero level set of Ψ over the (C_R, C_M) plane. Bisect Ψ=0 for
machine-precision boundary locations. Render as a heatmap of Ψ's sign with
the zero contour highlighted.

## 5. New modules in week4/

```
fcl_solver/
  carbon_functional.py  Implements Ψ (Prop 4 eqs 44/45) and
                         compute_functional() → FunctionalResult
  classification_sweep.py  Sweeps the full distribution library
  phase_diagram_w4.py  Level-set phase diagram, bisection boundary
  leverage_saddle.py   Leverage condition + robust saddle
  regularity_map.py    Regularity-region map (reuses hessian.py)
tests/
  test_carbon_functional.py  Identity + sign-match + component tests
```

## 6. How to run

```bash
cd week4/
.venv/bin/pip install -r requirements.txt  # if not done
.venv/bin/python -m pytest tests/ -q
.venv/bin/python run_week4_sweep.py --fast    # smoke test
.venv/bin/python run_week4_sweep.py           # full sweep
```
