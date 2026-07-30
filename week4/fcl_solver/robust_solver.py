"""
Week 3 Task 2: distributionally-robust capacity and contract solver (stub).

STATUS: scaffolded with the moment-based ambiguity set as a default while
awaiting Role 1's exact ambiguity-set specification. The structure below
is correct and will be filled in once the spec arrives; Task 2 is
intentionally placed last in the build order precisely because it depends
on Role 1's inputs the most.

The robust problem:
    min_{K,d(·)} max_{F̃ ∈ Γ(F₀,ε)}  carbon(F̃; K, d(·))
    s.t.  min_{F̃ ∈ Γ(F₀,ε)}  profit(F̃; K, d(·)) ≥ floor

where Γ(F₀, ε) is an ambiguity set centered at nominal distribution F₀.

Default ambiguity set (moment-based, pending Role 1's spec):
    Γ = { F : |E_F[x] − μ₀| ≤ ε·σ₀, |Var_F[x] − σ₀²| ≤ ε·σ₀² }
         subject to F supported on [-K_R, D_bar]

This is implemented as a finite-grid search over perturbed distributions,
not the exact saddle-point characterization (which requires Role 1's closed
form).

TODOs when Role 1's spec arrives:
  - Replace moment-based Γ with the actual ambiguity set (KL-divergence,
    Wasserstein ball, or the paper's specific perturbation class)
  - Implement the closed-form least-favorable F for the power-law family
    (Role 1's Task: "characterize saddle, prove minimax equality")
  - Validate numerically: minimax ≈ maximin (saddle certificate)
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .distributions import ResidualDemand
from .model import Params


@dataclass
class RobustResult:
    """Result of a distributionally-robust capacity/contract solve."""
    K_R: float
    K_F: float
    K_M: float
    robust_carbon: float         # max_{F̃ ∈ Γ} carbon at the robust optimum
    nominal_carbon: float        # carbon at the nominal F
    ambiguity_radius: float
    least_favorable_F: object    # the F̃ that achieves the max (or None if not found)
    minimax_gap: float           # |minimax - maximin| / max(1, minimax)
    saddle_certified: bool
    note: str                    # documentation of what's stub vs. implemented


def perturb_distribution_moments(
    dist: ResidualDemand,
    K_R: float,
    epsilon: float,
    n_perturb: int = 8,
) -> list:
    """Generate a finite set of perturbed distributions in Γ(F₀, ε).

    Uses ε-shifts of the mean and variance parameters of the nominal F,
    implemented as scaled versions of the distribution. This is the
    STUB implementation -- the actual ambiguity set boundary depends on
    Role 1's specification.

    Returns a list of (perturbed_dist, weight_description) pairs.
    """
    # Placeholder: returns just the nominal distribution until spec arrives
    return [(dist, "nominal_only_stub")]


def solve_robust_capacity(
    dist: ResidualDemand,
    params: Params,
    ambiguity_radius: float = 0.05,
    N_inner: int = 200,
) -> RobustResult:
    """Stub: robust capacity solver, awaiting Role 1's ambiguity-set spec.

    Currently returns the nominal (non-robust) solution with a documented
    placeholder for the true robust solve. The minimax_gap will be NaN until
    the real inner maximization is implemented.
    """
    from .contract_solver import solve_joint_carbon_optimal
    from .solver import solve_with_fcl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nominal = solve_joint_carbon_optimal(dist, params, N_inner=N_inner)

    return RobustResult(
        K_R=nominal.K_R, K_F=nominal.K_F, K_M=nominal.K_M,
        robust_carbon=nominal.carbon_contract,
        nominal_carbon=nominal.carbon_no_fcl,
        ambiguity_radius=ambiguity_radius,
        least_favorable_F=None,
        minimax_gap=float("nan"),
        saddle_certified=False,
        note=(
            "STUB: returning nominal (non-robust) solution. "
            "Full robust solve pending Role 1's ambiguity-set specification "
            "(KL-divergence ball / Wasserstein / moment-based). "
            "See robust_solver.py module docstring for TODOs."
        ),
    )
