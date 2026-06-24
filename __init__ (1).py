"""
Oligopoly mining demand: the foundation for Tasks 1 and 2.

This module implements miner i's problem (paper eq. 9),

    max_{d_i}  R * d_i / (d_i + sum_{j!=i} d_j)  -  d_i * P,

its symmetric Nash equilibrium aggregate demand (eq. 10),

    d = (1 - 1/n) * R / P,                                          (Task 1)

and the resulting miner revenue

    P * d = (1 - 1/n) * R,                                          (Task 2)

which is independent of P (and therefore of every utility decision). That
independence is the whole reason the utility's profit-maximization (eq. 6)
collapses to the cost-minimization problem of Section 3.5.

Everything here is cross-checked two independent ways, in the spirit of
Role 2's "re-derive, don't transcribe":
  - the closed form `equilibrium_demand` (eq. 10), and
  - `solve_equilibrium_numerically`, a from-scratch best-response iteration
    on eq. 9 that knows nothing about eq. 10.
tests/test_oligopoly.py asserts the two agree to ~1e-9.

Notation matches the paper exactly:
  R  total dollar block reward in the period (the "pie"; exogenous, set by
     Bitcoin's protocol + price, i.e. the xi of eqs 6-7).
  n  number of symmetric in-grid miners (n >= 2 for a genuine oligopoly).
  P  electricity price charged to miners (the regulator's lever).
  d  aggregate mining electricity demand = sum_i d_i.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OligopolyParams:
    """Primitives of the symmetric n-miner game (paper Section 3.4.1)."""

    R: float   # total dollar block reward in the representative period
    n: int     # number of symmetric miners

    def check(self) -> None:
        assert self.R > 0, "block reward R must be positive"
        assert self.n >= 2, "need n >= 2 for an oligopoly (n=1 is monopoly, n->inf is perfect competition)"


def equilibrium_demand(params: OligopolyParams, P: float) -> float:
    """Aggregate equilibrium mining demand, eq. (10): d = (1 - 1/n) R / P.

    Derivation (filled in fully in derivations.md, Lemma 1): miner i's FOC
    on eq. (9) is  R * (D - d_i) / D^2 = P  where D = sum_j d_j. Imposing
    symmetry d_i = d/n gives D - d_i = d (n-1)/n, hence R (n-1)/(n d) = P,
    i.e. d = (1 - 1/n) R / P.
    """
    if P <= 0:
        raise ValueError("price P must be positive (d -> infinity as P -> 0)")
    return (1.0 - 1.0 / params.n) * params.R / P


def inducing_price(params: OligopolyParams, d_target: float) -> float:
    """Price that induces a desired aggregate demand d_target (Task 1).

    Inverse of eq. (10): P = (1 - 1/n) R / d_target. Because eq. (10) is a
    continuous strictly-decreasing bijection P <-> d on (0, inf), ANY
    target d_target > 0 is implementable by exactly one price. This is the
    "regulator can hit any mining quantity" claim, made precise.
    """
    if d_target <= 0:
        raise ValueError("target demand must be positive")
    return (1.0 - 1.0 / params.n) * params.R / d_target


def miner_revenue(params: OligopolyParams, P: float | None = None) -> float:
    """Utility's revenue from miners, P*d = (1 - 1/n) R (Task 2).

    P is accepted only to make the point that the answer does not depend on
    it: for any P > 0, P * equilibrium_demand(P) returns the same constant.
    Passing P=None returns the closed-form constant directly.
    """
    constant = (1.0 - 1.0 / params.n) * params.R
    if P is None:
        return constant
    # Computed the "long way" on purpose, to show the P's cancel.
    return P * equilibrium_demand(params, P)


def per_miner_profit(params: OligopolyParams, P: float) -> float:
    """Each miner's equilibrium profit, used for the participation check.

    In symmetric equilibrium d_i = d/n and total revenue share is
    R/n, with electricity cost P*d_i = P*d/n = (1-1/n)R/n. So
    profit_i = R/n - (1-1/n)R/n = R/n^2 >= 0, independent of P. Hence no
    miner ever wants to exit, which is the participation condition behind
    "any d_target is inducible."
    """
    return params.R / params.n**2


# ---------------------------------------------------------------------------
# Independent numerical validation (does NOT use eq. 10).
# ---------------------------------------------------------------------------

def best_response(params: OligopolyParams, d_others: float, P: float) -> float:
    """Miner i's best response to rivals' total d_others, from eq. (9)'s FOC.

    FOC: R * d_others / (d_i + d_others)^2 = P
      => (d_i + d_others)^2 = R * d_others / P
      => d_i = sqrt(R * d_others / P) - d_others, floored at 0.

    The objective is concave in d_i (second derivative
    -2 R d_others / (d_i+d_others)^3 < 0), so this stationary point is the
    unique maximizer.
    """
    if P <= 0:
        raise ValueError("price P must be positive")
    target = (params.R * d_others / P) ** 0.5 - d_others
    return max(target, 0.0)


def solve_equilibrium_numerically(params: OligopolyParams, P: float) -> float:
    """Aggregate demand by root-finding the symmetric best-response fixed point.

    Solves h(d_i) = best_response((n-1) d_i, P) - d_i = 0 with Brent's
    method. (Naive *simultaneous* best-response iteration diverges once n is
    large -- the -(n-1) d_others slope makes the Jacobi map non-contracting
    -- so we root-find the fixed point directly instead.) h is positive near
    d_i = 0 and negative for large d_i, so a bracketed root exists and is
    unique. Returns aggregate d = n * d_i. Uses nothing from eq. (10).
    """
    from scipy.optimize import brentq

    def h(d_i):
        return best_response(params, (params.n - 1) * d_i, P) - d_i

    # Upper bracket: any d_i above the competitive single-miner demand R/P
    # makes h negative; use a comfortable multiple.
    hi = params.R / P
    d_i = brentq(h, 1e-15, hi, xtol=1e-15, rtol=1e-14)
    return params.n * d_i
