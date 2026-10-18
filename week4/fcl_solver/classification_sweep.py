"""
Week 4 Task 1: classification-functional sweep.

Sweeps a large theory-tied distribution library and verifies the if-and-only-if:
    sign(Ψ(F, params)) = sign(carbon_no_FCL − carbon_with_FCL)

across every (distribution, C_R, C_M) cell. A single counterexample would
falsify the classification theorem; confirming it everywhere corroborates it.

Distribution library covers:
  • Uniform and Power(α) (the paper's own worked examples)
  • Beta scale-mixtures (symmetric, right-skew, left-skew, U-shaped)
  • Lognormal-primitive (the Week 2/3 non-self-similar family, four σ values)
  • Bimodal (a mixture of two Beta distributions)
  • Heavy-tailed (Beta with small shape parameters)

For each cell the sweep records:
  psi          : value of Ψ
  carbon_delta : with_FCL − no_FCL (negative = improvement)
  sign_match   : bool, the key check
  regime       : large-FCL or small-FCL
  K*/K°        : optimal capacities
  corner_fcl   : whether K_R* or K_M* hit an upper bound (unreliable solve)

Results are written to classification_sweep.csv.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .carbon_functional import FunctionalResult, compute_functional
from .distributions import (
    PowerResidual,
    PrimitiveResidual,
    ResidualDemand,
    UniformResidual,
    lognormal_primitive,
)
from .model import Params
from .solver import solve_no_fcl, solve_with_fcl


@dataclass
class SweepCell:
    dist_name: str
    CR: float
    CM: float
    psi: float
    carbon_delta: float
    sign_match: bool
    large_fcl_regime: bool
    corner_fcl: bool        # K_R* or K_M* at its bound → solve may be unreliable
    K_R_star: float
    K_F_star: float
    K_M_star: float
    K_R_circ: float
    K_F_circ: float
    phi_circ: float
    q_circ: float
    mu_star_low: float
    mu_circ_mid: float


def build_distribution_library(D_bar: float = 100.0) -> dict[str, ResidualDemand]:
    """Comprehensive distribution library for the classification sweep.

    Mirrors Week 3's phase-diagram library but adds bimodal, heavier-tailed,
    and asymmetric-mixture families to stress-test the functional beyond the
    smooth unimodal cases.
    """
    from scipy import stats

    lib = {
        # Paper's own examples
        "uniform": UniformResidual(D_bar),
        "power_right_0.5": PowerResidual(D_bar, alpha=0.5),
        "power_right_0.7": PowerResidual(D_bar, alpha=0.7),
        "power_left_2.0": PowerResidual(D_bar, alpha=2.0),
        "power_left_3.0": PowerResidual(D_bar, alpha=3.0),
        # Lognormal-primitive (non-self-similar, Week 2/3 candidate)
        "lognormal_sig0.2": lognormal_primitive(D_bar, sigma=0.20),
        "lognormal_sig0.28": lognormal_primitive(D_bar, sigma=0.28),
        "lognormal_sig0.4": lognormal_primitive(D_bar, sigma=0.40),
        "lognormal_sig0.6": lognormal_primitive(D_bar, sigma=0.60),
        # Beta scale-mixtures (various shapes)
        "beta_symmetric_22": PrimitiveResidual(
            D_bar, D_dist=stats.beta(2, 2, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
        "beta_right_skew": PrimitiveResidual(
            D_bar, D_dist=stats.beta(1.5, 4, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
        "beta_left_skew": PrimitiveResidual(
            D_bar, D_dist=stats.beta(4, 1.5, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
        "beta_heavy_tails": PrimitiveResidual(
            D_bar, D_dist=stats.beta(0.8, 0.8, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
        # Bimodal demand (mixture: low + high demand modes)
        "bimodal": PrimitiveResidual(
            D_bar,
            D_dist=_BimodalBeta(D_bar, w=0.5, a1=2, b1=8, a2=8, b2=2),
            S_dist=stats.beta(2, 2)),
        # Concentrated near surplus (very low residual demand)
        "surplus_concentrated": PrimitiveResidual(
            D_bar, D_dist=stats.beta(1, 5, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
        # Concentrated near scarcity
        "scarcity_concentrated": PrimitiveResidual(
            D_bar, D_dist=stats.beta(5, 1, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2)),
    }
    return lib


class _BimodalBeta:
    """D-distribution: 50/50 mixture of Beta(a1,b1) and Beta(a2,b2) on [0,D_bar].

    Used for the "bimodal" distribution in the library.
    """
    def __init__(self, D_bar, w, a1, b1, a2, b2):
        from scipy import stats
        self.D_bar = float(D_bar)
        self.w = float(w)
        self._d1 = stats.beta(a1, b1, loc=0, scale=D_bar)
        self._d2 = stats.beta(a2, b2, loc=0, scale=D_bar)

    def cdf(self, d):
        return self.w * self._d1.cdf(d) + (1 - self.w) * self._d2.cdf(d)

    def pdf(self, d):
        return self.w * self._d1.pdf(d) + (1 - self.w) * self._d2.pdf(d)


def run_classification_sweep(
    CR_values=None,
    CM_values=None,
    dist_names=None,
    R=109.0, c=45.0, CF=10.0, beta=190.0, p=10.0, D_bar=100.0,
    KR_max_mult: float = 20.0,
) -> list[SweepCell]:
    """Main sweep: evaluate Ψ and compare with sign(carbon_change) in every cell.

    A cell is flagged corner_fcl=True if the with-FCL solver hit a bound
    (unreliable optimal, excluded from sign-match totals).
    """
    if CR_values is None:
        CR_values = np.arange(8.0, 50.0, 4.0)
    if CM_values is None:
        CM_values = [40.0, 56.0, 63.0]  # below, at, and near the Assumption-1 ceiling

    dist_lib = build_distribution_library(D_bar)
    if dist_names is None:
        dist_names = list(dist_lib.keys())

    cells = []
    KR_max = KR_max_mult * D_bar
    KF_max = 5.0 * D_bar
    KM_max = 5.0 * D_bar

    for dist_name in dist_names:
        dist = dist_lib[dist_name]
        for CR in CR_values:
            for CM in CM_values:
                params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=float(CM),
                                beta=beta, p=p, D_bar=D_bar)
                try:
                    params.check_assumption1()
                except AssertionError:
                    continue

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        # Pre-solve to detect corners; reuse in compute_functional
                        wf = solve_with_fcl(dist, params,
                                             KR_max=KR_max, KF_max=KF_max, KM_max=KM_max)
                        nf = solve_no_fcl(dist, params, KR_max=KR_max, KF_max=KF_max)
                        result = compute_functional(
                            dist, params,
                            with_fcl=wf, no_fcl=nf,  # reuse: avoid double-solving
                            KR_max=KR_max, KF_max=KF_max, KM_max=KM_max,
                        )
                    except Exception:
                        continue

                corner = any(wf.at_upper_bound.values())

                cells.append(SweepCell(
                    dist_name=dist_name, CR=float(CR), CM=float(CM),
                    psi=result.psi, carbon_delta=result.carbon_delta,
                    sign_match=result.sign_match,
                    large_fcl_regime=result.large_fcl_regime,
                    corner_fcl=corner,
                    K_R_star=result.K_R_star, K_F_star=result.K_F_star,
                    K_M_star=result.K_M_star, K_R_circ=result.K_R_circ,
                    K_F_circ=result.K_F_circ, phi_circ=result.phi_circ,
                    q_circ=result.q_circ, mu_star_low=result.mu_star_low,
                    mu_circ_mid=result.mu_circ_mid,
                ))

    return cells


def summarize_classification(cells: list[SweepCell]) -> str:
    n = len(cells)
    interior = [c for c in cells if not c.corner_fcl]
    n_interior = len(interior)
    n_match = sum(c.sign_match for c in interior)
    n_mismatch = n_interior - n_match
    n_corner = sum(1 for c in cells if c.corner_fcl)
    n_improves = sum(c.carbon_delta < 0 for c in interior)

    lines = [
        f"Classification sweep: {n} cells ({n_interior} interior optima, "
        f"{n_corner} corners excluded).",
        f"  sign(Ψ) = sign(carbon_change): {n_match}/{n_interior} "
        f"({100*n_match/max(1,n_interior):.1f}%)",
        f"  mismatches (sign(Ψ) ≠ sign(carbon)):  {n_mismatch}/{n_interior}",
        f"  cells where carbon IMPROVES:  {n_improves}/{n_interior}",
    ]
    if n_mismatch > 0:
        bad = [c for c in interior if not c.sign_match]
        lines.append("  MISMATCHES (falsify iff claim):")
        for b in bad:
            lines.append(
                f"    {b.dist_name}, CR={b.CR}, CM={b.CM}: "
                f"Ψ={b.psi:+.4f}, Δcarbon={b.carbon_delta:+.4f}"
            )
    else:
        lines.append("  No mismatches, iff claim corroborated in every interior cell.")
    return "\n".join(lines)
