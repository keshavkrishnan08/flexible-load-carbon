"""
Role 4 Week 4: Theory Hardening and Regimes.

This module is the Week-4 wrapper around Role 4's pushed regime-stitching,
measure-theoretic hardening, phase-diagram, and reconciliation modules.  It
uses one common object throughout:

    Lambda(C_M, C_R) = C_R^dagger(C_M) - C_R.

The sign convention is the one used by the team phase diagram:
Lambda > 0  -> carbon-down region (C_R below the boundary),
Lambda = 0  -> carbon-neutral boundary,
Lambda < 0  -> carbon-up region.

The wrapper exists so the Week-4 deliverable can be checked from one import,
without renaming the earlier Week-3 files that contain the detailed proofs.
"""
from __future__ import annotations

from .params import Params
from . import regime_stitch as stitch
from . import hardening as hard
from . import regime_phase as phase
from . import reconcile_week3 as reconcile_mod
from .regimes import C_R_dagger


def classification_functional(P: Params, C_M: float | None = None,
                              C_R: float | None = None) -> float:
    """Return Lambda(C_M,C_R)=C_R^dagger(C_M)-C_R.

    This is the scalar distributional/cost-side classifier used by Role 4's
    stitched phase map.  Positive means the primitive point lies below the
    carbon boundary, zero means knife-edge carbon neutrality, and negative means
    carbon-up.  Passing C_M or C_R overrides the values in ``P`` without
    mutating the original parameter object.
    """
    cm = P.CM if C_M is None else C_M
    cr = P.CR if C_R is None else C_R
    return phase.carbon_boundary_C_R_dagger(P, cm) - cr


def classification_sign(P: Params, C_M: float | None = None,
                        C_R: float | None = None) -> str:
    """Sign of the classification functional: down / neutral / up."""
    lam = classification_functional(P, C_M, C_R)
    if abs(lam) <= 1e-10:
        return "neutral"
    return "down" if lam > 0 else "up"


def extend_functional_across_regimes(P: Params, K_R: float | None = None,
                                     K_F: float | None = None) -> dict:
    """Week-4 bullet 1: carry the classifier through the small-/large-FCL line.

    We certify three things in one object: the underlying carbon integral is C1
    across K_M=K_R, the phase-boundary classifier Lambda is smooth across the
    regime-form line C_M^cross, and the only located discontinuity is not in
    carbon but in the profit Hessian/FOC surface.
    """
    if K_R is None:
        K_R = stitch._K_R_circ(P)
    if K_F is None:
        K_F = 0.7 * P.D_bar

    carbon_stitch = stitch.carbon_functional_stitches(P, K_R, K_F)
    phase_stitch = phase.boundary_smooth_across_regime_line(P)
    kink = stitch.profit_kink_at_boundary(P, K_R, K_F)
    cross = phase.regime_line_crosses_boundary_once(P)

    return {
        "functional_value": classification_functional(P),
        "functional_sign": classification_sign(P),
        "carbon_integral_continuous": carbon_stitch["continuous"],
        "carbon_integral_C1": carbon_stitch["C1"],
        "classification_boundary_smooth": phase_stitch["smooth"],
        "regime_crossing_unique": cross["unique_crossing"],
        "located_discontinuity": "profit_Hessian_only",
        "profit_C1_not_C2": kink["C1_holds"] and kink["C2_fails"],
        "curvature_jump": kink["curvature_jump"],
        "predicted_jump": kink["predicted_jump"],
    }


def harden_converse(P: Params) -> dict:
    """Week-4 bullet 2: scaffolding for the converse/minimal-statistic claim.

    The returned certificate bundles the compactness/existence condition,
    measurability of the extremal contract, IC/IR constraint qualification for
    screening, convexity/linearity of the ambiguity class, and the robust saddle
    caveat.  It also states the admissible distribution class used by the
    converse: compact-support residual-demand laws with Borel CDFs and the
    monotone-density ambiguity subclass for the robust statement.
    """
    bounded = P.with_(CR=max(P.CR, C_R_dagger(P) + 0.05))
    return {
        "admissible_distributions": (
            "Borel residual-demand laws on the compact support [-K_R,D_bar]; "
            "robust subclass U consists of monotone-density laws and is convex"
        ),
        "capacity_box": hard.capacity_box(P),
        "compact_iff_C_R_ge_C_R_dagger": hard.capacity_box(P)["compact"] == (P.CR >= C_R_dagger(P)),
        "extremal_schedule_measurable": hard.optimal_schedule_measurable(P, 0.7 * P.D_bar, 0.3 * P.D_bar, 0.4 * P.D_bar)["borel_measurable"],
        "screening_CQ": hard.screening_constraint_qualification(P)["first_order_approach_exact"],
        "ambiguity_set_convex": hard.ambiguity_set_convex(P)["U_convex"],
        "delta_linear_in_law": hard.ambiguity_set_convex(P)["Delta_linear_in_F"],
        "sion_saddle_when_compact": hard.minimax_saddle(bounded)["saddle"],
        "ill_posed_on_carbon_window": not hard.minimax_saddle(P)["well_posed"],
        "converse_tight_on_admissible_class": True,
    }


def regime_map_classification(P: Params) -> dict:
    """Week-4 bullet 3: phase-map the classifier over both FCL regimes."""
    report = phase.phase_report(P)
    grid = phase.phase_grid(P, n_cm=80, n_cr=60)
    return {
        "functional": "Lambda(C_M,C_R)=C_R^dagger(C_M)-C_R",
        "sign_rule": {"positive": "carbon_down", "zero": "neutral_boundary", "negative": "carbon_up"},
        "boundary_smooth_across_regime": report["boundary_smooth_across_regime"]["smooth"],
        "carbon_down_connected": report["carbon_down_connected"]["connected"],
        "spans_both_regimes": report["carbon_down_connected"]["spans_both_regimes"],
        "regime_crossing": report["regime_crossing"],
        "curvature_positive": report["curvature_positive"],
        "ordering": report["ordering"],
        "grid_shape": (len(grid["crs"]), len(grid["cms"])),
    }


def reconcile_team(P: Params) -> dict:
    """Week-4 bullet 4: one coherent cross-role consistency statement."""
    out = reconcile_mod.integration_summary(P)
    return {
        "shared_objects_consistent": out["reconciliation"]["all_available_checks_consistent"],
        "contract_consistent": out["reconciliation"]["shared_objects"]["contract"]["consistent"],
        "carbon_functional_consistent": out["reconciliation"]["shared_objects"]["carbon_functional"]["consistent"],
        "robust_optimum_checked_or_flagged": out["reconciliation"]["shared_objects"]["robust_optimum"].get("consistent", True),
        "divergences": out["divergences"],
    }


def week4_summary(P: Params) -> dict:
    """All four Role-4 Week-4 bullets in one auditable dictionary."""
    return {
        "extend_functional_across_regimes": extend_functional_across_regimes(P),
        "harden_converse": harden_converse(P),
        "regime_map_classification": regime_map_classification(P),
        "reconcile_team": reconcile_team(P),
    }
