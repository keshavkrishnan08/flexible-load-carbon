#!/usr/bin/env python3
"""
Does a witness pair exist ANYWHERE?  Search the capacity space.

For each candidate equilibrium capacity vector we solve two LPs over the polytope of
laws that make those capacities an equilibrium (constraints C1-C5 of
impossibility_witness.py) and record [min Delta, max Delta].

  straddle (min < 0 < max)  ->  the carbon sign is NOT identified by (cutoffs,capacities):
                                the impossibility is a theorem.
  no straddle everywhere    ->  the sign IS identified: Week 2's impossibility claim is
                                false as stated, which is itself a decisive finding.

Delta is linear in the law and the constraints are linear, so each cell is an exact LP;
there is no search heuristic inside a cell -- only the outer scan over capacities.
"""
from __future__ import annotations
import numpy as np, itertools, sys
from scipy.optimize import linprog

R, c, beta, p, CF, CR, CM, Dbar = 1.4, 0.5, 4.0, 1.0, 0.6, 0.5, 0.5, 10.0
BP = beta + p
gamma = CM / (R - c)
phi2  = (BP - c - CF - CM) / (BP - R)
phio  = (BP - c - CF) / (BP - c)

def delta_range(KRs, KFs, KMs, KRo, KFo, nD=150, nS=70):
    a = KFs - KMs
    if not (-KRs < a < KFs < Dbar):      return None
    if not (0.0 < KFo < Dbar):           return None
    if KMs < KRs:                        return None      # keep the large-FCL regime
    dD, dS = Dbar / nD, 1.0 / nS
    Dc = (np.arange(nD) + 0.5) * dD
    Sc = (np.arange(nS) + 0.5) * dS
    DD, SS = np.meshgrid(Dc, Sc, indexing="ij")
    D = DD.ravel(); S = SS.ravel()
    x  = D - KRs * S
    xo = D - KRo * S
    w_with = np.where(x <= a, c, np.where(x <= KFs, R, BP))
    w_no   = np.where(xo <= 0.0, 0.0, np.where(xo <= KFo, c, BP))
    A_eq = np.vstack([np.ones_like(x), (x <= a).astype(float), (x <= KFs).astype(float),
                      S * w_with, (xo <= KFo).astype(float), S * w_no])
    b_eq = np.array([1.0, gamma, phi2, CR, phio, CR])
    const = gamma * a - KFs + KFo * (1.0 - phio)
    coef  = -x * (x <= a) + xo * ((xo > 0.0) & (xo <= KFo))
    lo = linprog(coef,  A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    hi = linprog(-coef, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not (lo.success and hi.success): return None
    return const + coef @ lo.x, const + coef @ hi.x

def main():
    print("=" * 84)
    print("  SEARCH: does any equilibrium capacity vector leave the carbon sign unidentified?")
    print("=" * 84)
    print(f"  cutoffs  gamma={gamma:.4f}  phi2={phi2:.4f}  phio={phio:.4f}\n")
    best = None; straddles = []; feas = 0
    # capacity-substitution direction: big renewable build-out (K_R* >> K_R^o) shrinks K_F*
    KRs_g = [2.0, 4.0, 6.0, 8.0, 9.5]
    KFs_g = [1.5, 3.0, 5.0, 7.0, 9.0]
    KMs_g = [1.0, 2.0, 4.0, 6.0, 8.0]
    KRo_g = [0.5, 1.5, 3.0]
    KFo_g = [3.0, 5.0, 7.0, 9.0]
    tot = 0
    for KRs, KFs, KMs, KRo, KFo in itertools.product(KRs_g, KFs_g, KMs_g, KRo_g, KFo_g):
        if KMs < KRs or not (-KRs < KFs - KMs < KFs): continue
        if KRo >= KRs: continue                      # renewables must rise with the load
        tot += 1
        r = delta_range(KRs, KFs, KMs, KRo, KFo)
        if r is None: continue
        feas += 1
        dlo, dhi = r
        if dlo < 0 < dhi:
            straddles.append((KRs, KFs, KMs, KRo, KFo, dlo, dhi))
        if best is None or dhi > best[5]:
            best = (KRs, KFs, KMs, KRo, KFo, dhi, dlo)
    print(f"  scanned {tot} capacity vectors; {feas} admitted a law satisfying all 5 equilibrium conditions\n")
    if straddles:
        print(f"  *** {len(straddles)} STRADDLING capacity vectors found ***")
        for s in straddles[:10]:
            print(f"    K_R*={s[0]} K_F*={s[1]} K_M*={s[2]} | K_R^o={s[3]} K_F^o={s[4]}"
                  f"   Delta in [{s[5]:+.4f}, {s[6]:+.4f}]")
    else:
        print("  NO straddle found in this scan.")
        if best:
            print(f"  closest: K_R*={best[0]} K_F*={best[1]} K_M*={best[2]} | K_R^o={best[3]} K_F^o={best[4]}")
            print(f"           Delta in [{best[6]:+.4f}, {best[5]:+.4f}]   (max Delta = {best[5]:+.4f})")
    print("=" * 84)

if __name__ == "__main__":
    main()
