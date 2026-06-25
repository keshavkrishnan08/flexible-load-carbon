"""
Bullet 3: reconcile the regime boundaries into one consistent statement.

FCL-coverage axis (in C_M), strictly ordered (verified):

  full coverage         C_M <= C_M^fc = R - c - C_F     (p25 digression:
                        R >= c+C_F+C_M; build >= D̄ fossil, blackout = 0)
  interior / large-FCL  C_M^fc < C_M < C̄_M = (R-c)φ°    (Section 4.1)
  small-FCL adoption    C̄_M <= C_M < C̄_M^b = C̄_M + c q°  (Appendix G, eq 62:
                        large-FCL says "no adoption" but small-FCL still pays)
  no adoption           C_M >= C̄_M^b

Boundedness axis (in C_R), the hardening that reconciles Role 1 vs Role 2:

  C_R° = C_F^2/(2(β+p-c))   below it even no-FCL wants infinite K_R
  C_R† = ½[c + (R-C_M-c)^2/(R-c) + (R-c-C_F-C_M)^2/(β+p-R)]
                            with-FCL has a finite optimum iff C_R >= C_R†;
                            on C_R° <= C_R < C_R† the with-FCL program is
                            unbounded (Role 2's "infinite capacity"), which is
                            also the carbon-reduction regime (Role 1).

`unified_statement(P)` returns the single consistent classification across
both axes; `carbon_crossover_KR` is the buildout at which carbon crosses
below the no-FCL benchmark (the quantitative Role 1 <-> Role 2 bridge).
"""
from __future__ import annotations

from .params import Params
from .foc import C_M_bar, phi_circ
from .small_fcl import C_M_bar_b_eq62, surplus_prob_no_fcl


# --- C_R boundedness thresholds ---------------------------------------------

def C_R_circ(P: Params) -> float:
    """No-FCL boundedness threshold C_F^2/(2(β+p-c))."""
    return P.CF**2 / (2.0 * (P.bp - P.c))


def C_R_dagger(P: Params) -> float:
    """With-FCL boundedness / eq-24 knife-edge threshold."""
    return 0.5 * (P.c
                  + (P.R - P.CM - P.c)**2 / (P.R - P.c)
                  + (P.R - P.c - P.CF - P.CM)**2 / (P.bp - P.R))


def with_fcl_bounded(P: Params) -> bool:
    return P.CR >= C_R_dagger(P)


def no_fcl_bounded(P: Params) -> bool:
    return P.CR > C_R_circ(P)


# --- C_M coverage thresholds (bullet 3 ordering) ----------------------------

def C_M_fc(P: Params) -> float:
    """Full-coverage threshold C_M^fc = R - c - C_F (p25 digression)."""
    return P.R - P.c - P.CF


def coverage_regime(P: Params) -> str:
    if P.CM <= C_M_fc(P):
        return "full_coverage"
    if P.CM < C_M_bar(P):
        return "interior_large_fcl"
    if P.CM < C_M_bar_b_eq62(P):
        return "small_fcl_adoption"
    return "no_adoption"


def boundedness_regime(P: Params) -> str:
    if not no_fcl_bounded(P):
        return "both_unbounded"
    if not with_fcl_bounded(P):
        return "withfcl_unbounded"
    return "both_finite"


def thresholds_ordered(P: Params) -> bool:
    """The bullet-3 consistency check: C_M^fc < C̄_M < C̄_M^b."""
    return C_M_fc(P) < C_M_bar(P) < C_M_bar_b_eq62(P)


def carbon_crossover_KR(P: Params, K_R_hi_mult: float = 20.0, iters: int = 44):
    """Smallest renewable buildout at which with-FCL fossil output drops to the
    no-FCL benchmark, via Role 2's constrained solver. None if no-FCL is
    unbounded or no crossover below K_R_hi_mult*D_bar."""
    from .fcl_backend.model import Params as BP
    from .fcl_backend.distributions import UniformResidual
    from .fcl_backend import solver

    if not no_fcl_bounded(P):
        return None
    bp = BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
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
        lo, hi = (mid, hi) if g(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def unified_statement(P: Params) -> dict:
    """One consistent classification across both axes (bullet 3)."""
    return {
        "assumption1": P.assumption1_holds(),
        "coverage_regime": coverage_regime(P),
        "C_M_fc": C_M_fc(P),
        "C_M_bar": C_M_bar(P),
        "C_M_bar_b": C_M_bar_b_eq62(P),
        "coverage_ordered": thresholds_ordered(P),
        "boundedness_regime": boundedness_regime(P),
        "C_R_circ": C_R_circ(P),
        "C_R_dagger": C_R_dagger(P),
        "carbon_crossover_KR": carbon_crossover_KR(P),
    }
