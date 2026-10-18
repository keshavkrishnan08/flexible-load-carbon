"""
Week 4 Task 1 tests: the carbon classification functional Ψ.

Tests are structured to share expensive solver calls via module-level
fixtures (solved once at collection time), so the full suite runs in
< 5 min rather than hours.

Three groups:
1. PROP 4 IDENTITY: eqs (44)/(45) must recover numerical carbon values.
2. SIGN-MATCH: sign(Ψ) = sign(carbon_change) at confirmed historical points.
3. UNIT: functional components (phi, q, mu) satisfy obvious invariants.
"""
import math
import warnings

import numpy as np
import pytest

from fcl_solver.carbon_functional import (
    FunctionalResult,
    _conditional_mean_integral,
    compute_functional,
    prop4_fossil_no_fcl,
    prop4_fossil_with_fcl,
)
from fcl_solver.distributions import (
    PowerResidual,
    UniformResidual,
    lognormal_primitive,
)
from fcl_solver.model import Params

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Solve ONCE at module-level; reuse in every test.
# ─────────────────────────────────────────────────────────────────────────────

_D_BAR = 100.0
_PARAMS_CR25 = Params(R=109, c=45, CF=10, CR=25, CM=56, beta=190, p=10, D_bar=_D_BAR)
_PARAMS_CR26 = Params(R=109, c=45, CF=10, CR=26, CM=56, beta=190, p=10, D_bar=_D_BAR)

_UNI   = UniformResidual(_D_BAR)
_LN06  = lognormal_primitive(_D_BAR, sigma=0.6)
_POW05 = PowerResidual(_D_BAR, alpha=0.5)
_POW20 = PowerResidual(_D_BAR, alpha=2.0)

def _solve(dist, params):
    return compute_functional(dist, params, KR_max=500, KF_max=300, KM_max=300)

# Pre-compute four reference results: one each-way solver call per fixture
_RES_UNI_25   = None   # lazily populated below to avoid import-time cost
_RES_LN06_26  = None
_RES_POW05_25 = None
_RES_POW20_25 = None


@pytest.fixture(scope="module")
def res_uni_25():
    return _solve(_UNI, _PARAMS_CR25)

@pytest.fixture(scope="module")
def res_ln06_26():
    return _solve(_LN06, _PARAMS_CR26)

@pytest.fixture(scope="module")
def res_pow05_25():
    return _solve(_POW05, _PARAMS_CR25)

@pytest.fixture(scope="module")
def res_pow20_25():
    return _solve(_POW20, _PARAMS_CR25)


# ─────────────────────────────────────────────────────────────────────────────
# Group 1: Prop 4 identity checks (eqs 44 / 45)
# ─────────────────────────────────────────────────────────────────────────────

def test_prop4_fossil_with_fcl_matches_direct_uniform(res_uni_25):
    """eq. (44) must recover the model.py carbon / c to within 1%."""
    fossil_p4 = prop4_fossil_with_fcl(res_uni_25, _PARAMS_CR25)
    fossil_direct = res_uni_25.carbon_with_fcl / _PARAMS_CR25.c
    rel = abs(fossil_p4 - fossil_direct) / max(1e-9, fossil_direct)
    assert rel < 0.01, f"eq44 mismatch for uniform: Δrel={rel:.4f}"


def test_prop4_fossil_no_fcl_matches_direct_uniform(res_uni_25):
    """eq. (45) must recover the model.py no-FCL carbon / c within 1%."""
    fossil_p4 = prop4_fossil_no_fcl(res_uni_25)
    fossil_direct = res_uni_25.carbon_no_fcl / _PARAMS_CR25.c
    rel = abs(fossil_p4 - fossil_direct) / max(1e-9, fossil_direct)
    assert rel < 0.01, f"eq45 mismatch for uniform: Δrel={rel:.4f}"


def test_prop4_fossil_with_fcl_matches_direct_lognormal(res_ln06_26):
    """eq. (44) on the canonical Week-2 lognormal point."""
    fossil_p4 = prop4_fossil_with_fcl(res_ln06_26, _PARAMS_CR26)
    fossil_direct = res_ln06_26.carbon_with_fcl / _PARAMS_CR26.c
    rel = abs(fossil_p4 - fossil_direct) / max(1e-9, fossil_direct)
    assert rel < 0.01, f"eq44 mismatch for lognormal sig=0.6: Δrel={rel:.4f}"


def test_prop4_fossil_no_fcl_matches_direct_lognormal(res_ln06_26):
    """eq. (45) on the canonical Week-2 lognormal point."""
    fossil_p4 = prop4_fossil_no_fcl(res_ln06_26)
    fossil_direct = res_ln06_26.carbon_no_fcl / _PARAMS_CR26.c
    rel = abs(fossil_p4 - fossil_direct) / max(1e-9, fossil_direct)
    assert rel < 0.01, f"eq45 mismatch for lognormal sig=0.6: Δrel={rel:.4f}"


# ─────────────────────────────────────────────────────────────────────────────
# Group 2: sign-match checks
# ─────────────────────────────────────────────────────────────────────────────

def test_psi_sign_uniform_cr25(res_uni_25):
    """Uniform, C_R=25: carbon RISES (Weeks 1-3), so Ψ < 0."""
    assert res_uni_25.sign_match, (
        f"sign mismatch: Ψ={res_uni_25.psi:+.4f}, Δcarbon={res_uni_25.carbon_delta:+.4f}")
    assert res_uni_25.psi < 0, f"Expected Ψ<0 (carbon rose), got {res_uni_25.psi:+.4f}"


def test_psi_sign_lognormal_sigma06_cr26(res_ln06_26):
    """CANONICAL WEEK-2 POINT (sigma=0.6, C_R=26): shift-ratio condition TRUE,
    carbon STILL rose 71%. Ψ must be NEGATIVE, sign_match must be TRUE."""
    assert res_ln06_26.sign_match, (
        f"sign mismatch at Week-2 canonical point: "
        f"Ψ={res_ln06_26.psi:+.4f}, Δcarbon={res_ln06_26.carbon_delta:+.4f}")
    assert res_ln06_26.carbon_delta > 0, (
        f"Expected carbon to RISE at this point (Week 2 finding); "
        f"got Δ={res_ln06_26.carbon_delta:+.4f}")
    assert res_ln06_26.psi < 0, (
        f"Ψ should be negative (carbon rose); got Ψ={res_ln06_26.psi:+.4f}")


def test_psi_sign_power_alpha05(res_pow05_25):
    assert res_pow05_25.sign_match, (
        f"alpha=0.5 sign mismatch: Ψ={res_pow05_25.psi:+.4f}")


def test_psi_sign_power_alpha20(res_pow20_25):
    assert res_pow20_25.sign_match, (
        f"alpha=2.0 sign mismatch: Ψ={res_pow20_25.psi:+.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# Group 3: unit tests on functional components
# ─────────────────────────────────────────────────────────────────────────────

def test_phi_and_q_in_unit_interval(res_uni_25):
    assert 0.0 < res_uni_25.phi_circ < 1.0
    assert 0.0 <= res_uni_25.q_circ < 1.0


def test_q_leq_phi(res_uni_25):
    """q° = F(0; K°_R) ≤ φ° = F(K°_F; K°_R) since 0 ≤ K°_F."""
    assert res_uni_25.q_circ <= res_uni_25.phi_circ + 1e-10


def test_conditional_mean_integral_uniform():
    """For Uniform, ∫_a^b x f(x; K_R) dx = (b²-a²)/(2(D_bar+K_R))
    (since f = 1/(D_bar+K_R) on the support).  Cross-check analytically.
    """
    dist = UniformResidual(D_bar=100)
    K_R = 15.0
    a, b = 10.0, 40.0   # both inside support (-15, 100)
    D_bar = 100.0
    analytic = (b**2 - a**2) / (2 * (D_bar + K_R))
    numeric  = _conditional_mean_integral(dist, K_R, a, b)
    assert abs(numeric - analytic) / abs(analytic) < 1e-8, (
        f"Conditional mean integral mismatch: numeric={numeric:.6f}, analytic={analytic:.6f}")


def test_psi_arithmetic_consistent(res_uni_25):
    """Ψ = LHS(C) - RHS(C); verify the decomposed carbon difference is tight."""
    r = res_uni_25
    params = _PARAMS_CR25
    margin = params.R - params.c
    # Ψ should equal fossil_no_fcl - fossil_with_fcl (in MWh, × c = carbon)
    fossil_diff_p4 = prop4_fossil_no_fcl(r) - prop4_fossil_with_fcl(r, params)
    # The carbon sign is: positive fossil_diff → carbon improves → Ψ > 0
    # So sign(Ψ) = sign(fossil_diff_p4):
    if abs(fossil_diff_p4) > 1e-6:
        assert np.sign(r.psi) == np.sign(fossil_diff_p4), (
            f"Ψ={r.psi:+.4f} and fossil_diff={fossil_diff_p4:+.4f} have opposite signs")


def test_smoke_library(res_uni_25):
    """Trivial: the module-level fixtures all ran without error."""
    assert isinstance(res_uni_25, FunctionalResult)
