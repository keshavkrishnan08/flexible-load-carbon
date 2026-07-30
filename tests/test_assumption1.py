"""Bullet 4: each of the four conditions is necessary where claimed."""
import pytest
from role4 import assumption1 as a1


def test_all_four_hold_and_break_when_relaxed(P):
    st = a1.stress_test(P)
    for k in ("A1", "A2", "A3", "A4"):
        assert st[k]["holds"], f"{k} should hold for the fixture"
        assert st[k]["breaks_if_relaxed"], f"{k} should break at its boundary"
    assert a1.all_necessary(P)


def test_guarded_values_are_valid_when_conditions_hold(P):
    st = a1.stress_test(P)
    assert 0 < st["A1"]["guarded_value"] < 1     # eq12 RHS
    assert 0 < st["A2"]["guarded_value"] < 1     # eq13 RHS
    assert st["A3"]["guarded_value"] > 0         # phi_circ
    assert st["A4"]["guarded_value"] > 0         # β+p-R
