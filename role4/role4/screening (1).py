"""
Week-2 Bullet 4: the second-best contract when the renewable factor is private.

The paper treats residual demand x = D - K_R·S as observable and the dispatch
rule d* as self-enforcing (Lemma 1, Remark 1) -- true for Bitcoin because R is
publicly verifiable. But Section 8 / Remark 8 flag the AI-training case, where
the agent's signal is opaque and firm-specific. We formalize exactly that gap:
the principal (utility/regulator) observes demand D but NOT the renewable factor
S; since x = D - K_R·S, residual demand is the AGENT'S PRIVATE SIGNAL. We derive
the second-best screening contract and sign how its information rent shifts the
emission outcome versus the full-information benchmark.

MODEL (a faithful 1-D reduction of the dispatch problem).
  Type θ = S ∈ [0,1], density f(θ)>0, CDF F(θ), monotone hazard (default
  Uniform[0,1]). Higher θ = more renewable = lower residual demand = cheaper to
  dispatch FCL. In the carbon-relevant gap-filling region the principal's gross
  value of dispatching d units is the fossil-displacement margin (R-c)·d. The
  agent's private cost of providing dispatch d (curtailing its own compute) is

        C(d,θ) = (1-θ)·ψ(d),     ψ(d) = d²/2,

  so C_d = (1-θ)d > 0, C_θ = -ψ(d) < 0 (higher type cheaper), and the
  single-crossing condition C_{dθ} = -d < 0 holds. Dispatch is capped at K_M.

FULL INFORMATION (first best). max_d (R-c)d - C(d,θ):
        (R-c) = (1-θ)ψ'(d)  ⟹  d^FB(θ) = min{ (R-c)/(1-θ), K_M }.

SECOND BEST (private θ). With u(θ)=t(θ)-C(d(θ),θ) the agent's rent, IC gives the
envelope u'(θ)=ψ(d(θ)) ≥ 0 (rent rises in type), IR binds at the bottom u(θ_lo)=0,
and (Myerson) the principal maximizes virtual surplus pointwise:
        (R-c) = [ (1-θ) + (1-F(θ))/f(θ) ] · ψ'(d)
        ⟹  d^SB(θ) = min{ (R-c) / [ (1-θ) + (1-F)/f ], K_M }.
  Because the bracket is larger, d^SB(θ) ≤ d^FB(θ), with equality where the cap
  binds (the top) and as the inverse hazard (1-F)/f → 0 at θ=1: NO DISTORTION AT
  THE TOP, downward distortion below. Uniform[0,1] gives the clean closed form
  d^SB(θ) = ½·d^FB(θ) on the interior.

EMISSION CONSEQUENCES (the requested shift vs full information).
  (1) Short run / fixed capacities -- the utilization effect. Fossil drawn for
      FCL in the gap-filling region is proportional to dispatch; since
      d^SB ≤ d^FB, the carbon-RAISING utilization effect is DAMPENED:
      E[fossil-for-FCL]^SB ≤ E[...]^FB. Private info lowers short-run carbon, but
      only by running the program less (it also forfeits the profit/reliability
      gains).
  (2) Long run -- the capacity-substitution channel. The expected information
      rent E[u(θ)] > 0 is leaked to the agent, so the principal's CAPTURED FCL
      margin falls: the effective per-unit value feeding the renewable FOC
      (eq 15) drops from R to a virtual revenue R_eff < R. The carbon-reduction
      window is C_R < C_R†, and C_R†(R) = ½[c+(R-C_M-c)²/(R-c)+
      (R-c-C_F-C_M)²/(β+p-R)] is increasing in the FCL revenue; so a lower R_eff
      lowers C_R† and SHRINKS the window. Since the carbon reduction came
      precisely from the capacity channel (Prop 1 Step 3), the rent shrinks the
      very set of renewable-cost regimes in which it operates. (Under the
      uniform family K_R is a knife-edge corner that does not move with R -- the
      project's Week-1 finding -- so the channel is read off the threshold C_R†,
      exactly as Role 1 frames it, not off an interior K_R.)

  Net: information rent on the renewable factor erodes the carbon-reduction
  channel. The second-best emission outcome is worse than full information
  exactly in the regime where FCL was supposed to help -- a force against the
  carbon leg of the triple win, absent in the transparent-R (Bitcoin) case.

Checked in tests/test_screening.py (IC/IR, ordering, no-distortion-at-top, rent
≥0 and rising, the uniform ½-distortion closed form, the dampened utilization
effect, and K_R^SB < K_R* via the backend).
"""
from __future__ import annotations

import math

from .params import Params


# --- type distribution (default Uniform[0,1]; any monotone-hazard f works) ---

class TypeDist:
    """Type θ=S on [lo,hi] with pdf f, cdf F, inverse hazard (1-F)/f."""
    def __init__(self, lo: float = 0.0, hi: float = 1.0, pdf=None, cdf=None):
        self.lo, self.hi = lo, hi
        self._pdf = pdf or (lambda t: 1.0 / (hi - lo))
        self._cdf = cdf or (lambda t: (t - lo) / (hi - lo))

    def pdf(self, t): return self._pdf(t)
    def cdf(self, t): return self._cdf(t)

    def inv_hazard(self, t):
        f = self._pdf(t)
        return (1.0 - self._cdf(t)) / f if f > 0 else float("inf")


def _psi_prime(d: float) -> float:
    """ψ'(d) for ψ(d)=d²/2."""
    return d


def _psi(d: float) -> float:
    """ψ(d)=d²/2 (the agent's convex curtailment cost shape)."""
    return 0.5 * d * d


# --- first-best and second-best dispatch ------------------------------------

def first_best_dispatch(P: Params, theta: float, K_M: float) -> float:
    """d^FB(θ) = min{ (R-c)/(1-θ), K_M }."""
    if theta >= 1.0:
        return K_M
    return min((P.R - P.c) / (1.0 - theta), K_M)


def second_best_dispatch(P: Params, theta: float, K_M: float,
                         dist: TypeDist = None) -> float:
    """d^SB(θ) = min{ (R-c)/[ (1-θ)+(1-F)/f ], K_M }."""
    dist = dist or TypeDist()
    bracket = (1.0 - theta) + dist.inv_hazard(theta)
    if bracket <= 0:
        return K_M
    return min((P.R - P.c) / bracket, K_M)


# --- information rent (envelope) --------------------------------------------

def information_rent(P: Params, theta: float, K_M: float, dist: TypeDist = None,
                     n: int = 400) -> float:
    """u(θ) = ∫_{lo}^{θ} ψ(d^SB(s)) ds, with IR binding at the bottom."""
    dist = dist or TypeDist()
    if theta <= dist.lo:
        return 0.0
    h = (theta - dist.lo) / n
    s = 0.0
    for k in range(n + 1):
        t = dist.lo + k * h
        w = 0.5 if (k == 0 or k == n) else 1.0          # trapezoid
        s += w * _psi(second_best_dispatch(P, t, K_M, dist))
    return s * h


def expected_rent(P: Params, K_M: float, dist: TypeDist = None, n: int = 200) -> float:
    """E[u(θ)] -- the rent leaked to the agent (a transfer the principal forgoes)."""
    dist = dist or TypeDist()
    h = (dist.hi - dist.lo) / n
    tot = 0.0
    for k in range(n + 1):
        t = dist.lo + k * h
        w = 0.5 if (k == 0 or k == n) else 1.0
        tot += w * information_rent(P, t, K_M, dist) * dist.pdf(t)
    return tot * h


# --- screening properties (IC/IR) -------------------------------------------

def dispatch_is_monotone(P: Params, K_M: float, dist: TypeDist = None,
                         n: int = 60) -> bool:
    """IC requires d^SB(θ) non-decreasing in θ (single-crossing ⇒ monotone)."""
    dist = dist or TypeDist()
    prev = -1.0
    for k in range(n + 1):
        t = dist.lo + (dist.hi - dist.lo) * k / n
        d = second_best_dispatch(P, t, K_M, dist)
        if d < prev - 1e-9:
            return False
        prev = d
    return True


def no_distortion_at_top(P: Params, K_M: float, dist: TypeDist = None,
                         eps: float = 1e-3) -> bool:
    """d^SB → d^FB at the top type (inverse hazard → 0, and/or the cap binds)."""
    t = dist.hi - eps if dist else 1.0 - eps
    dist = dist or TypeDist()
    return abs(second_best_dispatch(P, t, K_M, dist)
               - first_best_dispatch(P, t, K_M)) < 1e-2 * max(K_M, 1.0)


def downward_distortion(P: Params, K_M: float, dist: TypeDist = None,
                        n: int = 60) -> bool:
    """d^SB(θ) ≤ d^FB(θ) everywhere (the second-best under-dispatches)."""
    dist = dist or TypeDist()
    for k in range(n + 1):
        t = dist.lo + (dist.hi - dist.lo) * k / n
        if second_best_dispatch(P, t, K_M, dist) > first_best_dispatch(P, t, K_M) + 1e-9:
            return False
    return True


# --- emission shift vs full information --------------------------------------

def expected_dispatch(P: Params, K_M: float, which: str = "SB",
                      dist: TypeDist = None, n: int = 200) -> float:
    """E[d(θ)] under 'FB' or 'SB'. Proportional to expected fossil drawn for FCL
    in the gap-filling region (the short-run utilization effect)."""
    dist = dist or TypeDist()
    f = (first_best_dispatch if which == "FB"
         else lambda P, t, KM: second_best_dispatch(P, t, KM, dist))
    h = (dist.hi - dist.lo) / n
    tot = 0.0
    for k in range(n + 1):
        t = dist.lo + k * h
        w = 0.5 if (k == 0 or k == n) else 1.0
        tot += w * f(P, t, K_M) * dist.pdf(t)
    return tot * h


def effective_R_capacity_channel(P: Params, K_M: float, dist: TypeDist = None,
                                 n: int = 200) -> float:
    """Effective per-unit FCL revenue that feeds the renewable FOC once the rent
    wedge is netted out: R minus the dispatch-weighted average marginal rent
    ((1-F)/f)·ψ'(d^SB). Strictly below R whenever any type is distorted."""
    dist = dist or TypeDist()
    h = (dist.hi - dist.lo) / n
    num = den = 0.0
    for k in range(n + 1):
        t = dist.lo + k * h
        w = 0.5 if (k == 0 or k == n) else 1.0
        d = second_best_dispatch(P, t, K_M, dist)
        wedge = dist.inv_hazard(t) * _psi_prime(d)
        num += w * (P.R - wedge) * d * dist.pdf(t)
        den += w * d * dist.pdf(t)
    return num / den if den > 0 else P.R


def capacity_channel_weakens(P: Params, K_M: float, dist: TypeDist = None) -> bool:
    """The rent lowers the effective FCL revenue (R_eff < R), so the renewable
    shadow value falls and K_R^SB < K_R*: the carbon-reduction channel weakens."""
    return effective_R_capacity_channel(P, K_M, dist) < P.R - 1e-9


def carbon_window_full_vs_private(P: Params, K_M: float = None,
                                  dist: TypeDist = None) -> dict:
    """The carbon-reduction window under full information (FCL revenue R) vs
    under private info (effective revenue R_eff). The window is C_R < C_R†, and
    C_R†(R) = ½[c + (R-C_M-c)²/(R-c) + (R-c-C_F-C_M)²/(β+p-R)] is increasing in
    the FCL revenue. Since the rent lowers R to R_eff, C_R† falls and the window
    shrinks: fewer renewable-cost regimes deliver the carbon reduction.

    (Under the uniform family K_R itself is a knife-edge corner that does not
    move with R -- the project's Week-1 finding -- so the capacity channel is
    correctly read off the *threshold* C_R†, exactly as Role 1 frames it, not
    off an interior K_R.)"""
    from .regimes import C_R_dagger
    dist = dist or TypeDist()
    if K_M is None:
        K_M = 0.3 * P.D_bar
    R_eff = effective_R_capacity_channel(P, K_M, dist)
    Cd_full = C_R_dagger(P)
    Cd_priv = C_R_dagger(P.with_(R=R_eff))
    return {"R": P.R, "R_eff": R_eff,
            "C_R_dagger_full": Cd_full, "C_R_dagger_private": Cd_priv,
            "window_shrinks": Cd_priv < Cd_full + 1e-12}


def emission_outcome(P: Params, K_M: float = None, dist: TypeDist = None) -> dict:
    """One-call summary of how the information rent shifts emissions vs full
    information."""
    dist = dist or TypeDist()
    if K_M is None:
        K_M = 0.3 * P.D_bar
    Ed_FB = expected_dispatch(P, K_M, "FB", dist)
    Ed_SB = expected_dispatch(P, K_M, "SB", dist)
    return {
        "E_dispatch_FB": Ed_FB,
        "E_dispatch_SB": Ed_SB,
        "dispatch_falls": Ed_SB < Ed_FB,                  # utilization dampened
        "expected_rent": expected_rent(P, K_M, dist),
        "R_effective": effective_R_capacity_channel(P, K_M, dist),
        "capacity_channel_weakens": capacity_channel_weakens(P, K_M, dist),
        "short_run_carbon_lower_SB": Ed_SB < Ed_FB,       # fewer FCL MWh on fossil
        "carbon_reduction_eroded": capacity_channel_weakens(P, K_M, dist),
    }
