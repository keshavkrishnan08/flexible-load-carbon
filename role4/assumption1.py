"""
Bullet 4: pressure-test Assumption 1 -- are the four conditions necessary
where claimed, and what breaks if each is relaxed?

The four conditions and the object each one guards (all traceable to a
specific equation), with the consequence of relaxing it:

  A1  R > c + C_M
      Guards: eq (12) RHS = C_M/(R-c) < 1, so F(·)=C_M/(R-c) has a CDF
      solution -> an interior K_M (FCL adoption) can exist.
      Relax (R <= c+C_M): C_M/(R-c) >= 1 (or <0); no interior K_M; FCL is
      never worth acquiring. The paper's own fallback ("then we should not
      acquire hardware"). NECESSARY for any FCL adoption.

  A2  R < c + C_F + C_M
      Guards: eq (13) RHS = (β+p-c-C_F-C_M)/(β+p-R) and the interior
      K_F* in (0,D̄).
      Relax (R >= c+C_F+C_M): marginal value of fossil is >=0 even at K_F=D̄
      -> full-coverage corner (build >= D̄, blackout = 0); strict inequality
      -> infinite fossil ("dedicated computing provider", out of scope).
      NECESSARY for the interior regime; relaxing gives the (favorable but
      degenerate) full-coverage regime, not a contradiction.

  A3  β + p > c + C_F
      Guards: no-FCL cutoff φ° = (β+p-c-C_F)/(β+p-c) > 0, i.e. blackout prob
      1-φ° = C_F/(β+p-c) < 1 and K_F° > 0 (fossil backup worth building).
      Relax (β+p <= c+C_F): φ° <= 0; no fossil backup is built; the grid
      tolerates blackouts rather than pay for backup. NECESSARY for an
      interior fossil benchmark.

  A4  β + p > R
      Guards: eq (13) denominator β+p-R > 0 (F* in (0,1)); the blackout
      comparison denominator; and the full-coverage ordering R-c-C_F < C̄_M.
      Relax (β+p <= R): the eq-13 denominator flips sign, F* leaves (0,1),
      and the utility would curtail consumers to serve FCL (blackouts to
      support computing). NECESSARY; relaxing is economically perverse.

`stress_test(P)` returns, per condition, whether it currently holds, the
value of the guarded quantity, and whether nudging the parameter just past
the boundary pushes that quantity out of its valid range -- a concrete
demonstration of necessity. tests/test_assumption1.py checks all four.
"""
from __future__ import annotations

from .params import Params
from .foc import cutoff_KM_eq12, cutoff_KF_eq13, phi_circ


def _in_unit(x: float) -> bool:
    return 0.0 < x < 1.0


def stress_test(P: Params) -> dict:
    """Per-condition: holds now? guarded quantity, and does it break just past
    the boundary?"""
    out = {}

    # A1: R > c + C_M  guards  C_M/(R-c) < 1
    Pa1 = P.with_(R=P.c + 0.95 * P.CM)  # relaxed just past: R < c + C_M -> RHS > 1
    out["A1"] = {
        "statement": "R > c + C_M",
        "holds": P.A1(),
        "guards": "eq12_rhs = C_M/(R-c) in (0,1) -> interior K_M exists",
        "guarded_value": cutoff_KM_eq12(P),
        "breaks_if_relaxed": not _in_unit(cutoff_KM_eq12(Pa1)),
    }

    # A2: R < c + C_F + C_M  guards interior eq13 RHS in (0,1)
    out["A2"] = {
        "statement": "R < c + C_F + C_M",
        "holds": P.A2(),
        "guards": "eq13_rhs in (0,1) -> interior K_F in (0,D̄)",
        "guarded_value": cutoff_KF_eq13(P),
    }
    Pa2 = P.with_(R=P.c + P.CF + P.CM + 0.05)  # relaxed: R > c+C_F+C_M -> RHS > 1
    out["A2"]["breaks_if_relaxed"] = not _in_unit(cutoff_KF_eq13(Pa2))

    # A3: β+p > c + C_F  guards φ° > 0
    out["A3"] = {
        "statement": "beta + p > c + C_F",
        "holds": P.A3(),
        "guards": "phi_circ = (β+p-c-C_F)/(β+p-c) > 0 -> fossil backup built",
        "guarded_value": phi_circ(P),
    }
    Pa3 = P.with_(beta=P.c + P.CF - P.p - 0.05)  # relaxed: β+p < c+C_F -> φ° < 0
    out["A3"]["breaks_if_relaxed"] = not (phi_circ(Pa3) > 0)

    # A4: β+p > R  guards eq13 denominator > 0
    out["A4"] = {
        "statement": "beta + p > R",
        "holds": P.A4(),
        "guards": "β+p-R > 0 -> eq13 F* well-defined in (0,1); no curtailing users for FCL",
        "guarded_value": P.bp - P.R,
    }
    # relaxed β+p < R: the eq-13 denominator (β+p-R) goes <= 0 (F* ill-defined)
    Pa4 = P.with_(beta=P.R - P.p - 0.05)  # makes β+p < R
    out["A4"]["breaks_if_relaxed"] = not ((Pa4.bp - Pa4.R) > 0)
    return out


def all_necessary(P: Params) -> bool:
    """True iff every condition both holds and is shown to break when relaxed."""
    st = stress_test(P)
    return all(st[k]["holds"] and st[k]["breaks_if_relaxed"] for k in ("A1", "A2", "A3", "A4"))
