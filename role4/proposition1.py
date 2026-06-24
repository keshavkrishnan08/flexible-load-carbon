"""
Bullet 1 (part B): walk the Proposition 1 proof (Appendix B.1) and flag gaps.

Prop 1: the utility strictly prefers the FCL program iff C_M < C̄_M, and then
(i) profit rises, (ii) blackout prob falls, (iii) carbon *may* fall. The
Appendix B.1 proof has three steps; we make each computable and check it
against Role 2's solver, then state precisely the one place the proof is not
general (Step 3), which is exactly what Role 1 hardened.

  Step 1 (profit, distribution-free): marginal profit of the first FCL unit
     at the no-FCL optimum = (R-c)φ° - C_M = C̄_M - C_M  > 0  iff  C_M < C̄_M.
  Step 2 (blackout, distribution-free): (1-F*) - (1-F°) has numerator
     C_M(β+p-c) - (R-c)(β+p-c-C_F), < 0 iff C_M < C̄_M.
  Step 3 (carbon): E[fossil] with FCL (eq 42) vs without (eq 43); the
     utilization effect raises carbon (distribution-free), the
     capacity-substitution effect (K_R* > K_R°) lowers it; net sign shown
     only for uniform/power via eqs 25-26.

GAP FLAGGED (Step 3): the net carbon sign is established in B.1 only for the
uniform (and, by footnote, power-law) family -- the general-F dominance of
the capacity channel is asserted, not proved, in B.1. Role 1 closes this with
the shift-ratio condition g(x)=F_{K_R}/f non-increasing; and Role 4's regime
analysis shows the dominance only bites once renewable buildout passes the
crossover K_R^cross (see regimes.py / reconcile.py). Steps 1-2 are fully
general; Step 3 is the conditional ("may") for a reason.
"""
from __future__ import annotations

from .params import Params
from .foc import C_M_bar, phi_circ, blackout_no_fcl, blackout_with_fcl_eq14


def step1_profit_gain(P: Params) -> float:
    """Marginal profit of the first FCL unit at the no-FCL optimum: C̄_M - C_M.
    Positive => the utility strictly gains by allowing FCL."""
    return C_M_bar(P) - P.CM


def step2_blackout_change(P: Params) -> float:
    """(1-F*) - (1-F°): change in blackout probability from allowing FCL.
    Negative => blackouts fall."""
    return blackout_with_fcl_eq14(P) - blackout_no_fcl(P)


def step2_numerator(P: Params) -> float:
    """Numerator of Step 2's difference: C_M(β+p-c) - (R-c)(β+p-c-C_F).
    Same sign as the blackout change. Negative iff C_M < C̄_M."""
    return P.CM * (P.bp - P.c) - (P.R - P.c) * (P.bp - P.c - P.CF)


def triple_win_holds(P: Params) -> dict:
    """Which parts of Prop 1 hold at these params (profit, blackout sure;
    carbon only 'may', handed to the regime/reconciliation analysis)."""
    adopt = P.CM < C_M_bar(P)
    return {
        "adopts_fcl": adopt,
        "profit_up": step1_profit_gain(P) > 0,
        "blackout_down": step2_blackout_change(P) < 0,
        "carbon_down": "conditional - see regimes.carbon_crossover_KR",
    }


# --- numerical re-verification of Steps 1-3 against Role 2's solver ----------

def verify_against_backend(P: Params) -> dict:
    """Confirm the analytic Step-1/2 predictions match the actual solver, and
    that the Step-3 utilization effect is positive at fixed capacities."""
    from .fcl_backend.model import (
        Params as BP, profit, blackout_probability, carbon_emissions,
    )
    from .fcl_backend.distributions import UniformResidual
    from .fcl_backend import solver

    bp = BP(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=P.CM, beta=P.beta, p=P.p, D_bar=P.D_bar)
    dist = UniformResidual(P.D_bar)

    no = solver.solve_no_fcl(dist, bp)
    # with-FCL at a fixed K_R = no.K_R, to isolate Steps 1-2 from K_R's corner
    wf = solver.solve_with_fcl_given_KR(dist, bp, no.K_R)

    # Step 3 utilization effect: same capacities, add FCL load -> fossil up
    K_R, K_F = no.K_R, no.K_F
    fossil_no = carbon_emissions(dist, bp, K_R, K_F, 0.0)
    fossil_fcl = carbon_emissions(dist, bp, K_R, K_F, 0.3 * P.D_bar)

    return {
        "analytic_profit_gain_sign": step1_profit_gain(P) > 0,
        "numeric_profit_gain_sign": wf.profit > no.profit,
        "analytic_blackout_down": step2_blackout_change(P) < 0,
        "numeric_blackout_down": wf.blackout_prob < no.blackout_prob,
        "utilization_raises_fossil": fossil_fcl > fossil_no,
    }
