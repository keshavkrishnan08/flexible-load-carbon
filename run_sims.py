"""
Updated Role 4 entry point: the regime map + the theory-vs-numerics
reconciliation.

Outputs:
  regime_map.png            (C_R, C_M) plane colored by boundedness regime,
                            with the C_R_circ and C_R_dagger lines.
  reconciliation.png        carbon and profit vs renewable buildout for a
                            point in the carbon-reduction window: carbon
                            rises then falls (crossover marked), profit
                            rises without bound (unboundedness).
  reconciliation.csv        the underlying buildout sweep.

Usage: .venv/bin/python run_regime_analysis.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from regimes.thresholds import Params, C_R_circ, C_R_dagger
from regimes.regime_map import boundedness_regime, classify
from regimes.reconcile import carbon_vs_buildout

BASE = dict(R=2.0, c=1.0, CF=1.0, CM=0.5, beta=1.0, p=2.0, D_bar=100.0)


def regime_map_figure():
    CRs = np.linspace(0.05, 1.2, 120)
    CMs = np.linspace(0.05, 1.2, 120)
    code = {"both_unbounded": 0, "withfcl_unbounded": 1, "both_finite": 2}
    grid = np.full((len(CMs), len(CRs)), np.nan)
    for i, CM in enumerate(CMs):
        for j, CR in enumerate(CRs):
            P = Params(CR=CR, CM=CM, **{k: v for k, v in BASE.items() if k != "CM"})
            if not P.assumption1_holds():
                continue
            grid[i, j] = code[boundedness_regime(P)]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    cmap = matplotlib.colors.ListedColormap(["#d73027", "#4575b4", "#1a9850"])
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=2,
                   extent=[CRs[0], CRs[-1], CMs[0], CMs[-1]])
    # reference C_R lines (use a representative CM for the dagger line)
    Pref = Params(CR=0.5, **BASE)
    ax.axvline(C_R_circ(Pref), color="k", ls=":", lw=1.3, label=f"C_R° = {C_R_circ(Pref):.2f} (no-FCL bound)")
    ax.axvline(C_R_dagger(Pref), color="k", ls="--", lw=1.3, label=f"C_R† = {C_R_dagger(Pref):.2f} (with-FCL bound)")
    ax.set_xlabel("renewable capital cost  C_R")
    ax.set_ylabel("FCL capital cost  C_M")
    ax.set_title("Boundedness regime map (white = Assumption 1 violated)\n"
                 "red: both unbounded   blue: with-FCL unbounded (carbon-reduction regime)   green: both finite")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig("regime_map.png", dpi=120)
    print("wrote regime_map.png")


def reconciliation_figure():
    P = Params(CR=0.5, **BASE)  # in the carbon-reduction window
    out = carbon_vs_buildout(P)
    caps = [r["K_R_cap"] for r in out["rows"]]
    carbon = [r["carbon"] for r in out["rows"]]
    profit = [r["profit"] for r in out["rows"]]
    base_carbon = out["no_fcl"]["carbon"]
    cross = out["carbon_crossover_cap"]

    with open("reconciliation.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["K_R_cap", "K_F", "K_M", "carbon", "carbon_minus_nofcl", "profit"])
        for r in out["rows"]:
            w.writerow([r["K_R_cap"], r["K_F"], r["K_M"], r["carbon"],
                        r["carbon_minus_nofcl"], r["profit"]])
    print("wrote reconciliation.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(caps, carbon, "o-", label="with-FCL carbon")
    ax1.axhline(base_carbon, color="grey", ls="--", label=f"no-FCL carbon = {base_carbon:.1f}")
    if cross:
        ax1.axvline(cross, color="crimson", ls=":", label=f"crossover ≈ {cross:.0f}")
    ax1.set_xlabel("renewable buildout K_R (cap)")
    ax1.set_ylabel("expected carbon (fossil output × c)")
    ax1.set_title("Carbon: RISES at modest buildout (utilization, Role 2's 0/210),\nFALLS past the crossover (capacity channel, Role 1)")
    ax1.legend(fontsize=8)

    ax2.plot(caps, profit, "s-", color="seagreen")
    ax2.set_xlabel("renewable buildout K_R (cap)")
    ax2.set_ylabel("with-FCL profit at the cap")
    ax2.set_title("Profit keeps rising with the cap →\nno finite optimum (C_R < C_R†): the 'infinite capacity'")
    fig.tight_layout()
    fig.savefig("reconciliation.png", dpi=120)
    print("wrote reconciliation.png")


def main():
    regime_map_figure()
    reconciliation_figure()
    P = Params(CR=0.5, **BASE)
    info = classify(P)
    print("\n--- Regime summary at C_R=0.5, C_M=0.5 ---")
    print(f"C_R° = {info['C_R_circ']:.3f},  C_R† = {info['C_R_dagger']:.3f}")
    print(f"boundedness: {info['boundedness_regime']}  (with-FCL wants infinite buildout)")
    print(f"coverage: {info['coverage_regime']}")
    print(f"carbon crossover buildout K_R ≈ {info['carbon_crossover_KR']:.1f} "
          f"(no-FCL optimum K_R ≈ 41.4)")
    print("\nReconciliation: Role 1 (carbon falls) and Role 2 (carbon never falls) are")
    print("both correct — they evaluate the program below vs above this crossover.")


if __name__ == "__main__":
    main()
