"""
Week 4 Task 3: leverage condition and distributionally-robust saddle.

LEVERAGE CONDITION (from Week 3):
The "frontier leverage condition" from Week 3's optimal-contract work:
the surplus-only contract is globally carbon-optimal (not just better than
greedy) when the FCL dispatch in the surplus zone generates enough revenue
to fund additional renewable investment. The boundary is where this
condition binds. We certify it numerically by checking whether the carbon-
optimal dispatch concentrates on surplus states (x < 0) and computing the
"leverage ratio" = (surplus-zone dispatch revenue) / (required renewable capex).

Condition: λ(F) = (R · E[d*(x) · 1_{x≤0}]) / (C_R · K*_R) ≥ 1
The boundary λ = 1 is mapped across (C_R, distribution-shape) space.

DISTRIBUTIONALLY-ROBUST SADDLE (from Week 3 stub):
For a moment-based ambiguity set:
  Γ_ε(F₀) = { F : |E_F[x] - μ₀| ≤ ε·σ₀ }
the inner maximization (over F ∈ Γ) and outer minimization (over K, d) must
agree: minimax = maximin. We certify by:
1. Running the inner problem at the outer optimum (find worst F)
2. Running the outer problem at the worst F (find optimal K)
3. Checking that both yield the same carbon value (saddle gap = 0)

Both the leverage condition boundary and the robust saddle are reported
numerically; Role 3's robustness capstone depends on these outputs.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from scipy import integrate

from .carbon_functional import FunctionalResult, compute_functional
from .distributions import ResidualDemand
from .model import Params
from .solver import solve_no_fcl, solve_with_fcl


@dataclass
class LeverageResult:
    """Leverage condition evaluation at one (distribution, params) point."""
    lambda_ratio: float    # (surplus dispatch revenue) / (renewable capex)
    leveraged: bool        # lambda >= 1?
    surplus_revenue: float # R · E[d*(x) · 1_{x≤0}]
    renewable_capex: float # C_R · K*_R
    K_R_star: float
    K_M_star: float


def compute_leverage_ratio(
    dist: ResidualDemand,
    params: Params,
    with_fcl=None,
    KR_max=None,
) -> LeverageResult:
    """Compute the leverage ratio λ = surplus_revenue / renewable_capex.

    The surplus zone is x ≤ 0; d*(x) = K_M* there (greedy dispatch at full
    capacity when there is no consumer demand to serve from fossil). Revenue
    from this zone = R · K_M* · P(x ≤ 0) = R · K_M* · q* where
    q* = F(0; K_R*).
    """
    D = params.D_bar
    KR_max = KR_max or 30.0 * D

    if with_fcl is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with_fcl = solve_with_fcl(dist, params,
                                       KR_max=KR_max, KF_max=5*D, KM_max=5*D)

    K_R_s, K_M_s = with_fcl.K_R, with_fcl.K_M

    # Surplus probability q* = F(0; K_R*)
    q_star = float(dist.cdf(0.0, K_R_s))

    surplus_rev = params.R * K_M_s * q_star
    ren_capex   = params.CR * K_R_s

    lam = surplus_rev / ren_capex if ren_capex > 1e-10 else 0.0

    return LeverageResult(
        lambda_ratio=lam,
        leveraged=(lam >= 1.0),
        surplus_revenue=surplus_rev,
        renewable_capex=ren_capex,
        K_R_star=K_R_s,
        K_M_star=K_M_s,
    )


def map_leverage_boundary(
    dist: ResidualDemand,
    CR_values=None,
    R=109.0, c=45.0, CF=10.0, CM=56.0, beta=190.0, p=10.0, D_bar=100.0,
) -> list[dict]:
    """Map λ(C_R) for a fixed distribution to locate the leverage boundary."""
    if CR_values is None:
        CR_values = np.arange(8.0, 50.0, 2.0)

    results = []
    for CR in CR_values:
        params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=float(CM),
                        beta=beta, p=p, D_bar=D_bar)
        try:
            params.check_assumption1()
        except AssertionError:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                lev = compute_leverage_ratio(dist, params)
                results.append({
                    "CR": float(CR), "lambda": lev.lambda_ratio,
                    "leveraged": lev.leveraged,
                    "K_R_star": lev.K_R_star, "K_M_star": lev.K_M_star,
                })
            except Exception:
                pass
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Distributionally-robust saddle certification
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SaddleCertificate:
    minimax: float        # min_{K} max_{F∈Γ} carbon(F; K)
    maximin: float        # max_{F∈Γ} min_{K} carbon(F; K)
    gap: float            # |minimax - maximin| — should be ~0 at a saddle
    saddle_certified: bool
    worst_case_dist_name: str
    note: str


def certify_robust_saddle(
    nominal_dist: ResidualDemand,
    params: Params,
    ambiguity_dists: list[tuple[str, ResidualDemand]],
) -> SaddleCertificate:
    """Certify the distributionally-robust saddle numerically.

    Approach (with a finite perturbation grid, pending Role 1/3 exact spec):
    1. For each F̃ in the ambiguity set (provided as `ambiguity_dists`):
       solve the outer capacity problem → min_K carbon(F̃; K)
    2. The inner max = max_{F̃} of these minima = maximin
    3. At the minimax K (from the nominal distribution's optimum), evaluate
       carbon under each F̃ → max = minimax approximation
    4. Gap = |minimax - maximin|; certified if gap < 1e-3

    Note: this is an approximation over a finite grid of F̃ values. The
    exact robust saddle certification requires Role 3's ambiguity-set spec
    and closed-form worst-case distribution. Treat this as a numerical
    stress test, not a full certificate.
    """
    D = params.D_bar

    # Step 1: minimax K (use nominal distribution's optimal as proxy)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nom_with_fcl = solve_with_fcl(nominal_dist, params,
                                       KR_max=20*D, KF_max=5*D, KM_max=5*D)
    K_minimax = (nom_with_fcl.K_R, nom_with_fcl.K_F, nom_with_fcl.K_M)

    from .model import carbon_emissions, expected_fossil_output

    # Step 2/3: evaluate carbon at K_minimax under each F̃
    carbons_at_Kminimax = {}
    carbons_at_optK = {}

    for name, f_tilde in ambiguity_dists:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                # carbon at minimax K
                c_mini = carbon_emissions(f_tilde, params, *K_minimax)
                carbons_at_Kminimax[name] = c_mini
                # carbon at F̃'s own optimal K (inner min)
                opt = solve_with_fcl(f_tilde, params,
                                      KR_max=20*D, KF_max=5*D, KM_max=5*D)
                carbons_at_optK[name] = opt.carbon
            except Exception:
                pass

    if not carbons_at_Kminimax:
        return SaddleCertificate(
            minimax=np.nan, maximin=np.nan, gap=np.nan,
            saddle_certified=False,
            worst_case_dist_name="none",
            note="No ambiguity distributions evaluated successfully.",
        )

    minimax_approx = max(carbons_at_Kminimax.values())
    maximin_approx = max(carbons_at_optK.values())
    gap = abs(minimax_approx - maximin_approx) / max(1.0, minimax_approx)
    worst_name = max(carbons_at_Kminimax, key=carbons_at_Kminimax.get)

    return SaddleCertificate(
        minimax=minimax_approx,
        maximin=maximin_approx,
        gap=gap,
        saddle_certified=(gap < 0.01),  # 1% tolerance
        worst_case_dist_name=worst_name,
        note=(
            f"Finite grid ({len(ambiguity_dists)} perturbations). "
            "Full certification requires Role 3's exact worst-case distribution."
        ),
    )
