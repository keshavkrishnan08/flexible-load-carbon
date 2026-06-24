"""
Regime classification + the theory-vs-numerics reconciliation (the headline).
The reconciliation runs Role 2's actual solver, so it's a bit slower.
"""
import pytest

from regimes.thresholds import Params
from regimes.regime_map import (
    boundedness_regime, coverage_regime, carbon_crossover_KR, classify,
)
from regimes.reconcile import carbon_vs_buildout, decompose


@pytest.fixture
def P():
    return Params(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.5, beta=1.0, p=2.0, D_bar=100.0)


def test_regime_labels(P):
    assert boundedness_regime(P) == "withfcl_unbounded"   # the carbon regime
    assert coverage_regime(P) in {"interior_small_fcl", "full_coverage"}


def test_carbon_crossover_exists_and_exceeds_nofcl_scale(P):
    """Carbon crosses below the benchmark only at buildout >> no-FCL scale."""
    kr_cross = carbon_crossover_KR(P)
    assert kr_cross is not None
    # no-FCL optimum K_R ~ 41.4; the crossover must be well above it
    assert kr_cross > 100.0


def test_classify_has_all_fields(P):
    out = classify(P)
    for key in ("C_R_circ", "C_R_dagger", "boundedness_regime",
                "coverage_regime", "carbon_crossover_KR"):
        assert key in out


@pytest.mark.slow
def test_reconciliation_carbon_rises_then_falls(P):
    """The crux: with Role 2's solver, carbon RISES at modest buildout
    (utilization effect, their 0/210) and FALLS at large buildout
    (capacity-substitution, Role 1's claim)."""
    out = carbon_vs_buildout(P)
    deltas = [r["carbon_minus_nofcl"] for r in out["rows"]]
    assert deltas[0] > 0           # near no-FCL scale: carbon worse
    assert deltas[-1] < 0          # large buildout: carbon better
    assert out["carbon_crossover_cap"] is not None
    assert not out["with_fcl_bounded"]   # and the program wants to build forever


@pytest.mark.slow
def test_decomposition_signs(P):
    """Utilization effect raises carbon; capacity effect lowers it once
    buildout exceeds the no-FCL level."""
    d = decompose(P, K_R=100.0)
    assert d["utilization_effect"] > 0
    assert d["capacity_effect"] < 0
