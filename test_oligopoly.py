"""
Task 3: the partial grid (Appendix A, eqs 61-68).

Checks (a) the closed form eq. (68) against an independent two-price
best-response solve, (b) the small-grid limit and its nR/4 revenue peak,
(c) the bounds d>=0 iff P<=Po and max inducement nR/Po, and -- the headline
-- (d) that revenue exogeneity BREAKS here.
"""
import numpy as np
import pytest

from miner_demand.partial_grid import (
    PartialGridParams, ingrid_demand, ingrid_revenue, is_revenue_exogenous,
    max_inducible_demand, revenue_peak, small_grid_demand, small_grid_revenue,
    solve_ingrid_demand_numerically, total_demand, usable_inducible_demand,
)


@pytest.mark.parametrize("P", [0.5, 1.0, 2.0, 3.9])
def test_eq68_matches_two_price_best_response(pg, P):
    closed = ingrid_demand(pg, P)
    numeric = solve_ingrid_demand_numerically(pg, P)
    assert numeric == pytest.approx(closed, rel=1e-7)


def test_total_demand_eq65(pg):
    P = 2.0
    expected = (pg.m + pg.n - 1) * pg.R / (pg.n * P + pg.m * pg.Po)
    assert total_demand(pg, P) == pytest.approx(expected)


def test_small_grid_limit_is_approached(pg):
    """As m -> inf with n fixed, eq. (68) -> (nR/Po)(1 - P/Po)."""
    P = 1.5
    limits = []
    for m in [500, 5_000, 50_000, 500_000]:
        p = PartialGridParams(R=pg.R, n=pg.n, m=m, Po=pg.Po)
        limits.append(ingrid_demand(p, P))
    target = small_grid_demand(pg, P)  # n,R,Po independent of m
    # monotonically closing in on the limit
    errs = [abs(x - target) for x in limits]
    assert errs[-1] < errs[0]
    assert limits[-1] == pytest.approx(target, rel=1e-3)


def test_revenue_peak_is_nR_over_4_at_Po_over_2(pg):
    P_star, rev_star = revenue_peak(pg)
    assert P_star == pytest.approx(pg.Po / 2)
    assert rev_star == pytest.approx(pg.n * pg.R / 4)
    # it really is the max of the small-grid revenue curve
    Ps = np.linspace(1e-3, pg.Po, 400)
    revs = [small_grid_revenue(pg, P) for P in Ps]
    assert max(revs) == pytest.approx(rev_star, rel=1e-4)


def test_demand_nonnegative_iff_price_below_Po(pg):
    assert small_grid_demand(pg, P=pg.Po) == pytest.approx(0.0, abs=1e-12)
    assert small_grid_demand(pg, P=0.5 * pg.Po) > 0
    assert small_grid_demand(pg, P=1.5 * pg.Po) < 0  # miners would leave


def test_inducement_bounds(pg):
    assert max_inducible_demand(pg) == pytest.approx(pg.n * pg.R / pg.Po)
    assert usable_inducible_demand(pg) == pytest.approx(pg.n * pg.R / (2 * pg.Po))


def test_revenue_exogeneity_BREAKS_in_partial_grid(pg):
    """The Task-3 headline: P*d is NOT constant here (contrast Task 2).

    In the clean oligopoly P*d = (1-1/n)R for all P (test_exogeneity). Here
    revenue varies substantially with P -- that is exactly why profit-max no
    longer collapses to cost-min in the partial grid.
    """
    assert not is_revenue_exogenous(pg, P1=1.0, P2=3.0)
    # Quantify the break: revenue at two interior prices differs by a lot.
    r_lo = ingrid_revenue(pg, 0.25 * pg.Po)
    r_mid = ingrid_revenue(pg, 0.50 * pg.Po)
    assert abs(r_mid - r_lo) / r_mid > 0.10  # >10% swing -> clearly not exogenous
