"""Bullet 4: cross-role reconciliation of the shared objects (contract, carbon
functional, robust optimum), with divergences flagged."""
import pytest
from role4 import reconcile_week3 as rc


def test_contract_matches_backend_across_regimes(P):
    """Role 4's regime-free d* == Role 2's backend dispatch, pointwise across
    both FCL regimes."""
    r = rc.contract_consistent(P)
    assert r["consistent"]
    assert r["max_pointwise_deviation"] < 1e-9


def test_carbon_functional_matches_backend(P):
    """Role 4's trapezoid E[fossil] == Role 2's quadrature backend, in both
    regimes."""
    r = rc.carbon_functional_consistent(P)
    assert r["consistent"]
    assert r["max_rel_error"] < 1e-4


def test_robust_optimum_consistent_or_flagged(P):
    """On the carbon window the robust capacity problem is ill-posed; Role 4 and
    Role 1 agree on that (consistent where defined) and it is flagged."""
    r = rc.robust_optimum_consistent(P)
    assert r["consistent_where_defined"] or r.get("consistent")
    # push above C_R† ⇒ well-posed saddle, least-favorable = uniform
    Pc = P.with_(CR=1.5)
    r2 = rc.robust_optimum_consistent(Pc)
    assert r2["well_posed"] and r2["consistent"]


def test_reconcile_all_available_checks_consistent(P):
    r = rc.reconcile(P)
    assert r["all_available_checks_consistent"]
    assert r["stitch_supports_agreement"]["carbon_functional_C1_across_boundary"]
    assert r["stitch_supports_agreement"]["phase_boundary_smooth_across_regime"]


def test_divergences_flagged(P):
    """The three honest flags are present, and the ill-posed-robust flag is
    active on the fixture (carbon window)."""
    d = rc.divergences(P)
    assert d["robust_capacity_ill_posed_on_carbon_window"]["active_here"]
    assert "general_F_step3_still_conditional" in d
    assert "awaiting_roles_2_3_week3_push" in d
