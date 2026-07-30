"""
Week 3 Task 1: optimal FCL dispatch-and-curtailment contract solver.

Week 1/2 built a solver for the *capacity* problem where the dispatch rule
is fixed as the paper's greedy eq. 3:

    d*(x) = min{ max(K_F - x, 0), K_M }

Week 3 asks whether an OPTIMALLY DESIGNED state-contingent contract can
achieve lower carbon than the greedy rule -- specifically, can it "flip the
carbon sign" in parameter regions where the greedy dispatch increases carbon
relative to no-FCL?

The admissible contract class:
    d: R → [0, K_M]  with  d(x) = 0  for x > K_F  (consumer priority,
                                                      Assumption 1: β+p > R)

For any dispatch schedule d(·), the economic quantities per state x are:
    fossil(x, d) = min(K_F, max(x + d, 0))   # eq-86 generalized
    mining revenue per state = R · d(x)
    blackout per state = max(x - K_F, 0)      # unchanged (d=0 in scarcity)

DISPATCH LP (fixed capacities K_R, K_F, K_M)
─────────────────────────────────────────────
The schedule is discretized: d_i = d(x_i), z_i = fossil(x_i, d_i) = min(K_F, (x_i+d_i)_+).

Since z_i is piecewise-linear in d_i, it's LP-tractable by introducing z_i
as a separate variable with constraints that force z_i = fossil(x_i, d_i):
    z_i ≥ 0
    z_i ≥ x_i + d_i      (forces z_i ≥ (x_i + d_i)_+  together with z_i≥0)
    z_i ≤ K_F
For minimization objectives (carbon or -profit), the optimizer drives z_i to
its tightest lower bound, so z_i = max(0, x_i+d_i) = min(K_F, ...) at the
optimum (proved in the docstrings of solve_firm_optimal_dispatch and
solve_carbon_optimal_dispatch below).

Firm-optimal contract:  maximize  Σ w_i (R·d_i − c·z_i)
Carbon-optimal contract: minimize Σ w_i · c · z_i
                         s.t.     Σ w_i (R·d_i − c·z_i) ≥ profit_floor

Both are LPs solved via scipy.optimize.linprog (HiGHS backend for ≥1.7).

JOINT CAPACITY + CONTRACT SOLVER
──────────────────────────────────
For the full question "does the optimal contract flip the carbon sign", we
jointly optimize over (K_R, K_F, K_M) as well as d(·):

    min_{K_R,K_F,K_M ≥ 0, d(·) admissible}  carbon(K_R, K_F, K_M, d(·))
    s.t.  profit(K_R, K_F, K_M, d(·)) ≥ profit_floor

This is a bilevel problem: inner LP (dispatch) nested inside outer NLP
(capacities). For each fixed (K_R, K_F, K_M), the inner LP is solved exactly,
so the outer objective is well-defined but non-smooth. We use scipy's
derivative-free L-BFGS-B with finite-difference gradients (the LP is fast
enough that each gradient evaluation is cheap).

COMPARISON TABLE (computed by run_contract_sweep.py):
    A) No-FCL benchmark:       optimal (K_R°, K_F°, K_M=0)
    B) Firm-optimal joint:     optimal (K_R*, K_F*, K_M*) with greedy dispatch
    C) Carbon-optimal joint:   optimal (K_R**, K_F**, K_M**) with LP contract,
                                profit floor = profit(B)

Week 3 keystone question: is carbon(C) < carbon(A)?
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import integrate
from scipy.optimize import linprog, minimize

from .distributions import ResidualDemand
from .model import Params
from .solver import SolveResult, solve_no_fcl


# ─────────────────────────────────────────────────────────────────────────────
# Grid helpers
# ─────────────────────────────────────────────────────────────────────────────

def state_grid(dist: ResidualDemand, K_R: float, N: int = 400) -> tuple:
    """Uniform grid over the residual-demand support [-K_R, D_bar], with
    PDF weights w_i (summing to 1) computed from the CDF.

    Returns (x_grid, weights) where weights[i] ≈ P(x ≈ x_i).
    """
    lo, hi = -K_R, dist.D_bar
    x = np.linspace(lo, hi, N)
    dx = x[1] - x[0]
    # f(x_i) ≈ (F(x_i + dx/2) - F(x_i - dx/2)) / dx * dx = CDF midpoint diff
    cdf_hi = np.array([dist.cdf(xi + dx / 2, K_R) for xi in x])
    cdf_lo = np.array([dist.cdf(xi - dx / 2, K_R) for xi in x])
    w = np.clip(cdf_hi - cdf_lo, 0.0, None)
    w /= w.sum()  # re-normalize to handle numerical edge effects
    return x, w


# ─────────────────────────────────────────────────────────────────────────────
# Single-dispatch LP (fixed capacities)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ContractResult:
    d: np.ndarray          # optimal dispatch schedule d(x_i)
    z: np.ndarray          # realized fossil output per state
    x: np.ndarray          # state grid
    w: np.ndarray          # state weights
    K_R: float
    K_F: float
    K_M: float
    profit_dispatch: float # dispatch contribution to profit (excl. capital)
    carbon: float          # c * E[fossil]
    blackout: float        # (beta+p) * E[(x-K_F)_+]
    dual_profit: float     # shadow price of profit-floor (0 for firm-optimal)
    lp_status: str         # 'Optimal', 'Infeasible', etc.

    def firm_profit(self, params: Params) -> float:
        """Full profit including capital costs."""
        cap = params.CF * self.K_F + params.CR * self.K_R + params.CM * self.K_M
        return self.profit_dispatch - self.blackout - cap

    def as_solve_result(self, params: Params) -> SolveResult:
        """Cast to the SolveResult format used by Week 1/2 code."""
        from .solver import SolveResult
        bp = float(np.sum(self.w * np.clip(self.x - self.K_F, 0, None)))
        return SolveResult(
            K_R=self.K_R, K_F=self.K_F, K_M=self.K_M,
            profit=self.firm_profit(params),
            blackout_prob=float(np.sum(self.w * (self.x > self.K_F))),
            carbon=self.carbon,
        )


def _build_dispatch_lp(x: np.ndarray, w: np.ndarray,
                        params: Params, K_F: float, K_M: float,
                        objective: str = 'profit',
                        profit_floor: float | None = None):
    """Build and solve the dispatch LP.

    Variables: v = [d_0, …, d_{N-1}, z_0, …, z_{N-1}]  (length 2N)
    d_i = dispatch at state x_i,  z_i = fossil output at state x_i.

    LP form: min c_obj @ v  s.t. A_ub @ v ≤ b_ub,  bounds on v.

    Constraints (for each i):
      (1) z_i ≥ x_i + d_i  →  d_i - z_i ≤ -x_i   [drives z_i to (x_i+d_i)_+]
      (2) If objective is 'carbon': profit ≥ floor
          Σ w_i (R·d_i − c·z_i) ≥ π_floor
          → Σ w_i (-R·d_i + c·z_i) ≤ -π_floor

    Bounds: 0 ≤ d_i ≤ K_M * 1(x_i ≤ K_F),  0 ≤ z_i ≤ K_F.
    """
    N = len(x)
    R, c = params.R, params.c
    scarcity = x > K_F  # d_i forced to 0 in these states

    # ── Objective ──
    if objective == 'profit':
        # max Σ w_i(R d_i - c z_i)  →  min Σ w_i(-R d_i + c z_i)
        c_obj = np.concatenate([-R * w, c * w])
    else:
        # carbon: min Σ w_i c z_i
        c_obj = np.concatenate([np.zeros(N), c * w])

    # ── Constraint (1): d_i - z_i ≤ -x_i, only for NON-scarcity states ──
    # For scarcity states (x_i > K_F), fossil output is exactly K_F regardless
    # of d (which is 0). Adding the constraint there would require z_i ≥ x_i > K_F
    # while z_i ≤ K_F, making the LP infeasible. We handle scarcity states by
    # fixing z_i bounds to (K_F, K_F) below (their contribution is a constant).
    non_scar = ~scarcity  # mask: states where constraint is non-trivial
    idx_ns = np.where(non_scar)[0]
    n_ns = len(idx_ns)

    A1 = np.zeros((n_ns, 2 * N))
    for row, i in enumerate(idx_ns):
        A1[row, i] = 1.0        # d_i coefficient
        A1[row, i + N] = -1.0   # z_i coefficient
    b1 = -x[idx_ns]

    rows_A = [A1]
    rows_b = [b1]

    # ── Constraint (2): profit floor (only for carbon objective) ──
    dual_row_idx = None
    if objective == 'carbon' and profit_floor is not None:
        A2 = np.zeros((1, 2 * N))
        A2[0, :N] = -R * w   # -R w_i on d_i
        A2[0, N:] = c * w    # +c w_i on z_i
        b2 = np.array([-profit_floor])
        rows_A.append(A2)
        rows_b.append(b2)
        dual_row_idx = len(rows_b) - 1

    A_ub = np.vstack(rows_A)
    b_ub = np.concatenate(rows_b)

    # ── Bounds ──
    # d: 0 in scarcity (consumer priority), [0,K_M] otherwise
    # z: forced to K_F in scarcity (fossil at capacity); [0,K_F] otherwise
    d_max = np.where(scarcity, 0.0, K_M)
    z_lo = np.where(scarcity, K_F, 0.0)  # force z_i = K_F in scarcity states
    z_hi = np.where(scarcity, K_F, K_F)  # K_F ceiling everywhere
    bounds = [(0.0, float(d_max[i])) for i in range(N)] + \
             [(float(z_lo[i]), float(z_hi[i])) for i in range(N)]

    return c_obj, A_ub, b_ub, bounds, dual_row_idx


def solve_firm_optimal_dispatch(dist: ResidualDemand, params: Params,
                                 K_R: float, K_F: float, K_M: float,
                                 N: int = 400) -> ContractResult:
    """Solve the firm-optimal dispatch LP for fixed (K_R, K_F, K_M).

    The firm-optimal contract maximizes E[R·d(x) - c·fossil(x,d)] over all
    admissible d(·). By Lemma 1 (paper Section 3.3), the unique optimal is
    the greedy rule d*(x) = min{max(K_F-x, 0), K_M}. This LP validates that
    claim numerically: the LP solution should agree with d* to machine
    precision.

    At the LP optimum: z_i = max(0, x_i + d_i) because the objective
    includes -c·z_i (we minimize z_i) and z_i ≥ x_i + d_i. Combined with
    z_i ≥ 0, this forces z_i = max(0, x_i + d_i) exactly. (For R > c, the
    objective also maximizes d_i, so d_i = K_M whenever x_i + K_M ≤ K_F,
    i.e. in the full-dispatch region, and d_i = K_F - x_i in the gap-filling
    zone -- exactly the greedy rule.)
    """
    x, w = state_grid(dist, K_R, N)
    c_obj, A_ub, b_ub, bounds, _ = _build_dispatch_lp(x, w, params, K_F, K_M, 'profit')

    res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    d = res.x[:len(x)]
    z = res.x[len(x):]
    status = res.message

    profit_disp = float(np.sum(w * (params.R * d - params.c * z)))
    carbon = float(params.c * np.sum(w * z))
    blackout = float((params.beta + params.p) * np.sum(w * np.clip(x - K_F, 0, None)))

    return ContractResult(
        d=d, z=z, x=x, w=w, K_R=K_R, K_F=K_F, K_M=K_M,
        profit_dispatch=profit_disp, carbon=carbon, blackout=blackout,
        dual_profit=0.0, lp_status=status,
    )


def solve_carbon_optimal_dispatch(dist: ResidualDemand, params: Params,
                                   K_R: float, K_F: float, K_M: float,
                                   profit_floor: float,
                                   N: int = 400) -> ContractResult:
    """Solve the carbon-optimal dispatch LP for fixed (K_R, K_F, K_M).

    Minimizes carbon c·E[fossil(x,d)] subject to:
      (a) dispatch profit E[R·d - c·fossil] ≥ profit_floor
      (b) admissibility: d(x) ∈ [0,K_M], d(x)=0 for x>K_F

    The carbon-optimal dispatch differs from the firm-optimal (greedy) in
    that it avoids dispatching in states where the fossil draw is high, even
    at the cost of some revenue. The 'profit_floor' is usually set to the
    firm-optimal dispatch profit so both solve the same constrained problem
    from opposite directions.

    Returns the dual variable on the profit-floor constraint as
    `dual_profit` -- this is the shadow price (how much extra carbon we'd
    avoid if we relaxed the profit floor by one unit).
    """
    x, w = state_grid(dist, K_R, N)
    c_obj, A_ub, b_ub, bounds, dual_row_idx = _build_dispatch_lp(
        x, w, params, K_F, K_M, 'carbon', profit_floor=profit_floor
    )

    res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    d = res.x[:len(x)] if res.x is not None else np.zeros(len(x))
    z = res.x[len(x):] if res.x is not None else np.zeros(len(x))
    status = res.message

    # Extract dual of the profit-floor constraint
    dual = 0.0
    if res.ineqlin is not None and dual_row_idx is not None:
        duals = res.ineqlin.marginals
        if duals is not None and len(duals) > dual_row_idx:
            dual = float(-duals[dual_row_idx])  # sign: ineq dual is ≤ form

    profit_disp = float(np.sum(w * (params.R * d - params.c * z)))
    carbon = float(params.c * np.sum(w * z))
    blackout = float((params.beta + params.p) * np.sum(w * np.clip(x - K_F, 0, None)))

    return ContractResult(
        d=d, z=z, x=x, w=w, K_R=K_R, K_F=K_F, K_M=K_M,
        profit_dispatch=profit_disp, carbon=carbon, blackout=blackout,
        dual_profit=dual, lp_status=status,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Joint capacity + contract solver
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class JointContractResult:
    """Result of the joint (capacity + contract) optimization."""
    K_R: float
    K_F: float
    K_M: float
    contract: ContractResult      # dispatch LP result at the optimal capacities
    no_fcl: SolveResult           # no-FCL benchmark at the same parameters
    carbon_no_fcl: float
    carbon_firm_optimal: float    # carbon under greedy dispatch + firm capacities
    carbon_contract: float        # carbon under optimal contract + contract capacities
    sign_flip: bool               # carbon_contract < carbon_no_fcl ?
    profit_floor_used: float

    def __repr__(self):
        return (
            f"JointContractResult(\n"
            f"  K=({self.K_R:.2f}, {self.K_F:.2f}, {self.K_M:.2f})\n"
            f"  carbon: no_fcl={self.carbon_no_fcl:.4f}, "
            f"firm={self.carbon_firm_optimal:.4f}, "
            f"contract={self.carbon_contract:.4f}\n"
            f"  carbon_sign_flip={self.sign_flip}  "
            f"(contract < no_fcl: {self.carbon_contract - self.carbon_no_fcl:+.4f})\n)"
        )


def _carbon_joint_objective(K_vec, dist, params, profit_floor, N_inner):
    """Inner function: for given capacities, solve the carbon-optimal LP
    and return total carbon (including capital).

    Used as the objective for the outer capacity optimizer. Returns a large
    penalty if the LP is infeasible (profit floor unattainable).
    """
    K_R, K_F, K_M = float(K_vec[0]), float(K_vec[1]), float(K_vec[2])
    if K_R <= 0 or K_F <= 0 or K_M <= 0:
        return 1e12

    res = solve_carbon_optimal_dispatch(
        dist, params, K_R, K_F, K_M, profit_floor=profit_floor, N=N_inner
    )
    if 'Infeasible' in res.lp_status or 'Error' in res.lp_status:
        return 1e12

    # Full carbon: E[fossil] only (capital doesn't emit carbon directly)
    return res.carbon


def solve_joint_carbon_optimal(
    dist: ResidualDemand,
    params: Params,
    profit_floor: float | None = None,
    N_inner: int = 300,
    KR_max: float | None = None,
    KF_max: float | None = None,
    KM_max: float | None = None,
) -> JointContractResult:
    """Jointly optimize (K_R, K_F, K_M) + dispatch contract to minimize carbon.

    If profit_floor is None, uses the firm-optimal joint profit as the floor
    (so we're asking: "can we achieve lower carbon than the greedy approach
    while maintaining the same profit?").

    Outer optimizer: L-BFGS-B with finite-difference gradients, multistart.
    Inner optimizer: exact LP (solve_carbon_optimal_dispatch).
    """
    from .solver import solve_with_fcl

    D = params.D_bar
    KR_max = KR_max or 50.0 * D
    KF_max = KF_max or 10.0 * D
    KM_max = KM_max or 10.0 * D
    bounds_outer = [(1e-3, KR_max), (1e-3, KF_max), (1e-3, KM_max)]

    # Step 1: get the no-FCL benchmark
    no_fcl = solve_no_fcl(dist, params, KR_max=KR_max, KF_max=KF_max)

    # Step 2: get the firm-optimal joint solution (greedy dispatch)
    firm_sol = solve_with_fcl(dist, params, KR_max=KR_max, KF_max=KF_max, KM_max=KM_max)

    # The firm-optimal's dispatch profit (excluding capital/blackout) is
    # computed from the LP at those capacities
    firm_contract = solve_firm_optimal_dispatch(
        dist, params, firm_sol.K_R, firm_sol.K_F, firm_sol.K_M, N=N_inner
    )
    firm_carbon = firm_contract.carbon

    # Step 3: set profit floor
    if profit_floor is None:
        # Floor = firm-optimal dispatch contribution to profit (excl. capital)
        profit_floor = firm_contract.profit_dispatch

    # Step 4: jointly optimize capacities + carbon-optimal contract
    starts = [
        [firm_sol.K_R, firm_sol.K_F, firm_sol.K_M],
        [no_fcl.K_R * 1.5, firm_sol.K_F * 0.8, firm_sol.K_M],
        [firm_sol.K_R * 2.0, firm_sol.K_F, firm_sol.K_M * 0.5],
    ]
    best_result = None
    best_carbon = np.inf

    for x0 in starts:
        try:
            opt = minimize(
                _carbon_joint_objective,
                x0=x0,
                args=(dist, params, profit_floor, N_inner),
                method='L-BFGS-B',
                bounds=bounds_outer,
                options={'ftol': 1e-8, 'gtol': 1e-6, 'maxiter': 200, 'eps': 1e-4},
            )
            if opt.fun < best_carbon:
                best_carbon = opt.fun
                best_result = opt
        except Exception:
            pass

    if best_result is None:
        K_R_opt, K_F_opt, K_M_opt = firm_sol.K_R, firm_sol.K_F, firm_sol.K_M
    else:
        K_R_opt, K_F_opt, K_M_opt = best_result.x

    contract_opt = solve_carbon_optimal_dispatch(
        dist, params, K_R_opt, K_F_opt, K_M_opt,
        profit_floor=profit_floor, N=N_inner
    )

    return JointContractResult(
        K_R=K_R_opt, K_F=K_F_opt, K_M=K_M_opt,
        contract=contract_opt,
        no_fcl=no_fcl,
        carbon_no_fcl=no_fcl.carbon,
        carbon_firm_optimal=firm_carbon,
        carbon_contract=contract_opt.carbon,
        sign_flip=(contract_opt.carbon < no_fcl.carbon),
        profit_floor_used=profit_floor,
    )
