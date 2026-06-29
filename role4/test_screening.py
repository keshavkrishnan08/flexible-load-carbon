"""Week-2 Bullet 4: second-best screening under a private renewable factor."""
import pytest
from role4 import screening as scr


KM = 30.0


def test_second_best_under_dispatches(P):
    # d^SB(θ) ≤ d^FB(θ) everywhere (downward distortion)
    assert scr.downward_distortion(P, KM)


def test_uniform_half_distortion_closed_form(P):
    # Uniform[0,1]: interior d^SB(θ) = ½ d^FB(θ) (before the cap binds)
    for theta in (0.1, 0.3, 0.5):
        dfb = scr.first_best_dispatch(P, theta, KM)
        dsb = scr.second_best_dispatch(P, theta, KM)
        if dfb < KM - 1e-9:                     # interior (cap slack)
            assert dsb == pytest.approx(0.5 * dfb, rel=1e-6)


def test_dispatch_monotone_and_no_distortion_at_top(P):
    assert scr.dispatch_is_monotone(P, KM)      # IC (single crossing)
    assert scr.no_distortion_at_top(P, KM)      # cap/inverse-hazard at the top


def test_information_rent_nonneg_and_rising(P):
    r_lo = scr.information_rent(P, 0.2, KM)
    r_hi = scr.information_rent(P, 0.8, KM)
    assert r_lo >= 0.0 and r_hi >= r_lo         # rent ≥ 0, rises in type
    assert scr.expected_rent(P, KM) > 0.0       # strictly positive leaked rent


def test_utilization_effect_dampened(P):
    # less FCL dispatched ⇒ short-run carbon (fossil for FCL) lower under SB
    out = scr.emission_outcome(P, KM)
    assert out["dispatch_falls"]
    assert out["short_run_carbon_lower_SB"]


def test_effective_R_below_R_and_capacity_channel_weakens(P):
    assert scr.effective_R_capacity_channel(P, KM) < P.R
    assert scr.capacity_channel_weakens(P, KM)


@pytest.mark.slow
def test_carbon_window_shrinks_under_private_info(P):
    out = scr.carbon_window_full_vs_private(P, KM)
    assert out["R_eff"] < out["R"]
    assert out["window_shrinks"]                # C_R†(R_eff) < C_R†(R)
