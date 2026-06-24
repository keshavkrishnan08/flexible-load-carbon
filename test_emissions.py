"""
Task 1: the n-miner equilibrium and price inducement.

Most fundamental check: the closed form d = (1-1/n)R/P (eq. 10) must equal
an independent best-response fixed point of eq. (9). If this fails, nothing
downstream is trustworthy.
"""
import numpy as np
import pytest

from miner_demand.oligopoly import (
    OligopolyParams, equilibrium_demand, inducing_price, per_miner_profit,
    solve_equilibrium_numerically,
)


@pytest.mark.parametrize("P", [0.5, 1.0, 2.0, 5.0, 13.7])
def test_closed_form_matches_best_response_iteration(oli, P):
    closed = equilibrium_demand(oli, P)
    numeric = solve_equilibrium_numerically(oli, P)
    assert numeric == pytest.approx(closed, rel=1e-9)


@pytest.mark.parametrize("n", [2, 3, 10, 100, 1000])
def test_perfect_competition_limit(n):
    """As n -> inf, (1-1/n) -> 1, so d -> R/P (price = marginal revenue)."""
    p = OligopolyParams(R=1000.0, n=n)
    d = equilibrium_demand(p, P=2.0)
    assert d < 1000.0 / 2.0  # always below the competitive benchmark
    assert d == pytest.approx((1 - 1 / n) * 1000.0 / 2.0)


def test_inducement_is_a_bijection(oli):
    """Any target demand is hit by exactly one price, and round-trips."""
    for d_target in [10.0, 123.4, 5000.0]:
        P = inducing_price(oli, d_target)
        assert equilibrium_demand(oli, P) == pytest.approx(d_target, rel=1e-12)


def test_demand_strictly_decreasing_in_price(oli):
    Ps = np.linspace(0.1, 20, 50)
    ds = [equilibrium_demand(oli, P) for P in Ps]
    assert all(d2 < d1 for d1, d2 in zip(ds, ds[1:]))


def test_participation_profit_nonnegative_and_price_free(oli):
    """Each miner earns R/n^2 >= 0 regardless of P -> nobody exits."""
    prof = [per_miner_profit(oli, P) for P in [0.5, 2.0, 50.0]]
    assert all(x == pytest.approx(oli.R / oli.n**2) for x in prof)
    assert oli.R / oli.n**2 > 0
