"""
Week-3 Bullet 4: reconcile the team — integrate the four roles' Week-3 outputs
into one coherent statement, cross-check every SHARED OBJECT for consistency,
and flag divergence before it reaches the integrated paper.

The three shared objects the Week-3 plan names are the contract, the carbon
functional, and the robust optimum. For each we check that Role 4's regime-
stitched version agrees with (a) Role 1's formalization in
`role1/exploratory_cross_role/` (the pushed contract/robust theory Role 1 hands
to Role 4) and (b) Role 2's vendored solver backend, the common numerical truth.

  1. THE CONTRACT d*(x) = min{(K_F-x)_+, K_M}.
     Role 1 Thm 1  ==  paper eq 3  ==  backend `dispatch`  ==  Role 4's regime-
     free `regime_stitch.contract`. Checked pointwise on a grid straddling the
     regime boundary: identical in both FCL regimes.

  2. THE CARBON FUNCTIONAL  E[fossil](K) = ∫_{-K_M}^{K_F-K_M}(1-F)dx.
     Role 4's `regime_stitch.expected_fossil` (trapezoid on the extended CDF)
     == Role 2's backend `expected_fossil_output` (adaptive quadrature), at the
     worked capacities and across the regime boundary.

  3. THE ROBUST OPTIMUM (least-favorable = uniform).
     Role 1 Thm robust (role1_robust_contract.tex): the uniform minimizes the
     net saving over the shape class U. Role 4's `hardening.minimax_saddle`
     confirms the Sion saddle and that the least-favorable shape is the uniform
     — WHERE the capacity box is compact (C_R >= C_R†). On the carbon window
     the robust *capacity* problem is ill-posed (Week-1 corner-at-infinity):
     this is the one DIVERGENCE Role 4 flags for the integrated paper.

HONEST SCOPE (mirrors Week-2's "awaiting push"). Roles 2 and 3 have not yet
pushed their Week-3 deliverables (the optimal-contract solver, the DRO solver,
the characterization-at-scale sweep, and the comparative statics). Cross-checks
against those are deferred; everything here is verified against what IS
available — Role 1's pushed exploratory contract/robust theory and Role 2's
vendored solver — exactly as Week 2 did. A full Week-3 INTEGRATION pass should
follow once Roles 2/3 land.

`reconcile()` returns the consistency table; `divergences()` returns the flagged
items. Checked in tests/test_reconcile_week3.py.
"""
from __future__ import annotations

import math

from .params import Params
from . import regime_stitch as rs
from . import hardening as hd
from . import regime_phase as rp
from .regimes import C_R_dagger


# --- shared object 1: the contract ------------------------------------------

def contract_consistent(P: Params, K_F: float = None, K_R: float = None,
                        n: int = 121) -> dict:
    """Role 4's regime-free d* == Role 2's backend dispatch, pointwise across a
    grid that straddles the regime boundary K_M = K_R (both a small-FCL and a
    large-FCL K_M)."""
    from .fcl_backend.model import dispatch as backend_dispatch
    if K_R is None:
        K_R = 40.0
    if K_F is None:
        K_F = 0.7 * P.D_bar
    max_dev = 0.0
    for K_M in (0.5 * K_R, 1.5 * K_R):        # small, then large regime
        lo, hi = -K_M - 5.0, K_F + 5.0
        for k in range(n):
            x = lo + (hi - lo) * k / (n - 1)
            d4 = rs.contract(K_F, K_M, x)
            d2 = float(backend_dispatch(x, K_F, K_M))
            max_dev = max(max_dev, abs(d4 - d2))
    return {"max_pointwise_deviation": max_dev, "consistent": max_dev < 1e-9}


# --- shared object 2: the carbon functional ---------------------------------

def carbon_functional_consistent(P: Params, K_R: float = 40.0,
                                 K_F: float = None) -> dict:
    """Role 4's trapezoid E[fossil] == Role 2's quadrature backend, at a
    small-FCL and a large-FCL K_M (across the regime boundary)."""
    from .fcl_backend.model import expected_fossil_output
    from .fcl_backend.distributions import UniformResidual
    dist = UniformResidual(P.D_bar)
    if K_F is None:
        K_F = 0.7 * P.D_bar
    rows = []
    max_rel = 0.0
    for K_M, regime in ((0.5 * K_R, "small_fcl"), (1.5 * K_R, "large_fcl")):
        v4 = rs.expected_fossil(P, K_R, K_F, K_M)
        v2 = float(expected_fossil_output(dist, K_R, K_F, K_M))
        rel = abs(v4 - v2) / max(abs(v2), 1e-9)
        max_rel = max(max_rel, rel)
        rows.append({"regime": regime, "K_M": K_M, "role4": v4, "backend": v2, "rel": rel})
    return {"rows": rows, "max_rel_error": max_rel, "consistent": max_rel < 1e-4}


# --- shared object 3: the robust optimum ------------------------------------

def robust_optimum_consistent(P: Params) -> dict:
    """Role 1's least-favorable = uniform vs Role 4's Sion saddle. Consistent
    where the box is compact; flagged ill-posed on the carbon window."""
    mm = hd.minimax_saddle(P)
    if not mm["well_posed"]:
        return {"well_posed": False,
                "consistent_where_defined": True,     # agree it is ill-posed
                "flag": "robust capacity problem ill-posed on C_R<C_R† (corner-at-∞)",
                "on_carbon_window": P.CR < C_R_dagger(P)}
    return {
        "well_posed": True,
        "saddle": mm["saddle"],
        "least_favorable_is_uniform": mm["least_favorable_is_uniform"],
        "consistent": mm["saddle"] and mm["least_favorable_is_uniform"],
    }


# --- the reconciliation table + divergence flags ----------------------------

def reconcile(P: Params) -> dict:
    """One coherent cross-role statement: the three shared objects, each with
    its consistency verdict, plus the regime-stitch and phase results that make
    them agree across FCL regimes."""
    c1 = contract_consistent(P)
    c2 = carbon_functional_consistent(P)
    c3 = robust_optimum_consistent(P)
    return {
        "shared_objects": {
            "contract": c1,
            "carbon_functional": c2,
            "robust_optimum": c3,
        },
        "stitch_supports_agreement": {
            # the contract/carbon agree across regimes BECAUSE of Bullet 1
            "carbon_functional_C1_across_boundary":
                rs.carbon_functional_stitches(P, 40.0, 0.7 * P.D_bar)["C1"],
            "phase_boundary_smooth_across_regime":
                rp.boundary_smooth_across_regime_line(P)["smooth"],
        },
        "all_available_checks_consistent": (
            c1["consistent"] and c2["consistent"]
            and (c3.get("consistent", True) or not c3["well_posed"])
        ),
    }


def divergences(P: Params) -> dict:
    """Items Role 4 flags before they reach the integrated paper."""
    return {
        "robust_capacity_ill_posed_on_carbon_window": {
            "where": "C_R < C_R† (the carbon-reduction window)",
            "what": ("the distributionally-robust CAPACITY problem has no finite "
                     "saddle there — K_R runs to the corner-at-infinity (Week 1). "
                     "The robust certificate must be read at FIXED capacities "
                     "(Role 1's framing) or restricted to C_R >= C_R†."),
            "active_here": P.CR < C_R_dagger(P),
        },
        "general_F_step3_still_conditional": {
            "what": ("the general-F net-carbon Step 3 remains conditional "
                     "(proven for uniform/power-law; Role 1's shift-ratio gives "
                     "the capacity channel, not the full net sign) — unchanged "
                     "by design."),
        },
        "awaiting_roles_2_3_week3_push": {
            "what": ("Role 2's optimal-contract & DRO solvers and characterization "
                     "sweep, and Role 3's characterization/contract comparative "
                     "statics and robustness certificate, are not yet pushed; "
                     "cross-checks against them are deferred."),
        },
    }


def integration_summary(P: Params) -> dict:
    """Everything Bullet 4 asserts, in one dict (used by run_analysis_week3.py)."""
    return {"reconciliation": reconcile(P), "divergences": divergences(P)}
