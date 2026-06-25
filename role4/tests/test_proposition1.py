"""Bullet 1B: walk Prop 1's three steps; verify against the solver."""
import pytest
from role4 import proposition1 as prop


def test_step1_profit_gain_positive_iff_adoption(P):
    assert (prop.step1_profit_gain(P) > 0) == (P.CM < prop.C_M_bar(P))


def test_step2_blackout_falls_iff_adoption(P):
    assert (prop.step2_blackout_change(P) < 0) == (P.CM < prop.C_M_bar(P))
    # numerator carries the same sign
    assert (prop.step2_numerator(P) < 0) == (prop.step2_blackout_change(P) < 0)


def test_steps_match_backend(P):
    v = prop.verify_against_backend(P)
    assert v["analytic_profit_gain_sign"] == v["numeric_profit_gain_sign"]
    assert v["analytic_blackout_down"] == v["numeric_blackout_down"]
    assert v["utilization_raises_fossil"]   # Step 3 utilization effect > 0
