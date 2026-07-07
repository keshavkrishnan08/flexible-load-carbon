"""
Week 4 Task 4: regularity-region map.

The classification functional Ψ is derived under the regularity conditions:
  (a) The with-FCL profit problem has a genuine INTERIOR optimum — not a
      corner solution (K_R* at a bound) and not the degenerate "runaway" case.
  (b) The no-FCL profit problem has a genuine interior optimum (which is
      always satisfied under Assumption 1 per the no-FCL FOC, eq. 7).
  (c) The Hessian at K* is negative-definite (the optimum is a true local
      maximum, certified by the Week 2 analytic Hessian).

We map where (a)/(c) hold / fail across the (C_R, distribution-shape) plane,
reusing the Week 2 hessian.certify_negative_definite machinery.

Regularity outcomes:
  "regular"          — interior optimum, Hessian neg-def
  "corner_KR"        — K*_R hit its upper bound (unbounded problem)
  "corner_KM"        — K*_M hit its upper bound
  "corner_zero"      — K*_R collapsed to 0 (renewable too expensive)
  "saddle"           — interior critical point but Hessian NOT neg-def
  "solver_failed"    — optimizer did not converge or LP was infeasible
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .distributions import ResidualDemand
from .hessian import certify_negative_definite
from .model import Params
from .solver import SolveResult, solve_no_fcl, solve_with_fcl


@dataclass
class RegularityCell:
    CR: float
    dist_param: float   # e.g. alpha or sigma (for shape-plane sweeps)
    dist_name: str
    outcome: str
    K_R_star: float
    K_F_star: float
    K_M_star: float
    neg_def: bool | None   # None if not checked (corner / failed)
    min_eigenvalue: float | None


def classify_regularity(
    dist: ResidualDemand,
    params: Params,
    with_fcl: SolveResult | None = None,
    KR_max: float | None = None,
    KF_max: float | None = None,
    KM_max: float | None = None,
    boundary_tol_frac: float = 1e-4,
) -> tuple[str, SolveResult, bool | None, float | None]:
    """Classify the regularity of the with-FCL optimum.

    Returns (outcome, with_fcl_result, neg_def, min_eigenvalue).
    """
    D = params.D_bar
    KR_max = KR_max or 30.0 * D
    KF_max = KF_max or 5.0 * D
    KM_max = KM_max or 5.0 * D

    if with_fcl is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                with_fcl = solve_with_fcl(dist, params,
                                           KR_max=KR_max, KF_max=KF_max, KM_max=KM_max)
            except Exception:
                return "solver_failed", None, None, None

    # ── Classify by bound status ─────────────────────────────────────────
    bounds = with_fcl.at_upper_bound
    tol = boundary_tol_frac * D

    if bounds.get("K_R", False) or with_fcl.K_R > KR_max - tol:
        return "corner_KR", with_fcl, None, None
    if bounds.get("K_M", False) or with_fcl.K_M > KM_max - tol:
        return "corner_KM", with_fcl, None, None
    if with_fcl.K_R < tol:
        return "corner_zero", with_fcl, None, None

    # ── Interior: check Hessian ──────────────────────────────────────────
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            cert = certify_negative_definite(
                dist, params, with_fcl.K_R, with_fcl.K_F, with_fcl.K_M
            )
            neg_def = cert.negative_definite
            min_eig = float(np.min(cert.eigenvalues))
        except Exception:
            return "solver_failed", with_fcl, None, None

    if neg_def:
        return "regular", with_fcl, True, min_eig
    return "saddle", with_fcl, False, min_eig


def map_regularity(
    dist_factory,  # callable(param) -> ResidualDemand
    CR_values,
    param_values,  # alpha or sigma or whatever
    param_name: str,
    R=109.0, c=45.0, CF=10.0, CM=56.0, beta=190.0, p=10.0, D_bar=100.0,
) -> list[RegularityCell]:
    """Sweep (C_R, distribution-shape-parameter) and classify each cell.

    dist_factory : callable that takes a single parameter (e.g. alpha)
                   and returns a ResidualDemand.
    """
    cells = []
    for CR in CR_values:
        for param_val in param_values:
            params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=float(CM),
                            beta=beta, p=p, D_bar=D_bar)
            try:
                params.check_assumption1()
            except AssertionError:
                continue

            dist = dist_factory(param_val)
            outcome, wf, neg_def, min_eig = classify_regularity(dist, params)

            K_R = wf.K_R if wf else 0.0
            K_F = wf.K_F if wf else 0.0
            K_M = wf.K_M if wf else 0.0

            cells.append(RegularityCell(
                CR=float(CR), dist_param=float(param_val),
                dist_name=f"{param_name}={param_val:.2f}",
                outcome=outcome,
                K_R_star=K_R, K_F_star=K_F, K_M_star=K_M,
                neg_def=neg_def, min_eigenvalue=min_eig,
            ))
    return cells
