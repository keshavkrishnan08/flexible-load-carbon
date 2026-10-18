"""
Week 4 entry point: the classification-functional sweep + phase diagram.

Usage:
  .venv/bin/python run_week4_sweep.py [--fast]

--fast: small grid (~10 cells) for smoke-test / CI (~5 min)
full:   large grid across 15 distributions × 3 C_R × 3 C_M (~60 cells)
"""
import argparse
import csv
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fcl_solver.classification_sweep import (
    build_distribution_library,
    run_classification_sweep,
    summarize_classification,
)
from fcl_solver.phase_diagram_w4 import sweep_cost_plane
from fcl_solver.distributions import UniformResidual


OUT_CLASS_CSV = "classification_sweep.csv"
OUT_PHASE_PNG = "phase_diagram_w4.png"


def main(fast: bool = False):
    warnings.filterwarnings("ignore")

    if fast:
        CR_values = [20.0, 25.0, 30.0]
        CM_values = [56.0]
        dist_names = ["uniform", "lognormal_sig0.28", "lognormal_sig0.6", "beta_symmetric_22"]
    else:
        CR_values = np.arange(8.0, 46.0, 6.0)
        CM_values = [40.0, 56.0, 62.0]
        dist_names = None  # all 15 distributions

    print(f"Running classification sweep ({'fast' if fast else 'full'}) "
          f"| {len(CR_values)} C_R × {len(CM_values)} C_M × "
          f"{'4' if fast else '~15'} dists ...")

    cells = run_classification_sweep(
        CR_values=CR_values, CM_values=CM_values, dist_names=dist_names,
    )
    print(summarize_classification(cells))

    # ── Write CSV ─────────────────────────────────────────────────────────
    with open(OUT_CLASS_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "dist_name", "CR", "CM", "psi", "carbon_delta",
            "sign_match", "large_fcl_regime", "corner_fcl",
            "K_R_star", "K_F_star", "K_M_star", "K_R_circ", "K_F_circ",
            "phi_circ", "q_circ", "mu_star_low", "mu_circ_mid",
        ])
        for c in cells:
            w.writerow([
                c.dist_name, c.CR, c.CM, c.psi, c.carbon_delta,
                c.sign_match, c.large_fcl_regime, c.corner_fcl,
                c.K_R_star, c.K_F_star, c.K_M_star, c.K_R_circ, c.K_F_circ,
                c.phi_circ, c.q_circ, c.mu_star_low, c.mu_circ_mid,
            ])
    print(f"Sweep written to {OUT_CLASS_CSV}")

    # ── Phase diagram for the uniform distribution ────────────────────────
    print("\nBuilding phase diagram for uniform distribution ...")
    dist_u = UniformResidual(D_bar=100)
    phase_cells = sweep_cost_plane(
        dist_u,
        CR_values=np.arange(10.0, 45.0, 5.0),
        CM_values=np.arange(32.0, 64.0, 4.0),
    )

    CRs = sorted({c.CR for c in phase_cells})
    CMs = sorted({c.CM for c in phase_cells})
    grid = np.full((len(CMs), len(CRs)), np.nan)
    for c in phase_cells:
        i = CMs.index(c.CM)
        j = CRs.index(c.CR)
        grid[i, j] = c.psi

    fig, ax = plt.subplots(figsize=(9, 5))
    vmax = max(abs(np.nanmax(grid)), abs(np.nanmin(grid)), 1.0)
    im = ax.imshow(grid, aspect="auto", origin="lower",
                    cmap="RdYlGn", vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(len(CRs)))
    ax.set_xticklabels([f"{v:.0f}" for v in CRs], fontsize=7)
    ax.set_yticks(range(len(CMs)))
    ax.set_yticklabels([f"{v:.0f}" for v in CMs], fontsize=7)
    ax.set_xlabel("C_R (renewable capital cost)")
    ax.set_ylabel("C_M (FCL hardware cost)")
    ax.set_title(
        "Classification functional Ψ, Uniform distribution\n"
        "Green (Ψ>0) = carbon improves; Red (Ψ<0) = carbon worsens\n"
        "White = carbon-neutral boundary (Ψ=0)"
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Ψ value")
    ax.contour(range(len(CRs)), range(len(CMs)), grid, levels=[0],
               colors="black", linewidths=1.5)
    fig.tight_layout()
    fig.savefig(OUT_PHASE_PNG, dpi=120)
    print(f"Phase diagram written to {OUT_PHASE_PNG}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    main(fast=parser.parse_args().fast)
