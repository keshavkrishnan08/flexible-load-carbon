#!/usr/bin/env python3
"""
A1 Role 1 -- The non-identification theorem, constructed and verified.

The witness pair must clear three bars, not one:
  (i)   both laws make the SAME capacities satisfy the equilibrium conditions,
  (ii)  both laws are REGULAR (continuous CDF, strictly positive density) -- an LP vertex
        is nearly atomic, so we impose a strictly positive floor on every cell,
  (iii) at both laws the target capacities are a genuine LOCAL MAXIMUM of the utility's
        profit (first order holds by (i); we verify the second-order condition directly).
Then Delta is computed from each law by direct state-by-state evaluation -- NOT from the
LP objective -- so the sign flip is confirmed independently of the construction.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog

R, c, beta, p, CF, CR, CM, Dbar = 1.4, 0.5, 4.0, 1.0, 0.6, 0.5, 0.5, 10.0
BP = beta + p
gamma = CM / (R - c); phi2 = (BP - c - CF - CM) / (BP - R); phio = (BP - c - CF) / (BP - c)

# straddling capacity vector found by the scan
KRs, KFs, KMs = 6.0, 1.5, 6.0
KRo, KFo = 0.5, 5.0
a = KFs - KMs

def grid(nD=170, nS=80):
    dD, dS = Dbar / nD, 1.0 / nS
    Dc = (np.arange(nD) + 0.5) * dD; Sc = (np.arange(nS) + 0.5) * dS
    DD, SS = np.meshgrid(Dc, Sc, indexing="ij")
    return DD.ravel(), SS.ravel(), dD * dS

def lp(D, S, sense, floor):
    x = D - KRs * S; xo = D - KRo * S
    w_w = np.where(x <= a, c, np.where(x <= KFs, R, BP))
    w_o = np.where(xo <= 0, 0.0, np.where(xo <= KFo, c, BP))
    A = np.vstack([np.ones_like(x), (x <= a).astype(float), (x <= KFs).astype(float),
                   S * w_w, (xo <= KFo).astype(float), S * w_o])
    b = np.array([1.0, gamma, phi2, CR, phio, CR])
    coef = -x * (x <= a) + xo * ((xo > 0) & (xo <= KFo))
    obj = coef if sense == "min" else -coef
    r = linprog(obj, A_eq=A, b_eq=b, bounds=(floor, None), method="highs")
    return r, A, b

def profit(w, D, S, KR, KF, KM):
    """State-by-state utility profit under law w (weights sum to 1)."""
    x = D - KR * S
    d = np.minimum(np.maximum(KF - x, 0.0), KM)
    fossil = np.minimum(KF, np.maximum(x + d, 0.0))
    black = np.maximum(x - KF, 0.0)
    per = p * D + R * d - c * fossil - BP * black
    return float(w @ per) - CF * KF - CR * KR - CM * KM

def carbon(w, D, S, KR, KF, KM):
    x = D - KR * S
    d = np.minimum(np.maximum(KF - x, 0.0), KM) if KM > 0 else 0.0
    return float(w @ np.minimum(KF, np.maximum(x + d, 0.0)))

def soc_check(w, D, S, KR, KF, KM, h=0.05):
    """Is (KR,KF,KM) a local max of profit under law w?  Probe the 3-D neighbourhood."""
    base = profit(w, D, S, KR, KF, KM)
    worse = 0; tot = 0
    for dR in (-h, 0, h):
        for dF in (-h, 0, h):
            for dM in (-h, 0, h):
                if dR == dF == dM == 0: continue
                tot += 1
                if profit(w, D, S, max(KR + dR, 1e-6), max(KF + dF, 1e-6), max(KM + dM, 1e-6)) <= base + 1e-9:
                    worse += 1
    return worse, tot, base

def main():
    print("=" * 80)
    print("  NON-IDENTIFICATION THEOREM: constructing and verifying the witness pair")
    print("=" * 80)
    D, S, cell = grid()
    floor = 1e-4 / len(D)          # strictly positive density on every cell => regular law
    print(f"\n  capacities  K_R*={KRs} K_F*={KFs} K_M*={KMs} (a={a})  |  K_R^o={KRo} K_F^o={KFo}")
    print(f"  cutoffs     gamma={gamma:.4f}  phi2={phi2:.4f}  phio={phio:.4f}")
    print(f"  grid {len(D)} cells, positive-density floor {floor:.2e} per cell\n")

    out = {}
    for sense in ("max", "min"):
        r, A, b = lp(D, S, sense, floor)
        if not r.success:
            print(f"  [{sense}] LP failed: {r.message}"); return
        w = r.x
        resid = np.abs(A @ w - b).max()
        # Delta computed DIRECTLY from the law, independent of the LP objective
        Cstar = carbon(w, D, S, KRs, KFs, KMs)
        Cno   = carbon(w, D, S, KRo, KFo, 0.0)
        Delta = Cno - Cstar
        pos = (w > 0).all()
        worse, tot, base = soc_check(w, D, S, KRs, KFs, KMs)
        print(f"  [{sense} Delta]")
        print(f"     Delta (direct, state-by-state) = {Delta:+.6f}")
        print(f"     E[fossil*]={Cstar:.6f}   E[fossil^o]={Cno:.6f}")
        print(f"     equilibrium-constraint residual = {resid:.2e}")
        print(f"     regular law? density>0 on every cell: {pos}   (min weight {w.min():.3e})")
        print(f"     local-max check: {worse}/{tot} neighbours not better   profit={base:.4f}")
        out[sense] = Delta

    print("\n" + "-" * 80)
    dmax, dmin = out["max"], out["min"]
    print(f"  Delta(law_1) = {dmax:+.6f}      Delta(law_2) = {dmin:+.6f}")
    if dmin < 0 < dmax:
        print("\n  THEOREM (non-identification).  Two residual-demand laws, identical primitives,")
        print("  identical distribution-free cutoffs, identical equilibrium capacities, both")
        print("  regular, both satisfying the equilibrium conditions -- and OPPOSITE carbon signs.")
        print("  Hence sign(Delta) is not a function of (cutoffs, capacities).")
    else:
        print("\n  No sign flip after imposing regularity -- the floor removed the straddle.")
    print("-" * 80)

if __name__ == "__main__":
    main()
