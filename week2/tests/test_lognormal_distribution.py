"""
Week 2 Task 1: generalize the solver's distribution validation beyond the
uniform/power "self-similar" families to a genuinely non-power-law,
semi-closed-form distribution -- CONTEXT2.md's named candidate is truncated
lognormal -- and validate every new derivative the Hessian (Task 3) and the
shift-ratio condition (Task 2) need: pdf, dcdf_dKR, and d2cdf_dKR2.

Every check here is a cross-validation against an independent finite
difference, NOT a tautology: distributions.py's analytic formulas were
hand-derived (see module/method docstrings there) and are tested against a
numerically-independent computation of the same quantity.

Tolerance note: pdf/dcdf_dKR are validated to ~1e-8 (first-order central
differences at h~1e-5 carry ~1e-8 of their own truncation error, matching
model.py's _QUAD_KWARGS comment on this same tradeoff). d2cdf_dKR2 is a
*second* derivative of a finite-difference-prone quantity, so its
cross-check tolerance is loosened to ~1e-5 -- still far tighter than
anything the solver/Hessian actually needs (see test_hessian.py).
"""
import math

import numpy as np
import pytest
from scipy import integrate, stats

from fcl_solver.distributions import (
    LOGNORMAL_PRIMITIVE_MU,
    LOGNORMAL_PRIMITIVE_SIGMA,
    PowerResidual,
    PrimitiveResidual,
    ResidualDemand,
    TruncatedLognormal,
    UniformResidual,
    g_ratio,
)

D_BAR = 100.0


def lognormal_primitive(mu=LOGNORMAL_PRIMITIVE_MU, sigma=LOGNORMAL_PRIMITIVE_SIGMA, a=2.0, b=2.0):
    """The Week 2 candidate family: D ~ truncated lognormal, S ~ Beta(a,b).
    Not a rescaling of a fixed shape in K_R (unlike Uniform/Power), so it is
    the family used to look for a genuine *interior* K*_R optimum (Task 2).

    Defaults use distributions.LOGNORMAL_PRIMITIVE_MU/SIGMA -- see that
    module's TruncatedLognormal "PARAMETER CHOICE WARNING" docstring: these
    keep the D-distribution's truncation jump at D_bar numerically
    negligible (f(D_bar) ~ 1e-9), which matters once second K_R-derivatives
    (the Hessian, test_hessian.py) are involved.
    """
    return PrimitiveResidual(
        D_bar=D_BAR,
        D_dist=TruncatedLognormal(mu=mu, sigma=sigma, D_bar=D_BAR),
        S_dist=stats.beta(a, b),
    )


# ---------------------------------------------------------------------------
# TruncatedLognormal itself (the D_dist primitive, not yet a ResidualDemand)
# ---------------------------------------------------------------------------

class TestTruncatedLognormal:
    # NOTE: this class deliberately uses mu=log(30), sigma=0.5 -- NOT the
    # LOGNORMAL_PRIMITIVE_MU/SIGMA defaults used everywhere else in this
    # file -- because these tests check the class's OWN cdf/pdf/pdf_prime
    # formulas, including right at the truncation edge, where (mu=log(30),
    # sigma=0.5) has deliberately NON-negligible density (~4e-4, vs ~1e-9
    # for the "safe" defaults). That non-negligible edge density is
    # exactly what makes test_zero_outside_support / the boundary checks
    # below a meaningful test of the truncation logic, rather than
    # trivially passing because the density was already ~0 there. The
    # "safe" defaults only matter once these get embedded in
    # PrimitiveResidual for the Hessian (see the PARAMETER CHOICE WARNING
    # in distributions.TruncatedLognormal's docstring) -- not for testing
    # this class in isolation.
    def test_cdf_boundary_and_monotonicity(self):
        ln = TruncatedLognormal(mu=math.log(30), sigma=0.5, D_bar=D_BAR)
        assert ln.cdf(0.0) == 0.0
        assert ln.cdf(D_BAR) == pytest.approx(1.0)
        assert ln.cdf(2 * D_BAR) == pytest.approx(1.0)  # clipped beyond D_bar
        grid = np.linspace(0.01, D_BAR, 200)
        vals = ln.cdf(grid)
        assert np.all(np.diff(vals) >= 0), "truncated CDF must be non-decreasing"

    def test_pdf_integrates_to_one_over_truncated_support(self):
        """Renormalization check: f must integrate to exactly 1 on (0,D_bar],
        not to the *untruncated* lognormal's mass on that interval."""
        ln = TruncatedLognormal(mu=math.log(30), sigma=0.5, D_bar=D_BAR)
        mass, err = integrate.quad(ln.pdf, 1e-8, D_BAR, limit=200, epsabs=1e-10)
        assert mass == pytest.approx(1.0, abs=1e-8)

    @pytest.mark.parametrize("d0", [5.0, 25.0, 50.0, 90.0])
    def test_pdf_prime_matches_finite_difference(self, d0):
        """Cross-check the hand-derived f'(d) = -(f(d)/d)*[1+(ln d-mu)/sigma^2]
        formula against an independent central difference of pdf()."""
        ln = TruncatedLognormal(mu=math.log(30), sigma=0.5, D_bar=D_BAR)
        h = 1e-5
        fd = (ln.pdf(d0 + h) - ln.pdf(d0 - h)) / (2 * h)
        analytic = ln.pdf_prime(d0)
        assert analytic == pytest.approx(fd, rel=1e-6, abs=1e-9)

    def test_zero_outside_support(self):
        ln = TruncatedLognormal(mu=math.log(30), sigma=0.5, D_bar=D_BAR)
        assert ln.pdf(-1.0) == 0.0
        assert ln.pdf(D_BAR + 1.0) == 0.0
        assert ln.pdf_prime(-1.0) == 0.0


# ---------------------------------------------------------------------------
# PrimitiveResidual(lognormal, beta): pdf, dcdf_dKR, d2cdf_dKR2
# ---------------------------------------------------------------------------

# A handful of (x, K_R) interior points to probe -- avoid the extreme tails
# where the lognormal density is numerically tiny and relative tolerances
# get noisy for reasons unrelated to the formulas being tested.
PROBE_POINTS = [(10.0, 5.0), (20.0, 15.0), (50.0, 30.0), (70.0, 60.0)]


class TestPrimitiveResidualLognormal:
    @pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
    def test_pdf_matches_finite_difference_of_cdf(self, x0, K_R0):
        dist = lognormal_primitive()
        h = 1e-5
        fd = (dist.cdf(x0 + h, K_R0) - dist.cdf(x0 - h, K_R0)) / (2 * h)
        analytic = dist.pdf(x0, K_R0)
        assert analytic == pytest.approx(fd, rel=1e-6, abs=1e-9)

    @pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
    def test_dcdf_dKR_matches_finite_difference_of_cdf(self, x0, K_R0):
        """Re-confirms Week 1's analytic dF/dK_R on the new family
        specifically (Week 1 only checked it on Beta/Beta primitives)."""
        dist = lognormal_primitive()
        h = 1e-5
        fd = (dist.cdf(x0, K_R0 + h) - dist.cdf(x0, K_R0 - h)) / (2 * h)
        analytic = dist.dcdf_dKR(x0, K_R0)
        assert analytic == pytest.approx(fd, rel=1e-6, abs=1e-9)

    @pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
    def test_d2cdf_dKR2_matches_finite_difference_of_dcdf_dKR(self, x0, K_R0):
        """The one genuinely new second-order quantity Task 3's Hessian
        needs: cross-check the analytic E_S[S^2 f_D'(x+K_R*S)] path
        (enabled by TruncatedLognormal.pdf_prime) against an independent
        finite difference of dcdf_dKR."""
        dist = lognormal_primitive()
        h = 1e-5
        fd = (dist.dcdf_dKR(x0, K_R0 + h) - dist.dcdf_dKR(x0, K_R0 - h)) / (2 * h)
        analytic = dist.d2cdf_dKR2(x0, K_R0)
        assert analytic == pytest.approx(fd, rel=1e-4, abs=1e-8)

    @pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
    def test_d2cdf_dKR2_generic_fallback_matches_analytic_path(self, x0, K_R0):
        """When D_dist has NO pdf_prime, d2cdf_dKR2 must fall back to a
        finite difference of D_dist.pdf -- still distribution-generic
        (Task 1: works for *any* D_dist), just one precision tier down.
        Confirm the fallback agrees with the fully-analytic path above."""

        class _NoDerivWrapper:
            """Same D as lognormal_primitive() but with pdf_prime hidden,
            to force PrimitiveResidual onto the generic fallback branch."""

            def __init__(self, base):
                self._base = base

            def cdf(self, d):
                return self._base.cdf(d)

            def pdf(self, d):
                return self._base.pdf(d)

        base_ln = TruncatedLognormal(mu=LOGNORMAL_PRIMITIVE_MU, sigma=LOGNORMAL_PRIMITIVE_SIGMA, D_bar=D_BAR)
        dist_analytic = lognormal_primitive()
        dist_fallback = PrimitiveResidual(
            D_bar=D_BAR, D_dist=_NoDerivWrapper(base_ln), S_dist=stats.beta(2, 2)
        )

        analytic = dist_analytic.d2cdf_dKR2(x0, K_R0)
        fallback = dist_fallback.d2cdf_dKR2(x0, K_R0)
        assert fallback == pytest.approx(analytic, rel=1e-4, abs=1e-8)

    def test_not_a_pure_rescaling_in_KR(self):
        """The whole point of choosing lognormal-D over uniform/power: this
        family must NOT be a pure rescaling of one fixed shape in K_R (the
        property responsible for Week 1's knife-edge/no-finite-optimum
        result). A pure rescaling F(x;K_R) = phi((x+K_R)/(D_bar+K_R)) would
        make the *shift ratio* g(x)=F_{K_R}/f constant in x at fixed K_R
        ratio structure; check g varies meaningfully across x here."""
        dist = lognormal_primitive()
        K_R0 = 20.0
        xs = np.array([-10.0, 10.0, 40.0, 70.0])
        g_vals = np.array([g_ratio(dist, x, K_R0) for x in xs])
        assert np.all(np.isfinite(g_vals))
        # under Uniform, g(x) = (D_bar-x)/(D_bar+K_R) -- exactly linear in x.
        # Confirm the lognormal-primitive g(x) is NOT well-approximated by
        # any single linear function of x (i.e. genuinely non-power-law).
        coeffs = np.polyfit(xs, g_vals, 1)
        linear_fit = np.polyval(coeffs, xs)
        residual = np.abs(g_vals - linear_fit).max()
        assert residual > 1e-3 * np.abs(g_vals).max(), (
            "g(x) looks suspiciously linear in x -- check this is really "
            "the non-power-law lognormal family, not an accidental rescaling"
        )


# ---------------------------------------------------------------------------
# Uniform/Power analytic pdf/d2cdf_dKR2 overrides, and the base-class
# generic finite-difference fallback (used by any distribution that
# doesn't override these methods)
# ---------------------------------------------------------------------------

CLOSED_FORM_DISTS = {
    "uniform": UniformResidual(D_bar=D_BAR),
    "power_0.5": PowerResidual(D_bar=D_BAR, alpha=0.5),
    "power_2.0": PowerResidual(D_bar=D_BAR, alpha=2.0),
}


@pytest.mark.parametrize("dist_name", CLOSED_FORM_DISTS.keys())
@pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
def test_uniform_power_pdf_matches_finite_difference(dist_name, x0, K_R0):
    dist = CLOSED_FORM_DISTS[dist_name]
    h = 1e-5
    fd = (dist.cdf(x0 + h, K_R0) - dist.cdf(x0 - h, K_R0)) / (2 * h)
    analytic = dist.pdf(x0, K_R0)
    assert analytic == pytest.approx(fd, rel=1e-6, abs=1e-9)


@pytest.mark.parametrize("dist_name", CLOSED_FORM_DISTS.keys())
@pytest.mark.parametrize("x0,K_R0", PROBE_POINTS)
def test_uniform_power_d2cdf_dKR2_matches_finite_difference(dist_name, x0, K_R0):
    dist = CLOSED_FORM_DISTS[dist_name]
    h = 1e-5
    fd = (dist.dcdf_dKR(x0, K_R0 + h) - dist.dcdf_dKR(x0, K_R0 - h)) / (2 * h)
    analytic = dist.d2cdf_dKR2(x0, K_R0)
    assert analytic == pytest.approx(fd, rel=1e-4, abs=1e-8)


def test_base_class_generic_fallback_works_for_an_undecorated_subclass():
    """A minimal ResidualDemand subclass that implements ONLY cdf() must
    still get correct pdf()/d2cdf_dKR2() via the base class's generic
    finite-difference fallbacks -- this is what makes Task 1's "any
    distribution" claim literally true, not just true for the three
    classes that happen to have analytic overrides."""

    class BareUniform(ResidualDemand):
        def __init__(self, D_bar):
            self.D_bar = float(D_bar)

        def cdf(self, x, K_R):
            u = np.clip((np.asarray(x, dtype=float) + K_R) / (self.D_bar + K_R), 0.0, 1.0)
            return u

    bare = BareUniform(D_BAR)
    decorated = UniformResidual(D_BAR)
    x0, K_R0 = 20.0, 15.0

    assert bare.pdf(x0, K_R0) == pytest.approx(decorated.pdf(x0, K_R0), rel=1e-5)
    # d2cdf_dKR2 here is FD-of-FD (the fallback calls dcdf_dKR, itself a
    # fallback), so it carries more compounded error -- loosen tolerance
    # accordingly; this is the "lower precision tier" documented in
    # distributions.py's ResidualDemand.d2cdf_dKR2 docstring.
    assert bare.d2cdf_dKR2(x0, K_R0) == pytest.approx(decorated.d2cdf_dKR2(x0, K_R0), rel=1e-2)


def test_g_ratio_is_nan_where_density_vanishes():
    dist = UniformResidual(D_bar=D_BAR)
    K_R0 = 10.0
    assert math.isnan(g_ratio(dist, -K_R0 - 1.0, K_R0))  # outside support: f=0
    assert math.isnan(g_ratio(dist, D_BAR + 1.0, K_R0))


def test_g_ratio_matches_definition():
    dist = lognormal_primitive()
    x0, K_R0 = 30.0, 20.0
    expected = dist.dcdf_dKR(x0, K_R0) / dist.pdf(x0, K_R0)
    assert g_ratio(dist, x0, K_R0) == pytest.approx(expected)
