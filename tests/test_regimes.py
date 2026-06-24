"""Bullet 3: regime boundaries fit one consistent statement."""
import pytest
from role4.params import Params
from role4 import regimes as rg


def test_coverage_thresholds_strictly_ordered(P):
    assert rg.thresholds_ordered(P)               # C_M^fc < C̄_M < C̄_M^b
    assert rg.C_M_fc(P) < rg.C_M_bar(P) < rg.C_M_bar_b_eq62(P)


def test_boundedness_regime_in_carbon_window(P):
    assert rg.C_R_circ(P) < P.CR < rg.C_R_dagger(P)
    assert rg.boundedness_regime(P) == "withfcl_unbounded"


def test_full_coverage_when_CM_small():
    # push C_M below R-c-C_F -> full coverage (p25 digression)
    P = Params(R=2.4, c=1.0, CF=1.0, CR=0.6, CM=0.3, beta=1.5, p=2.0, D_bar=100.0)
    assert P.CM <= rg.C_M_fc(P)
    assert rg.coverage_regime(P) == "full_coverage"


@pytest.mark.slow
def test_carbon_crossover_exceeds_nofcl_scale(P):
    kr = rg.carbon_crossover_KR(P)
    assert kr is not None and kr > 100.0


@pytest.mark.slow
def test_reconciliation_rises_then_falls(P):
    from role4.reconcile import carbon_vs_buildout, decompose
    out = carbon_vs_buildout(P)
    d = [r["carbon_minus_nofcl"] for r in out["rows"]]
    assert d[0] > 0 and d[-1] < 0
    dec = decompose(P, 100.0)
    assert dec["utilization_effect"] > 0 and dec["capacity_effect"] < 0
