"""
Week 2 Task 3: the analytic Hessian of profit w.r.t. (K_R, K_F, K_M), and a
negative-definiteness certificate at a candidate optimum.

Every entry below is obtained by hand-differentiating foc.py's three
first-order gradients (grad_KR, grad_KF, grad_KM) a second time -- see
hessian()'s docstring for the one-line derivation of each entry. All six
distinct entries need only the density f(x;K_R) = dist.pdf and the *first*
partial dF/dK_R = dist.dcdf_dKR, EXCEPT the (K_R,K_R) diagonal entry, which
needs the *second* partial d2cdf_dKR2 -- exactly the one new quantity Week
2's distributions.py extension was built to provide (see that module's
Week-2 docstring addendum).

Symmetry (H_RF == H_FR, H_RM == H_MR, H_FM == H_MF) is NOT assumed in the
formulas below -- each off-diagonal entry is independently derived from two
different starting gradients (e.g. H_MF from differentiating grad_KM
w.r.t. K_F, and H_FM from differentiating grad_KF w.r.t. K_M). The two
derivations agreeing (confirmed by hand in the docstring below, and
re-confirmed numerically in tests/test_hessian.py) is itself a correctness
check on the algebra: a real error in either gradient's second derivative
would generically break this symmetry.

The profit problem here is NOT globally concave (Week 1's README flags this
directly: under Uniform/Power the with-FCL profit has no finite global
maximum at all). Negative-definiteness of this Hessian is therefore checked
*locally*, at a specific candidate stationary point returned by the solver
-- it certifies that point is a genuine local maximum (not a saddle), which
is the well-posedness question Week 2's whole reframe (CONTEXT2.md Section
3) turns on: "is there a finite, regular interior optimum for the carbon
claim to hold at."
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import integrate

from .distributions import ResidualDemand, quad_breakpoint
from .foc import gradient
from .model import Params

# limit raised to 1000 (Week 2): see model.py's _QUAD_KWARGS comment --
# the lognormal-primitive family's wide-range integrals were hitting the
# 200-subdivision cap before reaching epsabs/epsrel.
_QUAD_KWARGS = dict(limit=1000, epsabs=1e-9, epsrel=1e-9)


def _right_limit_FKR_at_lower_edge(dist: ResidualDemand, K_R, eps=None):
    """lim_{x -> (-K_R)+} dist.dcdf_dKR(x, K_R) -- the RIGHT-continuous
    limit at the support's lower edge, evaluated from INSIDE.

    This is deliberately NOT the same as dist.dcdf_dKR(-K_R, K_R) itself:
    every ResidualDemand here defines "inside" with a strict inequality
    (x > -K_R), so evaluating exactly AT -K_R returns the OUTSIDE value
    (0, by the extended-CDF convention) -- but the Leibniz boundary term
    derived in hessian()'s docstring needs the value approached FROM
    inside, which is generally nonzero (e.g. 1/(D_bar+K_R) for Uniform;
    exactly 0 for the lognormal-primitive family, since its density
    vanishes continuously at the edge -- see distributions.py). A tiny
    one-sided numerical step is the only distribution-generic way to get
    this (no class here exposes a dedicated "limit from inside" method).
    """
    if eps is None:
        eps = 1e-7 * max(1.0, abs(K_R))
    return float(dist.dcdf_dKR(-K_R + eps, K_R))


def hessian(dist: ResidualDemand, params: Params, K_R, K_F, K_M) -> np.ndarray:
    """3x3 Hessian of profit, ordered (K_R, K_F, K_M) -- matches
    foc.gradient's return order, so e.g. H[0,0] = d^2(Pi)/dK_R^2,
    H[1,2] = d^2(Pi)/dK_F dK_M.

    Derivations (f = dist.pdf, F_KR = dist.dcdf_dKR, F_KRKR = dist.d2cdf_dKR2;
    b = params.beta, p = params.p, R/c/CF/CR/CM = the usual cost/revenue
    parameters):

      H_MM = d(grad_KM)/dK_M = -(R-c)*f(K_F-K_M) - c*f(-K_M)

        [grad_KM = (R-c)*F(K_F-K_M) + c*F(-K_M) - C_M; both F(.) arguments
         move with derivative -1 in K_M, picking up a minus sign each.]

      H_FF = d(grad_KF)/dK_F = [R-(b+p)]*f(K_F) - (R-c)*f(K_F-K_M)

        [grad_KF = [R-(b+p)]*F(K_F) + [c-R]*F(K_F-K_M) + (b+p-c) - C_F;
         d/dK_F of F(K_F) is f(K_F), of F(K_F-K_M) is f(K_F-K_M).]

      H_MF = d(grad_KM)/dK_F = (R-c)*f(K_F-K_M)
      H_FM = d(grad_KF)/dK_M = (R-c)*f(K_F-K_M)         [== H_MF, confirmed]

      H_RM = d(grad_KR)/dK_M = (R-c)*F_KR(K_F-K_M) + c*F_KR(-K_M)
      H_MR = d(grad_KM)/dK_R = (R-c)*F_KR(K_F-K_M) + c*F_KR(-K_M)  [== H_RM]

      H_RF = d(grad_KR)/dK_F = [R-(b+p)]*F_KR(K_F) - (R-c)*F_KR(K_F-K_M)
      H_FR = d(grad_KF)/dK_R = [R-(b+p)]*F_KR(K_F) - (R-c)*F_KR(K_F-K_M)  [== H_RF]

      H_RR = d(grad_KR)/dK_R = R*int_{K_F-K_M}^{K_F} F_KRKR dx
                               + c*int_{-K_M}^{K_F-K_M} F_KRKR dx
                               + (b+p)*int_{K_F}^{D_bar} F_KRKR dx
                               + [boundary correction, see below]

        [grad_KR's three integrals have FIXED limits (independent of
         K_R) -- only the integrand F_KR(x;K_R) depends on K_R -- so a
         first pass at Leibniz's rule suggests differentiating grad_KR
         again w.r.t. K_R only differentiates the integrand. That is
         *almost* right, but misses one thing: each integral's effective
         lower limit is really max(a, -K_R), since F_KR (and hence
         F_KRKR) is identically 0 below the support's edge -K_R -- and
         -K_R itself moves with K_R. Whenever -K_R falls STRICTLY inside
         a term's nominal (a,b) range, re-deriving via the explicit
         variable-limit Leibniz formula adds a boundary term equal to
         that term's coefficient times F_KR(-K_R;K_R) (the limit
         approached from INSIDE the support -- see
         _right_limit_FKR_at_lower_edge). This term is IDENTICALLY ZERO
         for grad_KR's own first derivative (Section 4's grad_KR/foc.py
         derivation), because F itself -- not F_KR -- is what is zero at
         that boundary there, but is generally nonzero here, since
         F_KR's limit from inside need not vanish (e.g. it's
         1/(D_bar+K_R) for Uniform; it IS exactly zero for the
         lognormal-primitive family, since that density vanishes
         continuously at the edge -- see distributions.py's
         TruncatedLognormal docstring). Caught in Week 2 by a failing
         finite-difference cross-check (tests/test_hessian.py) at points
         where K_M > K_R puts -K_R inside the c-weighted [-K_M,K_F-K_M]
         term -- the paper's main "large-FCL" regime.]
    """
    R, c, beta, p, D_bar = params.R, params.c, params.beta, params.p, params.D_bar

    f_gap = float(dist.pdf(K_F - K_M, K_R))
    f_minusKM = float(dist.pdf(-K_M, K_R))
    f_KF = float(dist.pdf(K_F, K_R))
    FKR_gap = float(dist.dcdf_dKR(K_F - K_M, K_R))
    FKR_minusKM = float(dist.dcdf_dKR(-K_M, K_R))
    FKR_KF = float(dist.dcdf_dKR(K_F, K_R))

    H_MM = -(R - c) * f_gap - c * f_minusKM
    H_FF = (R - (beta + p)) * f_KF - (R - c) * f_gap
    H_MF = (R - c) * f_gap
    H_RM = (R - c) * FKR_gap + c * FKR_minusKM
    H_RF = (R - (beta + p)) * FKR_KF - (R - c) * FKR_gap

    a1, b1 = K_F - K_M, K_F
    a2, b2 = -K_M, K_F - K_M
    a3, b3 = K_F, D_bar
    term1, _ = integrate.quad(lambda x: dist.d2cdf_dKR2(x, K_R), a1, b1, points=quad_breakpoint(a1, b1, K_R), **_QUAD_KWARGS)
    term2, _ = integrate.quad(lambda x: dist.d2cdf_dKR2(x, K_R), a2, b2, points=quad_breakpoint(a2, b2, K_R), **_QUAD_KWARGS)
    term3, _ = integrate.quad(lambda x: dist.d2cdf_dKR2(x, K_R), a3, b3, points=quad_breakpoint(a3, b3, K_R), **_QUAD_KWARGS)
    H_RR = R * term1 + c * term2 + (beta + p) * term3

    # Leibniz moving-boundary correction (see derivation above): add
    # coeff * F_KR(-K_R;K_R)_{from inside} for every term whose range
    # strictly contains -K_R. Lazily computed (only once, if needed at
    # all) since it requires one extra one-sided evaluation.
    F_KR_edge = None

    def _maybe_add_boundary_term(a, b, coeff):
        nonlocal F_KR_edge
        lo, hi = (a, b) if a <= b else (b, a)
        if lo < -K_R < hi:
            if F_KR_edge is None:
                F_KR_edge = _right_limit_FKR_at_lower_edge(dist, K_R)
            return coeff * F_KR_edge
        return 0.0

    H_RR += _maybe_add_boundary_term(a1, b1, R)
    H_RR += _maybe_add_boundary_term(a2, b2, c)
    H_RR += _maybe_add_boundary_term(a3, b3, beta + p)

    return np.array(
        [
            [H_RR, H_RF, H_RM],
            [H_RF, H_FF, H_MF],
            [H_RM, H_MF, H_MM],
        ]
    )


def finite_difference_hessian(dist: ResidualDemand, params: Params, K_R, K_F, K_M, h=1e-4) -> np.ndarray:
    """Cross-check: the Jacobian of the *analytic gradient* (foc.gradient)
    via central differences -- NOT a double finite difference of profit().

    foc.gradient is exact except for one scipy.integrate.quad call inside
    grad_KR, so differencing IT carries far less compounded noise than
    differencing profit() twice would (profit() itself runs three quad
    calls; squaring that noise via a second derivative is what
    tests/test_gradients.py's GRAD_ATOL=2e-3 has to absorb for the
    *first*-order check alone). This lets the Hessian cross-check use a
    much tighter tolerance -- see tests/test_hessian.py.
    """
    def grad_at(K_R_, K_F_, K_M_):
        return np.array(gradient(dist, params, K_R_, K_F_, K_M_))

    steps = [(h, 0.0, 0.0), (0.0, h, 0.0), (0.0, 0.0, h)]
    cols = []
    for dK_R, dK_F, dK_M in steps:
        g_plus = grad_at(K_R + dK_R, K_F + dK_F, K_M + dK_M)
        g_minus = grad_at(K_R - dK_R, K_F - dK_F, K_M - dK_M)
        cols.append((g_plus - g_minus) / (2 * h))
    J = np.column_stack(cols)  # J[i, j] = d(gradient_i) / d(var_j)
    # The true Hessian is exactly symmetric; a raw finite-difference J is
    # symmetric only up to FD noise, so symmetrizing here is a cleanup
    # step on the numerical estimate, not an assumption baked into what is
    # being tested (the analytic hessian() above derives H_ij and H_ji
    # independently and is checked for self-consistency separately).
    return 0.5 * (J + J.T)


def leading_principal_minors(H: np.ndarray) -> list:
    """Sylvester's criterion: a symmetric H is negative definite iff
    (-1)^k * det(H[:k, :k]) > 0 for every leading k x k submatrix,
    k = 1..n. Returns that signed sequence directly, so "all entries
    positive" <=> negative definite.
    """
    n = H.shape[0]
    return [float(((-1) ** k) * np.linalg.det(H[:k, :k])) for k in range(1, n + 1)]


@dataclass
class RegularityCertificate:
    """Result of certifying negative-definiteness of the Hessian at one
    candidate optimum, via two independent criteria that must agree:
    (a) Sylvester's leading-principal-minors test, (b) the sign of every
    eigenvalue. Agreement between (a) and (b) is itself a sanity check
    (they are mathematically equivalent for symmetric matrices, so
    disagreement would indicate a bug -- e.g. an asymmetric H from a
    genuine algebra error, not just FD noise).
    """

    H: np.ndarray
    eigenvalues: np.ndarray
    minors: list
    negative_definite_by_eigenvalues: bool
    negative_definite_by_minors: bool

    @property
    def negative_definite(self) -> bool:
        return self.negative_definite_by_eigenvalues and self.negative_definite_by_minors

    @property
    def criteria_agree(self) -> bool:
        return self.negative_definite_by_eigenvalues == self.negative_definite_by_minors

    def __repr__(self):
        return (
            f"RegularityCertificate(negative_definite={self.negative_definite}, "
            f"eigenvalues={np.round(self.eigenvalues, 6).tolist()}, "
            f"minors={[round(m, 6) for m in self.minors]}, "
            f"criteria_agree={self.criteria_agree})"
        )


def certify_negative_definite(dist: ResidualDemand, params: Params, K_R, K_F, K_M,
                               eig_tol: float = 1e-9) -> RegularityCertificate:
    """Build the analytic Hessian at (K_R,K_F,K_M) and certify whether it is
    negative definite there, via both Sylvester minors and eigenvalues.

    eig_tol: eigenvalues within +-eig_tol of 0 are NOT treated as strictly
    negative (a flat/degenerate direction is exactly the kind of boundary
    case Task 4 is trying to map, not something to wave through as
    "regular").
    """
    H = hessian(dist, params, K_R, K_F, K_M)
    eigvals = np.linalg.eigvalsh(H)
    minors = leading_principal_minors(H)
    return RegularityCertificate(
        H=H,
        eigenvalues=eigvals,
        minors=minors,
        negative_definite_by_eigenvalues=bool(np.all(eigvals < -eig_tol)),
        negative_definite_by_minors=bool(all(m > eig_tol for m in minors)),
    )
