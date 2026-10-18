"""
Week 4 Task 2: carbon phase diagram via the classification functional.

Instead of the brute-force carbon computation from Week 3, the phase
diagram here is drawn directly from the classification functional Ψ:
  Ψ > 0 ↔ carbon_down
  Ψ = 0 ↔ boundary (carbon-neutral)
  Ψ < 0 ↔ carbon_up

This makes the boundary a genuine level set of Ψ rather than an
interpolated boundary from discrete carbon-sign measurements.

The phase diagram partitions the (C_R, C_M) cost plane for a fixed
distribution, OR the (C_R, α/σ) distribution-shape plane for fixed costs.
Both are rendered as heatmaps of Ψ's sign with the zero-level boundary
highlighted.

Phase-diagram boundaries are also located to machine precision by bisection
on Ψ = 0 (the exact condition for carbon-neutrality), replacing the
interpolation noise from Week 3's discrete sweep.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .carbon_functional import compute_functional
from .distributions import ResidualDemand
from .model import Params
from .solver import solve_no_fcl, solve_with_fcl


@dataclass
class PhaseDiagramCell:
    CR: float
    CM: float         # or distribution parameter for shape-plane sweeps
    psi: float
    outcome: str      # "carbon_down" | "carbon_neutral" | "carbon_up"
    corner_fcl: bool  # solver hit a bound


_PSI_NEUTRAL_TOL = 1e-3  # |Ψ| below this → neutral boundary


def _outcome(psi: float) -> str:
    if psi > _PSI_NEUTRAL_TOL:
        return "carbon_down"
    if psi < -_PSI_NEUTRAL_TOL:
        return "carbon_up"
    return "carbon_neutral"


def sweep_cost_plane(
    dist: ResidualDemand,
    CR_values=None,
    CM_values=None,
    R=109.0, c=45.0, CF=10.0, beta=190.0, p=10.0, D_bar=100.0,
    KR_max_mult=20.0,
) -> list[PhaseDiagramCell]:
    """Sweep Ψ over the (C_R, C_M) cost plane for a fixed distribution."""
    if CR_values is None:
        CR_values = np.arange(8.0, 50.0, 3.0)
    if CM_values is None:
        CM_values = np.arange(30.0, 64.0, 4.0)

    KR_max = KR_max_mult * D_bar
    KF_max = 5.0 * D_bar
    KM_max = 5.0 * D_bar

    cells = []
    for CR in CR_values:
        for CM in CM_values:
            params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=float(CM),
                            beta=beta, p=p, D_bar=D_bar)
            try:
                params.check_assumption1()
            except AssertionError:
                continue

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    result = compute_functional(dist, params,
                                                KR_max=KR_max, KF_max=KF_max,
                                                KM_max=KM_max)
                    # Detect corner
                    wf = solve_with_fcl(dist, params, KR_max=KR_max,
                                         KF_max=KF_max, KM_max=KM_max)
                    corner = any(wf.at_upper_bound.values())
                except Exception:
                    continue

            cells.append(PhaseDiagramCell(
                CR=float(CR), CM=float(CM),
                psi=result.psi, outcome=_outcome(result.psi),
                corner_fcl=corner,
            ))
    return cells


def bisect_psi_boundary(
    dist: ResidualDemand,
    CR_lo: float, CR_hi: float,
    CM: float,
    R=109.0, c=45.0, CF=10.0, beta=190.0, p=10.0, D_bar=100.0,
    KR_max_mult=20.0,
    tol=1e-6,
    max_iter=50,
) -> float | None:
    """Bisect Ψ(C_R; C_M) = 0 along a C_R line for fixed C_M and distribution.

    Returns the C_R value where Ψ ≈ 0 (carbon-neutral boundary), or None if
    Ψ doesn't change sign on [CR_lo, CR_hi].

    This gives machine-precision boundary locations instead of interpolated
    discrete-sweep boundaries.
    """
    KR_max = KR_max_mult * D_bar

    def psi_at_CR(CR):
        params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=float(CM),
                        beta=beta, p=p, D_bar=D_bar)
        try:
            params.check_assumption1()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = compute_functional(dist, params, KR_max=KR_max,
                                       KF_max=5*D_bar, KM_max=5*D_bar)
                return r.psi
        except Exception:
            return np.nan

    psi_lo = psi_at_CR(CR_lo)
    psi_hi = psi_at_CR(CR_hi)

    if np.isnan(psi_lo) or np.isnan(psi_hi):
        return None
    if psi_lo * psi_hi > 0:  # same sign: no crossing
        return None

    for _ in range(max_iter):
        mid = 0.5 * (CR_lo + CR_hi)
        if CR_hi - CR_lo < tol:
            return mid
        psi_mid = psi_at_CR(mid)
        if np.isnan(psi_mid):
            return None
        if psi_lo * psi_mid <= 0:
            CR_hi = mid
        else:
            CR_lo = mid
            psi_lo = psi_mid
    return 0.5 * (CR_lo + CR_hi)
