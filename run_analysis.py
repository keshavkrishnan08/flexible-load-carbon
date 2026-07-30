"""
Updated Role 4 entry point. Produces:
  regime_map.png        (C_R, C_M) plane by boundedness regime + coverage lines
  reconciliation.png    carbon & profit vs renewable buildout (crossover marked)
  reconciliation.csv    the buildout sweep
and prints a summary covering all four spec bullets.

Usage: .venv/bin/python run_analysis.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from role4.params import Params
from role4 import regimes as rg
from role4 import proposition1 as prop
from role4 import small_fcl as sf
from role4 import assumption1 as a1
from role4.reconcile import carbon_vs_buildout

BASE = dict(R=2.0, c=1.0, CF=1.0, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)


def regime_map_figure():
    CRs = np.linspace(0.05, 1.2, 110)
    CMs = np.linspace(0.02, 1.0, 110)
    code = {"both_unbounded": 0, "withfcl_unbounded": 1, "both_finite": 2}
    grid = np.full((len(CMs), len(CRs)), np.nan)
    for i, CM in enumerate(CMs):
        for j, CR in enumerate(CRs):
            P = Params(CR=CR, **{k: v for k, v in BASE.items() if k != "CM"}, CM=CM)
            if P.assumption1_holds():
                grid[i, j] = code[rg.boundedness_regime(P)]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    cmap = matplotlib.colors.ListedColormap(["#d73027", "#4575b4", "#1a9850"])
    ax.imshow(grid, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=2,
              extent=[CRs[0], CRs[-1], CMs[0], CMs[-1]])
    Pref = Params(CR=0.5, **{k: v for k, v in BASE.items() if k != "CM"}, CM=0.3)
    ax.axvline(rg.C_R_circ(Pref), color="k", ls=":", lw=1.3,
               label=f"C_R° = {rg.C_R_circ(Pref):.2f}")
    ax.axvline(rg.C_R_dagger(Pref), color="k", ls="--", lw=1.3,
               label=f"C_R† = {rg.C_R_dagger(Pref):.2f}")
    ax.axhline(rg.C_M_bar(Pref), color="white", ls="-", lw=1.0,
               label=f"C̄_M = {rg.C_M_bar(Pref):.2f}")
    ax.set_xlabel("renewable capital cost  C_R")
    ax.set_ylabel("FCL capital cost  C_M")
    ax.set_title("Boundedness regimes (white = Assumption 1 violated)\n"
                 "red: both unbounded   blue: with-FCL unbounded (carbon regime)   green: both finite")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig("regime_map.png", dpi=120)
    print("wrote regime_map.png")


def reconciliation_figure():
    P = Params(CR=0.5, **{k: v for k, v in BASE.items() if k != "CM"}, CM=0.3)
    out = carbon_vs_buildout(P)
    caps = [r["K_R_cap"] for r in out["rows"]]
    carbon = [r["carbon"] for r in out["rows"]]
    profit = [r["profit"] for r in out["rows"]]
    base = out["no_fcl"]["carbon"]; cross = out["carbon_crossover_cap"]
    with open("reconciliation.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["K_R_cap", "K_F", "K_M", "carbon", "carbon_minus_nofcl", "profit"])
        for r in out["rows"]:
            w.writerow([r["K_R_cap"], r["K_F"], r["K_M"], r["carbon"], r["carbon_minus_nofcl"], r["profit"]])
    print("wrote reconciliation.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.5))
    a.plot(caps, carbon, "o-", label="with-FCL carbon")
    a.axhline(base, color="grey", ls="--", label=f"no-FCL carbon = {base:.1f}")
    if cross: a.axvline(cross, color="crimson", ls=":", label=f"crossover ≈ {cross:.0f}")
    a.set_xlabel("renewable buildout K_R"); a.set_ylabel("expected carbon")
    a.set_title("Carbon rises (utilization, Role 2) then falls (capacity, Role 1)"); a.legend(fontsize=8)
    b.plot(caps, profit, "s-", color="seagreen")
    b.set_xlabel("renewable buildout K_R"); b.set_ylabel("with-FCL profit")
    b.set_title("Profit rises without bound → no finite optimum (C_R < C_R†)")
    fig.tight_layout(); fig.savefig("reconciliation.png", dpi=120)
    print("wrote reconciliation.png")


def main():
    regime_map_figure()
    reconciliation_figure()
    P = Params(CR=0.5, **{k: v for k, v in BASE.items() if k != "CM"}, CM=0.3)
    print("\n=== Summary across the four bullets (C_R=0.5, C_M=0.3) ===")
    print("Bullet 1 (proofs):", prop.verify_against_backend(P))
    print("Bullet 2 (small-FCL eq62): C̄_M =", round(rg.C_M_bar(P), 3),
          "-> C̄_M^b =", round(sf.C_M_bar_b_eq62(P), 3),
          "(widened by c·q° =", round(sf.adoption_widening(P), 3), ")")
    print("Bullet 3 (regimes):", rg.unified_statement(P)["coverage_regime"],
          "| C_M^fc<C̄_M<C̄_M^b ordered:", rg.thresholds_ordered(P),
          "| boundedness:", rg.boundedness_regime(P))
    st = a1.stress_test(P)
    print("Bullet 4 (Assumption 1): all four necessary:",
          all(st[k]["holds"] and st[k]["breaks_if_relaxed"] for k in ("A1", "A2", "A3", "A4")))


if __name__ == "__main__":
    main()
