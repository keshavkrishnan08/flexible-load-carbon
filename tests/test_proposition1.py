"""
Task 3: validate Proposition 1's mining-preference condition across several
distribution families, not just the uniform one the paper hand-solves.

Proposition 1 claims parts (i) profit-higher and (ii) blackout-lower hold
for *any* residual-demand distribution satisfying Assumption 1, whenever
C_M < C_bar_M. That is the central, distribution-free claim, and it is
confirmed below across four distribution families (uniform, two power
shapes, and the primitive D/S construction) -- it held in every case tried.

Part (iii) (carbon lower) is explicitly *not* claimed in general -- the
paper only shows it under extra conditions (uniform + low C_R, or
Corollary 2's density-monotonicity conditions). Trying to reproduce that
specific case turned into the most substantial finding of this validation
pass: searching broadly (C_R across three orders of magnitude, several
R/c/C_F/C_M combinations, uniform and power distributions -- see sweep.py),
we could not find a single parameter combination where carbon actually
improves *within the model's economically valid domain*. Profit and
reliability improved every time, exactly as guaranteed; carbon did not, in
any case we tried, despite Section 4.3's worked uniform example suggesting
it should once C_R is "low enough." See test_part_iii_carbon_did_not_improve_in_our_search
and sweep.py for the full writeup of why (it traces back to Assumption 1's
own R < c+C_F+C_M constraint).
"""
import pytest
from scipy import stats

from fcl_solver.distributions import PowerResidual, PrimitiveResidual, UniformResidual
from fcl_solver.foc import grad_KM
from fcl_solver.model import Params
from fcl_solver.proposition1 import check_triple_win
from fcl_solver.solver import solve_no_fcl

DIST_FAMILIES = {
    "uniform": UniformResidual(D_bar=100),
    "power_alpha_0.5_right_skew": PowerResidual(D_bar=100, alpha=0.5),
    "power_alpha_2.0_left_skew": PowerResidual(D_bar=100, alpha=2.0),
    "primitive_beta_beta": PrimitiveResidual(
        D_bar=100,
        D_dist=stats.beta(2, 2, loc=0, scale=100),
        S_dist=stats.beta(2, 2),
    ),
}


@pytest.mark.parametrize("dist_name", DIST_FAMILIES.keys())
def test_parts_i_and_ii_hold_below_threshold(valid_params, dist_name):
    """C_M < C_bar_M => profit strictly higher, blackout strictly lower --
    for every distribution family, not just uniform (Assumption 1 only)."""
    dist = DIST_FAMILIES[dist_name]
    result = check_triple_win(dist, valid_params)

    assert result.below_threshold, "fixture is supposed to be the C_M < C_bar_M case"
    assert result.profit_higher, f"part (i) failed for {dist_name}: {result}"
    assert result.blackout_lower, f"part (ii) failed for {dist_name}: {result}"


def test_no_local_adoption_incentive_above_threshold():
    """C_M > C_bar_M => the FIRST unit of FCL capacity is unprofitable when
    evaluated AT the no-FCL benchmark (K_R^o, K_F^o) -- i.e. dPi/dK_M < 0
    there. This is precisely what the paper's Appendix B.1 proof
    establishes (it evaluates the marginal profit of FCL "at the no-FCL
    optimum" and reads off the sign).

    SUBTLETY caught while building this test: the FIRST unit of FCL
    capacity, starting from K_M=0 with K_R^o > 0, is *always* in the
    small-FCL regime (K_M=0 <= K_R^o), so the relevant threshold is not the
    bare C_bar_M (eq. 27, a large-FCL-regime quantity) but the WIDER
    small-FCL threshold C_bar_M^b = C_bar_M + c*F(0;K_R^o) the paper itself
    derives in Appendix G (eq. 62, referenced directly in Prop. 1's own
    statement). Using bare C_bar_M with valid_params's C_R=8 originally gave
    a false failure (grad_KM > 0 even though C_M exceeded "C_bar_M"),
    because for that parameter set C_bar_M^b (~78.6) exceeds the
    Assumption-1 ceiling on C_M (R-c=64) entirely -- there is *no* valid C_M
    for which that benchmark's K_R^o=71.2 rejects even the first unit of
    FCL. Raising C_R to 20 (below) shrinks K_R^o to ~6.9, which shrinks
    C_bar_M^b to ~62.8 -- just under R-c=64 -- opening a narrow window
    (62.8, 64) to actually demonstrate "no local adoption incentive."

    NOTE: this local (first-unit, at-the-benchmark) result is also *not*
    the same as "the unrestricted global joint optimum has K*_M=0" --
    test_with_fcl_profit_is_globally_unbounded_under_uniform shows the
    with-FCL profit surface has no finite global maximum at all under the
    uniform family, for C_M both above and below threshold, so "K*_M=0
    globally" isn't a meaningful claim to test in the first place. What
    *is* well-defined and provably correct is this local one.

    Restricted to the uniform distribution: C_bar_M^b depends on the
    no-FCL benchmark's own F(0;K_R^o), which varies a lot across
    distribution families (checked: power_alpha_0.5 and the primitive
    construction both land C_bar_M^b *above* 63.5 for this same parameter
    set, since their K_R^o differs from uniform's) -- the conclusion isn't
    distribution-free the way parts (i)/(ii) are, so a single shared C_M
    can't demonstrate it across families at once.
    """
    # Higher C_R than valid_params (8) -> smaller K_R^o -> smaller
    # C_bar_M^b = C_bar_M + c*F(0;K_R^o), opening room below R-c=64 for a
    # C_M that exceeds the (regime-correct) adoption threshold.
    params = Params(R=109, c=45, CF=10, CR=20, CM=63.5, beta=190, p=10, D_bar=100)
    params.check_assumption1()

    dist = UniformResidual(D_bar=params.D_bar)
    no_fcl = solve_no_fcl(dist, params)
    phi_o = 1.0 - no_fcl.blackout_prob
    q_o = dist.cdf(0.0, no_fcl.K_R)  # probability of renewable surplus at the no-FCL benchmark
    C_bar_M = (params.R - params.c) * phi_o
    C_bar_M_wide = C_bar_M + params.c * q_o  # eq. 62, the regime-correct threshold for the first unit

    assert params.CM > C_bar_M_wide > C_bar_M, "params constructed to land C_M above the WIDE threshold"

    marginal_profit_of_first_unit = grad_KM(dist, params, no_fcl.K_R, no_fcl.K_F, K_M=0.0)
    assert marginal_profit_of_first_unit < 0


def test_with_fcl_profit_is_globally_unbounded_under_uniform(valid_params):
    """FINDING, pinned down precisely: under the uniform distribution, the
    with-FCL profit function has no finite global maximum -- scaling
    (K_R, K_F, K_M) up together keeps increasing profit without bound, for
    C_M values both above and below C_bar_M (checked: C_M=56 in
    test_knife_edge.py, C_M=62 here). This is specific to introducing FCL:
    the SAME scaling exercise on the no-FCL profit (K_M=0) strictly
    decreases profit, confirming the no-FCL benchmark's closed-form
    stationary point genuinely is its global max, and that the
    unboundedness is a property of the mining-revenue term, not a general
    artifact of this model or solver.

    Practical reading: the paper's "K*_R, K*_F, K*_M" (eqs 18/19/22/23) are
    correctly understood as the *FOC-stationary point* the algebra
    constructs, not a literal unconstrained global maximizer -- consistent
    with the paper's own awareness that K*_R can be a degenerate corner
    (eq. 24's "infinite/arbitrary/zero" trichotomy). What this test adds is
    that, once K_M is also free, the degeneracy is not confined to K_R
    alone.
    """
    from fcl_solver.model import profit
    from fcl_solver.solver import solve_with_fcl_given_KR

    dist = UniformResidual(D_bar=valid_params.D_bar)
    # Must start safely above the no-FCL benchmark's own K_R^o (~71 for
    # valid_params): below that, no-FCL profit is still *rising* toward its
    # interior optimum, so a "no-FCL profit decreases" check would fail for
    # the wrong reason (not yet past the peak, rather than evidence against
    # unboundedness).
    KR_values = [200, 1000, 10000, 100000]

    # At each K_R, re-optimize (K_F, K_M) (the unified solver, correct in
    # whichever regime that K_R falls into) -- this traces the genuine
    # profit-maximizing ray, not an arbitrary fixed ratio.
    with_fcl_profits = [
        solve_with_fcl_given_KR(dist, valid_params, KR, KF_max=20 * KR, KM_max=20 * KR).profit
        for KR in KR_values
    ]
    no_fcl_profits = [profit(dist, valid_params, KR, KR, 0.0) for KR in KR_values]

    assert with_fcl_profits == sorted(with_fcl_profits), "with-FCL profit should keep climbing as K_R grows"
    assert with_fcl_profits[-1] > 10 * with_fcl_profits[1], "and not be converging to a finite limit"
    assert no_fcl_profits == sorted(no_fcl_profits, reverse=True), (
        "no-FCL profit, scaled the same way, should instead strictly DEcrease -- "
        "confirming the unboundedness is FCL-specific, not a general scaling artifact"
    )


def test_part_iii_carbon_did_not_improve_in_our_search(valid_params):
    """FINDING (see sweep.py for the full writeup and a wider search): we
    could not construct a parameter combination, within the model's
    economically valid domain (K_F, K_M >= 0), where carbon genuinely falls
    below the no-FCL benchmark -- not for the uniform distribution, and not
    for the power family either, across three orders of magnitude of C_R
    and several R/c/C_F/C_M combinations (see sweep.py).

    The reason traces back to Assumption 1 itself: it requires
    R < c+C_F+C_M, which makes the coefficient on (D_bar+K_R) in eq. 23
    (K*_F's closed form) *always* negative, so K*_F is *guaranteed* to hit
    zero and go negative at some finite K_R for every valid parameter set --
    "K*_R -> infinity" (eq. 24 > 0) is a knife-edge artifact of the model's
    linear-in-K_R structure under the uniform/power families, not a literal
    prediction; pushed that far, the closed form has already left its valid
    domain. This test pins down the qualitative result (i,ii hold; iii does
    not, here) rather than the carbon-improving outcome we originally
    expected to find -- see the module docstring for why this is flagged as
    a finding, not a solver bug (cross-checked against finite-difference
    gradients and a brute-force trapezoid integral throughout development).
    """
    dist = UniformResidual(D_bar=valid_params.D_bar)
    result = check_triple_win(dist, valid_params, KR_max=3 * valid_params.D_bar,
                               KF_max=3 * valid_params.D_bar, KM_max=3 * valid_params.D_bar)

    assert result.below_threshold
    assert result.profit_higher and result.blackout_lower  # (i), (ii): always hold, confirmed again here
    assert not result.carbon_lower, (
        "if this now passes (carbon_lower=True), the earlier search finding needs revisiting -- "
        f"got {result}"
    )
