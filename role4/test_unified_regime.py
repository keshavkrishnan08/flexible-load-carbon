"""Week-2 Bullet 2: the unified regime theorem + the K_M*=K_R° crossover."""
import math
import pytest
from role4.params import Params
from role4 import unified_regime as ur
from role4 import regimes as rg
from role4.small_fcl import C_M_bar_b_eq62
from role4.fcl_backend.model import Params as BP
from role4.fcl_backend.distributions import UniformResidual
from role4.fcl_backend import solver


def test_K_R_circ_matches_backend(P):
    bp = BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
    no = solver.solve_no_fcl(UniformResidual(P.D_bar), bp)
    assert ur.K_R_circ_uniform(P) == pytest.approx(no.K_R, rel=1e-4)


def test_crossover_closed_form_matches_numeric(P):
    # the closed-form crossover C_M equals the numerically located one
    cf = ur.C_M_cross_uniform(P)
    num = ur.crossover_KM_eq_KR0_numeric(P)
    assert cf == pytest.approx(num, rel=1e-3)


def test_at_crossover_KM_equals_KR0(P):
    # by construction, K_M*(C_M^cross) = K_R°
    cm = ur.C_M_cross_uniform(P)
    KR0 = ur.K_R_circ_uniform(P)
    assert ur.small_fcl_KM_at_base(P, cm) == pytest.approx(KR0, rel=1e-6)


def test_crossover_sits_inside_adoption_region(P):
    # the crossover is a genuine interior boundary, below the no-adoption edge
    assert ur.C_M_cross_uniform(P) < C_M_bar_b_eq62(P)


def test_fcl_scale_side_flips_across_crossover(P):
    cm = ur.C_M_cross_uniform(P)
    below = P.with_(CM=0.5 * cm)
    above = P.with_(CM=0.5 * (cm + C_M_bar_b_eq62(P)))
    assert ur.fcl_scale_side(below) == "large_fcl"
    assert ur.fcl_scale_side(above) == "small_fcl"


def test_unified_theorem_axes_consistent(P):
    out = ur.unified_theorem(P)
    assert out["axes_consistent"]
    assert out["coverage_ordered"]
    assert rg.C_R_circ(P) < rg.C_R_dagger(P)
    assert math.isfinite(out["C_M_cross"])
