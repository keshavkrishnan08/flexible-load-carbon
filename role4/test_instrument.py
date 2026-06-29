"""Week-2 Bullet 1: a single per-MWh price implements dispatch + capacities."""
import pytest
from role4 import instrument as inst
from role4.fcl_backend.model import Params as BP
from role4.fcl_backend.distributions import UniformResidual
from role4.fcl_backend import solver


def _bp(P): return BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)


def test_flat_price_induces_eq3_dispatch(P):
    # at the solver's own with-FCL capacities, the flat-price best response = d*
    dist = UniformResidual(P.D_bar)
    no = solver.solve_no_fcl(dist, _bp(P))
    r = solver.solve_with_fcl_given_KR(dist, _bp(P), no.K_R)
    assert inst.flat_price_implements_dispatch(P, r.K_F, r.K_M)


def test_best_response_matches_rule_pointwise(P):
    K_F, K_M = 40.0, 30.0
    for x in (-25.0, -5.0, 0.0, 5.0, 12.0, 20.0, 39.0, 45.0):
        br = inst.best_response_dispatch(P, K_F, K_M, x)
        fb = inst.first_best_dispatch(K_F, K_M, x)
        assert abs(br - fb) <= 1e-3 * K_M + 1e-6


def test_state_contingent_transfer_buys_nothing(P):
    # flat price already maximizes the per-period payoff pointwise → gain ≈ 0
    assert abs(inst.state_contingent_gain(P, 40.0, 30.0)) < 1e-6


def test_richness_window_and_assumption1(P):
    lo, hi = inst.price_richness_window(P)
    assert lo == P.c and hi == P.bp
    assert inst.price_is_rich_enough(P)
    assert inst.richness_implied_by_assumption1(P)


def test_richness_fails_outside_window():
    from role4.params import Params
    # push R above β+p (A4 violated) → not rich enough
    P = Params(R=4.0, c=1.0, CF=1.0, CR=0.5, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)
    assert not P.A4()
    assert not inst.price_is_rich_enough(P)


@pytest.mark.slow
def test_single_scalar_pins_capacity_vector(P):
    # a sweep of the single instrument R traces a 1-parameter capacity curve
    rows = inst.capacity_locus(P, [1.6, 1.8, 2.0, 2.2])
    assert len(rows) >= 3
    # K_M should respond monotonically to the single instrument R
    kms = [r["K_M"] for r in rows]
    assert kms == sorted(kms) or kms == sorted(kms, reverse=True)


def test_matches_role1_pushed_proposition(P):
    # consistency with Role 1's already-pushed prop:pa (handed off to Role 4):
    # same implementation conditions and the same distribution-free cutoff.
    from role4 import foc
    assert P.R > P.c and P.bp > P.R                 # prop:pa conditions
    assert inst.price_is_rich_enough(P)             # ⇔ R in (c, β+p)
    assert foc.cutoff_KM_eq12(P) == pytest.approx(P.CM / (P.R - P.c))  # cutoff C_M/(R-c)
