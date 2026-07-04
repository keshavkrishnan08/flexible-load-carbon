"""Bullet 2: measure-theoretic scaffolding — existence, measurability, IC/IR
constraint qualification, and the Sion minimax hypotheses for the ambiguity
set; Assumption 1 stress-tested against each."""
import pytest
from role4 import hardening as hd
from role4.params import Params


# (A) existence -------------------------------------------------------------

def test_box_compact_iff_C_R_ge_C_R_dagger(P):
    """The capacity box is compact (K_R face finite) exactly when the with-FCL
    program is bounded; the fixture (C_R in the carbon window) is NOT compact."""
    box = hd.capacity_box(P)
    # fixture C_R=0.5 < C_R†≈0.79 ⇒ carbon window ⇒ non-compact box
    assert not box["compact"]
    assert box["C_R"] < box["C_R_dagger"]
    # push C_R above C_R† ⇒ compact, and the optimum sits inside the box
    Pc = P.with_(CR=1.5)
    assert hd.box_compact(Pc)
    inb = hd.optimum_in_box(Pc)
    assert inb["compact"] and inb["exists_by_weierstrass"]


def test_assumption1_alone_insufficient_for_existence(P):
    """Assumption 1 holds at the fixture yet existence is NOT secured (box
    non-compact): the hardening verdict."""
    assert P.assumption1_holds()
    s = hd.assumption1_stress(P)
    assert s["existence_needs_more_than_A1"]
    assert not s["existence_secured"]          # because C_R < C_R† here


# (B) measurability ---------------------------------------------------------

def test_optimal_schedule_measurable_and_lipschitz(P):
    r = hd.optimal_schedule_measurable(P, K_F=70.0, K_M=20.0, K_R=40.0)
    assert r["borel_measurable"]
    assert r["one_lipschitz"]
    assert r["unique_served_maximizer"]


# (C) IC/IR constraint qualification ----------------------------------------

def test_screening_constraint_qualification(P):
    r = hd.screening_constraint_qualification(P)
    assert r["single_crossing_negative"]
    assert r["dispatch_monotone_global_IC"]     # global IC restored
    assert r["IR_binds_at_bottom"]
    assert r["rent_nonneg_and_rising"]
    assert r["first_order_approach_exact"]


# (D) Sion minimax ----------------------------------------------------------

def test_ambiguity_set_convex_and_Delta_linear(P):
    r = hd.ambiguity_set_convex(P)
    assert r["U_convex"]
    assert r["Delta_linear_in_F"]
    assert r["quasiconvex_and_quasiconcave_in_F"]


def test_minimax_saddle_where_box_compact(P):
    """Where the box is compact (C_R>=C_R†) the Sion saddle holds and the
    least-favorable distribution is the uniform (Role 1 Thm robust)."""
    Pc = P.with_(CR=1.5)
    r = hd.minimax_saddle(Pc)
    assert r["well_posed"]
    assert r["saddle"]
    assert r["least_favorable_is_uniform"]


def test_minimax_ill_posed_on_carbon_window(P):
    """On the carbon window the minimax is ill-posed (non-compact K_R): recorded
    honestly, not silently 'passed'."""
    r = hd.minimax_saddle(P)          # fixture is on the window
    assert not r["well_posed"]
    assert r["on_carbon_window"]
