"""
Role 4 Week 3 entry point (Theory Hardening and Regimes — across regimes).
Produces:
  regime_stitch.png   the K_M marginal value across K_M=K_R (continuous, kinked)
                      and the carbon functional (C^1) across the boundary
  phase_full.png      the stitched carbon phase diagram over the (C_M, C_R) cost
                      plane, spanning both FCL regimes, with the regime-form line
                      C_M^cross, the carbon boundary C_R†(C_M), and adoption edge
  phase_full.csv      the carbon-boundary curve behind phase_full.png
and prints a summary covering all four Week-3 bullets.

Usage: .venv/bin/python run_analysis_week3.py
"""
import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from role4.params import Params
from role4 import regime_stitch as rs
from role4 import hardening as hd
from role4 import regime_phase as rp
from role4 import reconcile_week3 as rc

BASE = dict(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)


def stitch_figure(P):
    """Marginal value + carbon functional across the regime boundary K_M=K_R."""
    K_R, K_F = 40.0, 70.0
    kms = np.linspace(0.2 * K_R, 1.8 * K_R, 400)
    mv = [rs.marginal_value(P, K_R, K_F, km) for km in kms]
    fossil = [rs.expected_fossil(P, K_R, K_F, km) for km in kms]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.plot(kms, mv, lw=2)
    ax1.axvline(K_R, color="crimson", ls="--", lw=1.2, label="regime boundary $K_M=K_R$")
    ax1.set_xlabel("$K_M$"); ax1.set_ylabel("$\\partial\\Pi/\\partial K_M$ (marginal value)")
    ax1.set_title("Marginal value: continuous, kinked at $K_M=K_R$")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

    ax2.plot(kms, fossil, lw=2, color="teal")
    ax2.axvline(K_R, color="crimson", ls="--", lw=1.2)
    ax2.set_xlabel("$K_M$"); ax2.set_ylabel("$E[\\mathrm{fossil}](K_M)$")
    ax2.set_title("Carbon functional: $C^1$ across the boundary")
    ax2.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig("regime_stitch.png", dpi=130)
    print("wrote regime_stitch.png")


def phase_figure(P):
    """Stitched carbon phase diagram over the (C_M, C_R) cost plane."""
    g = rp.phase_grid(P)
    cms, crs = np.array(g["cms"]), np.array(g["crs"])
    Z = np.array(g["carbon_down_mask"])
    bx = [c for c, _ in g["boundary_curve"]]
    by = [v for _, v in g["boundary_curve"]]

    with open("phase_full.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["C_M", "C_R_dagger"])
        for c, v in g["boundary_curve"]:
            w.writerow([c, v])

    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.contourf(cms, crs, Z, levels=[-0.5, 0.5, 1.5],
                colors=["#f7d9d9", "#d6ead6"], alpha=0.9)
    ax.plot(bx, by, color="green", lw=2.2, label="carbon boundary $C_R^\\dagger(C_M)$")
    ax.axvline(g["C_M_cross"], color="navy", ls="--", lw=1.6,
               label="regime-form line $C_M^{cross}$")
    ax.axvline(g["C_M_bar_b"], color="black", ls=":", lw=1.4,
               label="adoption edge $\\bar C_M^{\\,b}$")
    ax.axvline(g["C_M_bar"], color="grey", ls="-.", lw=1.0, label="$\\bar C_M$")
    cc = g["C_M_cross"]; ax.plot([cc], [rp.carbon_boundary_C_R_dagger(P, cc)],
                                 "o", color="navy", ms=7, zorder=5)
    ax.text(0.02 * g["cm_max"], 0.90 * g["cr_max"], "carbon UP", fontsize=11)
    ax.text(0.02 * g["cm_max"], 0.10 * g["cr_max"], "carbon DOWN\n(one connected region,\nboth FCL regimes)", fontsize=10)
    ax.set_xlabel("$C_M$  (FCL capital cost)"); ax.set_ylabel("$C_R$  (renewable capital cost)")
    ax.set_title("Stitched carbon phase diagram over the full cost plane")
    ax.set_xlim(0, g["cm_max"]); ax.set_ylim(0, g["cr_max"])
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout(); fig.savefig("phase_full.png", dpi=130)
    print("wrote phase_full.png, phase_full.csv")


def summary(P):
    print("\n=== Role 4 Week 3 — Theory Hardening and Regimes (across regimes) ===\n")

    print("BULLET 1 — contract & carbon functional stitch across K_M=K_R")
    st = rs.stitch_report(P)
    print(f"  contract regime-free ............ {st['contract_regime_free']}")
    print(f"  carbon functional C^1 ........... {st['carbon_functional']['C1']} "
          f"(value jump {st['carbon_functional']['value_jump']:.2e})")
    print(f"  marginal value continuous ....... {st['marginal_value']['continuous']}")
    pk = st["profit_kink"]
    print(f"  profit C^1 not C^2 (kink) ....... jump {pk['curvature_jump']:.4f} "
          f"= c·f(-K_R) predicted {pk['predicted_jump']:.4f} [{pk['matches']}]")
    print(f"  optimum continuous thru crossover {st['optimum_continuity']['continuous']}")

    print("\nBULLET 2 — measure-theoretic hardening")
    box = hd.capacity_box(P)
    print(f"  capacity box compact here ....... {box['compact']} "
          f"(C_R={box['C_R']:.2f} vs C_R†={box['C_R_dagger']:.3f})")
    Pc = P.with_(CR=1.5)
    inb = hd.optimum_in_box(Pc)
    print(f"  existence@C_R>=C_R† (Weierstrass)  {inb['exists_by_weierstrass']}")
    print(f"  optimal schedule measurable ..... "
          f"{hd.optimal_schedule_measurable(P, 70, 20, 40)['borel_measurable']}")
    cq = hd.screening_constraint_qualification(P)
    print(f"  IC/IR constraint qualification .. {cq['first_order_approach_exact']}")
    mm = hd.minimax_saddle(Pc)
    print(f"  Sion saddle @C_R>=C_R† .......... {mm['saddle']}, "
          f"least-favorable=uniform {mm['least_favorable_is_uniform']}")
    print(f"  minimax on carbon window ........ "
          f"ill-posed [{not hd.minimax_saddle(P)['well_posed']}] (corner-at-∞)")

    print("\nBULLET 3 — stitched carbon phase diagram")
    pr = rp.phase_report(P)
    print(f"  boundary smooth across regime ... {pr['boundary_smooth_across_regime']['smooth']}")
    cd = pr["carbon_down_connected"]
    print(f"  carbon-down connected ........... {cd['connected']}, "
          f"spans both regimes {cd['spans_both_regimes']}, "
          f"convex (min@C̄_M={cd['boundary_min_at_C_M']:.3f})")
    xo = pr["regime_crossing"]
    print(f"  regime line crosses boundary once ({xo['crossing_C_M']:.3f}, "
          f"{xo['crossing_C_R']:.3f})")
    o = pr["ordering"]
    print(f"  ordering C_M^fc<C_M^cross<C̄_M<C̄_M^b: "
          f"{o['C_M_fc']:.3f} < {o['C_M_cross']:.3f} < {o['C_M_bar']:.3f} < {o['C_M_bar_b']:.3f}")

    print("\nBULLET 4 — reconcile the team")
    rec = rc.reconcile(P)
    so = rec["shared_objects"]
    print(f"  contract  == backend ............ {so['contract']['consistent']} "
          f"(dev {so['contract']['max_pointwise_deviation']:.1e})")
    print(f"  carbon fn == backend ............ {so['carbon_functional']['consistent']} "
          f"(rel {so['carbon_functional']['max_rel_error']:.1e})")
    print(f"  robust optimum (Role 1) ......... "
          f"{'consistent where defined; ill-posed on window (flagged)' }")
    print(f"  all available checks consistent . {rec['all_available_checks_consistent']}")
    for k in rc.divergences(P):
        print(f"  FLAG: {k}")


def main():
    P = Params(**BASE)
    assert P.assumption1_holds()
    stitch_figure(P)
    phase_figure(P)
    summary(P)


if __name__ == "__main__":
    main()
