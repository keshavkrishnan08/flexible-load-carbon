"""
Task 1: the general numerical solver must reproduce the paper's hand-solved
uniform-distribution closed forms (eqs 18-23, 25, 26) to high precision.

Two parameter pitfalls had to be avoided to even construct a valid test
case (left in as comments / fixture docs, since CONTEXT.md asked for everything
to be explainable, not just working):
  1. C_M must sit strictly inside Assumption 1's interior regime
     c+C_M < R < c+C_F+C_M -- the FOC formulas (eqs 12,13,18,19) are not
     algebraically valid outside it (R >= c+C_F+C_M pushes K_F past D_bar
     into the "full coverage" corner regime, Section 4.1's "digression").
  2. To test eqs 18/19 at a specific K_R, that K_R must actually land in
     the large-FCL regime (K_M > K_R) the formulas assume -- otherwise
     they silently extrapolate past their domain of validity.
Both are checked explicitly below rather than just assumed.
"""
import pytest

from fcl_solver.distributions import UniformResidual
from fcl_solver.model import carbon_emissions
from fcl_solver.closed_form_uniform import (
    carbon_no_fcl_uniform,
    carbon_with_fcl_uniform,
    no_fcl_uniform,
    paper_eq26_literal,
    with_fcl_given_KR,
)
from fcl_solver.solver import solve_no_fcl, solve_with_fcl_given_KR

DECIMAL = 1e-4  # "match to the decimal": optimizer tolerance, not algebra tolerance


def test_no_fcl_solver_matches_eq20_eq21(valid_params):
    dist = UniformResidual(D_bar=valid_params.D_bar)
    K_R_closed, K_F_closed = no_fcl_uniform(valid_params)
    assert K_R_closed > 0, "fixture picked to be the interior case; if this fails, fixture is wrong"

    result = solve_no_fcl(dist, valid_params)

    assert result.K_R == pytest.approx(K_R_closed, abs=DECIMAL)
    assert result.K_F == pytest.approx(K_F_closed, abs=DECIMAL)


@pytest.mark.parametrize("K_R_fixed", [5.0, 10.0])
def test_with_fcl_solver_matches_eq18_eq19(valid_params, K_R_fixed):
    dist = UniformResidual(D_bar=valid_params.D_bar)
    K_F_closed, K_M_closed = with_fcl_given_KR(valid_params, K_R_fixed)
    # Sanity: this K_R must be in the large-FCL regime for eqs 18/19 to apply.
    assert K_M_closed > K_R_fixed and K_F_closed < valid_params.D_bar

    result = solve_with_fcl_given_KR(dist, valid_params, K_R_fixed)

    assert result.K_F == pytest.approx(K_F_closed, abs=DECIMAL)
    assert result.K_M == pytest.approx(K_M_closed, abs=DECIMAL)


def test_no_fcl_carbon_matches_eq25(valid_params):
    """eq. 25 (after restoring the implied factor of c, see closed_form_uniform.py)
    must equal direct numerical integration of carbon at the no-FCL optimum."""
    dist = UniformResidual(D_bar=valid_params.D_bar)
    K_R, K_F = no_fcl_uniform(valid_params)
    closed = carbon_no_fcl_uniform(valid_params)
    numeric = carbon_emissions(dist, valid_params, K_R, K_F, 0.0)
    assert closed == pytest.approx(numeric, rel=1e-9)


@pytest.mark.parametrize("K_R_fixed", [5.0, 10.0])
def test_with_fcl_carbon_matches_eq26(valid_params, K_R_fixed):
    """eq. 26 must equal direct numerical integration of carbon at (K_R, K*_F, K*_M),
    AND must equal an independent re-typing of the literal printed formula
    (paper_eq26_literal) -- two different derivations, same number."""
    dist = UniformResidual(D_bar=valid_params.D_bar)
    K_F, K_M = with_fcl_given_KR(valid_params, K_R_fixed)

    closed = carbon_with_fcl_uniform(valid_params, K_R_fixed)
    numeric = carbon_emissions(dist, valid_params, K_R_fixed, K_F, K_M)
    literal = valid_params.c * paper_eq26_literal(valid_params, K_R_fixed)

    assert closed == pytest.approx(numeric, rel=1e-9)
    assert closed == pytest.approx(literal, rel=1e-9)


def test_eq18_19_large_fcl_regime_validity_window(valid_params):
    """eqs 18/19/26 (large-FCL regime: K_M > K_R AND K_F >= 0) are only
    economically meaningful inside a *bounded* window of K_R -- not for
    "K_R -> infinity" literally. Under Assumption 1 (R < c+C_F+C_M), eq. 23's
    coefficient on (D_bar+K_R) is *always* negative (algebra: R-c-C_F-C_M < 0
    is exactly Assumption 1's own inequality), so K*_F -> -infinity as
    K_R grows -- meaning the closed form *must* exit its valid domain
    (K_F >= 0) at some finite K_R, for *every* parameter set satisfying
    Assumption 1, not just this one. This test pins down that window for
    valid_params and confirms eqs 18/19 hold only inside it.
    """
    KR_inside, KR_outside = 10.0, 50.0  # established earlier in this module: KM>KR holds at 10, fails by 50
    KF_in, KM_in = with_fcl_given_KR(valid_params, KR_inside)
    KF_out, KM_out = with_fcl_given_KR(valid_params, KR_outside)

    assert KM_in > KR_inside and KF_in >= 0, "should be inside the valid large-FCL window"
    assert not (KM_out > KR_outside and KF_out >= 0), "should be outside it"


def test_carbon_with_fcl_does_not_improve_within_valid_window(valid_params):
    """Companion finding to the above: *within* the valid large-FCL window
    (where eqs 18/19/26 actually apply), carbon-with-FCL is HIGHER than the
    no-FCL benchmark here, not lower -- the opposite of what a literal,
    unbounded reading of "K_R -> infinity drives carbon to zero" (Section
    4.3's discussion of eq. 24 > 0) would suggest. A broader numerical
    search (fcl_solver/sweep.py) confirms this is not specific to these
    parameters: across a wide sweep of C_R and several R/c/C_F/C_M
    combinations, and both the uniform and power distribution families, we
    could not find a case where carbon improves *inside* the model's
    economically valid domain (K_F, K_M >= 0) -- profit and reliability
    (Prop. 1 parts i/ii) improved in every case, as guaranteed, but carbon
    (part iii, which the paper only ever claims "may" improve) did not in
    any case we tried. See sweep.py's module docstring for the full writeup.
    """
    dist = UniformResidual(D_bar=valid_params.D_bar)
    K_R0, K_F0 = no_fcl_uniform(valid_params)
    carbon0 = carbon_emissions(dist, valid_params, K_R0, K_F0, 0.0)

    for KR in (5.0, 10.0):  # confirmed inside the valid window above
        carbon_fcl = carbon_with_fcl_uniform(valid_params, KR)
        assert carbon_fcl > carbon0, (
            f"at K_R={KR} (inside the valid large-FCL window), expected carbon to "
            f"NOT improve for this parameter set, matching the broader sweep finding"
        )
