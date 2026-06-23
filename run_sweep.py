"""
Entry point for Task 4: run the parameter sweep, print a summary, and save
a CSV + a rough heatmap chart of where (if anywhere) the carbon result
holds. See fcl_solver/sweep.py's module docstring for the full writeup of
what this sweep found and why it's set up this way.

Usage: .venv/bin/python run_sweep.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fcl_solver.sweep import DISTRIBUTIONS, run_sweep, summarize

OUT_CSV = "sweep_results.csv"
OUT_PNG = "sweep_carbon_heatmap.png"

# Robustness check across several distinct (R, c, C_F, C_M) ratios, each
# satisfying Assumption 1 with C_M comfortably below its own C_bar_M --
# confirms the main sweep's finding isn't an artifact of one parameter
# choice. (beta, p kept large enough that Assumption 1's beta+p>R holds.)
ROBUSTNESS_COMBOS = [
    dict(R=109, c=45, CF=10, CM=56, beta=190, p=10),
    dict(R=80, c=30, CF=20, CM=35, beta=140, p=20),
    dict(R=300, c=150, CF=60, CM=100, beta=350, p=100),
    dict(R=70, c=20, CF=15, CM=40, beta=120, p=30),
]


def run_robustness_check():
    print("\n--- Robustness check across 4 different (R,c,C_F,C_M) combinations ---")
    CR_values = np.geomspace(0.2, 20, 5)
    KR_cap_multiples = [1, 3, 8]
    for combo in ROBUSTNESS_COMBOS:
        cells = run_sweep(CR_values=CR_values, KR_cap_multiples=KR_cap_multiples,
                           dist_names=["uniform"], **combo)
        n_carbon = sum(c.carbon_lower for c in cells)
        best = min(cells, key=lambda c: c.carbon_pct_change)
        print(f"{combo}: carbon_lower {n_carbon}/{len(cells)}; "
              f"best={best.carbon_pct_change:+.1f}% (C_R={best.CR:.2f}, K_R_cap={best.KR_cap_mult}x)")


def main():
    CR_values = np.geomspace(0.1, 50, 10)
    KR_cap_multiples = [0.5, 1, 2, 5, 10]

    cells = run_sweep(CR_values=CR_values, KR_cap_multiples=KR_cap_multiples)

    print(summarize(cells))
    run_robustness_check()

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["distribution", "C_R", "K_R_cap_mult", "C_bar_M", "C_M",
                          "below_threshold", "profit_higher", "blackout_lower",
                          "carbon_lower", "carbon_pct_change"])
        for c in cells:
            writer.writerow([c.dist_name, c.CR, c.KR_cap_mult, c.C_bar_M, c.CM,
                              c.below_threshold, c.profit_higher, c.blackout_lower,
                              c.carbon_lower, c.carbon_pct_change])
    print(f"\nFull grid written to {OUT_CSV}")

    # Rough heatmap: carbon % change vs (C_R, K_R_cap) for each distribution,
    # one subplot per distribution family ("rough is fine" per CONTEXT.md).
    fig, axes = plt.subplots(1, len(DISTRIBUTIONS), figsize=(5 * len(DISTRIBUTIONS), 4.5), squeeze=False)
    for ax, dist_name in zip(axes[0], DISTRIBUTIONS.keys()):
        grid = np.full((len(KR_cap_multiples), len(CR_values)), np.nan)
        for c in cells:
            if c.dist_name != dist_name:
                continue
            i = KR_cap_multiples.index(c.KR_cap_mult)
            j = list(CR_values).index(c.CR)
            grid[i, j] = c.carbon_pct_change

        im = ax.imshow(grid, aspect="auto", origin="lower", cmap="RdYlGn_r",
                        vmin=-50, vmax=200)
        ax.set_xticks(range(len(CR_values)))
        ax.set_xticklabels([f"{v:.1f}" for v in CR_values], rotation=90, fontsize=7)
        ax.set_yticks(range(len(KR_cap_multiples)))
        ax.set_yticklabels([f"{m}x" for m in KR_cap_multiples])
        ax.set_xlabel("C_R")
        ax.set_ylabel("K_R cap (x D_bar)")
        ax.set_title(dist_name)
        fig.colorbar(im, ax=ax, label="carbon % change vs no-FCL\n(green<0=improves, red>0=worsens)")

    fig.suptitle("Carbon change from introducing FCL, by C_R and renewable-capacity cap "
                  "(green would mean improvement -- none found in this sweep)")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"Heatmap written to {OUT_PNG}")


if __name__ == "__main__":
    main()
