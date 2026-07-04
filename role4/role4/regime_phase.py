"""
Week-3 Bullet 3: regime-map the new objects and deliver the STITCHED carbon
phase diagram over the full cost plane, spanning both FCL regimes.

We work in the (C_M, C_R) cost plane at fixed (R, c, C_F, β, p, D̄). Three
analytic curves partition it:

  * CARBON boundary   C_R = C_R†(C_M)
        = ½[ c + (R-C_M-c)²/(R-c) + (R-c-C_F-C_M)²/(β+p-R) ].
    Carbon-DOWN below it (with-FCL program buildable and the capacity channel
    dominates, within Role 1's shape class U); carbon-UP above it.
  * REGIME-FORM line  C_M = C_M^cross   (Week-2 locus K_M* = K_R°): the optimal
    contract's K_M-FOC switches between the large-FCL form (eq 12) and the
    small-FCL form (eq 61) as C_M crosses it. This is where the CONTRACT
    "changes form".
  * ADOPTION line     C_M = C̄_M^b = C̄_M + c q°  (right edge of adoption).

THE STITCH (the Bullet-3 theorem). The carbon boundary C_R†(C_M) is ONE analytic
curve — a convex parabola in C_M — defined by the SAME closed form on both sides
of the regime-form line C_M^cross. It does not know about the small/large split,
because C_R† is the with-FCL boundedness threshold read off the interior FOCs,
whereas the regime split only changes the FORM of the K_M-FOC (Bullet 1), not the
carbon functional's value (which is C^1 across the boundary, also Bullet 1).
Consequently:

  (i)  the carbon-DOWN region {C_R < C_R†(C_M)} is a single CONNECTED set — the
       subgraph of a continuous function on an interval — that spans BOTH FCL
       regimes; it does not fracture at C_M^cross;
  (ii) its boundary C_R†(·) is SMOOTH across C_M^cross (an explicit quadratic,
       so C^∞ there — no kink in the phase boundary even though the FOC surface
       kinks); and
  (iii) the regime-form line crosses the carbon boundary TRANSVERSALLY at the
       single point (C_M^cross, C_R†(C_M^cross)).

So the phase diagram over the full cost plane is genuinely stitched: one
connected carbon-down region, one smooth boundary, crossed once by the regime
line. The boundary is CONVEX in C_M (curvature 1/(R-c)+1/(β+p-R) > 0), with its
minimum at C_M = C̄_M — i.e. the carbon-down window in C_R is NARROWEST exactly
at the adoption threshold C̄_M, and widens on either side. Convexity (not
monotonicity) is the correct global shape; connectedness of the subgraph holds
regardless, so the region is a clean, single, both-regime-spanning set.

`phase_label(P)` classifies a point; `phase_grid` renders the diagram data;
run_analysis_week3.py draws it. Checked in tests/test_regime_phase.py.
"""
from __future__ import annotations

import math

from .params import Params
from .foc import C_M_bar, phi_circ
from .regimes import C_R_dagger, C_R_circ, C_M_fc
from .small_fcl import C_M_bar_b_eq62


# --- the three analytic curves ----------------------------------------------

def carbon_boundary_C_R_dagger(P: Params, C_M: float) -> float:
    """C_R†(C_M): the carbon phase boundary as an explicit function of C_M
    (same closed form in both FCL regimes)."""
    return 0.5 * (P.c
                  + (P.R - C_M - P.c)**2 / (P.R - P.c)
                  + (P.R - P.c - P.CF - C_M)**2 / (P.bp - P.R))


def carbon_boundary_slope(P: Params, C_M: float) -> float:
    """dC_R†/dC_M (closed form). Used to certify monotonicity of the boundary."""
    return (-(P.R - C_M - P.c) / (P.R - P.c)
            - (P.R - P.c - P.CF - C_M) / (P.bp - P.R))


def carbon_boundary_curvature(P: Params) -> float:
    """d²C_R†/dC_M² = 1/(R-c) + 1/(β+p-R) > 0: the boundary is convex in C_M."""
    return 1.0 / (P.R - P.c) + 1.0 / (P.bp - P.R)


def _K_R_circ(P: Params) -> float:
    denom = 2.0 * P.CR - P.CF**2 / (P.bp - P.c)
    if denom <= 0:
        return float("nan")
    return max(P.D_bar * (math.sqrt(P.c / denom) - 1.0), 0.0)


def C_M_cross(P: Params) -> float:
    """Regime-form line C_M^cross (Week-2 crossover K_M*=K_R°, uniform closed
    form), reproduced self-contained. Where the contract's K_M-FOC changes
    form."""
    KR0 = _K_R_circ(P)
    if not math.isfinite(KR0):
        return float("nan")
    L = P.D_bar + KR0
    num = (P.R - P.c) * (P.D_bar * (P.bp - P.c - P.CF) + KR0 * (P.R - P.c - P.CF))
    return num / (L * (P.bp - P.c))


def adoption_edge(P: Params) -> float:
    """Right edge of adoption C̄_M^b (Week-1/Appendix G eq 62)."""
    return C_M_bar_b_eq62(P)


# --- point classification ----------------------------------------------------

def carbon_sign(P: Params, C_M: float, C_R: float) -> str:
    """'down' if C_R < C_R†(C_M) (carbon falls), 'up' otherwise. (Within Role
    1's shape class U, C_R† is the exact worst-case boundary.)"""
    return "down" if C_R < carbon_boundary_C_R_dagger(P, C_M) else "up"


def contract_form(P: Params, C_M: float) -> str:
    """'large_fcl' (eq-12 K_M-FOC) if C_M < C_M^cross, else 'small_fcl'
    (eq-61 form). Where the OPTIMAL CONTRACT changes form."""
    cc = C_M_cross(P)
    if not math.isfinite(cc):
        return "undefined"
    return "large_fcl" if C_M < cc else "small_fcl"


def phase_label(P: Params, C_M: float, C_R: float) -> dict:
    """Full classification of a cost-plane point: carbon sign, contract form,
    adoption status, and boundedness — the stitched map."""
    adopts = C_M < adoption_edge(P)
    return {
        "C_M": C_M, "C_R": C_R,
        "carbon": carbon_sign(P, C_M, C_R),
        "contract_form": contract_form(P, C_M),
        "adopts_fcl": adopts,
        "C_R_dagger_here": carbon_boundary_C_R_dagger(P, C_M),
        "C_M_cross": C_M_cross(P),
    }


# --- the stitch certificates -------------------------------------------------

def boundary_smooth_across_regime_line(P: Params, h: float = 1e-4) -> dict:
    """C_R†(C_M) is smooth (C^∞) across the regime-form line C_M^cross: the
    value and both one-sided derivatives agree there (it is a single quadratic).
    This is the phase-boundary half of the stitch — no kink in the boundary even
    though the FOC surface kinks (Bullet 1)."""
    cc = C_M_cross(P)
    v = carbon_boundary_C_R_dagger(P, cc)
    v_lo = carbon_boundary_C_R_dagger(P, cc - h)
    v_hi = carbon_boundary_C_R_dagger(P, cc + h)
    d_num = (v_hi - v_lo) / (2 * h)
    d_closed = carbon_boundary_slope(P, cc)
    return {
        "C_M_cross": cc,
        "C_R_dagger_at_cross": v,
        "value_symmetric_jump": abs((v_hi + v_lo) / 2 - v),
        "deriv_numeric": d_num,
        "deriv_closed_form": d_closed,
        "smooth": abs(d_num - d_closed) < 1e-4 and abs((v_hi + v_lo) / 2 - v) < 1e-6,
    }


def carbon_down_region_connected(P: Params, n: int = 400) -> dict:
    """The carbon-down region {C_R < C_R†(C_M)} over the adoption band is
    CONNECTED — the subgraph of the continuous boundary, which is single-valued
    and jump-free — and it spans both FCL regimes (the regime-form line lies
    inside the band). The boundary is CONVEX (U-shaped) with its minimum at
    C̄_M, not monotone; connectedness holds regardless. Returns the max boundary
    jump (≈0 ⇒ connected), the convexity flag, and the vertex."""
    lo = max(C_M_fc(P), 1e-4)
    hi = adoption_edge(P)
    cms = [lo + (hi - lo) * k / (n - 1) for k in range(n)]
    vals = [carbon_boundary_C_R_dagger(P, cm) for cm in cms]
    max_jump = max(abs(b - a) for a, b in zip(vals[:-1], vals[1:]))
    step = (hi - lo) / (n - 1)
    convex = carbon_boundary_curvature(P) > 0
    vertex = cms[min(range(len(vals)), key=lambda k: vals[k])]
    cc = C_M_cross(P)
    regime_inside = lo <= cc <= hi
    return {
        "max_boundary_jump": max_jump,
        "mesh_step": step,
        "connected": max_jump < 20.0 * step,     # continuous ⇒ connected subgraph
        "boundary_convex": convex,
        "boundary_min_at_C_M": vertex,           # ≈ C̄_M
        "regime_line_inside_band": regime_inside,
        "spans_both_regimes": regime_inside,
    }


def regime_line_crosses_boundary_once(P: Params) -> dict:
    """The regime-form line C_M = C_M^cross meets the carbon boundary at exactly
    one point (C_M^cross, C_R†(C_M^cross)) — a single transversal crossing (the
    regime line is vertical, the boundary is a graph over C_M, so they meet
    once)."""
    cc = C_M_cross(P)
    return {
        "crossing_C_M": cc,
        "crossing_C_R": carbon_boundary_C_R_dagger(P, cc),
        "unique_crossing": math.isfinite(cc),   # vertical line ∩ graph = 1 point
        "transversal": abs(carbon_boundary_slope(P, cc)) < float("inf"),
    }


# --- diagram data ------------------------------------------------------------

def phase_grid(P: Params, n_cm: int = 220, n_cr: int = 180,
               cm_max: float = None, cr_max: float = None) -> dict:
    """Grid of carbon labels over the (C_M, C_R) plane for plotting, plus the
    three analytic curves. Spans C_M through both FCL regimes (across
    C_M^cross)."""
    if cm_max is None:
        cm_max = 1.15 * adoption_edge(P)
    if cr_max is None:
        cr_max = 1.6 * carbon_boundary_C_R_dagger(P, 0.0)
    cms = [cm_max * (k + 0.5) / n_cm for k in range(n_cm)]
    crs = [cr_max * (k + 0.5) / n_cr for k in range(n_cr)]
    Z = [[1 if carbon_sign(P, cm, cr) == "down" else 0 for cm in cms] for cr in crs]
    boundary = [(cm, carbon_boundary_C_R_dagger(P, cm)) for cm in cms]
    return {
        "cms": cms, "crs": crs, "carbon_down_mask": Z,
        "boundary_curve": boundary,
        "C_M_cross": C_M_cross(P),
        "C_M_bar": C_M_bar(P),
        "C_M_bar_b": adoption_edge(P),
        "C_M_fc": C_M_fc(P),
        "cm_max": cm_max, "cr_max": cr_max,
    }


def phase_report(P: Params) -> dict:
    """Bullet-3 one-call summary: the stitch certificates and the curve
    orderings."""
    return {
        "boundary_smooth_across_regime": boundary_smooth_across_regime_line(P),
        "carbon_down_connected": carbon_down_region_connected(P),
        "regime_crossing": regime_line_crosses_boundary_once(P),
        "curvature_positive": carbon_boundary_curvature(P) > 0,
        "ordering": {
            "C_M_fc": C_M_fc(P), "C_M_cross": C_M_cross(P),
            "C_M_bar": C_M_bar(P), "C_M_bar_b": adoption_edge(P),
        },
    }
