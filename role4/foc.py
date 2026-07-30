"""
Bullet 1 (part A): re-verify the three FOC derivations, eqs (12), (13), (15).

We restate each FOC from the interior-regime profit (paper eq. 10),

    Pi = p E[D] + R ∫_{K_F-K_M}^{K_F} F dx - c ∫_{-K_M}^{K_F-K_M}(1-F) dx
                 - (β+p) ∫_{K_F}^{D̄}(1-F) dx - C_F K_F - C_R K_R - C_M K_M,

and expose the equilibrium CDF *values* (Lemma 2 / paper's distribution-free
cutoffs) that the carbon argument later rests on. Every cutoff is checked
against Role 2's solver (the FOCs solved numerically) in tests/test_foc.py.

  eq (11)  marginal value of K_M = (R-c) F(K_F-K_M;K_R) - C_M
  eq (12)  F(K_F*-K_M*;K_R*) = C_M/(R-c)                 [RHS in (0,1) by A1]
  eq (13)  F(K_F*;K_R*) = (β+p-c-C_F-C_M)/(β+p-R)         [interior, by A2,A4]
  eq (14)  blackout prob = 1 - F(K_F*) = (c+C_F+C_M-R)/(β+p-R)
  eq (15)  marginal value of K_R = R∫_{K_F-K_M}^{K_F}F_KR + c∫_{-K_M}^{K_F-K_M}F_KR
                                   + (β+p)∫_{K_F}^{D̄}F_KR - C_R
           (weight R on the FCL dispatch band vs c without FCL -> K_R* > K_R°)

No-FCL benchmark (K_M = 0), paper eq. (7):
  F(K_F°;K_R°) = φ° = (β+p-c-C_F)/(β+p-c).
"""
from __future__ import annotations

from .params import Params


# --- equilibrium CDF cutoffs (the values the FOCs pin, independent of shape) -

def cutoff_KM_eq12(P: Params) -> float:
    """RHS of eq (12): F(K_F*-K_M*;K_R*) = C_M/(R-c)."""
    return P.CM / (P.R - P.c)


def cutoff_KF_eq13(P: Params) -> float:
    """RHS of eq (13): F(K_F*;K_R*) = (β+p-c-C_F-C_M)/(β+p-R)."""
    return (P.bp - P.c - P.CF - P.CM) / (P.bp - P.R)


def blackout_with_fcl_eq14(P: Params) -> float:
    """eq (14): blackout prob with FCL = (c+C_F+C_M-R)/(β+p-R)."""
    return (P.c + P.CF + P.CM - P.R) / (P.bp - P.R)


def phi_circ(P: Params) -> float:
    """No-FCL cutoff φ° = F(K_F°;K_R°) = (β+p-c-C_F)/(β+p-c) (eq 7)."""
    return (P.bp - P.c - P.CF) / (P.bp - P.c)


def blackout_no_fcl(P: Params) -> float:
    """No-FCL blackout prob = 1 - φ° = C_F/(β+p-c)."""
    return P.CF / (P.bp - P.c)


def C_M_bar(P: Params) -> float:
    """Large-FCL adoption threshold C̄_M = (R-c)φ° (eq 27)."""
    return (P.R - P.c) * phi_circ(P)


# --- structural facts the FOCs guarantee under Assumption 1 ------------------

def eq12_rhs_in_unit_interval(P: Params) -> bool:
    """A1 (R>c+C_M) <=> C_M/(R-c) < 1, so eq (12) has a CDF solution."""
    r = cutoff_KM_eq12(P)
    return 0.0 < r < 1.0


def eq13_rhs_in_unit_interval(P: Params) -> bool:
    """A2 & A4 <=> (β+p-c-C_F-C_M)/(β+p-R) in (0,1): interior K_F* exists."""
    r = cutoff_KF_eq13(P)
    return 0.0 < r < 1.0


def KM_nonneg_iff_adoption(P: Params) -> bool:
    """K_M* >= 0 iff C_M <= C̄_M (eq 12 vs eq 13 comparison)."""
    return cutoff_KM_eq12(P) <= cutoff_KF_eq13(P) + 1e-15
