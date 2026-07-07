"""
Week 4 Task 1 (keystone): the carbon classification functional.

This module implements the closed-form carbon classification functional Ψ
derived from the FCL paper's Proposition 4 (Appendix B.1, p. 82–84). Ψ is
the *if-and-only-if* characterization of the carbon sign:

    sign(carbon_no_FCL − carbon_with_FCL) = sign(Ψ)

i.e., carbon IMPROVES with the FCL program iff Ψ > 0.

─────────────────────────────────────────────────────────────────────────────
Derivation (large-FCL regime, K*_M > K*_R):

From Proposition 4's equations (44) and (45):

  E[fossil_with_FCL] = K*_F − (C_M/(R-c)) · (K*_F − K*_M − μ*_low)   (44)
  E[fossil_no_FCL]   = K°_F·(1−φ°) + (φ°−q°)·μ°_mid                  (45)

where:
  φ° = F(K°_F ; K°_R)  = reliability at the no-FCL benchmark
  q° = F(0   ; K°_R)  = P(surplus | no-FCL benchmark)
  μ*_low = ∫_{K*_F-K*_M}^{K*_F-K*_R}  x·f(x;K*_R)dx / (C_M/(R-c))
          (conditional mean of x in the FCL *full-dispatch zone*)
  μ°_mid = ∫_0^{K°_F}                  x·f(x;K°_R)dx / (φ°−q°)
          (conditional mean of x in the no-FCL *fossil zone*)

Carbon improves (with_FCL < no_FCL) iff E[fossil_with_FCL] < E[fossil_no_FCL]:

  K*_F − (C_M/(R-c))·(K*_F−K*_M−μ*_low)  <  K°_F·(1−φ°) + (φ°−q°)·μ°_mid

Rearranging gives the classification functional:

  Ψ = (C_M/(R-c))·(K*_F−K*_M−μ*_low)  −  [K*_F − K°_F·(1−φ°) − (φ°−q°)·μ°_mid]

  sign(carbon_change) = −sign(Ψ)   (Ψ > 0 ↔ carbon improves)

─────────────────────────────────────────────────────────────────────────────
Minimal decisive statistic (Role 1's Task 1 companion):

The only quantity that is non-trivially determined by the distribution (beyond
the scalar parameters R, c, C_F, C_M, β, p that are already in params) is the
conditional mean μ*_low in the FCL full-dispatch zone. Everything else is
pinned by the FOC-determined cutoffs (K*, K°) and the two scalar reliabilities
(φ°, q°). The hypothesis that μ*_low is the *minimal decisive statistic* for
the carbon sign (no coarser functional of F suffices) is what makes Ψ sharp
rather than merely sufficient. We test this empirically: sweeping F and checking
that sign(Ψ) = sign(carbon_change) in every cell.

─────────────────────────────────────────────────────────────────────────────
Regime note:

Proposition 4 is stated for the large-FCL regime (K*_M > K*_R). In the
small-FCL regime (K*_M ≤ K*_R, Appendix G), the conditional mean μ*_low must
be replaced by a small-FCL analogue (Appendix G eq. G.2). FunctionalResult
reports which regime was observed; the sweep records this per cell. For cells
in the small-FCL regime the functional is still evaluated, but a regime flag
is set to alert downstream analysis.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import integrate

from .distributions import ResidualDemand
from .model import Params, carbon_emissions
from .solver import SolveResult, solve_no_fcl, solve_with_fcl

_QUAD_KWARGS = dict(limit=1000, epsabs=1e-9, epsrel=1e-9)


@dataclass
class FunctionalResult:
    """All components of the classification functional Ψ."""

    # ── Optimal capacities ──────────────────────────────────────────────
    K_R_star: float   # with-FCL
    K_F_star: float
    K_M_star: float
    K_R_circ: float   # no-FCL
    K_F_circ: float

    # ── Scalar reliabilities ────────────────────────────────────────────
    phi_circ: float   # F(K°_F; K°_R) = no-FCL reliability
    q_circ: float     # F(0; K°_R) = surplus probability at no-FCL benchmark

    # ── Conditional means (the distributional part) ─────────────────────
    mu_star_low: float   # conditional mean of x in FCL full-dispatch zone
    mu_circ_mid: float   # conditional mean of x in no-FCL fossil zone

    # ── Functional value and sign ───────────────────────────────────────
    psi: float          # Ψ — carbon falls iff Ψ > 0
    carbon_no_fcl: float
    carbon_with_fcl: float
    carbon_delta: float          # carbon_with_fcl - carbon_no_fcl (neg = improvement)
    sign_match: bool             # sign(Ψ) == sign(carbon_no_fcl - carbon_with_fcl)?
    large_fcl_regime: bool       # K*_M > K*_R?

    @property
    def carbon_improves(self) -> bool:
        return self.carbon_delta < 0

    def __repr__(self):
        regime = "large-FCL" if self.large_fcl_regime else "small-FCL"
        return (
            f"FunctionalResult(Ψ={self.psi:+.4f}, "
            f"Δcarbon={self.carbon_delta:+.4f}, "
            f"sign_match={self.sign_match}, "
            f"regime={regime})"
        )


def _conditional_mean_integral(dist: ResidualDemand, K_R: float,
                                lo: float, hi: float) -> float:
    """∫_lo^hi x · f(x; K_R) dx  (unnormalized first moment over [lo, hi]).

    f(x; K_R) = dist.pdf(x, K_R).  The quad_breakpoint guard for the
    density kink at x=-K_R is added whenever lo < -K_R < hi.
    """
    if lo >= hi:
        return 0.0
    from .distributions import quad_breakpoint
    pts = quad_breakpoint(lo, hi, K_R)
    val, _ = integrate.quad(
        lambda x: x * dist.pdf(x, K_R),
        lo, hi,
        points=pts,
        **_QUAD_KWARGS,
    )
    return val


def compute_functional(
    dist: ResidualDemand,
    params: Params,
    with_fcl: SolveResult | None = None,
    no_fcl: SolveResult | None = None,
    KR_max: float | None = None,
    KF_max: float | None = None,
    KM_max: float | None = None,
) -> FunctionalResult:
    """Compute Ψ(F, params) and verify sign(Ψ) = sign(carbon_change).

    If with_fcl / no_fcl are supplied they are used directly (avoids
    re-solving when called from a sweep that already has the solutions).

    Parameters
    ----------
    dist : the residual-demand distribution F
    params : model parameters (R, c, C_F, C_R, C_M, β, p, D_bar)
    with_fcl, no_fcl : pre-solved SolveResult objects (optional)
    KR_max, KF_max, KM_max : capacity bounds passed to the solver if
        with_fcl/no_fcl are not supplied.
    """
    D = params.D_bar
    KR_max = KR_max or 30.0 * D
    KF_max = KF_max or 5.0 * D
    KM_max = KM_max or 5.0 * D

    if no_fcl is None:
        no_fcl = solve_no_fcl(dist, params, KR_max=KR_max, KF_max=KF_max)
    if with_fcl is None:
        with_fcl = solve_with_fcl(dist, params,
                                   KR_max=KR_max, KF_max=KF_max, KM_max=KM_max)

    K_R_s, K_F_s, K_M_s = with_fcl.K_R, with_fcl.K_F, with_fcl.K_M
    K_R_o, K_F_o = no_fcl.K_R, no_fcl.K_F

    R, c, CM = params.R, params.c, params.CM
    margin = R - c  # > 0 by Assumption 1

    # ── Scalar reliabilities ────────────────────────────────────────────
    phi_o = float(dist.cdf(K_F_o, K_R_o))          # F(K°_F; K°_R)
    q_o   = float(dist.cdf(0.0,   K_R_o))           # F(0; K°_R)

    # ── Conditional means ───────────────────────────────────────────────
    # μ*_low: conditional mean of x in the FCL full-dispatch zone
    #         WITHIN the support, i.e. [-K*_R, K*_F-K*_M].
    #
    # Derivation (Appendix B.1, Step 3 "Derivation of expected fossil output"):
    # fossil output in state x = x + K*_M for x ∈ [-K*_R, K*_F-K*_M] (full dispatch),
    #                           = K*_F for x > K*_F-K*_M (gap-filling / scarcity).
    # E[fossil_with_FCL] = ∫_{-K*_R}^{K*_F-K*_M} (x+K*_M) f dx + K*_F·(1-F(K*_F-K*_M))
    # integration by parts + FOC F(K*_F-K*_M)=C_M/(R-c) →
    # E[fossil_with_FCL] = K*_F − (C_M/(R-c))·(K*_F−K*_M−μ*_low)  [eq 44]
    # where  μ*_low ≡ ∫_{-K*_R}^{K*_F-K*_M} x f(x;K*_R)dx / (C_M/(R-c)).
    #
    # BUG NOTE (caught by test_prop4_fossil_with_fcl_matches_direct): an
    # earlier version used [K*_F-K*_M, K*_F-K*_R] — the gap-filling zone —
    # instead of the full-dispatch zone [-K*_R, K*_F-K*_M]. Those two zones
    # are DIFFERENT in general and swapping them produces a 50% error in the
    # fossil formula and a sign flip in Ψ. Derivation cross-checked against
    # the direct numerical fossil integral from model.expected_fossil_output.
    lo_star = -K_R_s           # lower edge of the support
    hi_star = K_F_s - K_M_s   # upper edge of full-dispatch zone

    large_fcl = K_M_s > K_R_s

    mass_star = CM / margin  # = C_M/(R-c), the CDF mass in the full-dispatch zone
    if mass_star > 1e-12:
        raw_star = _conditional_mean_integral(dist, K_R_s, lo_star, hi_star)
        mu_star_low = raw_star / mass_star
    else:
        mu_star_low = 0.0

    # μ°_mid: unconditional integral over no-FCL fossil zone [0, K°_F]
    mass_mid = phi_o - q_o  # CDF mass between 0 and K°_F
    if mass_mid > 1e-12:
        raw_mid = _conditional_mean_integral(dist, K_R_o, 0.0, K_F_o)
        mu_circ_mid = raw_mid / mass_mid
    else:
        mu_circ_mid = 0.0

    # ── Classification functional Ψ ─────────────────────────────────────
    # Ψ = (C_M/(R-c))·(K*_F−K*_M−μ*_low) − [K*_F − K°_F·(1−φ°) − (φ°−q°)·μ°_mid]
    lhs = mass_star * (K_F_s - K_M_s - mu_star_low)
    rhs = K_F_s - K_F_o * (1.0 - phi_o) - (phi_o - q_o) * mu_circ_mid
    psi = lhs - rhs

    # ── Carbon values ────────────────────────────────────────────────────
    c_no_fcl   = no_fcl.carbon
    c_with_fcl = with_fcl.carbon
    delta      = c_with_fcl - c_no_fcl  # negative = improvement

    # sign match: Ψ > 0 ↔ carbon_improves ↔ delta < 0
    tol = 1e-6 * max(1.0, abs(delta))
    sign_psi    = psi > 0
    sign_delta  = delta < -tol
    sign_match  = (sign_psi == sign_delta) or (abs(delta) < tol and abs(psi) < tol)

    return FunctionalResult(
        K_R_star=K_R_s, K_F_star=K_F_s, K_M_star=K_M_s,
        K_R_circ=K_R_o, K_F_circ=K_F_o,
        phi_circ=phi_o, q_circ=q_o,
        mu_star_low=mu_star_low, mu_circ_mid=mu_circ_mid,
        psi=psi,
        carbon_no_fcl=c_no_fcl,
        carbon_with_fcl=c_with_fcl,
        carbon_delta=delta,
        sign_match=sign_match,
        large_fcl_regime=large_fcl,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Decomposed expected-fossil formulas (from Prop 4 eqs 44 & 45)
# — used to cross-validate the functional against direct carbon measurements
# ─────────────────────────────────────────────────────────────────────────────

def prop4_fossil_with_fcl(result: FunctionalResult, params: Params) -> float:
    """E[fossil_with_FCL] via eq. (44): K*_F − (C_M/(R-c))·(K*_F−K*_M−μ*_low)."""
    margin = params.R - params.c
    mass   = params.CM / margin
    return result.K_F_star - mass * (result.K_F_star - result.K_M_star - result.mu_star_low)


def prop4_fossil_no_fcl(result: FunctionalResult) -> float:
    """E[fossil_no_FCL] via eq. (45): K°_F·(1−φ°) + (φ°−q°)·μ°_mid."""
    return (result.K_F_circ * (1.0 - result.phi_circ)
            + (result.phi_circ - result.q_circ) * result.mu_circ_mid)
