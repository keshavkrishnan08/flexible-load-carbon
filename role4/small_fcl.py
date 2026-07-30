"""
Bullet 2: complete the small-FCL regime (Appendix G) and confirm the wider
adoption threshold eq (62).

In the small-FCL regime K_M < K_R, so -K_M lies *inside* the support and the
integration-by-parts simplification that produced eq (10) is unavailable; the
profit is the eq-(60) form. The K_M FOC gains an extra surplus-hour term
relative to the large-FCL FOC (eq 12):

  eq (61)  (R-c) F(K_F-K_M;K_R) + c F(-K_M;K_R) = C_M
  eq (63)  -(β+p-R) F(K_F;K_R) - (R-c) F(K_F-K_M;K_R) + (β+p-c) - C_F = 0

The extra c F(-K_M;K_R) is the marginal *pure-renewable-surplus* hour: in
states x <= -K_M no fossil runs, so the marginal FCL unit earns the full R
(not the R-c fossil-dispatch margin). Evaluating the first FCL unit's value
at the no-FCL optimum (which necessarily sits in the small-FCL regime, since
K_M -> 0 < K_R°) gives the WIDER adoption threshold

  eq (62)  C̄_M^b = (R-c)φ° + c F(0;K_R°) = C̄_M + c q°  >  C̄_M,

where q° = F(0;K_R°) is the probability of renewable surplus at the no-FCL
optimum. So allowing small-FCL programs widens adoption from C̄_M to C̄_M^b:
on (C̄_M, C̄_M^b) the large-FCL analysis says "no adoption" but a small-FCL
program is still strictly worth running. tests/test_small_fcl.py confirms
C̄_M^b > C̄_M and that the surplus term equals c q° both analytically and
against the solver.
"""
from __future__ import annotations

from .params import Params
from .foc import C_M_bar, phi_circ


def surplus_prob_no_fcl(P: Params) -> float:
    """q° = F(0;K_R°), the no-FCL probability of renewable surplus.
    Uniform benchmark: F(0;K_R°) = K_R°/(D̄+K_R°)."""
    import math
    denom = 2.0 * P.CR - P.CF**2 / (P.bp - P.c)
    if denom <= 0:
        return float("nan")  # no-FCL unbounded; q° not well-defined
    KR0 = max(P.D_bar * (math.sqrt(P.c / denom) - 1.0), 0.0)
    return KR0 / (P.D_bar + KR0)


def C_M_bar_b_eq62(P: Params) -> float:
    """Wider small-FCL adoption threshold, eq (62): C̄_M + c q°."""
    return C_M_bar(P) + P.c * surplus_prob_no_fcl(P)


def adoption_widening(P: Params) -> float:
    """How much the small-FCL regime widens adoption: C̄_M^b - C̄_M = c q° >= 0."""
    return C_M_bar_b_eq62(P) - C_M_bar(P)


def km_foc_residual_small(P: Params, K_R: float, K_F: float, K_M: float) -> float:
    """LHS - RHS of eq (61) using the uniform CDF; root => small-FCL K_M FOC met.
    F(x;K_R) = (x+K_R)/(D̄+K_R) clipped to [0,1]."""
    def F(x):
        return min(max((x + K_R) / (P.D_bar + K_R), 0.0), 1.0)
    return (P.R - P.c) * F(K_F - K_M) + P.c * F(-K_M) - P.CM
