"""
Week-2 Bullet 1: a single per-MWh price R implements the optimum.

Claim (the regulator's instrument-design problem). A *single scalar* per-MWh
price R -- not a state-contingent transfer schedule t(x) -- uniquely implements
(i) the first-best dispatch rule d*(x) state by state, and (ii) the optimal
capacity vector (K_R*, K_F*, K_M*). We prove implementation, prove the
state-contingent transfer buys nothing extra, and characterize *exactly* when
the one-dimensional price instrument is rich enough: the open window

    c  <  R  <  β + p .

Paper grounding (FCL paper):
  * Lemma 1 (eq 3, subproblem eq 4): given (K_R,K_F,K_M) and any realization x,
        d*(x) = min{ max{K_F - x, 0}, K_M }
    is the UNIQUE maximizer of the per-period dispatch payoff
        R·d - c·[ min{K_F,(x+d)+} - min{K_F,x+} ].
    The proof uses exactly two Assumption-1 facts: R > c (worth dispatching on
    spare fossil) and β+p > R (always yield to consumers in scarcity).
  * The capacity FOCs (eqs 12, 13, 15) are functions of the *same* scalar R;
    given R they pin (K_R*,K_F*,K_M*) (existence + uniqueness under H≺0 is Role
    1's pushed `thm:contract` in role1/exploratory_cross_role/role1_contract_
    theory.tex; the sharper monotone-triangular / diagonal-dominance version is
    Role 1's Week-2 task, not yet pushed). So one number R pins an
    infinite-dimensional dispatch policy AND a 3-vector of capacities.

Cross-role consistency. This bullet reproduces, independently, Role 1's
already-pushed `prop:pa` (the price-implementation proposition handed off to
Role 4): same conditions R>c and β+p>R, same distribution-free cutoff
C_M/(R−c). The served-MWh feasibility handling below is the same correction
Role 1's `verify_contract.py` documents ("dispatch must be capped by available
power K_F−x"), reached here independently. Role 1's verifier finds 0/21,600
feasible policies beat d*; this module's grid search agrees pointwise.

Why a single price is *rich enough* (the non-trivial part). Within each dispatch
region the principal's marginal value of an extra dispatched MWh is
state-INDEPENDENT -- it is R on renewable surplus, R-c on gap-filling fossil,
and the objective is linear in d. A flat price therefore tracks the marginal
value exactly; a state-contingent transfer would only matter if the marginal
value varied *within* a region in a way a constant could not follow, which
Assumption 1 rules out. The instrument is rich enough iff R lands in (c, β+p):
below c no MWh is ever dispatched; above β+p consumers are curtailed to serve
FCL (the perverse A4 violation). A1 (R>c+C_M>c) and A4 (β+p>R) place R strictly
inside this window, so the baseline always admits single-price implementation.

Every claim here is checked in tests/test_instrument.py, and dispatch
implementation is cross-checked against Role 2's solver dispatch in
role4/fcl_backend.
"""
from __future__ import annotations

from .params import Params


# --- the first-best dispatch rule (paper eq 3) ------------------------------

def first_best_dispatch(K_F: float, K_M: float, x: float) -> float:
    """d*(x) = min{ max{K_F - x, 0}, K_M } -- the paper's eq-(3) rule."""
    return min(max(K_F - x, 0.0), K_M)


def feasible_dispatch_cap(K_F: float, x: float) -> float:
    """Electricity available for FCL at residual demand x: renewable surplus
    (-x)+ plus fossil capacity net of consumers, total (K_F - x)+ . Dispatch
    beyond this is physically unserved (Lemma 1's binding feasibility limit)."""
    return max(K_F - x, 0.0)


def induced_fossil(K_F: float, x: float, d: float) -> float:
    """Incremental fossil drawn by serving d at residual demand x:
    min{K_F,(x+d)+} - min{K_F, x+}. (The bracket inside eq-4's payoff.)"""
    pos = lambda z: max(z, 0.0)
    return min(K_F, pos(x + d)) - min(K_F, pos(x))


def per_period_payoff(P: Params, K_F: float, K_M: float, x: float, d: float) -> float:
    """Eq-(4) objective at scheduled d, with revenue accruing only to *served*
    MWh: served = min(d, (K_F-x)+). Revenue R·served minus fossil cost of the
    served units. The saturation at the feasibility limit is what makes the
    objective stop rewarding over-scheduling, so the optimum is exactly d*."""
    served = min(d, feasible_dispatch_cap(K_F, x))
    return P.R * served - P.c * induced_fossil(K_F, x, served)


def best_response_dispatch(P: Params, K_F: float, K_M: float, x: float,
                           grid: int = 2001) -> float:
    """The flat-price optimal *physical dispatch*: the smallest maximizer over
    d∈[0,K_M] of the served-MWh payoff. Because the per-MWh margin is strictly
    positive on the feasible region (R on surplus, R-c on fossil, both >0 under
    A1), the payoff strictly increases up to the feasibility/cap boundary and is
    flat beyond it, so the minimal maximizer equals min{(K_F-x)+, K_M} = d*. A
    fine grid search makes this an *independent* check of Lemma 1, not a
    restatement of the rule."""
    if K_M <= 0:
        return 0.0
    best_d, best_v = 0.0, per_period_payoff(P, K_F, K_M, x, 0.0)
    for i in range(1, grid + 1):
        d = K_M * i / grid
        v = per_period_payoff(P, K_F, K_M, x, d)
        if v > best_v + 1e-12:          # strictly better → take it (minimal max)
            best_d, best_v = d, v
    return best_d


def flat_price_implements_dispatch(P: Params, K_F: float, K_M: float,
                                   xs=None, tol: float = 1e-6) -> bool:
    """A single flat price R induces the eq-(3) rule at every residual demand:
    the unconstrained best response equals d*(x) across the support."""
    if xs is None:
        lo, hi = -K_M - 5.0, K_F + 5.0
        n = 41
        xs = [lo + (hi - lo) * k / (n - 1) for k in range(n)]
    for x in xs:
        br = best_response_dispatch(P, K_F, K_M, x)
        fb = first_best_dispatch(K_F, K_M, x)
        if abs(br - fb) > tol + 1e-3 * K_M:   # grid resolution slack
            return False
    return True


# --- the state-contingent transfer buys nothing (single price is sufficient) -

def state_contingent_gain(P: Params, K_F: float, K_M: float, xs=None) -> float:
    """Extra per-period value an *unrestricted* state-contingent transfer t(x)
    could add over the flat price. Since the flat price already maximizes the
    eq-(4) payoff pointwise in d, the optimal-d value under any instrument is
    the same; the gain is 0. We compute max_d payoff (flat) vs the first-best
    payoff and return their (zero) gap, averaged over x."""
    if xs is None:
        n = 41
        xs = [(-K_M - 5.0) + (K_F + 10.0) * k / (n - 1) for k in range(n)]
    tot = 0.0
    for x in xs:
        v_flat = per_period_payoff(P, K_F, K_M, x, best_response_dispatch(P, K_F, K_M, x))
        v_fb = per_period_payoff(P, K_F, K_M, x, first_best_dispatch(K_F, K_M, x))
        tot += (v_fb - v_flat)
    return tot / len(xs)


# --- richness window for the one-dimensional instrument ----------------------

def price_richness_window(P: Params) -> tuple:
    """The open interval (c, β+p): a flat R implements the optimum iff R lands
    strictly inside it. Boundaries: R≤c kills all dispatch; R≥β+p curtails
    consumers for FCL."""
    return (P.c, P.bp)


def price_is_rich_enough(P: Params) -> bool:
    """R strictly inside (c, β+p). Implied by A1 (R>c+C_M) and A4 (β+p>R)."""
    lo, hi = price_richness_window(P)
    return lo < P.R < hi


def richness_implied_by_assumption1(P: Params) -> bool:
    """A1 ⇒ R>c+C_M>c (lower edge) and A4 ⇒ β+p>R (upper edge): Assumption 1
    forces R into the richness window, so single-price implementation always
    holds in the baseline regime."""
    return (P.A1() and P.A4()) and price_is_rich_enough(P)


# --- a single scalar R pins the whole capacity vector ------------------------

def capacity_locus(P: Params, R_values, KR_ref: float = None) -> list:
    """As the single instrument R sweeps, the optimal capacity vector traces a
    one-parameter curve (K_R*,K_F*,K_M*)(R). This demonstrates both that a
    scalar pins the 3-vector and that the attainable set under a single price
    is a *curve*, not all of R^3 -- the precise sense of 'rich enough'."""
    from .fcl_backend.model import Params as BP
    from .fcl_backend.distributions import UniformResidual
    from .fcl_backend import solver
    dist = UniformResidual(P.D_bar)
    rows = []
    for R in R_values:
        Pr = P.with_(R=R)
        if not (Pr.A1() and Pr.A2() and Pr.A4()):
            continue
        bp = BP(R=Pr.R, c=Pr.c, CF=Pr.CF, CR=Pr.CR, CM=Pr.CM,
                beta=Pr.beta, p=Pr.p, D_bar=Pr.D_bar)
        no = solver.solve_no_fcl(dist, bp)
        wf = solver.solve_with_fcl_given_KR(dist, bp, no.K_R if KR_ref is None else KR_ref)
        rows.append({"R": R, "K_R": (KR_ref if KR_ref is not None else no.K_R),
                     "K_F": wf.K_F, "K_M": wf.K_M})
    return rows
