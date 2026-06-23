"""
Most fundamental check: the hand-derived analytic FOCs (foc.grad_KR/KF/KM)
must equal a pure finite-difference gradient of model.profit(), for *any*
distribution and in *both* the small-FCL (K_M<=K_R) and large-FCL
(K_M>K_R) regimes. Nothing else in this repo is trustworthy if this fails.
"""
import numpy as np
import pytest
from scipy import stats

from fcl_solver.distributions import PowerResidual, PrimitiveResidual, UniformResidual
from fcl_solver.foc import gradient
from fcl_solver.model import profit


def numerical_gradient(dist, params, K_R, K_F, K_M, h=1e-3):
    def d(var, plus, minus):
        kwargs_plus = dict(K_R=K_R, K_F=K_F, K_M=K_M)
        kwargs_minus = dict(K_R=K_R, K_F=K_F, K_M=K_M)
        kwargs_plus[var] = plus
        kwargs_minus[var] = minus
        return (profit(dist, params, **kwargs_plus) - profit(dist, params, **kwargs_minus)) / (2 * h)

    return (
        d("K_R", K_R + h, K_R - h),
        d("K_F", K_F + h, K_F - h),
        d("K_M", K_M + h, K_M - h),
    )


DISTRIBUTIONS = {
    "uniform": UniformResidual(D_bar=100),
    "power_alpha_0.5": PowerResidual(D_bar=100, alpha=0.5),
    "power_alpha_2.0": PowerResidual(D_bar=100, alpha=2.0),
    # D_dist is Beta-shaped (smooth density, vanishing at both endpoints)
    # rather than Uniform: Uniform's box-shaped CDF has hard kinks at 0 and
    # D_bar, and PrimitiveResidual's fixed 40-point quadrature over S turns
    # those into ~40 separate small kinks spread across x, which is genuinely
    # harder for adaptive quadrature to resolve to tight tolerance than the
    # mathematically-smooth quantity it's approximating (confirmed while
    # debugging: switching to Beta resolved IntegrationWarnings and brought
    # finite-difference checks down to a stable ~1e-5 noise floor).
    "primitive_D_beta_S_beta": PrimitiveResidual(
        D_bar=100,
        D_dist=stats.beta(2, 2, loc=0, scale=100),
        S_dist=stats.beta(2, 2),
    ),
}

POINTS = {
    "small_fcl_regime (K_M < K_R)": dict(K_R=30.0, K_F=60.0, K_M=15.0),
    "large_fcl_regime (K_M > K_R)": dict(K_R=15.0, K_F=60.0, K_M=40.0),
    # Deliberately near, but not exactly on, K_M == K_R: AT that exact point
    # F's *density* has a genuine kink for PowerResidual(alpha != 1) (the
    # extended CDF's slope jumps at the support boundary x=-K_R), so the
    # classical derivative isn't even well-approximated by a centered finite
    # difference there. Just off the knife edge still exercises the regime
    # transition without asking a finite-difference check to resolve a kink.
    "near_boundary (K_M slightly > K_R)": dict(K_R=25.0, K_F=60.0, K_M=25.3),
    "near_boundary (K_M slightly < K_R)": dict(K_R=25.0, K_F=60.0, K_M=24.7),
}

# Tolerance is set by the noise floor of adaptive quadrature under finite
# differences (scipy.integrate.quad's subdivision pattern is not perfectly
# continuous in the integration limits), confirmed during development by
# cross-checking against a brute-force trapezoid-rule integral, which agreed
# with the *analytic* gradient, not the noisier quad-based finite difference.
# This is still tight enough to catch real formula bugs, which earlier
# produced O(1)-O(100) discrepancies, not O(1e-3).
GRAD_ATOL = 2e-3
GRAD_RTOL = 1e-4


@pytest.mark.parametrize("dist_name", DISTRIBUTIONS.keys())
@pytest.mark.parametrize("point_name", POINTS.keys())
def test_analytic_gradient_matches_finite_difference(valid_params, dist_name, point_name):
    dist = DISTRIBUTIONS[dist_name]
    point = POINTS[point_name]
    analytic = np.array(gradient(dist, valid_params, **point))
    numeric = np.array(numerical_gradient(dist, valid_params, **point))
    np.testing.assert_allclose(analytic, numeric, atol=GRAD_ATOL, rtol=GRAD_RTOL)
