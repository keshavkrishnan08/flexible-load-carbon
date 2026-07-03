"""Bullet 1: the contract and carbon functional stitch across the small-/large-
FCL regime boundary (continuous, with a located, explained kink in the FOC)."""
import pytest
from role4 import regime_stitch as rs


def test_contract_is_regime_free(P):
    """d*(x)=min{(K_F-x)_+,K_M} is the same continuous 1-Lipschitz non-increasing
    schedule in both FCL regimes."""
    assert rs.contract_is_regime_free(P, K_F=70.0, K_R=40.0)


def test_carbon_functional_C1_across_boundary(P):
    """E[fossil](K_M) is continuous and C^1 across K_M=K_R (no discontinuity in
    the carbon functional at the regime change)."""
    r = rs.carbon_functional_stitches(P, K_R=40.0, K_F=70.0)
    assert r["continuous"] and r["C1"]
    assert r["value_jump"] < 1e-3
    assert r["deriv_jump"] < 1e-2


def test_marginal_value_continuous_at_boundary(P):
    """MV_S(K_R)=MV_L(K_R): the small-FCL surplus term c*F(-K_M) vanishes at the
    boundary since F(-K_R;K_R)=0."""
    r = rs.marginal_value_continuous_at_boundary(P, K_R=40.0, K_F=70.0)
    assert r["continuous"]
    assert r["surplus_term_at_boundary"] == pytest.approx(0.0, abs=1e-12)


def test_profit_is_C1_not_C2_kink_located(P):
    """Π is C^1 but not C^2 at K_M=K_R: ∂²Π/∂K_M² jumps by exactly c*f(-K_R)=
    c/(D̄+K_R) as the surplus term switches on."""
    r = rs.profit_kink_at_boundary(P, K_R=40.0, K_F=70.0)
    assert r["C2_fails"]                       # there is a kink
    assert r["matches"]                        # jump equals the closed form
    assert r["curvature_jump"] == pytest.approx(r["predicted_jump"], rel=5e-3)


def test_optimum_varies_continuously_through_crossover(P):
    """K_M*(C_M) passes from large- to small-FCL continuously through C_M^cross
    (the regime boundary K_M*=K_R°), so carbon does not jump at the regime
    change."""
    r = rs.optimum_varies_continuously(P)
    assert r["continuous"]
    assert r["crosses_KR0"]


def test_carbon_equals_c_times_fossil(P):
    """carbon = c·E[fossil], and both are finite/positive at a worked point."""
    K_R, K_F, K_M = 40.0, 70.0, 20.0
    fossil = rs.expected_fossil(P, K_R, K_F, K_M)
    assert fossil > 0
    assert rs.carbon(P, K_R, K_F, K_M) == pytest.approx(P.c * fossil)
