"""
The "knife-edge" structural claim behind eq. 24: under the uniform
distribution, once K_F and K_M are re-optimized (eqs 18/19) at every K_R,
the *marginal value* of K_R is a constant, independent of K_R itself. That
constant being positive/zero/negative is what makes K*_R a corner solution
(infinity / indifferent / zero) rather than an interior optimum.

FINDING documented in closed_form_uniform.eq24_constant: the literal
eq. 24 expression equals exactly 2x the constant value of foc.grad_KR
along this curve, not 1x -- a benign overall-scale difference (it doesn't
flip the sign, which is the only thing the paper uses eq. 24 for). Both
facts -- the constancy, and the factor of 2 -- are checked here.
"""
import pytest

from fcl_solver.distributions import UniformResidual
from fcl_solver.foc import grad_KR
from fcl_solver.closed_form_uniform import eq24_constant, with_fcl_given_KR
from fcl_solver.model import Params
from fcl_solver.solver import solve_with_fcl


def test_marginal_value_of_KR_is_constant_along_eq18_19_curve(valid_params):
    dist = UniformResidual(D_bar=valid_params.D_bar)
    KR_values = [5.0, 10.0]  # both confirmed in the large-FCL regime for valid_params
    grads = []
    for KR in KR_values:
        K_F, K_M = with_fcl_given_KR(valid_params, KR)
        assert K_M > KR and K_F < valid_params.D_bar  # regime check
        grads.append(grad_KR(dist, valid_params, KR, K_F, K_M))

    assert grads[0] == pytest.approx(grads[1], rel=1e-9), "marginal value of K_R should not depend on K_R"


def test_eq24_equals_twice_the_marginal_value(valid_params, valid_params_small):
    dist = UniformResidual(D_bar=valid_params.D_bar)

    for params, KR_probe in [(valid_params, 5.0), (valid_params_small, 1.0)]:
        K_F, K_M = with_fcl_given_KR(params, KR_probe)
        marginal_value = grad_KR(UniformResidual(D_bar=params.D_bar), params, KR_probe, K_F, K_M)
        assert eq24_constant(params) == pytest.approx(2.0 * marginal_value, rel=1e-9)


def test_positive_eq24_drives_joint_solver_KR_to_upper_bound(valid_params):
    """valid_params has eq24_constant > 0 (renewable investment unboundedly
    attractive at the margin) -- the full joint solver should reflect this
    by pushing K_R to whatever upper bound it's given, not settling
    interior. This is the corner-solution behavior CONTEXT.md flagged as
    "correct, not a bug" -- this test pins that down precisely."""
    assert eq24_constant(valid_params) > 0

    dist = UniformResidual(D_bar=valid_params.D_bar)
    small_bound = 5.0 * valid_params.D_bar
    large_bound = 15.0 * valid_params.D_bar

    # K_M's natural scale tracks K_R in the large-FCL regime (eq. 19: K_M
    # grows roughly linearly with K_R), so K_M's own bound must be raised
    # along with K_R's -- otherwise K_M hits *its* default bound first and
    # distorts the joint optimum into a different (still-a-corner, but not
    # the K_R one) solution. Caught by this test originally failing.
    res_small = solve_with_fcl(dist, valid_params, KR_max=small_bound, KM_max=small_bound)
    res_large = solve_with_fcl(dist, valid_params, KR_max=large_bound, KM_max=large_bound)

    assert res_small.at_upper_bound["K_R"]
    assert res_large.at_upper_bound["K_R"]
    assert res_large.K_R > res_small.K_R, "raising the bound should keep pushing K*_R further out"


def test_negative_eq24_drives_joint_solver_KR_to_zero():
    """Construct a parameter set with C_R large enough to flip eq. 24
    negative, and confirm the joint solver's K*_R collapses to (near) 0."""
    params = Params(R=109, c=45, CF=10, CR=500, CM=56, beta=190, p=10, D_bar=100)
    params.check_assumption1()
    assert eq24_constant(params) < 0

    dist = UniformResidual(D_bar=params.D_bar)
    res = solve_with_fcl(dist, params)
    assert res.K_R == pytest.approx(0.0, abs=1e-3)
