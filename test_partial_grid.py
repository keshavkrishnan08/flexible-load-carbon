"""
Task 2: revenue exogeneity -- the duality linchpin.

P*d must equal the constant (1-1/n)R for EVERY price P. This is what lets
the utility's revenue term drop out of eq. (6) and collapse profit-max into
the Section 3.5 cost-minimization problem.
"""
import pytest

from miner_demand.oligopoly import miner_revenue


def test_revenue_is_constant_across_prices(oli):
    constant = miner_revenue(oli, P=None)
    for P in [0.01, 0.5, 1.0, 7.3, 100.0, 1e4]:
        assert miner_revenue(oli, P) == pytest.approx(constant, rel=1e-12)


def test_revenue_equals_closed_form(oli):
    assert miner_revenue(oli, P=None) == pytest.approx((1 - 1 / oli.n) * oli.R)


def test_revenue_independent_of_price_means_zero_derivative(oli):
    """Numerically: d(P*d)/dP = 0 (the economic content of 'exogenous')."""
    h = 1e-3
    P = 5.0
    deriv = (miner_revenue(oli, P + h) - miner_revenue(oli, P - h)) / (2 * h)
    assert deriv == pytest.approx(0.0, abs=1e-9)
