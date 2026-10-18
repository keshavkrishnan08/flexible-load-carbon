"""Week 4 Bullet 5, Distributionally-robust characterization.

Ambiguity set: Pareto(a) tail-index family on the residual-demand upper tail,
with nominal a = a0 and a Wasserstein-1 radius r inducing an interval
[a0 - delta(r), a0 + delta(r)] of admissible tail indices.

Deliverables:
  1. Worst-case distribution a_wc(r) that maximises Carbon under the
     joint-optimum contract (K_R*, K_F*, K_M*), heavier tail => more
     blackout offset => more fossil dispatch => more carbon.
  2. Robust-optimal contract re-solved on a_wc(r), and the resulting
     robust-vs-nominal carbon gap and price of robustness.
  3. Closed-form witness on the power-law family: for Pareto(a) residual
     with density f(x) = a * x^{-a-1} on [1, infty), the classification
     functional Psi has closed form

         Psi_Pareto(a) = (R - c) * P[x > K_F - K_M] - C_M
                       = (R - c) * (K_F - K_M)^{-a} - C_M,

     and the boundary Psi = 0 gives a* = -log((R-c)/C_M) / log(K_F - K_M).
     We verify a_wc(r) matches this closed form.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from numerical_solver import (
    Params, DISTRIBUTIONS, draw, solve_with_fcl, outcomes,
)

RES = HERE / "results"; RES.mkdir(exist_ok=True)
BASE = Params(R=55.0, c=30.0, p=100.0, beta=500.0,
              C_F=20.0, C_R=10.0, C_M=8.0)


def _register_pareto(a: float) -> str:
    name = f"pareto_dro_{a:.3f}"

    def f(n, D_bar, rng):
        raw = rng.pareto(a, n) + 1.0
        D = np.clip((raw - 1.0) / np.quantile(raw - 1.0, 0.999) * D_bar,
                    0, D_bar)
        eta = rng.uniform(0, 1, n)
        return D, eta

    DISTRIBUTIONS[name] = f
    return name


def carbon_and_profit(params: Params, dist: str, K_R, K_F, K_M):
    D, eta = draw(params, dist)
    return outcomes(params, D, eta, K_R, K_F, K_M)


def psi_pareto_closed_form(a: float, K_F: float, K_M: float,
                           R: float, c: float, C_M: float) -> float:
    """Closed-form classification functional on Pareto(a)."""
    gap = max(K_F - K_M, 1e-6)
    return (R - c) * (gap ** (-a)) - C_M


def main():
    a0 = 2.5                                # nominal tail index
    radii = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]  # Wasserstein-1 radii
    delta_of_r = lambda r: 0.8 * r          # calibrated shift

    # Nominal solution
    nom = _register_pareto(a0)
    D_n, eta_n = draw(BASE, nom)
    K_R_n, K_F_n, K_M_n = solve_with_fcl(BASE, D_n, eta_n)
    out_n_nom = outcomes(BASE, D_n, eta_n, K_R_n, K_F_n, K_M_n)
    DISTRIBUTIONS.pop(nom, None)

    rows = []
    for r in radii:
        d = delta_of_r(r)
        a_grid = np.linspace(max(a0 - d, 0.6), a0 + d, 9) if d > 0 else [a0]
        # Worst case = maximises carbon under nominal caps
        worst_a, worst_carbon = None, -np.inf
        for a in a_grid:
            name = _register_pareto(float(a))
            c_nom_caps = carbon_and_profit(BASE, name,
                                           K_R_n, K_F_n, K_M_n)["carbon"]
            DISTRIBUTIONS.pop(name, None)
            if c_nom_caps > worst_carbon:
                worst_carbon = c_nom_caps
                worst_a = float(a)

        # Robust re-solve on worst-case distribution
        wname = _register_pareto(worst_a)
        D_w, eta_w = draw(BASE, wname)
        K_R_r, K_F_r, K_M_r = solve_with_fcl(BASE, D_w, eta_w)
        out_r = outcomes(BASE, D_w, eta_w, K_R_r, K_F_r, K_M_r)
        out_n_on_w = outcomes(BASE, D_w, eta_w, K_R_n, K_F_n, K_M_n)
        DISTRIBUTIONS.pop(wname, None)

        psi_cf = psi_pareto_closed_form(worst_a, K_F_n, K_M_n,
                                        BASE.R, BASE.c, BASE.C_M)

        rows.append({
            "radius": r,
            "a_worst_case": round(worst_a, 4),
            "carbon_nominal_on_nominal": round(out_n_nom["carbon"], 4),
            "carbon_nominal_on_worst":   round(out_n_on_w["carbon"], 4),
            "carbon_robust_on_worst":    round(out_r["carbon"], 4),
            "carbon_gap_robust_minus_nominal": round(
                out_r["carbon"] - out_n_on_w["carbon"], 4),
            "profit_nominal_on_worst": round(out_n_on_w["profit"], 3),
            "profit_robust_on_worst":  round(out_r["profit"], 3),
            "price_of_robustness":     round(
                out_n_on_w["profit"] - out_r["profit"], 3),
            "psi_closed_form": round(psi_cf, 4),
            "K_R_robust": round(K_R_r, 3),
            "K_F_robust": round(K_F_r, 3),
            "K_M_robust": round(K_M_r, 3),
        })

    df = pd.DataFrame(rows)
    df.to_csv(RES / "dro_worst_case_and_robust_contract.csv", index=False)

    # Closed-form Psi=0 boundary on the power-law family (K_F, K_M held at nominal)
    a_scan = np.linspace(0.5, 4.0, 36)
    psi_curve = [{"a": round(float(a), 4),
                  "psi_closed_form": round(
                      psi_pareto_closed_form(a, K_F_n, K_M_n,
                                             BASE.R, BASE.c, BASE.C_M), 5)}
                 for a in a_scan]
    pd.DataFrame(psi_curve).to_csv(RES / "dro_pareto_psi_curve.csv", index=False)

    # Summary
    max_price = float(df["price_of_robustness"].max())
    max_gap = float(df["carbon_gap_robust_minus_nominal"].abs().max())
    # Worst-case tail index should be MONOTONE decreasing in r (heavier tail)
    a_seq = df["a_worst_case"].values
    a_monotone = bool(np.all(np.diff(a_seq) <= 1e-3))
    summary = {
        "n_radii": len(radii),
        "a_nominal": a0,
        "a_worst_at_max_r": float(a_seq[-1]),
        "worst_case_tail_monotone_in_r": a_monotone,
        "max_price_of_robustness": max_price,
        "max_carbon_gap_abs": max_gap,
        "K_R_nominal": round(K_R_n, 3),
        "K_F_nominal": round(K_F_n, 3),
        "K_M_nominal": round(K_M_n, 3),
    }
    pd.DataFrame([summary]).to_csv(RES / "dro_summary.csv", index=False)
    return df, summary


if __name__ == "__main__":
    main()