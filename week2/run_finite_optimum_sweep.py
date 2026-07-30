"""
Entry point for Week 2 Task 2 (keystone) + Task 4: sweep (C_R, lognormal
shape sigma), classify each cell (runaway / corner_zero / saddle /
optimizer_stalled / genuine_optimum), and -- for genuine_optimum cells --
record the shift-ratio condition and carbon comparison. See
fcl_solver/finite_optimum_sweep.py's module docstring for why one sweep
serves both tasks.

Usage: .venv/bin/python run_finite_optimum_sweep.py

Runtime note: each cell runs 2 solve_with_fcl calls (4-start L-BFGS-B each)
plus, for cells that turn out to be a genuine optimum, a solve_no_fcl call
and a Hessian certificate -- roughly 5-15s/cell depending on outcome. The
default 19x4=76-cell grid takes on the order of 10-15 minutes; shrink
CR_values/sigma_values below for a quicker, coarser pass.
"""
import csv
import warnings

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fcl_solver.finite_optimum_sweep import run_sweep, summarize

warnings.filterwarnings("ignore")

OUT_CSV = "finite_optimum_sweep_results.csv"
OUT_PNG = "finite_optimum_sweep_map.png"

OUTCOME_CODE = {
    "runaway": 0,
    "corner_zero": 1,
    "saddle": 2,
    "optimizer_stalled": 3,
    "genuine_optimum": 4,
}
OUTCOME_COLORS = ["#888888", "#4472C4", "#FFC000", "#C00000", "#2E7D32"]


def main():
    CR_values = np.arange(8.0, 46.0, 2.0)
    sigma_values = [0.2, 0.28, 0.4, 0.6]

    print(f"Sweeping {len(CR_values)} C_R values x {len(sigma_values)} sigma values "
          f"({len(CR_values)*len(sigma_values)} cells)...")
    cells = run_sweep(CR_values=CR_values, sigma_values=sigma_values)
    print(summarize(cells))

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CR", "sigma", "outcome", "regime", "shift_ratio_condition",
                          "KR_increased", "carbon_lower", "carbon_change", "grad_norm",
                          "min_eigenvalue"])
        for c in cells:
            writer.writerow([c.CR, c.sigma, c.outcome, c.regime, c.shift_ratio_condition,
                              c.KR_increased, c.carbon_lower, c.carbon_change, c.grad_norm,
                              c.min_eigenvalue])
    print(f"\nFull grid written to {OUT_CSV}")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    grid = np.zeros((len(sigma_values), len(CR_values)))
    for c in cells:
        i = sigma_values.index(c.sigma)
        j = list(CR_values).index(c.CR)
        grid[i, j] = OUTCOME_CODE.get(c.outcome, -1)

    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(OUTCOME_COLORS)
    norm = BoundaryNorm(np.arange(-0.5, 5.5, 1), cmap.N)
    im = ax.imshow(grid, aspect="auto", origin="lower", cmap=cmap, norm=norm)
    ax.set_xticks(range(len(CR_values)))
    ax.set_xticklabels([f"{v:.0f}" for v in CR_values], rotation=90, fontsize=7)
    ax.set_yticks(range(len(sigma_values)))
    ax.set_yticklabels([f"{s}" for s in sigma_values])
    ax.set_xlabel("C_R")
    ax.set_ylabel("lognormal sigma (tail thickness)")
    ax.set_title("Outcome map: lognormal-primitive family, varying C_R and sigma")
    cbar = fig.colorbar(im, ax=ax, ticks=list(OUTCOME_CODE.values()))
    cbar.ax.set_yticklabels(list(OUTCOME_CODE.keys()))
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"Outcome map written to {OUT_PNG}")


if __name__ == "__main__":
    main()
