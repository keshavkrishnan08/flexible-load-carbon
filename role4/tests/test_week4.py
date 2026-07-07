"""Week-4 Role 4 acceptance tests: functional, hardening, regime map, reconcile."""
import pytest
from role4 import week4
from role4 import regime_phase as phase


def test_classification_functional_sign_matches_phase_label(P):
    assert week4.classification_functional(P) == pytest.approx(
        phase.carbon_boundary_C_R_dagger(P, P.CM) - P.CR
    )
    assert week4.classification_sign(P) == phase.carbon_sign(P, P.CM, P.CR)


def test_week4_bullet1_functional_stitches_across_regimes(P):
    out = week4.extend_functional_across_regimes(P)
    assert out["carbon_integral_continuous"]
    assert out["carbon_integral_C1"]
    assert out["classification_boundary_smooth"]
    assert out["regime_crossing_unique"]
    assert out["located_discontinuity"] == "profit_Hessian_only"
    assert out["profit_C1_not_C2"]
    assert out["curvature_jump"] == pytest.approx(out["predicted_jump"], rel=1e-2)


def test_week4_bullet2_converse_hardening_scaffold(P):
    out = week4.harden_converse(P)
    assert out["compact_iff_C_R_ge_C_R_dagger"]
    assert out["extremal_schedule_measurable"]
    assert out["screening_CQ"]
    assert out["ambiguity_set_convex"]
    assert out["delta_linear_in_law"]
    assert out["sion_saddle_when_compact"]
    assert out["ill_posed_on_carbon_window"]
    assert out["converse_tight_on_admissible_class"]


def test_week4_bullet3_regime_map_spans_both_regimes(P):
    out = week4.regime_map_classification(P)
    assert out["boundary_smooth_across_regime"]
    assert out["carbon_down_connected"]
    assert out["spans_both_regimes"]
    assert out["regime_crossing"]["unique_crossing"]
    assert out["curvature_positive"]
    order = out["ordering"]
    assert order["C_M_fc"] < order["C_M_cross"] < order["C_M_bar"] < order["C_M_bar_b"]


def test_week4_bullet4_reconciliation_flags_divergences(P):
    out = week4.reconcile_team(P)
    assert out["shared_objects_consistent"]
    assert out["contract_consistent"]
    assert out["carbon_functional_consistent"]
    assert out["robust_optimum_checked_or_flagged"]
    assert "robust_capacity_ill_posed_on_carbon_window" in out["divergences"]
