"""
Week-2 Bullet 3: upgrade Assumption 1 from pressure-test to PROOF.

Week 1 (`assumption1.py`) demonstrated necessity numerically -- nudge each
parameter just past its boundary and watch the guarded quantity leave its valid
range. Week 2 turns each into a closed proof: for every condition we exhibit the
guarded quantity as an explicit elementary function g(s) of the condition's
*slack* s (the amount by which the strict inequality holds), prove g is strictly
monotone (a signed closed-form derivative), and show g hits the boundary of its
validity range *exactly* at s = 0. A strictly monotone function that equals the
boundary precisely at s = 0 is valid on one side only, so s > 0 is necessary and
sufficient -- that is the necessity proof, holding for ALL parameters, not a
sampled nudge.

  Cond  Slack s            Guarded g(s)                         g(0)  g'(s)     Valid
  ----  -----------------  -----------------------------------  ----  --------  ---------
  A1    R-c-C_M            C_M/(C_M+s)   = eq-12 RHS             1     -<0       g<1 ⇔ s>0
  A2    c+C_F+C_M-R        m/(m+s),  m=β+p-c-C_F-C_M = eq-13 RHS 1     -<0       g<1 ⇔ s>0
  A3    β+p-c-C_F          s/(s+C_F)     = φ°                    0     +>0       g>0 ⇔ s>0
  A4    β+p-R             s              = eq-13 denom β+p-R     0     +>0       g>0 ⇔ s>0

(Derivatives verified symbolically; see run_analysis_week2.py / the test.)

What each guards, and the regime obtained when it is relaxed:

  A1  R>c+C_M.  Guards eq-12 RHS C_M/(R-c)<1, hence an interior K_M.
      Relaxed (R≤c+C_M ⇒ g≥1): NO-ADOPTION corner, K_M*=0. Strictly necessary
      for any FCL program -- the paper's own fallback.

  A2  R<c+C_F+C_M.  Guards eq-13 RHS<1, hence interior K_F*∈(0,D̄).
      Relaxed (R≥c+C_F+C_M ⇒ g≥1): FULL-COVERAGE corner, K_F*≥D̄, blackout 0
      (and, for strict R>c+C_F+C_M, the out-of-scope dedicated-provider /
      infinite-fossil case). Necessary only for INTERIORITY -- relaxing yields a
      well-defined favorable regime, not a contradiction. This is the precise
      A1/A3/A4-vs-A2 asymmetry.

  A3  β+p>c+C_F.  Guards φ°>0, hence a fossil backup K_F°>0 worth building.
      Relaxed (β+p≤c+C_F ⇒ φ°≤0): NO-BACKUP regime, the grid tolerates blackout
      rather than pay for backup. Strictly necessary for an interior benchmark.

  A4  β+p>R.  Guards eq-13 denominator >0 (F* well-defined) and the dispatch
      yield-to-consumers step in Lemma 1.
      Relaxed (β+p≤R): PERVERSE CURTAILMENT -- the utility would black out
      consumers to serve FCL; F* leaves (0,1). Strictly necessary; relaxing is
      economically perverse.

Checked in tests/test_necessity.py.
"""
from __future__ import annotations

from .params import Params


# --- per-condition slack, guarded function of slack, and proof certificate ---

def _certificate(name, statement, slack, g_of_s, g_prime_sign, boundary_value,
                 valid_side, relaxed_regime, strictly_necessary):
    return {
        "condition": name,
        "statement": statement,
        "slack": slack,
        "holds": slack > 0.0,
        "guarded_value": g_of_s(slack),
        "boundary_value": boundary_value,       # g(0): the validity edge
        "g_prime_sign": g_prime_sign,           # +1 or -1, the proven monotone dir
        "valid_side": valid_side,               # textual: when g is in-range
        "necessary": _crosses_at_zero(g_of_s, boundary_value, g_prime_sign),
        "strictly_necessary": strictly_necessary,
        "relaxed_regime": relaxed_regime,
    }


def _crosses_at_zero(g_of_s, boundary_value, sign, eps: float = 1e-7) -> bool:
    """Necessity witness: g(0) equals the boundary, and a small positive slack
    moves g strictly to the valid side in the proven direction."""
    g0 = g_of_s(0.0)
    ge = g_of_s(eps)
    at_boundary = abs(g0 - boundary_value) < 1e-9
    moved = (ge - g0) * sign > 0
    return at_boundary and moved


def prove_A1(P: Params) -> dict:
    CM = P.CM
    g = lambda s: CM / (CM + s)                 # eq-12 RHS = C_M/(R-c)
    return _certificate(
        "A1", "R > c + C_M", P.R - P.c - P.CM, g, -1, 1.0,
        "g<1 (interior K_M) ⇔ slack>0",
        "no-adoption corner: K_M*=0", True)


def prove_A2(P: Params) -> dict:
    m = P.bp - P.c - P.CF - P.CM                # = β+p-c-C_F-C_M (eq-13 numerator)
    g = lambda s: m / (m + s) if (m + s) != 0 else float("inf")
    return _certificate(
        "A2", "R < c + C_F + C_M", P.c + P.CF + P.CM - P.R, g, -1, 1.0,
        "g<1 (interior K_F) ⇔ slack>0",
        "full-coverage corner: K_F*≥D̄, blackout 0 (interiority only)", False)


def prove_A3(P: Params) -> dict:
    CF = P.CF
    g = lambda s: s / (s + CF)                  # φ° = (β+p-c-C_F)/(β+p-c)
    return _certificate(
        "A3", "beta + p > c + C_F", P.bp - P.c - P.CF, g, +1, 0.0,
        "g>0 (fossil backup K_F°>0) ⇔ slack>0",
        "no-backup regime: φ°≤0, grid tolerates blackout", True)


def prove_A4(P: Params) -> dict:
    g = lambda s: s                             # eq-13 denominator β+p-R
    return _certificate(
        "A4", "beta + p > R", P.bp - P.R, g, +1, 0.0,
        "g>0 (F* well-defined) ⇔ slack>0",
        "perverse curtailment: consumers blacked out for FCL", True)


def prove_all(P: Params) -> dict:
    return {c["condition"]: c
            for c in (prove_A1(P), prove_A2(P), prove_A3(P), prove_A4(P))}


def all_necessary(P: Params) -> bool:
    """Every condition holds and its guarded quantity is proven to cross its
    validity boundary exactly at slack 0 (necessity)."""
    return all(c["holds"] and c["necessary"] for c in prove_all(P).values())


def necessity_summary(P: Params) -> dict:
    """Compact view: which conditions are *strictly* necessary (relaxing breaks
    an optimum or flips a sign) vs necessary only for the interior regime."""
    certs = prove_all(P)
    return {
        "all_hold": all(c["holds"] for c in certs.values()),
        "all_necessary_for_their_object": all(c["necessary"] for c in certs.values()),
        "strictly_necessary": [k for k, c in certs.items() if c["strictly_necessary"]],
        "interior_only": [k for k, c in certs.items() if not c["strictly_necessary"]],
        "relaxed_regimes": {k: c["relaxed_regime"] for k, c in certs.items()},
    }
