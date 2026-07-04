"""Bullet 3: the stitched carbon phase diagram over the full cost plane — one
connected carbon-down region spanning both FCL regimes, smooth boundary crossed
once by the regime-form line."""
import pytest
from role4 import regime_phase as rp


def test_boundary_convex_in_C_M(P):
    """C_R†(C_M) is a convex parabola: d²C_R†/dC_M² = 1/(R-c)+1/(β+p-R) > 0."""
    assert rp.carbon_boundary_curvature(P) > 0
    assert rp.carbon_boundary_curvature(P) == pytest.approx(
        1.0 / (P.R - P.c) + 1.0 / (P.bp - P.R))


def test_boundary_smooth_across_regime_line(P):
    """The carbon boundary is smooth across the regime-form line C_M^cross — one
    quadratic, no kink — even though the FOC surface kinks (Bullet 1)."""
    r = rp.boundary_smooth_across_regime_line(P)
    assert r["smooth"]
    assert r["deriv_numeric"] == pytest.approx(r["deriv_closed_form"], abs=1e-4)


def test_carbon_down_region_connected_spans_both_regimes(P):
    """{C_R < C_R†(C_M)} is connected (continuous boundary), spans both FCL
    regimes (regime line inside the band), and its boundary is convex (U-shaped)
    with the carbon-window minimum at C̄_M."""
    r = rp.carbon_down_region_connected(P)
    assert r["connected"]
    assert r["spans_both_regimes"]
    assert r["boundary_convex"]
    assert r["boundary_min_at_C_M"] == pytest.approx(rp.C_M_bar(P), abs=5e-3)


def test_regime_line_crosses_boundary_once(P):
    r = rp.regime_line_crosses_boundary_once(P)
    assert r["unique_crossing"]
    assert r["crossing_C_R"] == pytest.approx(
        rp.carbon_boundary_C_R_dagger(P, r["crossing_C_M"]))


def test_curve_ordering(P):
    """The cost-plane curves are ordered C_M^fc < C_M^cross < C̄_M < C̄_M^b: the
    regime-form line sits inside the interior/large-FCL adoption band."""
    rep = rp.phase_report(P)["ordering"]
    assert rep["C_M_fc"] < rep["C_M_cross"] < rep["C_M_bar"] < rep["C_M_bar_b"]


def test_phase_label_agrees_with_boundary(P):
    """A point just below/above C_R†(C_M) is labelled carbon down/up, and the
    contract-form label flips across C_M^cross."""
    cc = rp.C_M_cross(P)
    cr = rp.carbon_boundary_C_R_dagger(P, cc)
    assert rp.phase_label(P, cc, 0.5 * cr)["carbon"] == "down"
    assert rp.phase_label(P, cc, 1.5 * cr)["carbon"] == "up"
    assert rp.contract_form(P, 0.5 * cc) == "large_fcl"
    assert rp.contract_form(P, min(1.5 * cc, rp.adoption_edge(P) - 1e-6)) == "small_fcl"
