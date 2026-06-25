"""Bullet 1A: the FOC cutoffs (eqs 12,13,15) match Role 2's numerical solver."""
import pytest
from role4.params import Params
from role4 import foc
from role4.fcl_backend.model import Params as BP
from role4.fcl_backend.distributions import UniformResidual
from role4.fcl_backend import solver


def _bp(P): return BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)


def test_eq12_eq13_rhs_in_unit_interval(P):
    assert foc.eq12_rhs_in_unit_interval(P)
    assert foc.eq13_rhs_in_unit_interval(P)


def test_no_fcl_cutoff_matches_solver(P):
    """φ° = F(K_F°;K_R°) from the FOC equals the solver's realized CDF value."""
    dist = UniformResidual(P.D_bar)
    no = solver.solve_no_fcl(dist, _bp(P))
    F_val = dist.cdf(no.K_F, no.K_R)
    assert F_val == pytest.approx(foc.phi_circ(P), rel=1e-4)


def test_with_fcl_cutoffs_match_solver(P):
    """eqs 12 & 13: F(K_F*-K_M*) and F(K_F*) match the solver at fixed K_R."""
    dist = UniformResidual(P.D_bar)
    no = solver.solve_no_fcl(dist, _bp(P))
    r = solver.solve_with_fcl_given_KR(dist, _bp(P), no.K_R)
    assert dist.cdf(r.K_F - r.K_M, no.K_R) == pytest.approx(foc.cutoff_KM_eq12(P), rel=1e-3)
    assert dist.cdf(r.K_F, no.K_R) == pytest.approx(foc.cutoff_KF_eq13(P), rel=1e-3)


def test_KM_nonneg_iff_adoption(P):
    assert foc.KM_nonneg_iff_adoption(P) == (P.CM <= foc.C_M_bar(P))
