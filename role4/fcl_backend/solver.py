"""
Joint numerical solver: maximizes utility profit over capacities, for any
residual-demand distribution (Task 1 + Task 2).

Two problems are solved, both as special cases of the same machinery:
  - solve_no_fcl   : maximize profit(K_R, K_F, K_M=0) over (K_R, K_F) -- the
                      no-FCL benchmark (paper eqs 6-9).
  - solve_with_fcl : maximize profit(K_R, K_F, K_M) over all three -- the
                      full joint problem (paper eq. 10 / Section 4).

Both use scipy.optimize.minimize on -profit with the *analytic* gradient
from foc.py (so optimization is fast and exact, not a noisy finite-diff
climb), bounded below by 0 and above by a generous multiple of D_bar.
Multiple starting points are tried and the best (highest-profit) result is
kept, since the paper's own analysis shows the problem can have a corner
solution in K_R (eq. 24's knife edge under the uniform family) -- the
solver reports whether any variable is sitting at its upper bound so that
a corner solution is visible rather than silently misreported as interior.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import minimize

from .distributions import ResidualDemand
from .foc import gradient
from .model import Params, blackout_probability, carbon_emissions, profit


@dataclass
class SolveResult:
    K_R: float
    K_F: float
    K_M: float
    profit: float
    blackout_prob: float
    carbon: float
    at_upper_bound: dict = field(default_factory=dict)  # {"K_R": True, ...} if corner
    converged: bool = True

    def __repr__(self):
        corner = ", ".join(k for k, v in self.at_upper_bound.items() if v) or "none"
        return (
            f"SolveResult(K_R={self.K_R:.4f}, K_F={self.K_F:.4f}, K_M={self.K_M:.4f}, "
            f"profit={self.profit:.4f}, blackout_prob={self.blackout_prob:.4f}, "
            f"carbon={self.carbon:.4f}, corner=[{corner}])"
        )


def _multistart_minimize(neg_obj, neg_jac, bounds, starts, tol=1e-10):
    best = None
    for x0 in starts:
        res = minimize(neg_obj, x0=x0, jac=neg_jac, bounds=bounds, method="L-BFGS-B",
                        options={"ftol": tol, "gtol": 1e-10, "maxiter": 2000})
        if best is None or res.fun < best.fun:
            best = res
    return best


def solve_no_fcl(dist: ResidualDemand, params: Params, KR_max=None, KF_max=None) -> SolveResult:
    """Maximize profit over (K_R, K_F) with K_M fixed at 0 (eqs 6-9)."""
    D = params.D_bar
    KR_max = KR_max if KR_max is not None else 20.0 * D
    KF_max = KF_max if KF_max is not None else 5.0 * D
    bounds = [(0.0, KR_max), (0.0, KF_max)]

    def neg_obj(z):
        K_R, K_F = z
        return -profit(dist, params, K_R, K_F, 0.0)

    def neg_jac(z):
        K_R, K_F = z
        g_KR, g_KF, _ = gradient(dist, params, K_R, K_F, 0.0)
        return np.array([-g_KR, -g_KF])

    starts = [(0.1 * D, 0.5 * D), (0.5 * D, 0.5 * D), (1.0 * D, 0.9 * D), (2.0 * D, 0.5 * D)]
    res = _multistart_minimize(neg_obj, neg_jac, bounds, starts)
    K_R, K_F = res.x
    at_bound = {"K_R": K_R > KR_max - 1e-6 * D, "K_F": K_F > KF_max - 1e-6 * D}
    return SolveResult(
        K_R=K_R, K_F=K_F, K_M=0.0,
        profit=-res.fun,
        blackout_prob=blackout_probability(dist, K_R, K_F),
        carbon=carbon_emissions(dist, params, K_R, K_F, 0.0),
        at_upper_bound=at_bound,
        converged=res.success,
    )


def solve_with_fcl_given_KR(dist: ResidualDemand, params: Params, K_R: float,
                             KF_max=None, KM_max=None) -> SolveResult:
    """Maximize profit over (K_F, K_M) only, at a *fixed* K_R (FOCs 12 & 13).

    Used to test eqs 18/19 (equivalently 22/23) -- the paper's closed forms
    for K*_F, K*_M *given* K_R -- without running into K*_R's own
    corner-solution behavior under the uniform/power families (CONTEXT.md's
    "K*_R is a corner, not a bug" point). The full 3-variable solve
    (solve_with_fcl) is for the joint problem including K_R.
    """
    D = params.D_bar
    KF_max = KF_max if KF_max is not None else 5.0 * D
    KM_max = KM_max if KM_max is not None else 5.0 * D
    bounds = [(0.0, KF_max), (0.0, KM_max)]

    def neg_obj(z):
        K_F, K_M = z
        return -profit(dist, params, K_R, K_F, K_M)

    def neg_jac(z):
        K_F, K_M = z
        _, g_KF, g_KM = gradient(dist, params, K_R, K_F, K_M)
        return np.array([-g_KF, -g_KM])

    starts = [(0.5 * D, 0.1 * D), (0.9 * D, 0.5 * D), (1.2 * D, 1.2 * D)]
    res = _multistart_minimize(neg_obj, neg_jac, bounds, starts)
    K_F, K_M = res.x
    at_bound = {"K_F": K_F > KF_max - 1e-6 * D, "K_M": K_M > KM_max - 1e-6 * D}
    return SolveResult(
        K_R=K_R, K_F=K_F, K_M=K_M,
        profit=-res.fun,
        blackout_prob=blackout_probability(dist, K_R, K_F),
        carbon=carbon_emissions(dist, params, K_R, K_F, K_M),
        at_upper_bound=at_bound,
        converged=res.success,
    )


def solve_with_fcl(dist: ResidualDemand, params: Params, KR_max=None, KF_max=None, KM_max=None) -> SolveResult:
    """Maximize profit over (K_R, K_F, K_M) jointly (paper eq. 10 / Section 4)."""
    D = params.D_bar
    KR_max = KR_max if KR_max is not None else 20.0 * D
    KF_max = KF_max if KF_max is not None else 5.0 * D
    KM_max = KM_max if KM_max is not None else 5.0 * D
    bounds = [(0.0, KR_max), (0.0, KF_max), (0.0, KM_max)]

    def neg_obj(z):
        K_R, K_F, K_M = z
        return -profit(dist, params, K_R, K_F, K_M)

    def neg_jac(z):
        K_R, K_F, K_M = z
        g_KR, g_KF, g_KM = gradient(dist, params, K_R, K_F, K_M)
        return np.array([-g_KR, -g_KF, -g_KM])

    starts = [
        (0.1 * D, 0.5 * D, 0.1 * D),
        (0.5 * D, 0.5 * D, 0.5 * D),
        (1.0 * D, 0.9 * D, 1.0 * D),
        (2.0 * D, 0.5 * D, 2.0 * D),
    ]
    res = _multistart_minimize(neg_obj, neg_jac, bounds, starts)
    K_R, K_F, K_M = res.x
    at_bound = {
        "K_R": K_R > KR_max - 1e-6 * D,
        "K_F": K_F > KF_max - 1e-6 * D,
        "K_M": K_M > KM_max - 1e-6 * D,
    }
    return SolveResult(
        K_R=K_R, K_F=K_F, K_M=K_M,
        profit=-res.fun,
        blackout_prob=blackout_probability(dist, K_R, K_F),
        carbon=carbon_emissions(dist, params, K_R, K_F, K_M),
        at_upper_bound=at_bound,
        converged=res.success,
    )
