"""
First-order conditions (FOCs) for the joint capacity problem.

These are dPi/dK_M, dPi/dK_F, dPi/dK_R obtained by hand-differentiating the
*unified* profit integral (model.profit, = paper eq. 5) with respect to
each capacity, using Leibniz's rule on the integration limits. Doing the
differentiation directly on eq. 5 (rather than copying the paper's
large-FCL-only eqs 11/13/15) is what makes these formulas valid in *both*
regimes automatically -- see the docstring of each function for the
by-hand derivation that was checked against the paper's eqs 11-15 (large
K_M) and eqs 61/63-65 (small K_M, Appendix G): both are special cases of
the formulas below (the small/large split disappears because F is already
0 below -K_R, matching the paper's "extended CDF" convention).

grad_KM and grad_KF are evaluated in closed form (no quadrature needed,
since differentiating the integral w.r.t. its own limit just evaluates the
integrand at that limit). grad_KR needs one integral of dF/dK_R, since K_R
shifts the *shape* of F everywhere, not just an integration limit.
"""
from __future__ import annotations

from scipy import integrate

from .distributions import ResidualDemand, quad_breakpoint
from .model import Params


def grad_KM(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> float:
    """dPi/dK_M = (R-c) F(K_F-K_M; K_R) + c F(-K_M; K_R) - C_M.

    Derivation: differentiating R*int_{K_F-K_M}^{K_F} F dx w.r.t. K_M (only
    the lower limit K_F-K_M moves, derivative -1) gives +R*F(K_F-K_M).
    Differentiating -c*int_{-K_M}^{K_F-K_M}(1-F) dx w.r.t. K_M (both limits
    move with derivative -1) gives -c*F(K_F-K_M) + c*F(-K_M). Summing and
    subtracting the capital cost C_M gives the expression above.

    At K_M >= K_R, F(-K_M;K_R) = 0 by the extended-CDF convention, and this
    collapses to the paper's large-FCL eq. 12: (R-c)F(K_F-K_M;K_R) = C_M.
    At K_M < K_R it matches Appendix G eq. 61 exactly.
    """
    return (
        (params.R - params.c) * dist.cdf(K_F - K_M, K_R)
        + params.c * dist.cdf(-K_M, K_R)
        - params.CM
    )


def grad_KF(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> float:
    """dPi/dK_F = R[F(K_F)-F(K_F-K_M)] - c[1-F(K_F-K_M)] + (beta+p)[1-F(K_F)] - C_F.

    Derivation: the R-integral has K_F in *both* limits (net effect
    +R*F(K_F) - R*F(K_F-K_M)); the fossil integral's upper limit K_F-K_M
    moves with derivative +1 (gives -c*(1-F(K_F-K_M))); the blackout
    integral's lower limit K_F moves with derivative +1, with an overall
    minus sign in front of that term in profit, giving +(beta+p)(1-F(K_F)).

    Collapses to the paper's large-FCL eq. 13 when F(-K_M;K_R)=0 (solve
    for F(K_F) using grad_KM=0 to eliminate F(K_F-K_M)); matches Appendix G
    eq. 63/64 otherwise.
    """
    F_KF = dist.cdf(K_F, K_R)
    F_gap = dist.cdf(K_F - K_M, K_R)
    return (
        params.R * (F_KF - F_gap)
        - params.c * (1.0 - F_gap)
        + (params.beta + params.p) * (1.0 - F_KF)
        - params.CF
    )


def grad_KR(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> float:
    """dPi/dK_R = R*int_{K_F-K_M}^{K_F} dF/dK_R dx + c*int_{-K_M}^{K_F-K_M} dF/dK_R dx
                  + (beta+p)*int_{K_F}^{D_bar} dF/dK_R dx - C_R.

    K_R does not appear in any integration limit, only inside F itself, so
    every term picks up a dF/dK_R integral (with the two "(1-F)" terms in
    profit flipping sign, d(1-F)/dK_R = -dF/dK_R, which cancels the minus
    sign already in front of those terms in profit -- hence all three
    integral terms enter with a *plus* sign here).

    Matches the paper's large-FCL eq. 15 when K_M >= K_R (since dF/dK_R is
    then 0 on (-K_M,-K_R), so the lower integration limit can equivalently
    be written as -K_R) and Appendix G eq. 65 when K_M < K_R.

    `points=quad_breakpoint(...)` on each call tells quad about dF/dK_R's
    (otherwise undeclared) kink at x=-K_R whenever a term's fixed range
    straddles it -- see quad_breakpoint's docstring in distributions.py
    for the silent quad mis-convergence this avoids (a Week 2 finding;
    the bias is too small to matter for any Week 1 VALUE check, but
    corrupts the Week 2 analytic-Hessian finite-difference cross-check).
    """
    # limit raised to 1000 (Week 2): see model.py's _QUAD_KWARGS comment --
    # the lognormal-primitive family's wide-range integrals were hitting
    # the 200-subdivision cap before reaching epsabs/epsrel.
    quad_kwargs = dict(limit=1000, epsabs=1e-9, epsrel=1e-9)
    a1, b1 = K_F - K_M, K_F
    a2, b2 = -K_M, K_F - K_M
    a3, b3 = K_F, params.D_bar
    term1, _ = integrate.quad(lambda x: dist.dcdf_dKR(x, K_R), a1, b1, points=quad_breakpoint(a1, b1, K_R), **quad_kwargs)
    term2, _ = integrate.quad(lambda x: dist.dcdf_dKR(x, K_R), a2, b2, points=quad_breakpoint(a2, b2, K_R), **quad_kwargs)
    term3, _ = integrate.quad(lambda x: dist.dcdf_dKR(x, K_R), a3, b3, points=quad_breakpoint(a3, b3, K_R), **quad_kwargs)
    return params.R * term1 + params.c * term2 + (params.beta + params.p) * term3 - params.CR


def gradient(dist: ResidualDemand, params: Params, K_R, K_F, K_M):
    """(dPi/dK_R, dPi/dK_F, dPi/dK_M) -- the full FOC vector."""
    return (
        grad_KR(dist, params, K_R, K_F, K_M),
        grad_KF(dist, params, K_R, K_F, K_M),
        grad_KM(dist, params, K_R, K_F, K_M),
    )
