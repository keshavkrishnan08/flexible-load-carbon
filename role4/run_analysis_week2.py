"""
Role 4 Week 2 entry point (Mechanism Design and Regimes). Produces:
  crossover.png        small-FCL K_M* vs C_M with the K_M*=K_R° crossover marked
  screening.png        d^FB vs d^SB(θ) and the information rent u(θ)
  crossover.csv        the C_M sweep behind crossover.png
and prints a summary covering all four Week 2 bullets. Also re-derives the
small-FCL crossover closed form symbolically (sympy) if available.

Usage: .venv/bin/python run_analysis_week2.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from role4.params import Params
from role4 import instrument as inst
from role4 import unified_regime as ur
from role4 import necessity as nec
from role4 import screening as scr
from role4.small_fcl import C_M_bar_b_eq62

BASE = dict(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)


def crossover_derivation():
    """Re-derive C_M^cross from the small-FCL FOCs (App. G eqs 61, 63) at the
    renewable base, symbolically. Printed so the closed form in
    unified_regime.py is auditable, not transcribed."""
    try:
        import sympy as sp
    except Exception:
        print("(sympy not installed; skipping symbolic re-derivation)")
        return
    R, c, CF, CM, bp, Dbar, KR0, KF, KM = sp.symbols(
        "R c CF CM bp Dbar KR0 KF KM", positive=True)
    L = Dbar + KR0
    F = lambda z: (z + KR0) / L
    eq61 = sp.Eq((R - c) * F(KF - KM) + c * F(-KM), CM)
    eq63 = sp.Eq((bp - R) * F(KF) + (R - c) * F(KF - KM), bp - c - CF)
    sol = sp.solve([eq61, eq63], [KF, KM], dict=True)[0]
    cm_cross = sp.factor(sp.solve(sp.Eq(sol[KM], KR0), CM)[0])
    print("symbolic C_M^cross =", cm_cross)


def crossover_figure():
    P = Params(**BASE)
    KR0 = ur.K_R_circ_uniform(P)
    cm_cross = ur.C_M_cross_uniform(P)
    cms = np.linspace(0.05, C_M_bar_b_eq62(P), 80)
    kms = [ur.small_fcl_KM_at_base(P, cm) for cm in cms]
    with open("crossover.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C_M", "K_M_star_at_base", "K_R_circ"])
        for cm, km in zip(cms, kms):
            w.writerow([cm, km, KR0])
    print("wrote crossover.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(cms, kms, "o-", ms=3, label="small-FCL K_M*(C_M) at K_R°")
    ax.axhline(KR0, color="grey", ls="--", label=f"K_R° = {KR0:.1f}")
    ax.axvline(cm_cross, color="crimson", ls=":",
               label=f"crossover C_M^cross = {cm_cross:.3f}")
    ax.set_xlabel("FCL capital cost  C_M")
    ax.set_ylabel("optimal FCL capacity  K_M*")
    ax.set_title("Small-/large-FCL crossover: K_M* = K_R°  (Week-1 open item, closed)")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig("crossover.png", dpi=120)
    print("wrote crossover.png")


def screening_figure():
    P = Params(**BASE)
    K_M = 30.0
    thetas = np.linspace(0.0, 0.95, 80)
    dfb = [scr.first_best_dispatch(P, t, K_M) for t in thetas]
    dsb = [scr.second_best_dispatch(P, t, K_M) for t in thetas]
    rent = [scr.information_rent(P, t, K_M) for t in thetas]
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.5))
    a.plot(thetas, dfb, label="d^FB (full info)")
    a.plot(thetas, dsb, label="d^SB (private S)")
    a.set_xlabel("renewable type  θ = S"); a.set_ylabel("dispatch d(θ)")
    a.set_title("Downward distortion, none at the top"); a.legend(fontsize=8)
    b.plot(thetas, rent, color="seagreen")
    b.set_xlabel("renewable type  θ = S"); b.set_ylabel("information rent u(θ)")
    b.set_title("Rent rises in type (IR binds at the bottom)")
    fig.tight_layout(); fig.savefig("screening.png", dpi=120)
    print("wrote screening.png")


def main():
    crossover_derivation()
    crossover_figure()
    screening_figure()
    P = Params(**BASE)
    print("\n=== Week 2 summary across the four bullets (C_R=0.5, C_M=0.3) ===")
    lo, hi = inst.price_richness_window(P)
    print(f"Bullet 1 (single-price instrument): window (c,β+p)=({lo:.1f},{hi:.1f}),"
          f" R={P.R} rich enough: {inst.price_is_rich_enough(P)};"
          f" state-contingent gain={inst.state_contingent_gain(P, 40.0, 30.0):.2e}")
    print(f"Bullet 2 (unified theorem): K_R°={ur.K_R_circ_uniform(P):.3f},"
          f" C_M^cross={ur.C_M_cross_uniform(P):.3f}"
          f" (numeric {ur.crossover_KM_eq_KR0_numeric(P):.3f}),"
          f" side={ur.fcl_scale_side(P)}, axes_consistent={ur.axes_consistent(P)}")
    s = nec.necessity_summary(P)
    print(f"Bullet 3 (necessity proof): strictly necessary={s['strictly_necessary']},"
          f" interior-only={s['interior_only']}, all_necessary={nec.all_necessary(P)}")
    o = scr.emission_outcome(P, 30.0)
    win = scr.carbon_window_full_vs_private(P, 30.0)
    print(f"Bullet 4 (private-S screening): E[d] FB={o['E_dispatch_FB']:.2f} ->"
          f" SB={o['E_dispatch_SB']:.2f}; R_eff={o['R_effective']:.3f};"
          f" C_R† {win['C_R_dagger_full']:.3f}->{win['C_R_dagger_private']:.3f}"
          f" (window shrinks: {win['window_shrinks']})")


if __name__ == "__main__":
    main()
