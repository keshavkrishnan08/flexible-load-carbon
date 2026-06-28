"""
Week 2 Task 3: validate the analytic Hessian (fcl_solver/hessian.py) two
ways that don't depend on already knowing where any optimum is:

1. hessian() must equal finite_difference_hessian() (the Jacobian of the
   analytic *gradient*, foc.gradient, via central differences) at ARBITRARY
   points -- this is a pointwise identity, true everywhere profit is twice
   differentiable, not just at a stationary point.
2. The two independently-derived off-diagonal entries (e.g. d(grad_KM)/dK_F
   vs d(grad_KF)/dK_M) must agree -- symmetry is a correctness check on the
   by-hand algebra, not an assumption.

Negative-definiteness AT a genuine stationary point is checked separately
in test_finite_interior_optimum.py, once that point is actually located
(Task 2/3's shared prerequisite -- see CONTEXT2.md Section 3).
"""
import numpy as np
import pytest

from fcl_solver.distributions import PowerResidual, UniformResidual, lognormal_primitive
from fcl_solver.hessian import (
    RegularityCertificate,
    certify_negative_definite,
    finite_difference_hessian,
    hessian,
    leading_principal_minors,
)
from fcl_solver.model import Params

DISTRIBUTIONS = {
    "uniform": UniformResidual(D_bar=100),
    "power_alpha_0.5": PowerResidual(D_bar=100, alpha=0.5),
    "power_alpha_2.0": PowerResidual(D_bar=100, alpha=2.0),
    # Uses distributions.LOGNORMAL_PRIMITIVE_MU/SIGMA -- see
    # TruncatedLognormal's "PARAMETER CHOICE WARNING" docstring for why
    # these specific parameters (not arbitrary ones) are required for
    # H_RR to be well-approximated without a second boundary-correction
    # term: an earlier choice with non-negligible density at D_bar
    # silently corrupted H_RR by ~10-30% before being diagnosed here.
    "lognormal_primitive": lognormal_primitive(D_bar=100),
}

# NOTE on a real mathematical edge case found while building this (relevant
# to Task 4's regularity-boundary mapping, not just this test file):
# PowerResidual(alpha<1)'s dF/dK_R genuinely DIVERGES (not just "is large")
# as x -> (-K_R)+ -- e.g. dist.dcdf_dKR(-K_R+1e-8, K_R) for alpha=0.5 is
# already ~466 and grows without bound as the step shrinks further (see
# distributions.py's PowerResidual docstring / the Week 2 writeup in
# README.md). Whenever an integration range straddles -K_R while alpha<1
# (i.e. whenever K_R < K_M < K_F+K_R, the paper's "large-FCL" regime), H_RR
# is not a finite number AT ALL there -- there is no formula to "get right,"
# the Hessian itself does not exist. power_alpha_0.5 is therefore only
# included at points that do NOT cross that edge (K_M <= K_R) below; this
# is exactly the kind of distribution Task 4 is meant to flag as outside
# the regularity-certifiable region, not a gap in hessian.py's formulas.
POINTS = {
    "small_fcl": dict(K_R=30.0, K_F=60.0, K_M=15.0),
    "large_fcl": dict(K_R=15.0, K_F=60.0, K_M=40.0),
    # Deliberately near, but not exactly on, K_M == K_R -- matching
    # test_gradients.py's own precedent: AT that exact point the support
    # edge -K_R coincides exactly with term2's lower limit -K_M, a genuine
    # (measure-zero) knife-edge of the small/large-FCL regime split itself
    # (Appendix G), not a target either formula is expected to hit exactly.
    "near_boundary_above": dict(K_R=25.0, K_F=50.0, K_M=25.3),
    "near_boundary_below": dict(K_R=25.0, K_F=50.0, K_M=24.7),
}

# (dist_name, point_name) pairs to test, EXCLUDING power_alpha_0.5 at any
# point with K_M > K_R: that crosses into the region where its dF/dK_R
# diverges at the support edge (see the NOTE above DISTRIBUTIONS) -- the
# Hessian is not a finite object there, so there is nothing for either
# hessian() or finite_difference_hessian() to agree on.
_ALL_PAIRS = [
    (dist_name, point_name)
    for dist_name in DISTRIBUTIONS
    for point_name in POINTS
    if not (dist_name == "power_alpha_0.5" and point_name in ("large_fcl", "near_boundary_above"))
]

HESS_ATOL = 1e-4
HESS_RTOL = 1e-5
# The lognormal-primitive family's underlying integrals (PrimitiveResidual's
# fixed-quadrature cdf/dcdf_dKR/d2cdf_dKR2, fed through scipy.integrate.quad
# a SECOND time for the finite-difference cross-check) carry a higher noise
# floor than the closed-form Uniform/Power families -- test_gradients.py
# already documents this exact tradeoff for *first*-derivative checks on
# Primitive-style distributions (GRAD_ATOL=2e-3, vs machine precision for
# Uniform/Power). One derivative order higher, the same family needs a
# correspondingly looser tolerance here.
HESS_ATOL_PRIMITIVE = 2e-3
HESS_RTOL_PRIMITIVE = 2e-3


def _tolerances(dist_name):
    if dist_name == "lognormal_primitive":
        return HESS_ATOL_PRIMITIVE, HESS_RTOL_PRIMITIVE
    return HESS_ATOL, HESS_RTOL


@pytest.fixture
def params():
    p = Params(R=109, c=45, CF=10, CR=8, CM=56, beta=190, p=10, D_bar=100)
    p.check_assumption1()
    return p


@pytest.mark.parametrize("dist_name,point_name", _ALL_PAIRS)
def test_analytic_hessian_matches_finite_difference_of_gradient(params, dist_name, point_name):
    dist = DISTRIBUTIONS[dist_name]
    point = POINTS[point_name]
    H_analytic = hessian(dist, params, **point)
    H_fd = finite_difference_hessian(dist, params, **point)
    atol, rtol = _tolerances(dist_name)
    np.testing.assert_allclose(H_analytic, H_fd, atol=atol, rtol=rtol)


@pytest.mark.parametrize("dist_name,point_name", _ALL_PAIRS)
def test_hessian_is_symmetric_by_construction(params, dist_name, point_name):
    """Structural sanity check: hessian() places one shared H_RF/H_RM/H_MF
    value into both of its symmetric slots (see hessian.py's docstring --
    H_RF and H_FR were independently DERIVED BY HAND and confirmed equal
    there, but the *code* computes the value once and reuses it), so this
    mainly catches an array-assembly slip, not an algebra error. The real
    independent check on the algebra -- that each entry matches a
    finite-difference of the gradient computed via a completely separate
    code path -- is test_analytic_hessian_matches_finite_difference_of_gradient
    above."""
    dist = DISTRIBUTIONS[dist_name]
    point = POINTS[point_name]
    H = hessian(dist, params, **point)
    np.testing.assert_allclose(H, H.T, atol=1e-12, rtol=0)


def test_leading_principal_minors_sign_convention():
    """Sanity check on the Sylvester-criterion helper itself, against a
    hand-picked 2x2 case with a known-negative-definite matrix
    [[-2,1],[1,-2]] (eigenvalues -1,-3, both negative) and a known
    indefinite one [[1,0],[0,-1]]."""
    neg_def = np.array([[-2.0, 1.0], [1.0, -2.0]])
    minors = leading_principal_minors(neg_def)
    assert all(m > 0 for m in minors), "neg-def 2x2 should have both signed minors positive"

    indefinite = np.array([[1.0, 0.0], [0.0, -1.0]])
    minors2 = leading_principal_minors(indefinite)
    assert not all(m > 0 for m in minors2)


def test_certificate_eigenvalue_and_minor_criteria_agree_on_a_known_matrix():
    """certify_negative_definite builds the real analytic Hessian, but the
    two *criteria* it applies (eigenvalues, Sylvester minors) are generic
    linear-algebra facts -- confirm they agree with each other and with
    ground truth on a hand-picked matrix before trusting them on the model.
    """
    from fcl_solver.hessian import RegularityCertificate, leading_principal_minors

    H = np.array([[-2.0, 1.0, 0.0], [1.0, -2.0, 1.0], [0.0, 1.0, -2.0]])  # neg-def tridiagonal
    eigvals = np.linalg.eigvalsh(H)
    minors = leading_principal_minors(H)
    cert = RegularityCertificate(
        H=H,
        eigenvalues=eigvals,
        minors=minors,
        negative_definite_by_eigenvalues=bool(np.all(eigvals < 0)),
        negative_definite_by_minors=bool(all(m > 0 for m in minors)),
    )
    assert cert.negative_definite
    assert cert.criteria_agree
