"""
Week 3 Task 3: carbon phase diagram and characterization theorem validation.

Sweeps across a distribution library and cost-parameter grid, classifying
each cell into one of three regions:

    "carbon_up"      : carbon(with-FCL contract) > carbon(no-FCL)
    "carbon_neutral" : carbon(with-FCL contract) ≈ carbon(no-FCL)  [< 0.1% diff]
    "carbon_down"    : carbon(with-FCL contract) < carbon(no-FCL)  [the FLIP]

Two comparison types are reported side-by-side:
    "greedy": firm-optimal dispatch (the Week 1/2 result) vs no-FCL
    "contract": carbon-optimal dispatch vs no-FCL  (the new Week 3 question)

If "contract" ever shows "carbon_down" where "greedy" shows "carbon_up", that
is a CARBON SIGN FLIP -- the optimal contract achieves what the myopic rule
cannot. This is the keystone Week 3 result.

CONTEXT3's note: Role 1's carbon functional is the quantity we minimize.
From first principles it equals c * E[fossil(x̃, d(x̃); K_F)], which is
exactly what solve_carbon_optimal_dispatch minimizes. The "characterization
theorem" is the claim that the sign of Δ(carbon) = carbon(with-FCL) - carbon(no-FCL)
is determined by a specific functional of the distribution F. We validate this
empirically by sweeping F and checking whether the sign prediction from any
candidate statistic (shift-ratio condition, skewness, tail parameters) is
consistent with the sign of Δ.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .contract_solver import solve_joint_carbon_optimal
from .distributions import (
    PowerResidual,
    PrimitiveResidual,
    ResidualDemand,
    TruncatedLognormal,
    UniformResidual,
    lognormal_primitive,
)
from .model import Params
from .solver import solve_no_fcl, solve_with_fcl


# Tolerance below which we call the carbon change "neutral" (0.1%)
NEUTRAL_TOL = 0.001


@dataclass
class PhaseDiagramCell:
    dist_name: str
    CR: float
    CM: float
    outcome_greedy: str     # "carbon_up" / "carbon_neutral" / "carbon_down"
    outcome_contract: str
    delta_greedy: float     # carbon_greedy - carbon_no_fcl  (positive = worse)
    delta_contract: float   # carbon_contract - carbon_no_fcl
    sign_flip: bool         # contract < no_fcl AND greedy ≥ no_fcl
    carbon_no_fcl: float
    carbon_greedy: float
    carbon_contract: float


def _classify(delta: float, ref: float) -> str:
    if ref < 1e-9:
        return "carbon_neutral"
    rel = delta / ref
    if rel > NEUTRAL_TOL:
        return "carbon_up"
    if rel < -NEUTRAL_TOL:
        return "carbon_down"
    return "carbon_neutral"


def build_distribution_library(D_bar: float = 100.0) -> dict:
    """Standard distribution library for the characterization sweep.

    Includes: uniform, power-law (alpha=0.5 right-skew, 2.0 left-skew),
    lognormal-primitive (four sigma values), and Beta-based primitives.
    """
    from scipy import stats
    lib = {
        "uniform": UniformResidual(D_bar),
        "power_right_0.5": PowerResidual(D_bar, alpha=0.5),
        "power_left_2.0": PowerResidual(D_bar, alpha=2.0),
        "lognormal_sigma0.2": lognormal_primitive(D_bar, sigma=0.20),
        "lognormal_sigma0.28": lognormal_primitive(D_bar, sigma=0.28),
        "lognormal_sigma0.4": lognormal_primitive(D_bar, sigma=0.40),
        "lognormal_sigma0.6": lognormal_primitive(D_bar, sigma=0.60),
        "beta_symmetric": PrimitiveResidual(
            D_bar, D_dist=stats.beta(2, 2, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2),
        ),
        "beta_right_skew": PrimitiveResidual(
            D_bar, D_dist=stats.beta(1.5, 4, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2),
        ),
        "beta_left_skew": PrimitiveResidual(
            D_bar, D_dist=stats.beta(4, 1.5, loc=0, scale=D_bar),
            S_dist=stats.beta(2, 2),
        ),
    }
    return lib


def run_dispatch_phase_sweep(
    CR_values=None,
    CM_values=None,
    dist_names=None,
    R=109.0, c=45.0, CF=10.0, beta=190.0, p=10.0, D_bar=100.0,
    N_inner: int = 300,
    KR_max_mult: float = 20.0,
) -> list[PhaseDiagramCell]:
    """Fast phase sweep: fixes capacities at firm-optimal, then compares
    greedy vs carbon-optimal DISPATCH at those same capacities.

    This answers a slightly simpler but still interesting question:
    "At the profit-maximizing capacities, does the carbon-optimal dispatch
    achieve lower carbon than the no-FCL benchmark?"

    Avoids the expensive outer capacity optimizer in run_phase_sweep, making
    this suitable for large parameter grids.
    """
    from .contract_solver import solve_carbon_optimal_dispatch, solve_firm_optimal_dispatch
    if CR_values is None:
        CR_values = np.arange(8.0, 42.0, 4.0)
    if CM_values is None:
        CM_values = [56.0]

    dist_lib = build_distribution_library(D_bar)
    if dist_names is None:
        dist_names = list(dist_lib.keys())

    cells = []
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

                KR_max = KR_max_mult * D_bar
                KF_max = 5.0 * D_bar
                KM_max = 5.0 * D_bar

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        no_fcl = solve_no_fcl(dist, params, KR_max=KR_max, KF_max=KF_max)
                        firm_cap = solve_with_fcl(dist, params, KR_max=KR_max,
                                                   KF_max=KF_max, KM_max=KM_max)
                        firm_dispatch = solve_firm_optimal_dispatch(
                            dist, params, firm_cap.K_R, firm_cap.K_F, firm_cap.K_M, N=N_inner
                        )
                        # Small epsilon relaxation avoids floating-point
                        # infeasibility when floor is set at the exact maximum
                        floor = firm_dispatch.profit_dispatch - 1e-4
                        co_dispatch = solve_carbon_optimal_dispatch(
                            dist, params, firm_cap.K_R, firm_cap.K_F, firm_cap.K_M,
                            profit_floor=floor, N=N_inner,
                        )
                        # If infeasible, fall back to firm-optimal dispatch
                        # (conservative: not a sign flip, just no improvement)
                        if 'Infeasible' in co_dispatch.lp_status:
                            co_dispatch = firm_dispatch
                    except Exception:
                        continue

                c_no_fcl = no_fcl.carbon
                c_greedy = firm_dispatch.carbon
                c_contract = co_dispatch.carbon

                delta_g = c_greedy - c_no_fcl
                delta_c = c_contract - c_no_fcl

                cells.append(PhaseDiagramCell(
                    dist_name=dist_name, CR=float(CR), CM=float(CM),
                    outcome_greedy=_classify(delta_g, c_no_fcl),
                    outcome_contract=_classify(delta_c, c_no_fcl),
                    delta_greedy=delta_g,
                    delta_contract=delta_c,
                    sign_flip=(delta_c < -NEUTRAL_TOL * c_no_fcl and delta_g >= 0),
                    carbon_no_fcl=c_no_fcl,
                    carbon_greedy=c_greedy,
                    carbon_contract=c_contract,
                ))
    return cells


def run_phase_sweep(
    CR_values=None,
    CM_values=None,
    dist_names=None,
    R=109.0, c=45.0, CF=10.0, beta=190.0, p=10.0, D_bar=100.0,
    N_inner: int = 200,
    KR_max_mult: float = 20.0,
) -> list[PhaseDiagramCell]:
    """Main sweep for the carbon phase diagram (Task 3).

    For each (distribution, C_R, C_M) combination, computes:
      - No-FCL benchmark carbon
      - Greedy-dispatch (firm-optimal) carbon
      - Carbon-optimal contract carbon

    and classifies the outcome.
    """
    if CR_values is None:
        CR_values = np.arange(8.0, 42.0, 4.0)
    if CM_values is None:
        CM_values = [40.0, 56.0]   # below and at the reference C_M

    dist_lib = build_distribution_library(D_bar)
    if dist_names is None:
        dist_names = list(dist_lib.keys())

    cells = []
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

                KR_max = KR_max_mult * D_bar
                KF_max = 5.0 * D_bar
                KM_max = 5.0 * D_bar

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        no_fcl = solve_no_fcl(dist, params, KR_max=KR_max, KF_max=KF_max)
                        firm = solve_with_fcl(dist, params, KR_max=KR_max,
                                               KF_max=KF_max, KM_max=KM_max)
                        joint = solve_joint_carbon_optimal(
                            dist, params, N_inner=N_inner,
                            KR_max=KR_max, KF_max=KF_max, KM_max=KM_max,
                        )
                    except Exception:
                        continue

                c_no_fcl = no_fcl.carbon
                c_greedy = firm.carbon
                c_contract = joint.carbon_contract

                delta_g = c_greedy - c_no_fcl
                delta_c = c_contract - c_no_fcl

                cells.append(PhaseDiagramCell(
                    dist_name=dist_name, CR=float(CR), CM=float(CM),
                    outcome_greedy=_classify(delta_g, c_no_fcl),
                    outcome_contract=_classify(delta_c, c_no_fcl),
                    delta_greedy=delta_g,
                    delta_contract=delta_c,
                    sign_flip=(delta_c < -NEUTRAL_TOL * c_no_fcl and delta_g >= 0),
                    carbon_no_fcl=c_no_fcl,
                    carbon_greedy=c_greedy,
                    carbon_contract=c_contract,
                ))

    return cells


def summarize_phase(cells: list[PhaseDiagramCell]) -> str:
    n = len(cells)
    n_flip = sum(c.sign_flip for c in cells)
    n_cdown = sum(c.outcome_contract == "carbon_down" for c in cells)
    n_gdown = sum(c.outcome_greedy == "carbon_down" for c in cells)

    lines = [
        f"Phase sweep: {n} (dist, C_R, C_M) cells.",
        f"  greedy carbon_down:   {n_gdown}/{n} ({100*n_gdown/n:.0f}%)",
        f"  contract carbon_down: {n_cdown}/{n} ({100*n_cdown/n:.0f}%)",
        f"  sign flips (contract flips greedy's carbon_up): {n_flip}/{n}",
    ]
    if n_flip > 0:
        flip_cells = [c for c in cells if c.sign_flip]
        lines.append("  SIGN FLIPS found:")
        for fc in flip_cells:
            lines.append(
                f"    {fc.dist_name}, C_R={fc.CR}, C_M={fc.CM}: "
                f"greedy={fc.delta_greedy:+.3f}, contract={fc.delta_contract:+.3f}"
            )
    else:
        lines.append("  No sign flips found in this sweep.")
    return "\n".join(lines)
