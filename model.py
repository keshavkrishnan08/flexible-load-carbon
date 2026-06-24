"""
Regime classification and the carbon crossover (updated Role 4).

Stitches the two regime axes the team needs into one map:

  * Boundedness axis (in C_R), from thresholds.py:
      C_R < C_R_circ            -> BOTH no-FCL and with-FCL unbounded
      C_R_circ <= C_R < C_R_dag -> no-FCL finite, with-FCL UNBOUNDED
                                   (this is the carbon-reduction regime)
      C_R >= C_R_dagger         -> BOTH finite
  * FCL-coverage axis (in C_M), ordered C_M^fc < C_bar_M < C_bar_M^b:
      C_M >= C_bar_M^b  -> no adoption (K_M = 0)
      C_M^fc < C_M < C_bar_M^b -> interior / small-FCL
      C_M <= C_M^fc     -> full coverage (fossil fully shadowed by FCL)

It also computes the **carbon crossover buildout** K_R_cross: the renewable
capacity at which with-FCL fossil output equals the no-FCL benchmark. Below
K_R_cross the FCL *utilization* effect dominates (carbon rises -- Role 2's
finding); above it the *capacity-substitution* effect dominates (carbon
falls -- Role 1's claim). K_R_cross is the quantitative bridge between the
two models.
"""
from __future__ import annotations



from .thresholds import (
    Params, C_R_circ, C_R_dagger, C_M_fc, C_M_bar, C_M_bar_b,
    with_fcl_is_bounded, no_fcl_is_bounded,
)


def boundedness_regime(P: Params) -> str:
    """Which boundedness regime in C_R the parameters sit in."""
    if not no_fcl_is_bounded(P):
        return "both_unbounded"
    if not with_fcl_is_bounded(P):
        return "withfcl_unbounded"   # carbon-reduction regime
    return "both_finite"


def coverage_regime(P: Params) -> str:
    """Which FCL-coverage regime in C_M the parameters sit in."""
    if P.CM >= C_M_bar_b(P):
        return "no_adoption"
    if P.CM <= C_M_fc(P):
        return "full_coverage"
    return "interior_small_fcl"


def carbon_crossover_KR(P: Params, K_R_hi_mult: float = 20.0,
                        iters: int = 44) -> float | None:
    """Smallest renewable buildout K_R at which the with-FCL fossil output
    drops to the no-FCL benchmark, computed through Role 2's constrained
    solver (which handles the K_F/K_M >= 0 corners correctly across the
    small-/large-FCL regimes -- a standalone large-FCL closed form is wrong
    at low buildout, where the inner optimum is a corner).

    Returns None if no-FCL is itself unbounded, or no crossover is found
    below K_R_hi_mult * D_bar.
    """
    from .fcl_backend.model import Params as BParams
    from .fcl_backend.distributions import UniformResidual
    from .fcl_backend import solver

    if not no_fcl_is_bounded(P):
        return None
    bp = BParams(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
    dist = UniformResidual(P.D_bar)
    base = solver.solve_no_fcl(dist, bp).carbon
    g = lambda KR: solver.solve_with_fcl_given_KR(dist, bp, KR).carbon - base

    lo = max(solver.solve_no_fcl(dist, bp).K_R, 1e-6)
    hi = K_R_hi_mult * P.D_bar
    if g(lo) <= 0:
        return lo
    if g(hi) > 0:
        return None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def classify(P: Params) -> dict:
    """Full regime summary for a parameter point."""
    return {
        "assumption1": P.assumption1_holds(),
        "C_R_circ": C_R_circ(P),
        "C_R_dagger": C_R_dagger(P),
        "boundedness_regime": boundedness_regime(P),
        "coverage_regime": coverage_regime(P),
        "C_M_fc": C_M_fc(P),
        "C_M_bar": C_M_bar(P),
        "C_M_bar_b": C_M_bar_b(P),
        "carbon_crossover_KR": carbon_crossover_KR(P),
    }
