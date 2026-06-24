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
"""
from __future__ import annotations

import numpy as np
from scipy import integrate


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

    def cdf(self, x, K_R):
        x = np.asarray(x, dtype=float)
        scalar_input = x.ndim == 0
        xf = np.atleast_1d(x).astype(float)
        # shape (len(xf), n_quad): x_i + K_R * s_j
        shifted = xf[:, None] + K_R * self._s_nodes[None, :]
        Fd = self.D_dist.cdf(shifted)
        out = np.clip(Fd @ self._s_pdf_w, 0.0, 1.0)
        return float(out[0]) if scalar_input else out.reshape(x.shape)

    def dcdf_dKR(self, x, K_R, h=None):
        """Analytic: dF/dK_R = E_S[ S * f_D(x + K_R*S) ] (chain rule)."""
        x = np.asarray(x, dtype=float)
        scalar_input = x.ndim == 0
        xf = np.atleast_1d(x).astype(float)
        shifted = xf[:, None] + K_R * self._s_nodes[None, :]
        fd = self.D_dist.pdf(shifted)
        out = fd @ (self._s_nodes * self._s_pdf_w)
        return float(out[0]) if scalar_input else out.reshape(x.shape)
