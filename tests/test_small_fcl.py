"""Bullet 2: small-FCL widens adoption (eq 62) beyond the large-FCL C̄_M."""
import pytest
from role4 import small_fcl as sf
from role4.foc import C_M_bar


def test_eq62_widens_adoption(P):
    assert sf.C_M_bar_b_eq62(P) > C_M_bar(P)
    assert sf.adoption_widening(P) == pytest.approx(P.c * sf.surplus_prob_no_fcl(P))


def test_surplus_prob_in_unit_interval(P):
    q = sf.surplus_prob_no_fcl(P)
    assert 0.0 < q < 1.0


def test_small_fcl_marginal_value_decreasing_and_above_large_fcl(P):
    """eq 61's marginal value is decreasing in K_M (well-posed FOC) and exceeds
    the large-FCL FOC by the positive surplus term c*F(-K_M)."""
    K_R, K_F = 60.0, 40.0
    r1 = sf.km_foc_residual_small(P, K_R, K_F, 5.0)
    r2 = sf.km_foc_residual_small(P, K_R, K_F, 15.0)
    assert r1 > r2                      # marginal value falls as K_M rises
    # small-FCL marginal value (eq 61) > large-FCL marginal value (eq 12 form)
    # by exactly the surplus term c*F(-K_M) > 0
    def F(x): return min(max((x + K_R) / (P.D_bar + K_R), 0.0), 1.0)
    K_M = 10.0
    large_fcl_mv = (P.R - P.c) * F(K_F - K_M) - P.CM
    small_fcl_mv = sf.km_foc_residual_small(P, K_R, K_F, K_M)
    assert small_fcl_mv - large_fcl_mv == pytest.approx(P.c * F(-K_M))
    assert P.c * F(-K_M) > 0
