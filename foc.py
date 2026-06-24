"""
Theory vs numerics reconciliation (updated Role 4) -- the headline.

Runs the *actual* numerical model (Role 2's solver, vendored in
`fcl_backend/`) against Role 1's theory to show they don't actually
disagree: they evaluate the with-FCL program at different renewable
buildout levels.

`carbon_vs_buildout` traces carbon (and the profit that keeps rising,
i.e. the unboundedness) as the renewable cap grows, and reports where
carbon crosses below the no-FCL benchmark. `decompose` splits the carbon
change at a given cap into the utilization effect (FCL draws power -> more
fossil, always raises carbon) and the capacity-substitution effect (FCL
-> more renewables -> less fossil), which is Role 1's condition (C).
"""
from __future__ import annotations

from .thresholds import Params, C_R_dagger, with_fcl_is_bounded
from .fcl_backend.model import Params as BParams, carbon_emissions
from .fcl_backend.distributions import UniformResidual
from .fcl_backend import solver


def _to_backend(P: Params) -> BParams:
    return BParams(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM,
                   beta=P.beta, p=P.p, D_bar=P.D_bar)


def carbon_vs_buildout(P: Params, caps=None) -> dict:
    """Carbon and profit at the constrained with-FCL optimum for a series of
    renewable-capacity caps, vs the no-FCL benchmark. Uses Role 2's solver."""
    bp = _to_backend(P)
    dist = UniformResidual(P.D_bar)
    no = solver.solve_no_fcl(dist, bp)
    if caps is None:
        base = no.K_R
        caps = [base, 1.5 * base, 2 * base, 3 * base, 5 * base, 8 * base, 12 * base, 20 * base]

    rows = []
    crossover = None
    for cap in caps:
        r = solver.solve_with_fcl_given_KR(dist, bp, cap)
        delta = r.carbon - no.carbon
        if delta < 0 and crossover is None:
            crossover = cap
        rows.append({"K_R_cap": cap, "K_F": r.K_F, "K_M": r.K_M,
                     "carbon": r.carbon, "carbon_minus_nofcl": delta,
                     "profit": r.profit})
    return {
        "no_fcl": {"K_R": no.K_R, "K_F": no.K_F, "carbon": no.carbon, "profit": no.profit},
        "rows": rows,
        "carbon_crossover_cap": crossover,
        "with_fcl_bounded": with_fcl_is_bounded(P),
        "C_R_dagger": C_R_dagger(P),
    }


def decompose(P: Params, K_R: float) -> dict:
    """Split the carbon change at buildout K_R into utilization vs
    capacity-substitution effects.

      utilization  = carbon(with-FCL K_F,K_M) - carbon(no-FCL K_F,0) at the
                     SAME K_R  (pure effect of adding the FCL load)
      capacity     = carbon(no-FCL inner soln) at K_R - at no-FCL K_R
                     (pure effect of moving renewable capacity)
    Their sum is the total carbon change vs the no-FCL optimum.
    """
    bp = _to_backend(P)
    dist = UniformResidual(P.D_bar)
    no = solver.solve_no_fcl(dist, bp)

    # with-FCL inner optimum at this K_R
    rw = solver.solve_with_fcl_given_KR(dist, bp, K_R)
    # no-FCL inner optimum at this same K_R (K_M = 0): solve K_F only
    rn = solver.solve_with_fcl_given_KR(dist, bp, K_R, KM_max=1e-9)

    carbon_withfcl = rw.carbon
    carbon_nofcl_sameKR = rn.carbon
    utilization = carbon_withfcl - carbon_nofcl_sameKR
    capacity = carbon_nofcl_sameKR - no.carbon
    return {
        "K_R": K_R,
        "utilization_effect": utilization,   # >= 0 (raises carbon)
        "capacity_effect": capacity,         # <= 0 if more K_R than benchmark
        "total_vs_nofcl_opt": carbon_withfcl - no.carbon,
    }
