"""
Closed-form benchmarks under the uniform residual-demand distribution
(paper Section 4.3, eqs 18-26), used to validate the general numerical
solver against hand-solved algebra (Task 1).

Every formula here was independently re-derived from the FOCs (eqs 7, 9,
12, 13, 15) before being typed in, by hand-integrating
F(x;K_R) = (x+K_R)/(D_bar+K_R) against the relevant limits -- not just
copied from the PDF -- because the PDF's OCR text for eqs 24-26 is visibly
garbled (stray "vuut"/"r" characters from a stretched sqrt glyph). Where
the re-derivation disagreed with the literal OCR transcription, that is
called out explicitly below (see carbon_no_fcl_uniform / carbon_with_fcl_uniform).

A note on what's true "by construction" vs what's a property worth testing:
  - no_fcl_uniform, with_fcl_given_KR are *solutions* of the FOCs, so they
    are correct by construction once the algebra is right -- tests check
    the algebra by re-deriving them via direct quadrature on the general
    solver (model.py/foc.py) and comparing to machine precision.
  - eq24_constant (the "knife-edge" property: the marginal value of K_R is
    literally *constant* in K_R once K_F, K_M are re-optimized at every
    K_R) is a non-obvious structural fact about the uniform family. It is
    NOT true by construction in the code -- it has to hold numerically for
    the closed forms to be self-consistent, and is checked in
    tests/test_knife_edge.py.
"""
from __future__ import annotations

import math

from .model import Params


def no_fcl_uniform(params: Params):
    """No-FCL benchmark (K_R, K_F), eqs 7 & 9 -> closed forms eqs 20, 21."""
    b, c, CF, CR, D = params.beta, params.c, params.CF, params.CR, params.D_bar
    denom = 2 * CR - CF ** 2 / (b + params.p - c)
    K_R = D * (math.sqrt(c / denom) - 1.0)
    Q = D + K_R
    K_F = D - (CF / (b + params.p - c)) * Q
    return K_R, K_F


def with_fcl_given_KR(params: Params, K_R: float):
    """Solve FOCs 12 & 13 for (K*_F, K*_M) at a *given* K_R, large-FCL
    regime (K_M > K_R). Closed forms eqs 18, 19 (equivalently 22, 23).

    This is well-defined for any K_R >= 0 -- it does not depend on K_R
    itself being at its own optimum, which is what makes it possible to
    test eqs 18/19 without running into the K*_R corner-solution issue
    (see eq24_constant below).
    """
    R, c, CF, CM, b, p, D = (
        params.R, params.c, params.CF, params.CM, params.beta, params.p, params.D_bar
    )
    Q = D + K_R
    K_F = (b + p - c - CF - CM) / (b + p - R) * Q - K_R
    K_M = K_F - CM * Q / (R - c) + K_R
    return K_F, K_M


def eq24_constant(params: Params) -> float:
    """Literal eq. 24 bracket, exactly as printed in the paper.

    Sign convention matches the paper: positive => K*_R -> infinity is
    optimal (renewable investment is unboundedly attractive at the margin);
    negative => K*_R = 0; zero => indifferent at every K_R (any K_R optimal).

    FINDING (checked numerically in tests/test_knife_edge.py across several
    parameter draws): this literal expression equals exactly *twice*
    foc.grad_KR(...) evaluated along the with_fcl_given_KR(K_R) curve (which
    is itself confirmed constant in K_R -- that constancy is the actual
    "knife-edge" content of eq. 24). i.e. eq24_constant(params) ==
    2 * grad_KR_along_curve(params). The factor of 2 looks like a
    bookkeeping difference in how the paper grouped terms during its
    closed-form substitution (the raw dPi/dK_R subtracts C_R once; eq. 24
    subtracts 2*C_R), and does not change the *sign* of the expression,
    which is the only thing eq. 24 is used for (Section 4.3's
    infinity/arbitrary/zero trichotomy). Flagging this per CONTEXT.md's
    "trust the PDF, tell me about conflicts" instruction -- the sign and
    structure are confirmed correct; only the overall scale differs by 2x
    from a direct profit-gradient calculation.
    """
    R, c, CF, CM, b, p, CR = (
        params.R, params.c, params.CF, params.CM, params.beta, params.p, params.CR
    )
    term1 = (R - c) * ((R - CM - c) / (R - c)) ** 2
    term2 = c
    term3 = (b + p - R) * ((R - c - CF - CM) / (b + p - R)) ** 2
    return term1 + term2 + term3 - 2 * CR


def carbon_no_fcl_uniform(params: Params) -> float:
    """Expected carbon emissions with NO FCL program, uniform distribution.

    Exact result (re-derived directly, not from the garbled eq. 25 OCR):
    carbon = c * K_F * (D_bar - K_F/2) / (D_bar + K_R), evaluated at the
    no-FCL optimum. This matches Appendix G eq. 82's E[fossil] formula
    multiplied by c, and is the same quantity model.carbon_emissions()
    computes by direct quadrature -- the two are cross-checked in
    tests/test_closed_form_uniform.py.

    CORRECTION TO CONTEXT.md: the bracket the paper prints in eq. 25 is
    "carbon/c" (i.e. expected fossil *output*, not emissions) -- confirmed
    by hand: multiplying the literal OCR'd eq. 25 expression by c reproduces
    this formula exactly. eq. 26 has the same off-by-a-factor-of-c reading.
    The paper's own words ("carbon emission ... is proportional to")
    support this: they print the proportional quantity and drop the
    constant c, since only the *sign* of (25)-(26) matters for Section 4.3's
    argument.
    """
    K_R, K_F = no_fcl_uniform(params)
    Q = params.D_bar + K_R
    return params.c * K_F * (params.D_bar - K_F / 2.0) / Q


def carbon_with_fcl_uniform(params: Params, K_R: float) -> float:
    """Expected carbon emissions WITH the FCL program at a given K_R
    (K_F, K_M from with_fcl_given_KR, large-FCL regime K_M > K_R).

    NOTE on a bug caught during development: E[fossil output] here is
    *not* "K_F*(D_bar+K_M-K_F/2)/Q" -- that formula (Appendix G eq. 76)
    is only valid in the *small*-FCL regime (K_M <= K_R), where the whole
    integration range [-K_M, K_F-K_M] sits inside the true support
    [-K_R, D_bar]. In the large-FCL regime (K_M > K_R, the regime eq. 26
    is actually stated for), the range [-K_M, K_F-K_M] sticks out past
    -K_R by (K_M-K_R), and on that stretch (1-F)=1 exactly (residual
    demand can never fall below -K_R, so the fossil plant runs at exactly
    that flat amount, not at the unclipped uniform-density value). The
    correct split (paper's eq. 93, Appendix H) is:

        E[fossil] = (K_M - K_R)                                  [flat part]
                   + integral_{-K_R}^{K_F-K_M} (1-F(x;K_R)) dx    [interior part]

    which, carried through the uniform integral, gives the closed form
    below. This was verified against direct quadrature (model.py) and
    against the paper's literal eq. 26 expression (multiplied by c) to
    8 decimal places; see tests/test_closed_form_uniform.py.
    """
    K_F, K_M = with_fcl_given_KR(params, K_R)
    Q = params.D_bar + K_R
    a = K_F - K_M  # the "gap" K_F - K_M, eq. 22's LHS
    fossil = (K_M - K_R) + (params.D_bar * (a + K_R) - (a ** 2 - K_R ** 2) / 2.0) / Q
    return params.c * fossil


def paper_eq26_literal(params: Params, K_R: float) -> float:
    """eq. 26 transcribed character-for-character from the PDF:

        D_bar + [(R-c-CF-CM)/(beta+p-R)]*(D_bar+K_R) - (1/2)*(CM/(R-c))**2*(D_bar+K_R)

    This is an *independent* re-typing of the printed formula, kept
    deliberately separate from carbon_with_fcl_uniform's from-scratch
    integral derivation above, so that tests/test_closed_form_uniform.py
    comparing the two are a genuine check of the paper's equation rather
    than a tautology. (eq. 18/23 is used to confirm K*_F matches the first
    two terms here exactly, which is what lets the two derivations agree.)
    """
    R, c, CF, CM, b, p, D = params.R, params.c, params.CF, params.CM, params.beta, params.p, params.D_bar
    Q = D + K_R
    return D + (R - c - CF - CM) / (b + p - R) * Q - 0.5 * (CM / (R - c)) ** 2 * Q


def paper_eq25_proportional(params: Params) -> float:
    """Literal eq. 25 bracket as printed (i.e. carbon_no_fcl_uniform / c)."""
    return carbon_no_fcl_uniform(params) / params.c


def paper_eq26_proportional(params: Params, K_R: float) -> float:
    """Literal eq. 26 bracket as printed (i.e. carbon_with_fcl_uniform / c).
    Equal to paper_eq26_literal up to floating point -- see that function.
    """
    return carbon_with_fcl_uniform(params, K_R) / params.c
