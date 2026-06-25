"""
Partial-grid mining demand: Task 3 (Appendix A, eqs 61-68).

When the grid serves only n of the n+m miners (the other m mine elsewhere
at price Po), in-grid demand and revenue change qualitatively. This module
implements the appendix's closed forms and the small-grid (m >> n) limit,
and -- the point of Task 3 -- shows that the clean revenue-exogeneity of
oligopoly.miner_revenue() BREAKS here.

Closed forms (paper):
  total over all miners (eq. 65):
      D_total = (m + n - 1) R / (n P + m Po)
  in-grid aggregate demand (eq. 68):
      d = n (m + n - 1) R [m Po - (m - 1) P] / (n P + m Po)^2
  in-grid revenue:
      P d = n P (m + n - 1) R [m Po - (m - 1) P] / (n P + m Po)^2,
      "approximately exogenous ... if P is not too far away from Po."

Small-grid limit m/n -> 0 (eq. unlabeled, p.56):
      d   -> (n R / Po) (1 - P/Po)
      P d -> n R (P/Po) (1 - P/Po),  concave in P, peak n R / 4 at P = Po/2.

Constraints the paper draws from this (all asserted in tests):
  - d >= 0 iff P <= Po (else miners leave the focal grid),
  - max inducible in-grid demand is n R / Po (at P -> 0),
  - revenue is maximized at P = Po/2 with value n R / 4, so the regulator
    will never push P past Po/2 -> usable inducement is capped at the
    d = n R / (2 Po) that the adapted DR program (eq. 69) clips to.

Notation: Po here is the out-of-grid electricity price (the paper first
calls it c, then renames it Po to free up c for fossil marginal cost).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PartialGridParams:
    """Primitives for the n in-grid + m out-of-grid game (Appendix A)."""

    R: float    # total dollar block reward in the period
    n: int      # in-grid miners (served by the focal grid at price P)
    m: int      # out-of-grid miners (mine elsewhere at price Po)
    Po: float   # out-of-grid electricity price

    def check(self) -> None:
        assert self.R > 0
        assert self.n >= 1 and self.m >= 1
        assert self.Po > 0


def total_demand(params: PartialGridParams, P: float) -> float:
    """All-miner aggregate demand, eq. (65): (m+n-1) R / (n P + m Po)."""
    return (params.m + params.n - 1) * params.R / (params.n * P + params.m * params.Po)


def ingrid_demand(params: PartialGridParams, P: float) -> float:
    """In-grid aggregate demand, eq. (68).

        d = n (m+n-1) R [m Po - (m-1) P] / (n P + m Po)^2

    Re-derived in derivations.md (Prop. 3): sum the n in-grid FOCs to get
    R[(n-1) sum_N d + n sum_M d] / D_total^2 = nP (eq. 66), write
    sum_M = D_total - sum_N, solve for sum_N, and substitute eq. (65).
    """
    R, n, m, Po = params.R, params.n, params.m, params.Po
    denom = (n * P + m * Po) ** 2
    return n * (m + n - 1) * R * (m * Po - (m - 1) * P) / denom


def ingrid_revenue(params: PartialGridParams, P: float) -> float:
    """Utility's revenue from in-grid miners, P * d (eq. 68 x P).

    Unlike oligopoly.miner_revenue (a constant), this depends on P -- that
    dependence is exactly the Task-3 finding (see is_revenue_exogenous).
    """
    return P * ingrid_demand(params, P)


def small_grid_demand(params: PartialGridParams, P: float) -> float:
    """m >> n limit: d -> (n R / Po)(1 - P/Po)."""
    return (params.n * params.R / params.Po) * (1.0 - P / params.Po)


def small_grid_revenue(params: PartialGridParams, P: float) -> float:
    """m >> n limit: P d -> n R (P/Po)(1 - P/Po)."""
    return params.n * params.R * (P / params.Po) * (1.0 - P / params.Po)


def revenue_peak(params: PartialGridParams) -> tuple[float, float]:
    """(P_star, revenue_star) maximizing small-grid revenue: (Po/2, nR/4)."""
    return params.Po / 2.0, params.n * params.R / 4.0


def max_inducible_demand(params: PartialGridParams) -> float:
    """Largest in-grid demand the regulator can induce: n R / Po (at P->0)."""
    return params.n * params.R / params.Po


def usable_inducible_demand(params: PartialGridParams) -> float:
    """Demand at the revenue-maximizing price P = Po/2: n R / (2 Po).

    This is the clip level the adapted demand-response program (eq. 69)
    uses, because a profit-seeking grid will not set P below Po/2.
    """
    return params.n * params.R / (2.0 * params.Po)


def is_revenue_exogenous(params: PartialGridParams, P1: float, P2: float, tol: float = 1e-9) -> bool:
    """Task-3 test: is P*d the same at two different prices? (It isn't.)

    In the clean oligopoly P*d = (1-1/n)R for ALL P. Here we evaluate
    in-grid revenue at P1 and P2 and report whether they coincide. They
    only (approximately) do when P is near Po; in general the duality that
    lets profit-max collapse to cost-min FAILS. Returns True iff exogenous.
    """
    return abs(ingrid_revenue(params, P1) - ingrid_revenue(params, P2)) < tol


# ---------------------------------------------------------------------------
# Independent numerical validation of eq. 68 (asymmetric two-price game).
# ---------------------------------------------------------------------------

def solve_ingrid_demand_numerically(params: PartialGridParams, P: float) -> float:
    """In-grid aggregate demand by solving the two-price FOC system directly.

    Two symmetric blocs (n in-grid at P, m out-of-grid at Po). With
    D = n*d_in + m*d_out, the per-miner FOCs from eqs (61)-(62) are
        R (D - d_in) / D^2  = P,
        R (D - d_out)/ D^2  = Po.
    We solve this 2x2 system for (d_in, d_out) with a Newton solver and
    return n * d_in. Independent of eq. (68).
    """
    from scipy.optimize import fsolve

    R, n, m, Po = params.R, params.n, params.m, params.Po

    def residual(z):
        d_in, d_out = z
        D = n * d_in + m * d_out
        return [
            R * (D - d_in) / D**2 - P,
            R * (D - d_out) / D**2 - Po,
        ]

    # Start near the equal-split competitive guess.
    guess = [R / (n + m) / P, R / (n + m) / Po]
    sol = fsolve(residual, guess, xtol=1e-13, full_output=False)
    return n * sol[0]
