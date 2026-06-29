"""Week-2 Bullet 3: Assumption 1 necessity proofs (slack-monotone certificates)."""
import pytest
from role4 import necessity as nec


def test_all_four_hold_and_are_necessary(P):
    certs = nec.prove_all(P)
    for k in ("A1", "A2", "A3", "A4"):
        assert certs[k]["holds"], f"{k} should hold for the fixture"
        assert certs[k]["necessary"], f"{k} guarded quantity must cross boundary at slack 0"
    assert nec.all_necessary(P)


def test_guarded_quantity_at_boundary_equals_validity_edge(P):
    certs = nec.prove_all(P)
    # g(0) sits exactly on the validity edge: 1 for A1/A2 (RHS<1), 0 for A3/A4 (>0)
    assert certs["A1"]["boundary_value"] == 1.0
    assert certs["A2"]["boundary_value"] == 1.0
    assert certs["A3"]["boundary_value"] == 0.0
    assert certs["A4"]["boundary_value"] == 0.0


def test_monotone_direction_signs(P):
    certs = nec.prove_all(P)
    assert certs["A1"]["g_prime_sign"] == -1   # RHS falls below 1 as slack grows
    assert certs["A2"]["g_prime_sign"] == -1
    assert certs["A3"]["g_prime_sign"] == +1   # φ° rises above 0 as slack grows
    assert certs["A4"]["g_prime_sign"] == +1


def test_strict_vs_interior_only_asymmetry(P):
    s = nec.necessity_summary(P)
    assert set(s["strictly_necessary"]) == {"A1", "A3", "A4"}
    assert s["interior_only"] == ["A2"]
    assert "full-coverage" in s["relaxed_regimes"]["A2"]


def test_relaxing_pushes_guarded_value_out_of_range(P):
    # relaxing each condition to its boundary lands the guarded value on the edge
    A1b = P.with_(R=P.c + P.CM)            # slack 0
    assert nec.prove_A1(A1b)["guarded_value"] == pytest.approx(1.0)
    A3b = P.with_(beta=P.c + P.CF - P.p)   # β+p = c+C_F, slack 0
    assert nec.prove_A3(A3b)["guarded_value"] == pytest.approx(0.0)
