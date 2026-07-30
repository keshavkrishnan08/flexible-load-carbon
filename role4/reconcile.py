"""
Theory-vs-numerics reconciliation (Keshav/Role 1 vs Dhruv/Role 2), run
against Role 2's actual solver. Used by bullets 1 and 3.

carbon_vs_buildout traces carbon and profit as renewable buildout grows, and
reports the crossover; decompose splits the carbon change at a buildout into
the (carbon-raising) utilization effect and the (carbon-lowering)
capacity-substitution effect (Step 3 of the Prop 1 proof).
"""
from __future__ import annotations

from .params import Params
from .regimes import C_R_dagger, with_fcl_bounded


def _backend(P: Params):
    from .fcl_backend.model import Params as BP
    from .fcl_backend.distributions import UniformResidual
    from .fcl_backend import solver
    bp = BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
    return bp, UniformResidual(P.D_bar), solver


def carbon_vs_buildout(P: Params, caps=None) -> dict:
    bp, dist, solver = _backend(P)
    no = solver.solve_no_fcl(dist, bp)
    if caps is None:
        b = no.K_R
        caps = [b, 1.5 * b, 2 * b, 3 * b, 5 * b, 8 * b, 12 * b, 20 * b]
    rows, crossover = [], None
    for cap in caps:
        r = solver.solve_with_fcl_given_KR(dist, bp, cap)
        d = r.carbon - no.carbon
        if d < 0 and crossover is None:
            crossover = cap
        rows.append({"K_R_cap": cap, "K_F": r.K_F, "K_M": r.K_M,
                     "carbon": r.carbon, "carbon_minus_nofcl": d, "profit": r.profit})
    return {"no_fcl": {"K_R": no.K_R, "K_F": no.K_F, "carbon": no.carbon, "profit": no.profit},
            "rows": rows, "carbon_crossover_cap": crossover,
            "with_fcl_bounded": with_fcl_bounded(P), "C_R_dagger": C_R_dagger(P)}


def decompose(P: Params, K_R: float) -> dict:
    bp, dist, solver = _backend(P)
    no = solver.solve_no_fcl(dist, bp)
    rw = solver.solve_with_fcl_given_KR(dist, bp, K_R)
    rn = solver.solve_with_fcl_given_KR(dist, bp, K_R, KM_max=1e-9)
    utilization = rw.carbon - rn.carbon
    capacity = rn.carbon - no.carbon
    return {"K_R": K_R, "utilization_effect": utilization,
            "capacity_effect": capacity, "total_vs_nofcl_opt": rw.carbon - no.carbon}
