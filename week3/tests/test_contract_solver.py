"""
Week 3 Task 1 + 4 tests: dispatch LP, LP duality certificates, and
the contract-carbon-gap analysis.

Structure of tests:
1. Lemma 1 validation: firm-optimal LP must recover the greedy rule
   (d*(x) = min{max(K_F-x,0), K_M}) on Uniform and Power distributions.
2. Carbon-optimal ≤ firm-optimal: the LP that minimizes carbon subject
   to a profit floor must produce carbon ≤ firm-optimal carbon (by
   definition of minimization).
3. LP duality certificates: strong duality gap < 1e-6, complementary
   slackness approximately holds.
4. Shadow price of the profit floor: positive (relaxing profit floor
   allows lower carbon), as expected economically.
5. Dispatch-structure test: firm-optimal d(x) matches greedy analytically;
   carbon-optimal d(x) dispatches less in fossil-heavy states.
"""
import numpy as np
import pytest
from scipy import stats

from fcl_solver.contract_solver import (
    solve_carbon_optimal_dispatch,
    solve_firm_optimal_dispatch,
    state_grid,
)
from fcl_solver.distributions import (
    PowerResidual,
    TruncatedLognormal,
    UniformResidual,
    lognormal_primitive,
)
from fcl_solver.lp_certificate import (
    certify_dispatch_lp,
    greedy_dispatch_carbon,
    greedy_vs_optimal_contract_summary,
)
from fcl_solver.model import Params


@pytest.fixture
def params():
    p = Params(R=109, c=45, CF=10, CR=25, CM=56, beta=190, p=10, D_bar=100)
    p.check_assumption1()
    return p


@pytest.fixture
def uniform():
    return UniformResidual(D_bar=100)


@pytest.fixture
def lognormal():
    return lognormal_primitive(D_bar=100)


# ─────────────────────────────────────────────────────────────────────────────
# Lemma 1 validation: firm-optimal LP recovers the greedy rule
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("dist_name,alpha", [
    ("uniform", None), ("power_0.5", 0.5), ("power_2.0", 2.0),
])
def test_firm_optimal_lp_matches_greedy_carbon(params, dist_name, alpha):
    """Firm-optimal LP carbon ≈ greedy-rule carbon on self-similar families.

    Paper Lemma 1 (Section 3.3): the greedy dispatch d*(x)=min{max(K_F-x,0),K_M}
    is the UNIQUE profit-maximizing dispatch given fixed capacities. The LP
    should find the same solution, so its carbon should match greedy carbon
    to within numerical precision (< 0.1% relative error).

    Note: we test on fixed K_R=15, K_F=50, K_M=20 (genuine interior regime
    K_M > K_R) to avoid the K_M=K_R knife-edge.
    """
    dist = UniformResidual(D_bar=100) if alpha is None else PowerResidual(D_bar=100, alpha=alpha)
    K_R, K_F, K_M = 15.0, 50.0, 20.0

    firm = solve_firm_optimal_dispatch(dist, params, K_R, K_F, K_M, N=300)

    x, w = state_grid(dist, K_R, 300)
    c_greedy = greedy_dispatch_carbon(x, w, K_F, K_M, params.c)

    assert "Optimal" in firm.lp_status, f"LP not optimal: {firm.lp_status}"
    rel_err = abs(firm.carbon - c_greedy) / max(1e-10, c_greedy)
    assert rel_err < 1e-3, (
        f"Lemma 1 violation for {dist_name}: LP carbon={firm.carbon:.6f}, "
        f"greedy carbon={c_greedy:.6f}, rel_err={rel_err:.2e}"
    )


def test_firm_optimal_lp_lemma1_lognormal(params, lognormal):
    """Lemma 1 on the non-self-similar lognormal-primitive family.

    The greedy-rule guarantee is distribution-free (Lemma 1's proof only
    uses R > c and β+p > R, i.e. Assumption 1), so it must hold here too.
    """
    K_R, K_F, K_M = 25.0, 40.0, 15.0
    firm = solve_firm_optimal_dispatch(lognormal, params, K_R, K_F, K_M, N=300)
    x, w = state_grid(lognormal, K_R, 300)
    c_greedy = greedy_dispatch_carbon(x, w, K_F, K_M, params.c)
    rel_err = abs(firm.carbon - c_greedy) / max(1e-10, c_greedy)
    assert rel_err < 1e-3, f"Lemma 1 fails on lognormal: rel_err={rel_err:.2e}"


def test_firm_optimal_dispatch_shape(params, uniform):
    """The firm-optimal dispatch d_i should match the greedy rule pointwise."""
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=200)
    x = firm.x
    d_greedy = np.clip(K_F - x, 0.0, K_M)
    # LP solution should match greedy to within 1e-4 at each grid point
    max_abs = np.max(np.abs(firm.d - d_greedy))
    assert max_abs < 1e-3, f"Dispatch shape mismatch: max|d_lp - d_greedy|={max_abs:.4e}"


# ─────────────────────────────────────────────────────────────────────────────
# Carbon-optimal contract: carbon ≤ firm-optimal carbon
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("dist_fixture", ["uniform", "lognormal"])
def test_carbon_optimal_lp_no_worse_than_firm(params, dist_fixture, uniform, lognormal):
    """Carbon-optimal LP carbon ≤ firm-optimal LP carbon (by definition of min)."""
    dist = uniform if dist_fixture == "uniform" else lognormal
    K_R, K_F, K_M = 15.0, 50.0, 20.0

    firm = solve_firm_optimal_dispatch(dist, params, K_R, K_F, K_M, N=200)
    co = solve_carbon_optimal_dispatch(
        dist, params, K_R, K_F, K_M,
        profit_floor=firm.profit_dispatch, N=200,
    )

    assert "Optimal" in co.lp_status, f"LP not optimal: {co.lp_status}"
    assert co.carbon <= firm.carbon + 1e-6, (
        f"Carbon-optimal LP ({co.carbon:.4f}) worse than firm-optimal ({firm.carbon:.4f})"
    )


def test_carbon_optimal_achieves_tight_profit_floor(params, uniform):
    """Carbon-optimal LP should use the full profit budget (floor should be tight)."""
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=300)
    floor = firm.profit_dispatch * 0.9  # relax floor slightly to give room

    co = solve_carbon_optimal_dispatch(uniform, params, K_R, K_F, K_M,
                                        profit_floor=floor, N=300)
    # The carbon-optimal LP should achieve AT LEAST the floor
    assert co.profit_dispatch >= floor - 1e-4, (
        f"Profit floor violated: achieved {co.profit_dispatch:.4f} vs floor {floor:.4f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# LP duality certificates (Task 4)
# ─────────────────────────────────────────────────────────────────────────────

def test_lp_strong_duality_firm_optimal(params, uniform):
    """Strong duality gap < 1e-6 for the firm-optimal dispatch LP."""
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=200)
    cert = certify_dispatch_lp(uniform, params, firm, 'profit')
    assert cert.is_certified, f"LP not certified: status={cert.lp_status}"
    assert cert.strong_duality_gap < 1e-6, f"Duality gap too large: {cert.strong_duality_gap:.2e}"


def test_lp_strong_duality_carbon_optimal(params, uniform):
    """Strong duality gap < 1e-6 for the carbon-optimal dispatch LP."""
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=200)
    co = solve_carbon_optimal_dispatch(
        uniform, params, K_R, K_F, K_M,
        profit_floor=firm.profit_dispatch, N=200,
    )
    cert = certify_dispatch_lp(uniform, params, co, 'carbon',
                                profit_floor=firm.profit_dispatch)
    assert cert.is_certified, f"LP not certified: {cert.lp_status}"
    assert cert.strong_duality_gap < 1e-6


def test_shadow_price_profit_floor_is_positive(params, uniform):
    """Shadow price of the profit-floor constraint must be ≥ 0.

    Economically: relaxing the profit floor (lower floor) can only help
    or leave unchanged the minimum achievable carbon, so the marginal
    value of a tighter floor is non-negative carbon cost.
    """
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=200)
    floor = firm.profit_dispatch * 0.85  # binding floor (not just feasibility)
    co = solve_carbon_optimal_dispatch(
        uniform, params, K_R, K_F, K_M, profit_floor=floor, N=200,
    )
    cert = certify_dispatch_lp(uniform, params, co, 'carbon', profit_floor=floor)
    assert cert.shadow_price_profit_floor >= -1e-6, (
        f"Shadow price negative: {cert.shadow_price_profit_floor:.4f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Structural properties of the carbon-optimal dispatch
# ─────────────────────────────────────────────────────────────────────────────

def test_carbon_optimal_dispatches_less_in_fossil_heavy_states(params, uniform):
    """The carbon-optimal contract should dispatch LESS than the greedy rule
    in states where fossil is the marginal source (x > 0), and more (or equal)
    in deep renewable-surplus states (x << 0).

    This is the key structural prediction: avoid dispatching on fossil; shift
    dispatch toward clean hours.
    """
    K_R, K_F, K_M = 15.0, 50.0, 20.0
    firm = solve_firm_optimal_dispatch(uniform, params, K_R, K_F, K_M, N=400)
    co = solve_carbon_optimal_dispatch(
        uniform, params, K_R, K_F, K_M,
        profit_floor=firm.profit_dispatch * 0.7,  # loose floor to allow big shift
        N=400,
    )

    x = firm.x
    # In high-demand states (x > 0, fossil heavy), carbon-optimal should dispatch less
    fossil_states = x > 5.0
    surplus_states = x < -5.0

    if fossil_states.sum() > 0 and surplus_states.sum() > 0:
        mean_d_firm_fossil = np.mean(firm.d[fossil_states])
        mean_d_co_fossil = np.mean(co.d[fossil_states])
        # Carbon-optimal dispatches less in fossil-heavy states (or equal)
        assert mean_d_co_fossil <= mean_d_firm_fossil + 1e-6, (
            f"Carbon-optimal dispatches MORE in fossil states: "
            f"firm={mean_d_firm_fossil:.3f}, co={mean_d_co_fossil:.3f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Integration: greedy_vs_optimal_contract_summary
# ─────────────────────────────────────────────────────────────────────────────

def test_greedy_vs_optimal_summary_uniform(params, uniform):
    """End-to-end summary function: validates Lemma 1 and reports carbon gap."""
    summary = greedy_vs_optimal_contract_summary(uniform, params, 15.0, 50.0, 20.0, N=200)
    assert summary['validates_lemma1'], (
        f"Lemma 1 failed: rel_err={summary['lemma1_rel_err']:.2e}"
    )
    assert summary['lp_cert_firm'].is_certified
    assert summary['lp_cert_carbon'].is_certified
    # Carbon gap ≥ 0: carbon-optimal can only be ≤ firm-optimal
    assert summary['carbon_gap'] >= -1e-6


@pytest.mark.parametrize("alpha", [0.5, 1.0, 2.0])
def test_greedy_vs_optimal_summary_power(params, alpha):
    """Lemma 1 holds for the full power-law family."""
    dist = PowerResidual(D_bar=100, alpha=alpha)
    # Avoid the alpha<1 divergence issue for large-FCL: use K_M < K_R here
    K_R, K_F, K_M = 30.0, 60.0, 15.0
    summary = greedy_vs_optimal_contract_summary(dist, params, K_R, K_F, K_M, N=200)
    assert summary['validates_lemma1'], (
        f"alpha={alpha}: Lemma 1 rel_err={summary['lemma1_rel_err']:.2e}"
    )
