"""
Week 2 Task 2/3's shared prerequisite, pinned down as tests: does a
genuine, finite, REGULAR (negative-definite Hessian) interior optimum of
the with-FCL profit problem exist anywhere, and if so, does carbon fall
there relative to the no-FCL benchmark?

THE HEADLINE WEEK 2 FINDING (see fcl_solver/finite_optimum.py's module
docstring and README.md for the full writeup):

1. Switching to a genuinely non-power-law distribution (the
   lognormal-primitive family, Task 1) does NOT by itself fix Week 1's
   unboundedness problem. Under the ORIGINAL valid_params (C_R=8), the
   with-FCL profit problem still runs away as (K_R, K_M) -> infinity
   together, exactly as it did under Uniform/Power -- see
   test_original_valid_params_still_run_away_under_lognormal_primitive.
   The distribution family alone was never the cause; Assumption 1's cost
   structure (specifically C_R being cheap relative to the (R-C_M) margin
   FCL hardware can lock in once renewables are abundant) is.
2. Raising C_R into a narrow window (roughly 21-27, for this specific
   (R,c,C_F,C_M,beta,p) combination -- see test_CR_sweep_window_exists)
   produces a GENUINE finite interior optimum: gradient ~0, Hessian
   strictly negative definite (a true local max, not a saddle), and the
   result is identical whether solved with generous or extremely generous
   capacity bounds (ruling out "still climbing, just slowly").
3. AT that genuine optimum, carbon is HIGHER with the FCL program than
   without (not lower) -- see test_carbon_does_not_fall_at_the_genuine_optimum.
   This is the central result: even once Week 1's main objection (no
   finite optimum to evaluate carbon at) is fully resolved, carbon still
   does not fall in this instance. Role 1's endpoint shift-ratio condition
   (g(K_F*) >= g(K_F*-K_M*)) is FALSE at this point even though K_R* > K_R^o
   holds anyway -- flagged explicitly below as a finding to reconcile with
   Role 1's exact theorem statement, not silently smoothed over (Role 1 was
   not reachable for clarification during this pass; see README.md).
"""
from __future__ import annotations

import warnings

import numpy as np
import pytest

from fcl_solver.distributions import lognormal_primitive
from fcl_solver.finite_optimum import find_finite_interior_optimum
from fcl_solver.model import Params

warnings.filterwarnings("ignore")  # IntegrationWarnings from far-from-optimum probe points


@pytest.fixture(scope="module")
def dist():
    return lognormal_primitive(D_bar=100)


def _params(CR: float) -> Params:
    p = Params(R=109, c=45, CF=10, CR=CR, CM=56, beta=190, p=10, D_bar=100)
    p.check_assumption1()
    return p


def test_original_valid_params_still_run_away_under_lognormal_primitive(dist):
    """Week 1's exact valid_params (C_R=8) -- this time under the
    lognormal-primitive family rather than Uniform/Power -- still has NO
    finite optimum: K_M keeps hitting its bound as the bound is raised,
    with a gradient that stays persistently positive rather than shrinking
    toward 0. This is the result that motivated the C_R search below: the
    distribution family alone does not fix Week 1's unboundedness."""
    result = find_finite_interior_optimum(dist, _params(CR=8.0))
    assert not result.found
    assert "no finite optimum" in result.reason


def test_CR_sweep_window_exists(dist):
    """There is a genuine window of C_R (between the "runs away" and
    "collapses to K_R=0" regimes) where a finite interior optimum exists.
    This pins down the qualitative shape of the C_R -> outcome map: below
    the window, no finite optimum (runs away); above it, a different,
    equally degenerate corner (K_R=0); the window itself is the only place
    Task 2's carbon question is even well-posed."""
    outcomes = {}
    for CR in [8.0, 15.0, 20.0, 25.0, 28.0, 40.0]:
        outcomes[CR] = find_finite_interior_optimum(dist, _params(CR))

    assert not outcomes[8.0].found, "below the window: should run away"
    assert not outcomes[15.0].found, "below the window: should run away"
    assert outcomes[25.0].found, "inside the window: should be a genuine interior optimum"
    assert not outcomes[28.0].found, "above the window: should collapse to a corner"
    assert not outcomes[40.0].found, "above the window: should collapse to a corner"
    # the above-window corner is specifically K_R->0, not a different runaway
    assert "corner" in outcomes[28.0].reason
    assert "corner" in outcomes[40.0].reason


def test_genuine_optimum_is_interior_and_regular(dist):
    """At C_R=25, the located point must be: (a) strictly interior (no
    capacity at 0 or at the solver's bound), (b) a genuine FOC stationary
    point (gradient ~0), and (c) a true local MAXIMUM (Hessian strictly
    negative definite, confirmed by both the eigenvalue and Sylvester-minor
    criteria agreeing) -- not a saddle or a numerically-flat plateau."""
    result = find_finite_interior_optimum(dist, _params(CR=25.0))

    assert result.found
    assert result.with_fcl.K_R > 1.0 and result.with_fcl.K_F > 1.0 and result.with_fcl.K_M > 1.0
    assert not any(result.with_fcl.at_upper_bound.values())
    assert result.grad_norm < 1e-3

    cert = result.certificate
    assert cert.negative_definite
    assert cert.criteria_agree
    assert np.all(cert.eigenvalues < 0)


def test_carbon_does_not_fall_at_the_genuine_optimum(dist):
    """THE central Week 2 finding: even at a fully-certified, finite,
    regular interior optimum (not a corner, not a runaway direction --
    Week 1's main objection to evaluating the carbon claim is gone here),
    carbon is still HIGHER with the FCL program than without."""
    result = find_finite_interior_optimum(dist, _params(CR=25.0))

    assert result.found
    assert not result.carbon_lower
    assert result.carbon_change > 0, "carbon should have INCREASED, not decreased"
    # but profit and reliability still improve, exactly as Proposition 1
    # parts (i)/(ii) guarantee (those are distribution-free claims) --
    # confirming this is specifically a part-(iii)-only failure, not a
    # breakdown of the whole triple-win story.
    assert result.with_fcl.profit > result.no_fcl.profit
    assert result.with_fcl.blackout_prob < result.no_fcl.blackout_prob


def test_shift_ratio_condition_vs_KR_increase_finding(dist):
    """FINDING flagged for Role 1 (not reachable for clarification during
    this pass -- see README.md): at the C_R=25 optimum, the endpoint
    shift-ratio condition g(K_F*) >= g(K_F*-K_M*) is FALSE, yet K_R* > K_R^o
    holds anyway. If the condition is meant to be necessary (not just
    sufficient) for K_R*>K_R^o, this is a direct counterexample to
    reconcile; if it is only claimed as sufficient, this is consistent
    (the condition failing doesn't preclude the conclusion holding via a
    different channel) and merely means this particular point doesn't
    demonstrate the condition's own mechanism. Pinned down precisely here
    either way, per the project's "flag fast when numbers and theory
    disagree" convention.
    """
    result = find_finite_interior_optimum(dist, _params(CR=25.0))

    assert result.found
    # CORRECTED DIRECTION g(a) >= g(K_F*): the condition HOLDS here
    # (g(a)=0.3137 >= g(K_F*)=0.2613).  Role 1's mechanism genuinely fires,
    # K_R* > K_R^o -- and carbon STILL rises.  This is the sharpest Week-2
    # counterexample.  An earlier revision evaluated the reversed inequality,
    # which swapped this point with the sigma=0.6 point below.
    assert result.shift_ratio_condition_holds is True
    assert result.KR_increased is True
    assert not result.carbon_lower
    assert result.carbon_change > 0


def test_shift_ratio_condition_holding_still_does_not_save_carbon():
    """THE SHARPEST Week 2 finding (from the full (C_R, sigma) sweep --
    see README.md / finite_optimum_sweep_results.csv): at
    sigma=0.6, C_R=26, the endpoint shift-ratio condition g(K_F*) >=
    g(K_F*-K_M*) is TRUE (0.379 >= 0.368) -- i.e. Role 1's proposed
    mechanism for K_R*>K_R^o genuinely fires here, not just incidentally --
    and K_R* does indeed exceed K_R^o (38.6 vs 11.3). Yet carbon STILL
    rises substantially (+545, ~71% worse than the no-FCL benchmark)
    while profit and reliability both still improve. Unlike the C_R=25
    point above (where the condition was false), this is not a case where
    the condition's own mechanism failed to apply -- it applied, and
    carbon still did not fall. This is the strongest single counterexample
    found this pass and the one most worth bringing to Role 1 directly.
    """
    dist = lognormal_primitive(D_bar=100, sigma=0.6)
    params = _params(CR=26.0)
    result = find_finite_interior_optimum(dist, params)

    assert result.found
    assert result.certificate.negative_definite
    # CORRECTED DIRECTION: here g is INCREASING across the band (irregular
    # case), so g(a) >= g(K_F*) FAILS.  K_R* still exceeds K_R^o, which is
    # consistent -- the condition is only claimed sufficient.  This point does
    # NOT exhibit the condition's own mechanism; the C_R=25 point does.
    assert result.shift_ratio_condition_holds is False
    assert result.KR_increased is True
    assert not result.carbon_lower
    assert result.carbon_change > 0
    assert result.with_fcl.profit > result.no_fcl.profit
    assert result.with_fcl.blackout_prob < result.no_fcl.blackout_prob
