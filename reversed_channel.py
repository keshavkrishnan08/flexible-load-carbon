"""
Role 3 Week 2 — Bullet 3: Reversed-channel counterexample.

Goal: construct a residual-demand distribution where the realised endpoint
shift-ratio condition FAILS,
    g(K_F*) < g(K_F* - K_M*),
and SHOW numerically that K_R* < K_R^o (channel reverses), certifying the
endpoint inequality is *necessary*, not merely sufficient.

Construction: bimodal D = 0.5 * Beta(8,2) + 0.5 * Beta(2,8) (mixture of a
strongly left-skewed and a strongly right-skewed mode). f has a deep valley
near the centre, so the shift-ratio g(x) is non-monotone and dips at the
upper threshold K_F*.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numerical_solver import (Params, outcomes, solve_no_fcl, solve_with_fcl,
                              residual)
from comparative_statics import shift_ratio_g

ROOT = Path(__file__).parent
RES = ROOT / "results"; RES.mkdir(exist_ok=True)


def bimodal_sampler(n, D_bar, rng):
    mask = rng.uniform(0, 1, n) < 0.5
    a = rng.beta(8.0, 2.0, n) * D_bar
    b = rng.beta(2.0, 8.0, n) * D_bar
    D = np.where(mask, a, b)
    eta = rng.uniform(0, 1, n)
    return D, eta


def main():
    # Pick parameters that put both thresholds inside the bimodal valley
    base = Params(R=55, c=30, p=100, beta=500, C_F=20, C_R=25, C_M=18)
    assert base.assumption1_ok()
    rng = np.random.default_rng(base.seed)
    D, eta = bimodal_sampler(base.n_samples, base.D_bar, rng)

    K_R0, K_F0 = solve_no_fcl(base, D, eta)
    K_R, K_F, K_M = solve_with_fcl(base, D, eta)
    g_hi = shift_ratio_g(D, eta, K_R, K_F)
    g_lo = shift_ratio_g(D, eta, K_R, K_F - K_M)

    no = outcomes(base, D, eta, K_R0, K_F0, 0.0)
    yes = outcomes(base, D, eta, K_R, K_F, K_M)

    row = {
        "construction": "0.5*Beta(8,2)+0.5*Beta(2,8) (bimodal)",
        "K_F_star": round(K_F, 4),
        "K_M_star": round(K_M, 4),
        "K_R_no_fcl": round(K_R0, 4),
        "K_R_fcl":    round(K_R, 4),
        "K_R_lower_than_benchmark": bool(K_R < K_R0 - 1e-4),
        "g_at_K_F":            round(g_hi, 4),
        "g_at_K_F_minus_K_M":  round(g_lo, 4),
        "endpoint_condition_holds": bool(g_hi >= g_lo - 1e-4),
        "carbon_no_fcl": round(no["carbon"], 5),
        "carbon_fcl":    round(yes["carbon"], 5),
        "delta_carbon":  round(yes["carbon"] - no["carbon"], 5),
    }

    with open(RES / "reversed_channel_counterexample.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        w.writeheader(); w.writerow(row)

    # Diagnostic: g(x) profile along the relevant x grid
    xs = np.linspace(0.05, 1.5, 30)
    prof = [{"x": round(float(x), 3),
             "g_x": round(float(shift_ratio_g(D, eta, K_R, float(x))), 4)}
            for x in xs]
    with open(RES / "reversed_channel_g_profile.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["x", "g_x"]); w.writeheader(); w.writerows(prof)

    return row


if __name__ == "__main__":
    r = main()
    print("Counterexample:")
    for k, v in r.items(): print(f"  {k}: {v}")
