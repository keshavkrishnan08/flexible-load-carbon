"""
Theory-hardening checks: the boundedness thresholds and the identity that
ties them to Role 2's own eq.-24 constant.
"""
import math

import pytest

from regimes.thresholds import (
    Params, C_R_circ, C_R_dagger, profile_slope_KR,
    with_fcl_is_bounded, no_fcl_is_bounded, C_M_fc, C_M_bar, C_M_bar_b,
)
from regimes.fcl_backend.model import Params as BParams
from regimes.fcl_backend import closed_form_uniform as cf


@pytest.fixture
def P():
    # In the carbon-reduction window: C_R_circ=0.25 < C_R=0.5 < C_R_dagger=0.75
    p = Params(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.5, beta=1.0, p=2.0, D_bar=100.0)
    assert p.assumption1_holds()
    return p


def test_eq24_constant_equals_2_times_slope(P):
    """eq24_constant (Role 2's literal eq.24) == 2*(C_R_dagger - C_R).

    This is the bridge: it ties our boundedness threshold to the paper's
    own knife-edge expression, computed by an independent module (Role 2).
    """
    bp = BParams(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
    e24 = cf.eq24_constant(bp)
    assert e24 == pytest.approx(2.0 * profile_slope_KR(P), rel=1e-12)


def test_threshold_values(P):
    assert C_R_circ(P) == pytest.approx(0.25)
    assert C_R_dagger(P) == pytest.approx(0.75)
    assert C_R_circ(P) < C_R_dagger(P)


def test_boundedness_regime_logic(P):
    # C_R = 0.5 is in (C_R_circ, C_R_dagger): no-FCL finite, with-FCL unbounded
    assert no_fcl_is_bounded(P)
    assert not with_fcl_is_bounded(P)

    # raise C_R above C_R_dagger -> with-FCL becomes finite
    P_hi = Params(**{**P.__dict__, "CR": 1.0})
    assert with_fcl_is_bounded(P_hi)

    # drop C_R below C_R_circ -> even no-FCL unbounded
    P_lo = Params(**{**P.__dict__, "CR": 0.1})
    assert not no_fcl_is_bounded(P_lo)


def test_unbounded_iff_positive_slope(P):
    """Sign of the profile slope decides boundedness (knife-edge logic)."""
    assert profile_slope_KR(P) > 0      # C_R < C_R_dagger -> build forever
    P_hi = Params(**{**P.__dict__, "CR": 1.0})
    assert profile_slope_KR(P_hi) < 0   # C_R > C_R_dagger -> finite


def test_C_M_thresholds_strictly_ordered(P):
    """Role 1's regime ordering C_M^fc < C_bar_M < C_bar_M^b."""
    assert C_M_fc(P) < C_M_bar(P) < C_M_bar_b(P)
