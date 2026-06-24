"""
Core FCL economics: dispatch rule, profit, blackout probability, carbon.

Every quantity here is built directly from the *unified* eq. (5)/(84)-(86)
integrals against the extended CDF F(x;K_R) (see distributions.py). Because
F is already 0 below -K_R and 1 above D_bar, these same integrals are
correct in both the large-FCL regime (K_M > K_R, paper Section 4) and the
small-FCL regime (K_M <= K_R, Appendix G) -- no regime branch is needed.

Equation map (paper):
  dispatch            -> eq. 3
  mining_revenue      -> eq. 84  (R * integral_{K_F-K_M}^{K_F} F dx)
  fossil_output       -> eq. 86  (integral_{-K_M}^{K_F-K_M} (1-F) dx);
                          carbon = c * fossil_output, Remark 2 / eq. 17
  blackout_integral   -> eq. 85  (integral_{K_F}^{D_bar} (1-F) dx)
  profit              -> eq. 5 / eq. 10 (R-term + fossil + blackout + capital)
  blackout_probability-> 1 - F(K_F; K_R)
"""
from __future__ import annotations

from dataclasses import dataclass

from scipy import integrate

from .distributions import ResidualDemand

# scipy.integrate.quad's default tolerance (epsabs ~1.5e-8) is fine for the
# integral *values* themselves, but it is not tight enough to support
# finite-difference derivative checks at the step sizes (h ~ 1e-4 to 1e-5)
# used in tests/test_gradients.py: dividing a ~1e-8 integration error by 2h
# produces ~1e-4 of spurious "derivative" noise, which is the same order as
# the tolerance those tests use. Tightening here removes that noise floor
# (confirmed against an independent brute-force trapezoid-rule integral
# while debugging the PowerResidual(alpha=0.5) test failure).
_QUAD_KWARGS = dict(limit=200, epsabs=1e-9, epsrel=1e-9)


@dataclass
class Params:
    """Model primitives (paper Section 3, Assumption 1)."""

    R: float       # FCL/mining revenue per MWh dispatched
    c: float       # fossil variable (carbon) cost per MWh
    CF: float      # amortized fossil capital cost per MW
    CR: float      # amortized renewable capital cost per MW
    CM: float      # amortized FCL/ASIC capital cost per MW
    beta: float    # blackout penalty per MWh unserved
    p: float       # regulated retail price per MWh
    D_bar: float   # upper bound of (non-FCL) consumer demand support

    def check_assumption1(self) -> None:
        """Paper's Assumption 1 parameter regularity (Section 3.1)."""
        assert self.R > self.c + self.CM, "need R > c + C_M"
        assert self.R < self.c + self.CF + self.CM, "need R < c + C_F + C_M (interior regime)"
        assert self.beta + self.p > self.c + self.CF, "need beta+p > c+C_F"
        assert self.beta + self.p > self.R, "need beta+p > R"


def dispatch(x, K_F, K_M):
    """FCL dispatch rule, eq. 3: d(x) = min(max(K_F - x, 0), K_M)."""
    import numpy as np

    return np.clip(K_F - x, 0.0, K_M)


def expected_mining_revenue(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> float:
    """eq. 84: R * integral_{K_F-K_M}^{K_F} F(x;K_R) dx."""
    if K_M <= 0:
        return 0.0
    val, _ = integrate.quad(lambda x: dist.cdf(x, K_R), K_F - K_M, K_F, **_QUAD_KWARGS)
    return params.R * val


def expected_fossil_output(dist: ResidualDemand, K_R, K_F, K_M) -> float:
    """eq. 86 (unified, no c factor): integral_{-K_M}^{K_F-K_M} (1-F(x;K_R)) dx."""
    val, _ = integrate.quad(lambda x: 1.0 - dist.cdf(x, K_R), -K_M, K_F - K_M, **_QUAD_KWARGS)
    return val


def expected_blackout_integral(dist: ResidualDemand, params: Params, K_R, K_F) -> float:
    """eq. 85 (unified, no beta+p factor): integral_{K_F}^{D_bar} (1-F(x;K_R)) dx."""
    if K_F >= params.D_bar:
        return 0.0
    val, _ = integrate.quad(lambda x: 1.0 - dist.cdf(x, K_R), K_F, params.D_bar, **_QUAD_KWARGS)
    return val


def profit(dist: ResidualDemand, params: Params, K_R, K_F, K_M, E_D: float = 0.0) -> float:
    """Utility expected profit, eq. 5 (= eq. 10 in the large-FCL regime).

    E_D = E[D_tilde] only adds the constant p*E[D_tilde] term; it does not
    affect any first-order condition or comparison and defaults to 0.
    """
    mining_rev = expected_mining_revenue(dist, params, K_R, K_F, K_M)
    fossil_cost = params.c * expected_fossil_output(dist, K_R, K_F, K_M)
    blackout_cost = (params.beta + params.p) * expected_blackout_integral(dist, params, K_R, K_F)
    capital = params.CF * K_F + params.CR * K_R + params.CM * K_M
    return params.p * E_D + mining_rev - fossil_cost - blackout_cost - capital


def blackout_probability(dist: ResidualDemand, K_R, K_F) -> float:
    """P(x_tilde > K_F) = 1 - F(K_F; K_R)."""
    return float(1.0 - dist.cdf(K_F, K_R))


def carbon_emissions(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> float:
    """Expected carbon = c * E[fossil output] (Remark 2 / Section 4.3 eq. 17)."""
    return params.c * expected_fossil_output(dist, K_R, K_F, K_M)
