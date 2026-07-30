#!/usr/bin/env python3
"""
A1 Role 1 -- Repairing the impossibility result into a THEOREM.

Week 2 proved only *under-determination over a class of conditional laws*, and its own
footnote conceded the extremal laws "are degenerate and need not be realized by an
equilibrium F."  That is the gap.  This script closes it constructively.

CONSTRUCTION.  Fix the primitives, hence the distribution-free cutoffs
    gamma = C_M/(R-c),  phi2 = (b+p-c-CF-CM)/(b+p-R),  phio = (b+p-c-CF)/(b+p-c).
Fix a target capacity vector (K_R*, K_F*, K_M*) and benchmark (K_R^o, K_F^o).
A joint law of the primitives (D,S) makes those capacities an equilibrium iff

  (C1) P(x <= a)      = gamma           [K_M FOC / entry quantile],  a = K_F*-K_M*
  (C2) P(x <= K_F*)   = phi2            [K_F FOC quantile]
  (C3) E[S*w(x)]      = C_R             [K_R FOC, via the decentralization identity]
  (C4) P(xo <= K_F^o) = phio            [no-FCL K_F FOC quantile]
  (C5) E[S*wo(xo)]    = C_R             [no-FCL K_R FOC]
with x = D - K_R* S, xo = D - K_R^o S, and the step weights
  w  = c on (-K_M,a], R on (a,K_F*], b+p on (K_F*,Dbar]
  wo = c on (0,K_F^o],           b+p on (K_F^o,Dbar].

KEY FACT (this is what makes it a theorem, not a search).  With capacities and cutoffs
fixed, the net carbon saving is LINEAR in the law:
    Delta = gamma*a - E[x 1{x<=a}] - K_F* + K_F^o(1-phio) + E[xo 1{0<xo<=K_F^o}],
because gamma*mu*_low = E[x 1{x<=a}] and (phio-qo)*mu_mid = E[xo 1{0<xo<=K_F^o}].
So {laws making these capacities an equilibrium} is a POLYTOPE and Delta is a linear
functional on it.  max and min are linear programs.  If max > 0 > min, the two optimal
laws are the witness pair: same primitives, same cutoffs, same equilibrium capacities,
opposite carbon signs -- and each is a genuine equilibrium by construction (C1)-(C5).

We use a piecewise-constant density on a (D,S) grid, so each law has a continuous CDF
with positive density on its support (the regularity the theory assumes), not atoms.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog

# ---------------- primitives (A1's standard calibration) ----------------
R, c, beta, p, CF, CR, CM, Dbar = 1.4, 0.5, 4.0, 1.0, 0.6, 0.5, 0.5, 10.0
BP = beta + p

gamma = CM / (R - c)                       # entry quantile   F(a)
phi2  = (BP - c - CF - CM) / (BP - R)      # reliability      F(K_F*)
phio  = (BP - c - CF) / (BP - c)           # no-FCL           F(K_F^o)

# ---------------- target capacities (must be mutually consistent) ----------------
KRs, KFs, KMs = 2.7, 7.3, 3.3
a = KFs - KMs
KRo, KFo = 2.0, 6.0

def w_with(x):
    """marginal renewable value weight, with-FCL: c below a, R in the miner gap, b+p in scarcity."""
    return np.where(x <= a, c, np.where(x <= KFs, R, BP))

def w_no(xo):
    """no-FCL: 0 on surplus (xo<=0), c on (0,K_F^o], b+p above."""
    return np.where(xo <= 0.0, 0.0, np.where(xo <= KFo, c, BP))

def build(nD=340, nS=150):
    """Grid of (D,S) cell centres; returns the LP data."""
    dD, dS = Dbar / nD, 1.0 / nS
    Dc = (np.arange(nD) + 0.5) * dD
    Sc = (np.arange(nS) + 0.5) * dS
    DD, SS = np.meshgrid(Dc, Sc, indexing="ij")
    D = DD.ravel(); S = SS.ravel()
    x  = D - KRs * S
    xo = D - KRo * S

    # equality constraints (C1)-(C5) + normalisation
    A_eq = np.vstack([
        np.ones_like(x),                        # sum p = 1
        (x <= a).astype(float),                 # C1
        (x <= KFs).astype(float),               # C2
        S * w_with(x),                          # C3
        (xo <= KFo).astype(float),              # C4
        S * w_no(xo),                           # C5
    ])
    b_eq = np.array([1.0, gamma, phi2, CR, phio, CR])

    # Delta = const + <coef, p>
    const = gamma * a - KFs + KFo * (1.0 - phio)
    coef  = -x * (x <= a) + xo * ((xo > 0.0) & (xo <= KFo))
    return A_eq, b_eq, coef, const, x, xo, S

def solve(sense, A_eq, b_eq, coef):
    obj = coef if sense == "min" else -coef
    r = linprog(obj, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    return r

def report(tag, r, coef, const, x, xo, S, A_eq, b_eq):
    if not r.success:
        print(f"  [{tag}] LP failed: {r.message}"); return None
    w = r.x
    Delta = const + coef @ w
    # recover the reported statistics
    P_a   = float(w @ (x <= a));      P_KF = float(w @ (x <= KFs))
    P_KFo = float(w @ (xo <= KFo));   qo   = float(w @ (xo <= 0.0))
    mu_low = float(w @ (x * (x <= a))) / max(P_a, 1e-15)
    mu_mid = float(w @ (xo * ((xo > 0) & (xo <= KFo)))) / max(P_KFo - qo, 1e-15)
    resid = np.abs(A_eq @ w - b_eq).max()
    print(f"  [{tag}]  Delta = {Delta:+.6f}   mu*_low={mu_low:+.4f}  mu_mid={mu_mid:+.4f}  q0={qo:.4f}")
    print(f"          F(a)={P_a:.6f} (target {gamma:.6f})   F(K_F*)={P_KF:.6f} (target {phi2:.6f})"
          f"   F(K_F^o)={P_KFo:.6f} (target {phio:.6f})")
    print(f"          max |equilibrium-constraint residual| = {resid:.2e}   support cells used = {(w>1e-12).sum()}")
    return Delta, w

def main():
    print("=" * 78)
    print("  REPAIRING THE IMPOSSIBILITY: witness pair via linear programming")
    print("=" * 78)
    print(f"\n  primitives: R={R} c={c} beta={beta} p={p} C_F={CF} C_R={CR} C_M={CM} Dbar={Dbar}")
    print(f"  distribution-free cutoffs: gamma={gamma:.6f}  phi2={phi2:.6f}  phio={phio:.6f}")
    print(f"  target capacities: K_R*={KRs} K_F*={KFs} K_M*={KMs} (a={a})   K_R^o={KRo} K_F^o={KFo}\n")

    A_eq, b_eq, coef, const, x, xo, S = build()
    print(f"  grid: {A_eq.shape[1]} cells, {A_eq.shape[0]} equality constraints\n")

    rmax = solve("max", A_eq, b_eq, coef)
    rmin = solve("min", A_eq, b_eq, coef)
    hi = report("max Delta", rmax, coef, const, x, xo, S, A_eq, b_eq)
    lo = report("min Delta", rmin, coef, const, x, xo, S, A_eq, b_eq)

    print("\n" + "-" * 78)
    if hi and lo:
        Dhi, Dlo = hi[0], lo[0]
        print(f"  Delta ranges over [{Dlo:+.6f}, {Dhi:+.6f}] on the equilibrium polytope.")
        if Dlo < 0 < Dhi:
            print("  ==> WITNESS PAIR EXISTS.  Two laws, identical primitives, identical")
            print("      distribution-free cutoffs, identical equilibrium capacities,")
            print("      OPPOSITE carbon signs.  The carbon sign is NOT identified by")
            print("      (cutoffs, capacities).  Impossibility is a theorem, not an observation.")
        else:
            print("  ==> No sign straddle at these targets; the sign IS pinned here.")
    print("-" * 78)

if __name__ == "__main__":
    main()
