"""
Emissions check: does the carbon-reduction result survive the partial grid?

Task 3's final question. In the full-grid model the regulator can induce
ANY mining demand, giving it full freedom to shape d(D,S) and (Section 3.6)
push emissions below the no-mining benchmark. In the partial grid that
freedom is bounded (max usable surplus mining = nR/(2Po),
partial_grid.usable_inducible_demand) and the program must clip (eq. 69).
This module asks numerically whether emission reduction still goes through.

Model (uniform case, Section 3.6.2 primitives):
  D ~ Uniform[0, D_bar],  S ~ Uniform[0, S_bar],  independent.
  Renewable supply = S*k.

Working out fossil output under each program (proportional to emissions,
paper's "variable cost"):
  * No mining (eq. clean program, delta=0): surplus mining uses only
    renewable, so fossil(D,S,k) = max(D - S k, 0).
  * Adapted program (eq. 69) with shortfall floor d_floor: surplus mining
    still draws no fossil, but the floor adds d_floor of fossil-fed mining
    whenever S k < D, so
        fossil(D,S,k) = max(D - S k, 0) + d_floor * 1{S k < D}.
  (Both derived in derivations.md, Prop. 4. Note d_floor = 0 makes the two
  identical at every k -- so a positive floor is what creates any effect,
  at the cost of adding fossil directly; the benefit must come from the
  floor pushing the utility to build more k. That tension is the whole
  question.)

Utility picks k to minimize variable + capital cost c*E[fossil] + C*k;
emissions are c*E[fossil] at that k. We compare no-mining vs adapted, each
at its own optimal k. Integration is a vectorized midpoint grid (fast and
ample for this monotone, piecewise-smooth integrand).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import optimize

# Module-level grid (midpoints) reused across all evaluations.
_NG = 240


@dataclass
class EmissionParams:
    D_bar: float    # upper bound of consumer demand support
    S_bar: float    # upper bound of renewable capacity factor (<= 1)
    c: float        # fossil marginal (carbon) cost per unit
    C: float        # renewable capital cost per unit of k
    R: float        # block reward (sets the mining clip, unused if d_floor=0)
    n: int          # in-grid miners
    Po: float       # out-of-grid price


def _grids(params: EmissionParams):
    D = (np.arange(_NG) + 0.5) / _NG * params.D_bar
    S = (np.arange(_NG) + 0.5) / _NG * params.S_bar
    DD, SS = np.meshgrid(D, S, indexing="ij")
    return DD, SS


def expected_fossil(k: float, params: EmissionParams, d_floor: float = 0.0) -> float:
    """E[max(D - S k, 0) + d_floor*1{S k < D}] over uniform (D, S)."""
    DD, SS = _grids(params)
    short = DD - SS * k          # positive where renewables fall short
    base = np.clip(short, 0.0, None)
    floor_term = d_floor * (short > 0)
    return float(np.mean(base + floor_term))


def optimal_k(params: EmissionParams, d_floor: float = 0.0,
              k_hi_mult: float = 6.0) -> tuple[float, float]:
    """Utility-optimal k = argmin c*E[fossil] + C*k, and emission there."""
    def cost(k):
        return params.c * expected_fossil(k, params, d_floor) + params.C * k

    res = optimize.minimize_scalar(
        cost, bounds=(0.0, k_hi_mult * params.D_bar / max(params.S_bar, 1e-9)),
        method="bounded", options={"xatol": 1e-4},
    )
    k_star = float(res.x)
    return k_star, params.c * expected_fossil(k_star, params, d_floor)


def compare(params: EmissionParams, d_floor: float = 0.0):
    """No-mining vs adapted-program (eq. 69) emissions, each at its optimal k."""
    k0, e0 = optimal_k(params, d_floor=0.0)          # no-mining benchmark
    k1, e1 = optimal_k(params, d_floor=d_floor)      # adapted program
    return {
        "k_no_mining": k0,
        "emission_no_mining": e0,
        "k_with_mining": k1,
        "emission_with_mining": e1,
        "carbon_lower": e1 < e0 - 1e-9,
        "carbon_pct_change": 100.0 * (e1 - e0) / e0 if e0 > 0 else float("nan"),
        "d_floor": d_floor,
    }
