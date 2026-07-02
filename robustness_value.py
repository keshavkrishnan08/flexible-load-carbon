"""Week 3 Bullet 3 — Value of distributional robustness.

Ambiguity set: a Beta(a_0 + s, b_0 - s) family indexed by a Wasserstein-1
radius r(s) = |E[F_s] - E[F_0]|. For each radius we compute the worst-case
(over s in ±s_max) carbon under the nominal joint optimum vs the robust
optimum re-solved on the least-favorable distribution.

Deliverables:
  - monotonicity of the robust-minus-nominal carbon gap in r
  - price of robustness (max profit loss / carbon avoided)
  - LR-path certificate (verify the sign is invariant along Beta MLR path)
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from numerical_solver import (
    Params, DISTRIBUTIONS, draw, solve_with_fcl, solve_no_fcl, outcomes,
)

RES = HERE / "results"; RES.mkdir(exist_ok=True)
BASE = Params(R=55.0, c=30.0, p=100.0, beta=500.0,
              C_F=20.0, C_R=10.0, C_M=8.0)


def _register_beta(a, b):
    name = f"beta_r_{a:.2f}_{b:.2f}"

    def f(n, D_bar, rng):
        D = rng.beta(a, b, n) * D_bar
        eta = rng.uniform(0, 1, n)
        return D, eta

    DISTRIBUTIONS[name] = f
    return name


def carbon_at(params: Params, dist: str, K_R, K_F, K_M):
    D, eta = draw(params, dist)
    return outcomes(params, D, eta, K_R, K_F, K_M)


def main():
    a0, b0 = 2.0, 2.0  # nominal symmetric Beta
    nominal = _register_beta(a0, b0)
    D, eta = draw(BASE, nominal)
    K_R_n, K_F_n, K_M_n = solve_with_fcl(BASE, D, eta)

    rows = []
    for s in np.linspace(0.0, 1.2, 7):
        # perturbations preserve a+b = 4, radius ~ |mean shift|
        for direction in (+1, -1):
            a = a0 + direction * s
            b = b0 - direction * s
            if a <= 0.2 or b <= 0.2:
                continue
            dist = _register_beta(a, b)
            # nominal capacities evaluated on worst F
            c_nom = carbon_at(BASE, dist, K_R_n, K_F_n, K_M_n)["carbon"]
            # robust: re-solve on the perturbed F
            D_p, eta_p = draw(BASE, dist)
            K_R_r, K_F_r, K_M_r = solve_with_fcl(BASE, D_p, eta_p)
            out_r = outcomes(BASE, D_p, eta_p, K_R_r, K_F_r, K_M_r)
            out_n = outcomes(BASE, D_p, eta_p, K_R_n, K_F_n, K_M_n)
            rows.append({
                "radius_signed": round(direction * s, 3),
                "a": round(a, 3), "b": round(b, 3),
                "carbon_nominal_caps": round(c_nom, 4),
                "carbon_robust_caps": round(out_r["carbon"], 4),
                "gap_robust_minus_nominal": round(
                    out_r["carbon"] - out_n["carbon"], 4),
                "profit_nominal": round(out_n["profit"], 3),
                "profit_robust": round(out_r["profit"], 3),
                "price_of_robustness": round(
                    out_n["profit"] - out_r["profit"], 3),
            })
            DISTRIBUTIONS.pop(dist, None)

    df = pd.DataFrame(rows).sort_values("radius_signed").reset_index(drop=True)
    df.to_csv(RES / "robustness_gap_vs_radius.csv", index=False)

    # LR path: check gap sign is invariant along direction s ∈ [0, 1.2]
    lr = df[df["radius_signed"] >= 0]
    lr_certificate = bool((lr["gap_robust_minus_nominal"] <= 0).all() or
                          (lr["gap_robust_minus_nominal"] >= 0).all())
    # Monotonicity (weak) test in |r|
    df_abs = df.assign(r_abs=df["radius_signed"].abs())\
               .groupby("r_abs", as_index=False)["price_of_robustness"].max()\
               .sort_values("r_abs")
    prs = df_abs["price_of_robustness"].values
    monotone = bool(np.all(np.diff(prs) >= -1e-3))

    summary = {"lr_path_sign_invariant": lr_certificate,
               "price_of_robustness_monotone_in_r": monotone,
               "max_price_of_robustness": float(prs.max()) if len(prs) else 0.0,
               "max_carbon_gap_abs": float(df["gap_robust_minus_nominal"].abs().max())}
    pd.DataFrame([summary]).to_csv(RES / "robustness_summary.csv", index=False)
    DISTRIBUTIONS.pop(nominal, None)
    return df, summary


if __name__ == "__main__":
    main()