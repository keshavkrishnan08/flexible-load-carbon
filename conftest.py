"""
Demand-response program shape (eq. 69) and the emissions survival check.

The emissions test is a regression guard on compare()'s qualitative output,
not a tight numeric assertion -- mirrors Role 2's sweep regression style.
"""
import pytest

from miner_demand.demand_response import adapted_program, clean_program
from miner_demand.emissions import compare


def test_clean_program_surplus_and_shortfall():
    # surplus: mining = exactly the surplus
    assert clean_program(D=10, S=0.5, k=40, delta=0.0) == pytest.approx(0.5 * 40 - 10)
    # shortfall: mining = delta floor
    assert clean_program(D=30, S=0.5, k=40, delta=2.0) == 2.0


def test_adapted_program_clips_surplus_at_nR_over_2Po():
    R, n, Po = 1000.0, 5, 4.0
    clip = n * R / (2 * Po)  # = 625
    # huge surplus gets clipped to the cap, not the full surplus
    d = adapted_program(D=0, S=1.0, k=10_000, R=R, n=n, Po=Po)
    assert d == pytest.approx(clip)
    # modest surplus below the cap passes through unclipped
    d2 = adapted_program(D=10, S=0.5, k=40, R=R, n=n, Po=Po)
    assert d2 == pytest.approx(0.5 * 40 - 10)


def test_emissions_compare_runs_and_is_self_consistent(emi):
    out = compare(emi, d_floor=0.0)
    assert out["emission_no_mining"] > 0
    assert out["emission_with_mining"] >= 0
    # carbon_lower flag must agree with the sign of the % change
    if out["carbon_lower"]:
        assert out["carbon_pct_change"] < 0
    else:
        assert out["carbon_pct_change"] >= -1e-9
