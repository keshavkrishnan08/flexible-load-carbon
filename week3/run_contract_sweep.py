"""
Entry point for Week 3 Task 3: carbon phase diagram sweep.

Compares carbon outcomes across (distribution, C_R) grid for:
  A) No-FCL benchmark
  B) Firm-optimal dispatch (greedy rule, Week 1/2 result)
  C) Carbon-optimal contract (LP optimal, Week 3 new question)

Writes phase_diagram_results.csv and phase_diagram.png.

Usage: .venv/bin/python run_contract_sweep.py [--fast]
  --fast: small grid for quick validation (~5 min)
"""
import argparse
import csv
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fcl_solver.phase_diagram import (
    run_dispatch_phase_sweep,
    run_phase_sweep,
    summarize_phase,
)

OUT_CSV = "phase_diagram_results.csv"
OUT_PNG = "phase_diagram.png"


def main(fast: bool = False):
    warnings.filterwarnings("ignore")

    if fast:
        # Fast: dispatch-only sweep (fixed firm-optimal capacities, much faster)
        CR_values = np.arange(20.0, 40.0, 4.0)
        CM_values = [56.0]
        dist_names = ["uniform", "lognormal_sigma0.28", "lognormal_sigma0.6",
                      "beta_right_skew"]
        N_inner = 300
        sweep_fn = run_dispatch_phase_sweep
    else:
        # Full: joint capacity + contract optimizer (slower but complete)
        CR_values = np.arange(8.0, 42.0, 4.0)
        CM_values = [40.0, 56.0]
        dist_names = None
        N_inner = 200
        sweep_fn = run_phase_sweep  # joint optimizer version

    print(f"Running {'fast dispatch-only' if fast else 'full joint'} sweep: "
          f"{len(CR_values)} C_R x "
          f"{'all dists' if dist_names is None else len(dist_names)} x "
          f"{len(CM_values)} C_M ...")

    cells = sweep_fn(
        CR_values=CR_values, CM_values=CM_values,
        dist_names=dist_names, N_inner=N_inner,
    )
    print(summarize_phase(cells))

    # Write CSV
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dist_name", "CR", "CM",
                          "outcome_greedy", "outcome_contract",
                          "delta_greedy", "delta_contract",
                          "sign_flip", "carbon_no_fcl",
                          "carbon_greedy", "carbon_contract"])
        for c in cells:
            writer.writerow([
                c.dist_name, c.CR, c.CM,
                c.outcome_greedy, c.outcome_contract,
                c.delta_greedy, c.delta_contract,
                c.sign_flip, c.carbon_no_fcl,
                c.carbon_greedy, c.carbon_contract,
            ])
    print(f"Grid written to {OUT_CSV}")

    # Visualize
    dist_names_used = sorted({c.dist_name for c in cells})
    CM_used = sorted({c.CM for c in cells})
    CRs = sorted({c.CR for c in cells})

    fig, axes = plt.subplots(
        len(CM_used), len(dist_names_used),
        figsize=(3 * len(dist_names_used), 3 * len(CM_used)),
        squeeze=False,
    )
    color_map = {"carbon_up": "#d73027", "carbon_neutral": "#ffffbf", "carbon_down": "#1a9850"}

    for cm_idx, CM in enumerate(CM_used):
        for d_idx, dn in enumerate(dist_names_used):
            ax = axes[cm_idx][d_idx]
            subset = [c for c in cells if c.dist_name == dn and c.CM == CM]
            if not subset:
                ax.axis("off")
                continue
            subset_sorted = sorted(subset, key=lambda c: c.CR)
            x_pos = [c.CR for c in subset_sorted]
            greedy_c = [c.delta_greedy for c in subset_sorted]
            contract_c = [c.delta_contract for c in subset_sorted]
            ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
            ax.plot(x_pos, greedy_c, marker="o", color="#d73027", label="greedy", markersize=4)
            ax.plot(x_pos, contract_c, marker="s", color="#1a9850", label="contract", markersize=4)
            ax.set_title(f"{dn}\nC_M={CM}", fontsize=7)
            ax.set_xlabel("C_R", fontsize=6)
            ax.set_ylabel("Δcarbon vs no-FCL", fontsize=6)
            ax.tick_params(labelsize=6)
            if cm_idx == 0 and d_idx == 0:
                ax.legend(fontsize=6)

    fig.suptitle(
        "Carbon Δ: greedy (red) vs carbon-optimal contract (green) vs no-FCL\n"
        "Below zero = carbon IMPROVEMENT over no-FCL",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"Phase diagram written to {OUT_PNG}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    main(fast=args.fast)
