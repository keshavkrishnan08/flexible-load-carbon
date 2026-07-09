"""
Residual-demand distributions F(x; K_R) for the FCL model.

Paper definition (eq. 1): residual demand is

    x_tilde = D_tilde - K_R * S_tilde

where D_tilde is exogenous (non-FCL) consumer demand on [0, D_bar] and
S_tilde in [0,1] is the renewable capacity factor. F(x; K_R) is the CDF of
x_tilde, *extended* so that F = 0 for x <= -K_R and F = 1 for x >= D_bar
(Section 3.4's "extended CDF" convention).

That extension convention is what lets one profit formula (eq. 5) and one
pair of first-order conditions cover *both* the "large-FCL" regime
(K_M > K_R) and the "small-FCL" regime (K_M <= K_R, Appendix G) with no
if/else branch: outside the true support, F is just clipped to 0 or 1, and
every integral in model.py is taken directly against this extended F.

Three implementations are provided:
  - UniformResidual : F(x;K_R) = (x+K_R)/(D_bar+K_R), the paper's main
    worked example (eqs 18-26). K_R has a degenerate ("knife-edge", eq 24)
    optimum under this family -- that is a property of the paper's model,
    not a bug in the solver (see CONTEXT.md).
  - PowerResidual : F(x;K_R) = ((x+K_R)/(D_bar+K_R))**alpha, footnote 6 on
    p.30 of the paper. Nests Uniform at alpha=1. Same knife-edge issue,
    since it is still a pure rescaling of the uniform shape.
  - PrimitiveResidual : built from independent marginal distributions for
    D_tilde and S_tilde (any scipy.stats frozen distributions), with
    F(x;K_R) obtained by numerically integrating out S_tilde. This is the
    literal eq. 1 construction and is generally *not* a pure rescaling in
    K_R, so it is the family used to test for genuine interior K*_R optima
    (Task 2: "generalize to any residual-demand distribution").

Week 2 adds:
  - pdf() and d2cdf_dKR2() on every class above (generic finite-difference
    fallbacks on the base class; analytic overrides on Uniform/Power; an
    analytic-when-possible path on Primitive) -- the density and the
    second K_R-derivative of F are exactly the two extra ingredients
    foc.py's first-order gradients didn't need but the analytic Hessian
    (hessian.py, Task 3) does.
  - TruncatedLognormal : a D_dist plug-in for PrimitiveResidual (lognormal
    truncated to (0, D_bar], renormalized), with a closed-form pdf_prime --
    CONTEXT2.md's named candidate for a genuinely non-power-law residual-
    demand family with a finite *interior* K*_R optimum (Task 1/2).
  - g_ratio() : the "shift ratio" g(x) = F_{K_R}(x)/f(x) used by Role 1's
    endpoint shift-ratio condition (Task 2).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import integrate
from scipy import stats as _stats
from scipy.stats import norm as _norm

_norm_cdf = _norm.cdf


class ResidualDemand:
    """Abstract base: subclasses must implement cdf(x, K_R)."""

    D_bar: float

    def cdf(self, x, K_R):
        raise NotImplementedError

    def dcdf_dKR(self, x, K_R, h=None):
        """∂F/∂K_R via central finite difference (generic fallback).

        Subclasses with a closed-form derivative should override this for
        speed/accuracy; the finite-difference version is what makes the
        solver work for *any* distribution (Task 2) without extra code.
        """
        K_R = float(K_R)
        if h is None:
            h = max(1e-6, abs(K_R) * 1e-6)
        h = min(h, K_R / 2) if K_R > 0 else h
        return (self.cdf(x, K_R + h) - self.cdf(x, K_R - h)) / (2 * h)

    def pdf(self, x, K_R, h=None):
        """f(x;K_R) = dF/dx, via central finite difference (generic
        fallback; Week 2 Task 1/3 -- the Hessian's K_M/K_F entries and the
        shift-ratio g(x)=F_{K_R}/f all need the *density*, not just the
        CDF, for an arbitrary distribution. Subclasses with closed-form
        densities (Uniform, Power, Primitive) override this for precision.
        """
        x = np.asarray(x, dtype=float)
        if h is None:
            scale = max(1.0, float(np.max(np.abs(x))) if x.size else 1.0, self.D_bar)
            h = scale * 1e-6
        return (self.cdf(x + h, K_R) - self.cdf(x - h, K_R)) / (2 * h)

    def d2cdf_dKR2(self, x, K_R, h=None):
        """∂²F/∂K_R² via central finite difference of dcdf_dKR (generic
        fallback). This is the one new second-order quantity the analytic
        Hessian needs beyond foc.py's first derivatives (Week 2 Task 3):
        every Hessian entry except d²Π/dK_R² is expressible purely in terms
        of f and ∂F/∂K_R, which Week 1 already provides. Subclasses with a
        closed-form ∂F/∂K_R should override this analytically wherever
        possible -- see PrimitiveResidual, which needs the D-density's own
        derivative (f_D') and so only has a closed form when D_dist
        exposes a `pdf_prime` (e.g. TruncatedLognormal below); otherwise it
        falls back to this same finite-difference scheme one level down.
        """
        K_R = float(K_R)
        if h is None:
            h = max(1e-6, abs(K_R) * 1e-6, self.D_bar * 1e-6)
        h = min(h, K_R / 2) if K_R > 0 else h
        return (self.dcdf_dKR(x, K_R + h) - self.dcdf_dKR(x, K_R - h)) / (2 * h)


class UniformResidual(ResidualDemand):
    """F(x;K_R) = (x+K_R)/(D_bar+K_R) on [-K_R, D_bar] (paper Section 4.3)."""

    def __init__(self, D_bar: float):
        self.D_bar = float(D_bar)

    def cdf(self, x, K_R):
        x = np.asarray(x, dtype=float)
        u = (x + K_R) / (self.D_bar + K_R)
        return np.clip(u, 0.0, 1.0)

    def dcdf_dKR(self, x, K_R, h=None):
        # d/dK_R[(x+K_R)/(D_bar+K_R)] = (D_bar-x)/(D_bar+K_R)**2, but only
        # inside the support; outside, the extended F is flat (0 or 1), so
        # the derivative is 0 there.
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        deriv = (self.D_bar - x) / (self.D_bar + K_R) ** 2
        return np.where(inside, deriv, 0.0)

    def pdf(self, x, K_R, h=None):
        """f(x;K_R) = 1/(D_bar+K_R) inside the support, 0 outside."""
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        return np.where(inside, 1.0 / (self.D_bar + K_R), 0.0)

    def d2cdf_dKR2(self, x, K_R, h=None):
        """d/dK_R[(D_bar-x)/(D_bar+K_R)**2] = -2*(D_bar-x)/(D_bar+K_R)**3."""
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        deriv2 = -2.0 * (self.D_bar - x) / (self.D_bar + K_R) ** 3
        return np.where(inside, deriv2, 0.0)


class PowerResidual(ResidualDemand):
    """F(x;K_R) = ((x+K_R)/(D_bar+K_R))**alpha (paper footnote 6, p.30).

    alpha=1 nests UniformResidual. alpha<1 is right-skewed (more mass on
    deep renewable-surplus states); alpha>1 is left-skewed.
    """

    def __init__(self, D_bar: float, alpha: float):
        self.D_bar = float(D_bar)
        self.alpha = float(alpha)

    def cdf(self, x, K_R):
        x = np.asarray(x, dtype=float)
        u = np.clip((x + K_R) / (self.D_bar + K_R), 0.0, 1.0)
        return u ** self.alpha

    def dcdf_dKR(self, x, K_R, h=None):
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        u = np.clip((x + K_R) / (self.D_bar + K_R), 1e-300, 1.0)
        du_dKR = (self.D_bar - x) / (self.D_bar + K_R) ** 2
        deriv = self.alpha * u ** (self.alpha - 1) * du_dKR
        return np.where(inside, deriv, 0.0)

    def pdf(self, x, K_R, h=None):
        """f(x;K_R) = d/dx[u**alpha] = alpha*u**(alpha-1)/(D_bar+K_R)."""
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        u = np.clip((x + K_R) / (self.D_bar + K_R), 1e-300, 1.0)
        deriv = self.alpha * u ** (self.alpha - 1) / (self.D_bar + K_R)
        return np.where(inside, deriv, 0.0)

    def d2cdf_dKR2(self, x, K_R, h=None):
        """d/dK_R[alpha*u**(alpha-1)*du_dKR], hand-differentiated:

            = alpha*u**(alpha-2)*du_dKR*[(alpha-1)*du_dKR - 2*u/(D_bar+K_R)]

        using d(du_dKR)/dK_R = -2*du_dKR/(D_bar+K_R). Cross-checked against
        the generic finite-difference base-class fallback in
        tests/test_lognormal_distribution.py's parametrized sweep.
        """
        x = np.asarray(x, dtype=float)
        inside = (x > -K_R) & (x < self.D_bar)
        u = np.clip((x + K_R) / (self.D_bar + K_R), 1e-300, 1.0)
        du_dKR = (self.D_bar - x) / (self.D_bar + K_R) ** 2
        deriv2 = (
            self.alpha
            * u ** (self.alpha - 2)
            * du_dKR
            * ((self.alpha - 1) * du_dKR - 2.0 * u / (self.D_bar + K_R))
        )
        return np.where(inside, deriv2, 0.0)


class PrimitiveResidual(ResidualDemand):
    """F(x;K_R) built from the literal primitives x = D - K_R*S (eq. 1).

    D_dist, S_dist: scipy.stats frozen distributions (D on [0,D_bar],
    S on [0,1]), assumed independent. F is obtained by integrating the
    D-distribution's CDF against the S-distribution's density:

        F(x;K_R) = P(D - K_R*S <= x) = E_S[ F_D(x + K_R*S) ]

    Unlike Uniform/Power, this is generally *not* a rescaling of a fixed
    shape in K_R, so it typically has a genuine interior K*_R optimum --
    used in tests as the "non-degenerate" distribution family.

    The E_S[...] expectation is a smooth (no kinks) integral over S in
    [0,1], so it is evaluated with a *fixed* Gauss-Legendre quadrature rule
    (computed once in __init__) rather than scipy.integrate.quad. This
    matters a lot in practice: model.py's profit() already wraps cdf() in
    an *outer* adaptive quad call (over x); using adaptive quad again for
    every single cdf() evaluation ("quad-in-quad") makes each outer
    evaluation re-run an independent adaptive subdivision search, which is
    what made an early version of this class take minutes instead of
    seconds in the test suite. A fixed-order rule turns every cdf() call
    into one vectorized weighted sum, which is both fast and (for the
    smooth S_dist densities used here) accurate well past the precision
    the rest of the solver needs.
    """

    def __init__(self, D_bar: float, D_dist, S_dist, n_quad: int = 40):
        self.D_bar = float(D_bar)
        self.D_dist = D_dist
        self.S_dist = S_dist
        nodes, weights = np.polynomial.legendre.leggauss(n_quad)
        # transform Gauss-Legendre nodes/weights from [-1,1] to [0,1]
        self._s_nodes = 0.5 * (nodes + 1.0)
        self._s_weights = 0.5 * weights
        self._s_pdf_w = self._s_weights * self.S_dist.pdf(self._s_nodes)  # precomputed

    def _shifted_grid(self, x, K_R):
        """Shared grid-construction step for cdf/pdf/dcdf_dKR/d2cdf_dKR2:
        return (x_orig, shifted, scalar_input) where
        shifted[i,j] = x_i + K_R*s_j, shape (len(x), n_quad). Factored out
        (Week 2) so the two new methods below reuse exactly the same
        scalar/array handling as the two methods Week 1 already validated,
        rather than risking a second, slightly-different reshape path.
        """
        x = np.asarray(x, dtype=float)
        scalar_input = x.ndim == 0
        xf = np.atleast_1d(x).astype(float)
        shifted = xf[:, None] + K_R * self._s_nodes[None, :]
        return x, shifted, scalar_input

    def _collapse(self, vals_2d, x_orig, scalar_input, clip=None):
        """E_S[vals_2d] = vals_2d @ s_pdf_w, then restore scalar/shape."""
        out = vals_2d @ self._s_pdf_w
        if clip is not None:
            out = np.clip(out, *clip)
        return float(out[0]) if scalar_input else out.reshape(x_orig.shape)

    def cdf(self, x, K_R):
        x_orig, shifted, scalar_input = self._shifted_grid(x, K_R)
        Fd = self.D_dist.cdf(shifted)
        return self._collapse(Fd, x_orig, scalar_input, clip=(0.0, 1.0))

    def pdf(self, x, K_R, h=None):
        """f(x;K_R) = E_S[ f_D(x + K_R*S) ] (differentiate cdf wrt x
        under the expectation -- valid since S has a continuous density).
        """
        x_orig, shifted, scalar_input = self._shifted_grid(x, K_R)
        fd = self.D_dist.pdf(shifted)
        return self._collapse(fd, x_orig, scalar_input)

    def d2cdf_dKR2(self, x, K_R, h=None):
        """d^2F/dK_R^2 = E_S[ S^2 * f_D'(x+K_R*S) ] (chain rule applied a
        second time to dcdf_dKR's E_S[S*f_D(x+K_R*S)]). f_D' is the
        D-distribution's own density derivative: analytic whenever D_dist
        exposes a `pdf_prime` method (e.g. TruncatedLognormal below);
        otherwise this falls back to a central finite difference of
        D_dist.pdf itself, so the second-order Hessian entry is still
        available (at one lower precision tier) for *any* scipy.stats
        D_dist, preserving Task 1's "any distribution" generality.
        """
        x_orig, shifted, scalar_input = self._shifted_grid(x, K_R)
        if hasattr(self.D_dist, "pdf_prime"):
            fd_prime = self.D_dist.pdf_prime(shifted)
        else:
            hh = 1e-6 * max(1.0, float(np.max(np.abs(shifted))) if shifted.size else 1.0)
            fd_prime = (self.D_dist.pdf(shifted + hh) - self.D_dist.pdf(shifted - hh)) / (2 * hh)
        weighted = fd_prime * (self._s_nodes[None, :] ** 2)
        return self._collapse(weighted, x_orig, scalar_input)

    def dcdf_dKR(self, x, K_R, h=None):
        """Analytic: dF/dK_R = E_S[ S * f_D(x + K_R*S) ] (chain rule)."""
        x = np.asarray(x, dtype=float)
        scalar_input = x.ndim == 0
        xf = np.atleast_1d(x).astype(float)
        shifted = xf[:, None] + K_R * self._s_nodes[None, :]
        fd = self.D_dist.pdf(shifted)
        out = fd @ (self._s_nodes * self._s_pdf_w)
        return float(out[0]) if scalar_input else out.reshape(x.shape)


class TruncatedLognormal:
    """D ~ Lognormal(mu, sigma) truncated to the support (0, D_bar] and
    renormalized -- a D_dist plug-in for PrimitiveResidual (NOT itself a
    ResidualDemand: it models the primitive consumer-demand variable D,
    not the residual x = D - K_R*S).

    Week 2 Task 1's "generalize beyond the uniform/power *self-similar*
    families" candidate: CONTEXT2.md names truncated lognormal as the
    natural non-power-law choice. Unlike Uniform/PowerResidual (both pure
    rescalings of one fixed shape in K_R -- the source of the Week 1
    knife-edge/no-finite-optimum problem), a lognormal D mixed with a
    smooth S (e.g. Beta) is not a rescaling in K_R at all, so
    PrimitiveResidual(D_dist=TruncatedLognormal(...), S_dist=...) is a
    genuine candidate for a finite *interior* K*_R optimum (Task 2).

    Closed forms (truncating at 0 needs no left-tail renormalization,
    since the untruncated lognormal CDF is already 0 there):

        Z      = Phi((ln(D_bar) - mu) / sigma)            (total mass kept)
        f(d)   = LN(d; mu, sigma) / Z,            0 < d <= D_bar
        F(d)   = Phi((ln(d) - mu) / sigma) / Z,   0 < d <= D_bar
        f'(d)  = -(f(d)/d) * [1 + (ln(d)-mu)/sigma**2]

    f'(d) is derived by hand from d/dd[ln LN(d)] = -(1/d)*[1+(ln d-mu)/sigma**2]
    (LN(d) = (d*sigma*sqrt(2*pi))**-1 * exp(-(ln d-mu)**2/(2*sigma**2)), so
    ln LN(d) = const - ln d - (ln d-mu)**2/(2*sigma**2)); the truncation
    constant Z cancels in the *ratio* f'(d)/f(d), so it does not need to be
    tracked separately for pdf_prime. Cross-checked against a central
    finite difference of pdf() in tests/test_lognormal_distribution.py.

    PARAMETER CHOICE WARNING (Week 2 finding -- read before changing mu/sigma):
    truncating at D_bar creates a genuine JUMP in f(d) at d=D_bar itself
    (f(D_bar-) generally nonzero, f(D_bar+ and beyond)=0 by construction --
    same kind of hard edge as Uniform's jump at x=-K_R, just at the OTHER
    end of D's support). Inside PrimitiveResidual, this propagates into a
    K_R-DEPENDENT kink of dcdf_dKR(x;K_R) at x = D_bar - K_R (the x where
    the S-integral's effective upper limit (D_bar-x)/K_R first exceeds 1),
    which silently corrupted hessian.py's H_RR by ~10-30% before being
    diagnosed (the value itself, and even dF/dK_R, are continuous there --
    only the SECOND K_R-derivative the Hessian needs picks it up, the same
    way F itself stays continuous at x=-K_R while dF/dK_R jumps there).
    Properly handling this in general would need a second Leibniz boundary
    term (mirroring quad_breakpoint/hessian.py's existing one for -K_R) at
    this second, D_dist-specific location -- NOT implemented, because the
    simpler and equally rigorous fix is to choose (mu, sigma) so that
    f(D_bar) is negligible at double-precision scale, making the jump's
    magnitude irrelevant rather than correcting for it. mu=log(20),
    sigma=0.28 (used throughout this codebase) gives f(D_bar=100-) ~ 1e-9.
    If you change these parameters, recompute f(D_bar) and keep it below
    ~1e-8, or implement the second boundary term.
    """

    def __init__(self, mu: float, sigma: float, D_bar: float):
        self.mu = float(mu)
        self.sigma = float(sigma)
        self.D_bar = float(D_bar)
        self._Z = float(_norm_cdf((math.log(self.D_bar) - self.mu) / self.sigma))

    def _safe_log(self, d):
        # log(d) only where d>0 (placeholder elsewhere); callers mask the
        # result with `pos` before it is ever used, so the placeholder
        # value itself is never read -- this just avoids RuntimeWarnings.
        d = np.asarray(d, dtype=float)
        safe_d = np.where(d > 0, d, 1.0)
        return np.log(safe_d)

    def pdf(self, d):
        d = np.asarray(d, dtype=float)
        pos = (d > 0) & (d <= self.D_bar)
        z = (self._safe_log(d) - self.mu) / self.sigma
        raw = np.exp(-0.5 * z ** 2) / (np.where(d > 0, d, 1.0) * self.sigma * math.sqrt(2.0 * math.pi))
        return np.where(pos, raw / self._Z, 0.0)

    def cdf(self, d):
        d = np.asarray(d, dtype=float)
        z = (self._safe_log(d) - self.mu) / self.sigma
        raw = np.clip(_norm_cdf(z) / self._Z, 0.0, 1.0)
        out = np.where(d <= 0, 0.0, raw)
        out = np.where(d >= self.D_bar, 1.0, out)
        return out

    def pdf_prime(self, d):
        """f'(d) = -(f(d)/d) * [1 + (ln(d)-mu)/sigma**2], 0 < d <= D_bar."""
        d = np.asarray(d, dtype=float)
        pos = (d > 0) & (d <= self.D_bar)
        f = self.pdf(d)
        z_term = 1.0 + (self._safe_log(d) - self.mu) / self.sigma ** 2
        deriv = -(f / np.where(d > 0, d, 1.0)) * z_term
        return np.where(pos, deriv, 0.0)


# Default (mu, sigma) for TruncatedLognormal, scaled to D_bar=100: see the
# "PARAMETER CHOICE WARNING" in TruncatedLognormal's docstring -- these
# keep f(D_bar) ~ 1e-9 (negligible truncation jump). Defined once here so
# every test/sweep that wants "the Task 1/2 lognormal-primitive family"
# uses the same numerically-safe parametrization rather than re-deriving
# it (or accidentally reintroducing the jump with a wider sigma).
LOGNORMAL_PRIMITIVE_MU = math.log(20.0)
LOGNORMAL_PRIMITIVE_SIGMA = 0.28


def lognormal_primitive(D_bar: float, S_dist=None, mu=None, sigma=None, n_quad: int = 40) -> "PrimitiveResidual":
    """The Task 1/2 "genuinely non-power-law" family: D ~ TruncatedLognormal
    (LOGNORMAL_PRIMITIVE_MU/SIGMA by default), S ~ Beta(2,2) by default.
    Unlike Uniform/PowerResidual, this is not a rescaling of one fixed
    shape in K_R, so it is the family used to search for a genuine
    *interior* K*_R optimum (Task 2) rather than a corner solution.
    """
    if S_dist is None:
        S_dist = _stats.beta(2, 2)
    mu = LOGNORMAL_PRIMITIVE_MU if mu is None else mu
    sigma = LOGNORMAL_PRIMITIVE_SIGMA if sigma is None else sigma
    return PrimitiveResidual(
        D_bar=D_bar,
        D_dist=TruncatedLognormal(mu=mu, sigma=sigma, D_bar=D_bar),
        S_dist=S_dist,
        n_quad=n_quad,
    )


def g_ratio(dist: ResidualDemand, x, K_R):
    """The "shift ratio" g(x) = F_{K_R}(x;K_R) / f(x;K_R) (Week 2 CONTEXT2.md
    Section 1): how much a marginal unit of K_R moves the CDF at x,
    normalized by the local density. This is the building block of the
    endpoint shift-ratio condition g(K_F*-K_M*) >= g(K_F*) that Role 1's
    Task-2 sufficient condition for K*_R > K_R^o is stated in terms of
    (lower dispatch endpoint carries the larger shift ratio; g non-increasing
    on regular families). See fcl_solver/finite_optimum.py for the check.

    Returns NaN where f(x;K_R)==0 (g is not meaningfully defined where the
    density vanishes, e.g. exactly at -K_R or D_bar in the Uniform family).
    """
    f = dist.pdf(x, K_R)
    F_KR = dist.dcdf_dKR(x, K_R)
    f = np.asarray(f, dtype=float)
    F_KR = np.asarray(F_KR, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(f > 0, F_KR / np.where(f > 0, f, 1.0), np.nan)
    return float(out) if out.ndim == 0 else out


def quad_breakpoint(a: float, b: float, K_R: float):
    """Week 2 bugfix helper: return [-K_R] if the residual-demand support's
    lower edge falls *strictly inside* the fixed range (a,b), else None.

    Every ResidualDemand subclass in this file shares the same "extended
    CDF" convention (cdf/pdf/dcdf_dKR/d2cdf_dKR2 are all identically 0 for
    x<=-K_R), so -K_R is a genuine breakpoint of the integrand -- and, for
    Uniform/Power, a literal jump discontinuity in the density -- whenever
    it falls inside an otherwise-K_R-independent integration range (this
    happens routinely: e.g. model.expected_fossil_output's range
    [-K_M, K_F-K_M] contains -K_R exactly whenever K_R < K_M < K_F+K_R,
    the paper's main "large-FCL" regime).

    THE BUG THIS FIXES: scipy.integrate.quad's plain adaptive rule (QAGS)
    is given no information about this breakpoint, and was found (Week 2,
    while cross-checking the analytic Hessian against finite differences)
    to occasionally converge to a value that is wrong by ~1e-5 to 1e-4 in
    absolute terms *while reporting an estimated error of ~1e-15* -- i.e.
    silently, with no warning and a falsely tiny error estimate. This bias
    is far too small to matter for any single profit/blackout/carbon VALUE
    Week 1 checked (well within those tests' tolerances), but it is large
    enough to completely corrupt a finite-difference SECOND derivative,
    which divides a fixed-size bias by a small step h. Passing this point
    explicitly via `points=` switches scipy to QAGP, which integrates each
    side of the breakpoint separately and does not exhibit this failure
    mode (confirmed against an independent trapezoid-rule integral -- see
    tests/test_quad_breakpoint.py for the worked example that surfaced
    this).
    """
    lo, hi = (a, b) if a <= b else (b, a)
    return [-K_R] if lo < -K_R < hi else None
