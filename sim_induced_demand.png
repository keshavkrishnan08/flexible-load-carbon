"""
Task 4: confirm the algebra numerically and produce the figures.

Outputs:
  sim_induced_demand.png    induced demand d(P): full-grid eq.(10) vs
                            partial-grid eq.(68) vs small-grid limit, with
                            the d>=0-iff-P<=Po cutoff marked.
  sim_revenue.png           revenue P*d(P): flat (exogenous) full grid vs
                            concave hump peaking at nR/4 at P=Po/2 (the
                            Task-3 break of exogeneity).
  emissions_sweep.csv       does the adapted program (eq.69) cut emissions
                            vs no-mining, swept over (C_R, d_floor)?
  emissions_heatmap.png     the same grid, visually.

Usage: .venv/bin/python run_sims.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from miner_demand.oligopoly import OligopolyParams, equilibrium_demand, miner_revenue
from miner_demand.partial_grid import (
    PartialGridParams, ingrid_demand, ingrid_revenue, revenue_peak,
    small_grid_demand, small_grid_revenue,
)
from miner_demand.emissions import EmissionParams, compare

OLI = OligopolyParams(R=1000.0, n=5)
PG = PartialGridParams(R=1000.0, n=5, m=500, Po=4.0)


def fig_induced_demand():
    Ps = np.linspace(0.05, 6.0, 400)
    full = [equilibrium_demand(OLI, P) for P in Ps]
    partial = [ingrid_demand(PG, P) for P in Ps]
    limit = [small_grid_demand(PG, P) for P in Ps]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(Ps, full, label="full grid, eq.(10):  d=(1-1/n)R/P", lw=2)
    ax.plot(Ps, partial, label="partial grid, eq.(68)", lw=2)
    ax.plot(Ps, limit, "--", label="small-grid limit (nR/Po)(1-P/Po)", lw=1.5)
    ax.axvline(PG.Po, color="grey", ls=":", label="P = Po (demand hits 0)")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("electricity price charged to miners, P")
    ax.set_ylabel("induced in-grid mining demand, d")
    ax.set_ylim(-200, 4000)
    ax.set_title("Task 1 & 3: any demand is inducible (full grid) but bounded once miners can leave")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("sim_induced_demand.png", dpi=120)
    print("wrote sim_induced_demand.png")


def fig_revenue():
    Ps = np.linspace(0.05, PG.Po, 400)
    full_rev = [miner_revenue(OLI, P) for P in Ps]          # constant
    partial_rev = [ingrid_revenue(PG, P) for P in Ps]
    limit_rev = [small_grid_revenue(PG, P) for P in Ps]
    P_star, rev_star = revenue_peak(PG)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(Ps, full_rev, label="full grid: P*d = (1-1/n)R  (exogenous, flat)", lw=2)
    ax.plot(Ps, partial_rev, label="partial grid: P*d, eq.(68)", lw=2)
    ax.plot(Ps, limit_rev, "--", label="small-grid limit: nR(P/Po)(1-P/Po)", lw=1.5)
    ax.plot([P_star], [rev_star], "o", color="crimson",
            label=f"peak nR/4={rev_star:.0f} at P=Po/2={P_star:.1f}")
    ax.set_xlabel("electricity price charged to miners, P")
    ax.set_ylabel("utility revenue from miners, P*d")
    ax.set_title("Task 2 vs 3: revenue exogeneity (flat) holds full-grid, BREAKS in the partial grid")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("sim_revenue.png", dpi=120)
    print("wrote sim_revenue.png")


def emissions_sweep():
    CR_values = np.geomspace(0.002, 0.2, 8)
    d_floors = [0.0, 5.0, 20.0, 50.0]
    rows = []
    for CR in CR_values:
        for df in d_floors:
            emi = EmissionParams(D_bar=200.0, S_bar=0.5, c=0.10, C=CR,
                                 R=1000.0, n=5, Po=4.0)
            out = compare(emi, d_floor=df)
            rows.append((CR, df, out["emission_no_mining"], out["emission_with_mining"],
                         out["carbon_lower"], out["carbon_pct_change"]))

    with open("emissions_sweep.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C_R", "d_floor", "emission_no_mining", "emission_with_mining",
                    "carbon_lower", "carbon_pct_change"])
        w.writerows(rows)
    n_lower = sum(1 for r in rows if r[4])
    print(f"wrote emissions_sweep.csv  ({n_lower}/{len(rows)} cells reduce carbon)")

    grid = np.array([[r[5] for r in rows if r[0] == CR] for CR in CR_values])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(grid, aspect="auto", origin="lower", cmap="RdYlGn_r",
                   vmin=-30, vmax=60)
    ax.set_xticks(range(len(d_floors)))
    ax.set_xticklabels([f"{d:.0f}" for d in d_floors])
    ax.set_yticks(range(len(CR_values)))
    ax.set_yticklabels([f"{v:.3f}" for v in CR_values])
    ax.set_xlabel("mining floor d_floor (fossil-fed mining when short)")
    ax.set_ylabel("renewable capital cost C_R")
    ax.set_title("Carbon % change vs no-mining under adapted program eq.(69)\n(green<0 = emissions fall)")
    fig.colorbar(im, ax=ax, label="carbon % change")
    fig.tight_layout()
    fig.savefig("emissions_heatmap.png", dpi=120)
    print("wrote emissions_heatmap.png")
    return rows


def main():
    fig_induced_demand()
    fig_revenue()
    rows = emissions_sweep()

    print("\n--- Summary ---")
    print(f"Full-grid revenue (should be constant): "
          f"{[round(miner_revenue(OLI, P), 4) for P in (0.5, 2.0, 50.0)]}")
    P_star, rev_star = revenue_peak(PG)
    print(f"Partial-grid revenue peak: nR/4 = {rev_star:.1f} at P = Po/2 = {P_star:.2f}")
    best = min(rows, key=lambda r: r[5])
    print(f"Best emissions cell: {best[5]:+.1f}% at C_R={best[0]:.3f}, d_floor={best[1]:.0f} "
          f"({'reduces' if best[4] else 'does NOT reduce'} carbon)")


if __name__ == "__main__":
    main()
