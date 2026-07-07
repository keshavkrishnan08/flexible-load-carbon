"""
Week-2 Bullet 2: the unified regime theorem, and the small-/large-FCL crossover
pinned as the locus K_M* = K_R°.

Two regime axes were mapped separately in Week 1 (`regimes.py`):

  Coverage axis (in C_M):  full coverage | interior/large-FCL | small-FCL
                           adoption | no adoption, ordered
                               C_M^fc < C̄_M < C̄_M^b.
  Boundedness axis (in C_R): both finite | with-FCL unbounded (the carbon
                           window) | both unbounded, split by C_R° < C_R†.

This module composes them into ONE statement (`unified_theorem`) and closes the
single open finishing item flagged in Week 1's THEORY_HARDENING.md: the
small-/large-FCL boundary K_M* = K_R°, previously located only numerically, now
has an explicit closed form under the uniform family.

The crossover (derivation in the module docstring of the test + reproduced by
sympy in run_analysis_week2.py). Solving the small-FCL FOCs (App. G eqs 61, 63)
at the renewable base K_R = K_R° for (K_F*, K_M*) and imposing K_M* = K_R° gives

    C_M^cross = (R-c)·[ D̄(β+p-c-C_F) + K_R°(R-c-C_F) ]
                ------------------------------------------ .
                        (D̄ + K_R°)(β+p-c)

For C_M < C_M^cross the optimal FCL program is *large* relative to the renewable
base (K_M* > K_R°); for C_M > C_M^cross it is *small* (K_M* < K_R°). The locus
sits inside the adoption region (C_M^cross < C̄_M^b) so it is a genuine interior
boundary, not an artifact of the no-adoption corner.

THE UNIFIED REGIME THEOREM (what `unified_theorem` certifies).
  Every Assumption-1 parameter point carries exactly one label on each of three
  independent axes -- coverage(C_M), boundedness(C_R), and FCL-scale relative to
  the renewable base (side of C_M^cross) -- and these labels are mutually
  consistent: the orderings C_M^fc < C̄_M < C̄_M^b and C_R° < C_R† always hold,
  C_M^cross lies strictly below C̄_M^b, and the boundedness label is independent
  of the coverage label (the two axes never constrain each other). The crossover
  K_M* = K_R° is the unique C_M at which the realized FCL capacity equals the
  no-FCL renewable benchmark.

Checked in tests/test_unified_regime.py (closed form vs the backend root, the
three orderings, and label consistency on a parameter grid).
"""
from __future__ import annotations

import math

from .params import Params
from .foc import C_M_bar, phi_circ
from .small_fcl import C_M_bar_b_eq62, surplus_prob_no_fcl, km_foc_residual_small
from . import regimes as rg


# --- no-FCL renewable benchmark K_R° (uniform closed form) ------------------

def K_R_circ_uniform(P: Params) -> float:
    """No-FCL optimal renewable capacity under the uniform family, K_R°.
    Matches Role 2's backend solver to machine precision (see test). Returns
    nan if the no-FCL program is itself unbounded (C_R below C_R°)."""
    denom = 2.0 * P.CR - P.CF**2 / (P.bp - P.c)
    if denom <= 0:
        return float("nan")
    return max(P.D_bar * (math.sqrt(P.c / denom) - 1.0), 0.0)


# --- the small-/large-FCL crossover  K_M* = K_R°  ---------------------------

def C_M_cross_uniform(P: Params) -> float:
    """Closed-form crossover C_M at which the small-FCL optimum K_M*(K_R°)
    equals the renewable base K_R° (uniform family). Closes Week 1's open item.

        C_M^cross = (R-c)[ D̄(β+p-c-C_F) + K_R°(R-c-C_F) ] / [ (D̄+K_R°)(β+p-c) ].
    """
    KR0 = K_R_circ_uniform(P)
    if not math.isfinite(KR0):
        return float("nan")
    L = P.D_bar + KR0
    num = (P.R - P.c) * (P.D_bar * (P.bp - P.c - P.CF) + KR0 * (P.R - P.c - P.CF))
    return num / (L * (P.bp - P.c))


def small_fcl_KM_at_base(P: Params, C_M: float = None) -> float:
    """Optimal small-FCL K_M* solved at the renewable base K_R = K_R° for a
    given C_M (default P.CM), via the uniform closed form of the App. G system.
    Used to *verify* the crossover formula and to classify the FCL scale."""
    KR0 = K_R_circ_uniform(P)
    if not math.isfinite(KR0):
        return float("nan")
    CM = P.CM if C_M is None else C_M
    L = P.D_bar + KR0
    R, c, CF, bp = P.R, P.c, P.CF, P.bp
    # sympy-derived solution of eqs (61),(63) at K_R=K_R° (see run_analysis_week2)
    KM = (CF*P.D_bar*R - CF*P.D_bar*c + CF*KR0*R - CF*KR0*c
          + CM*P.D_bar*bp - CM*P.D_bar*c + CM*KR0*bp - CM*KR0*c
          - P.D_bar*R*bp + P.D_bar*R*c + P.D_bar*bp*c - P.D_bar*c**2
          - KR0*R*bp + KR0*R*c) / (R**2 - R*bp - R*c + c**2)
    return KM


def fcl_scale_side(P: Params) -> str:
    """Which side of the crossover: 'large_fcl' if K_M* > K_R°, else
    'small_fcl', using the closed-form small-FCL K_M* at the renewable base."""
    KR0 = K_R_circ_uniform(P)
    KM = small_fcl_KM_at_base(P)
    if not (math.isfinite(KR0) and math.isfinite(KM)):
        return "undefined"
    return "large_fcl" if KM > KR0 else "small_fcl"


def crossover_KM_eq_KR0_numeric(P: Params, lo: float = 1e-4, hi: float = None,
                                iters: int = 60) -> float:
    """Locate the crossover C_M numerically (general-F ready): the C_M at which
    the small-FCL K_M* solved at K_R° equals K_R°. Bisection on C_M. This is
    the Week-1 'located numerically' object; C_M_cross_uniform gives its closed
    form, and the test pins the two together."""
    KR0 = K_R_circ_uniform(P)
    if not math.isfinite(KR0):
        return float("nan")
    if hi is None:
        hi = C_M_bar_b_eq62(P)
    g = lambda CM: small_fcl_KM_at_base(P, CM) - KR0   # decreasing in CM
    if g(lo) < 0:          # already small even at tiny C_M
        return lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --- the composed theorem ----------------------------------------------------

def axes_consistent(P: Params) -> bool:
    """The structural orderings the unified theorem asserts always hold:
    C_M^fc < C̄_M < C̄_M^b, C_R° < C_R†, and C_M^cross < C̄_M^b."""
    KR0 = K_R_circ_uniform(P)
    if not math.isfinite(KR0):
        return rg.thresholds_ordered(P) and (rg.C_R_circ(P) < rg.C_R_dagger(P))
    return (rg.thresholds_ordered(P)
            and rg.C_R_circ(P) < rg.C_R_dagger(P)
            and C_M_cross_uniform(P) < C_M_bar_b_eq62(P))


def unified_theorem(P: Params) -> dict:
    """One consistent classification across all three axes (Week-2 Bullet 2),
    extending regimes.unified_statement with the FCL-scale axis and the pinned
    crossover."""
    base = rg.unified_statement(P)
    base.update({
        "K_R_circ": K_R_circ_uniform(P),
        "fcl_scale_side": fcl_scale_side(P),
        "C_M_cross": C_M_cross_uniform(P),
        "C_M_cross_numeric": crossover_KM_eq_KR0_numeric(P),
        "axes_consistent": axes_consistent(P),
    })
    return base
