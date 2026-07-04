"""
Week 2 Task 2 (the keystone task): locate GENUINE finite interior optima
under the lognormal-primitive family, and at each one check (a) Role 1's
endpoint shift-ratio condition and (b) whether carbon actually falls
relative to the no-FCL benchmark.

Why this module exists (see README.md / CONTEXT2.md Section 3 for the full
story): Week 1 found that under the Uniform/Power families, the with-FCL
profit problem has NO finite global maximum at all (it runs away as
K_R, K_M -> infinity together), so "does carbon fall at K*_R" was never a
well-posed question there. CONTEXT2.md's Week 2 reframe says: find a
distribution + parameter regime where a finite, REGULAR (negative-definite
Hessian) interior optimum genuinely exists, and check carbon there.

WHAT WAS FOUND: a finite interior optimum certified by both the
analytic-Hessian regularity check (hessian.certify_negative_definite) and
the bound-independence check below DOES exist for the lognormal-primitive
family -- but it required searching for the right C_R (Week 1's own
uniform-family precedent: C_R has to be tuned away from the runs-away
regime, same as test_knife_edge.py's C_R=500 example for Uniform). Simply
swapping the distribution family was NOT, on its own, enough to produce an
interior optimum under the original valid_params -- C_R=8 still ran away
under lognormal-primitive too (see find_finite_interior_optimum's
docstring and tests/test_finite_interior_optimum.py for the concrete
before/after).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .distributions import ResidualDemand, g_ratio
from .hessian import RegularityCertificate, certify_negative_definite
from .model import Params, carbon_emissions
from .solver import SolveResult, solve_no_fcl, solve_with_fcl


@dataclass
class FiniteOptimumResult:
    """Outcome of trying to certify a genuine finite interior optimum."""

    found: bool
    reason: str  # human-readable explanation when found=False
    with_fcl: SolveResult | None = None
    no_fcl: SolveResult | None = None
    certificate: RegularityCertificate | None = None
    grad_norm: float | None = None
    shift_ratio_KF: float | None = None       # g(K_F*)
    shift_ratio_gap: float | None = None       # g(K_F*-K_M*)
    shift_ratio_condition_holds: bool | None = None  # g(K_F*-K_M*) >= g(K_F*)
    KR_increased: bool | None = None           # K_R* > K_R^o ?
    carbon_lower: bool | None = None
    carbon_change: float | None = None         # with_fcl.carbon - no_fcl.carbon

    def __repr__(self):
        if not self.found:
            return f"FiniteOptimumResult(found=False, reason={self.reason!r})"
        return (
            f"FiniteOptimumResult(found=True, K=({self.with_fcl.K_R:.2f},"
            f"{self.with_fcl.K_F:.2f},{self.with_fcl.K_M:.2f}), "
            f"neg_def={self.certificate.negative_definite}, "
            f"shift_ratio_condition={self.shift_ratio_condition_holds}, "
            f"K_R_increased={self.KR_increased}, carbon_lower={self.carbon_lower}, "
            f"d_carbon={self.carbon_change:+.4f})"
        )


def find_finite_interior_optimum(
    dist: ResidualDemand,
    params: Params,
    bound_scales=(4.0, 15.0),
    grad_tol: float = 1e-3,
    boundary_tol: float = 1e-4,
) -> FiniteOptimumResult:
    """Try to certify a genuine finite interior optimum of the WITH-FCL
    profit problem, for the given (dist, params).

    Three independent checks all have to pass -- any one of them failing
    means the "optimum" found is a corner, a runaway direction, or not a
    true stationary point, exactly the situation Week 1 hit under
    Uniform/Power:

      1. BOUND-INDEPENDENCE: re-solve at >=2 increasingly generous bound
         scales (multiples of D_bar); if the solution keeps growing with
         the bound, there is no finite optimum at all (Week 1's finding
         for Uniform/Power -- the joint problem runs away).
      2. GRADIENT: the analytic FOC gradient (foc.gradient) must vanish at
         the (larger-bound) solution -- a genuine first-order condition,
         not just "the optimizer stopped improving."
      3. HESSIAN: hessian.certify_negative_definite must report
         negative-definite -- a genuine local MAXIMUM, not a saddle.

    Returns a FiniteOptimumResult with found=False and a `reason` string
    if any check fails, so callers (the sweep below) can report exactly
    why a given (distribution, parameter) combination did not yield a
    usable point, rather than silently skipping it.
    """
    D = params.D_bar
    results = []
    for scale in bound_scales:
        res = solve_with_fcl(dist, params, KR_max=scale * D, KF_max=0.5 * scale * D, KM_max=0.5 * scale * D)
        results.append((scale, res))

    last_scale, last_res = results[-1]
    prev_scale, prev_res = results[-2]

    # Check 1: bound-independence. Growth tolerance is relative to D_bar so
    # it scales sensibly across different D_bar choices.
    grew = (
        last_res.K_R > prev_res.K_R + boundary_tol * D
        or last_res.K_M > prev_res.K_M + boundary_tol * D
        or last_res.K_F > prev_res.K_F + boundary_tol * D
    )
    at_bound = any(last_res.at_upper_bound.values())
    if grew or at_bound:
        return FiniteOptimumResult(
            found=False,
            reason=(
                f"no finite optimum: solution grew from {prev_res.K_R:.1f}/{prev_res.K_F:.1f}/"
                f"{prev_res.K_M:.1f} (scale={prev_scale}) to {last_res.K_R:.1f}/{last_res.K_F:.1f}/"
                f"{last_res.K_M:.1f} (scale={last_scale}); at_upper_bound={last_res.at_upper_bound}"
            ),
        )

    if last_res.K_R <= boundary_tol * D or last_res.K_F <= boundary_tol * D:
        return FiniteOptimumResult(found=False, reason="collapsed to a zero-capacity corner, not interior")

    # Check 2: gradient.
    from .foc import gradient

    grad = np.array(gradient(dist, params, last_res.K_R, last_res.K_F, last_res.K_M))
    grad_norm = float(np.linalg.norm(grad))
    if grad_norm > grad_tol:
        return FiniteOptimumResult(found=False, reason=f"gradient did not vanish: ||grad||={grad_norm:.4f}")

    # Check 3: Hessian negative-definiteness.
    cert = certify_negative_definite(dist, params, last_res.K_R, last_res.K_F, last_res.K_M)
    if not cert.negative_definite:
        return FiniteOptimumResult(
            found=False,
            reason=f"Hessian not negative definite: eigenvalues={cert.eigenvalues.tolist()}",
            certificate=cert,
            grad_norm=grad_norm,
        )

    no_fcl = solve_no_fcl(dist, params, KR_max=last_scale * D, KF_max=0.5 * last_scale * D)

    K_F_star, K_M_star, K_R_star = last_res.K_F, last_res.K_M, last_res.K_R
    # Role 1's endpoint condition for the capacity channel K_R* > K_R^o:
    # g(a) >= g(K_F*), where a = K_F* - K_M* is the LOWER dispatch endpoint
    # and g(x) = F_KR(x)/f(x). Since g is non-increasing and a < K_F*, this
    # holds under regularity, consistent with K_R* > K_R^o.
    g_KF = g_ratio(dist, K_F_star, K_R_star)
    g_gap = g_ratio(dist, K_F_star - K_M_star, K_R_star)
    shift_condition = bool(g_gap >= g_KF) if np.isfinite(g_KF) and np.isfinite(g_gap) else None

    return FiniteOptimumResult(
        found=True,
        reason="ok",
        with_fcl=last_res,
        no_fcl=no_fcl,
        certificate=cert,
        grad_norm=grad_norm,
        shift_ratio_KF=float(g_KF),
        shift_ratio_gap=float(g_gap),
        shift_ratio_condition_holds=shift_condition,
        KR_increased=bool(K_R_star > no_fcl.K_R),
        carbon_lower=bool(last_res.carbon < no_fcl.carbon),
        carbon_change=float(last_res.carbon - no_fcl.carbon),
    )
