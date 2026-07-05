"""Week 3 Bullet 4 — Fragility map / knife-edge witnesses.

We locate two boundaries and produce explicit witnesses on both sides:

  (a) The adoption boundary C_M = C_M_bar. Just below: FCL is deployed;
      just above: K_M* collapses to 0. Carbon and profit jump.
  (b) The endpoint shift-ratio boundary g(K_F*) = g(K_F* - K_M*).
      Verified by scanning the Beta(a, 5-a) family and reporting the a*
      at which the inequality flips.
"""
from __future__ import annotations
import sys
from pathlib import Path
from dataclasses import replace

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from numerical_solver import (
    Params, DISTRIBUTIONS, draw, solve_with_fcl, residual, F,
)

RES = HERE / "results"; RES.mkdir(exist_ok=True)
BASE = Params(R=55.0, c=30.0, p=100.0, beta=500.0,
              C_F=20.0, C_R=10.0, C_M=8.0)


def _register(a, b):
    name = f"beta_frag_{a:.2f}_{b:.2f}"

    def f(n, D_bar, rng):
        D = rng.beta(a, b, n) * D_bar
        eta = rng.uniform(0, 1, n)
        return D, eta
    DISTRIBUTIONS[name] = f
    return name


def snapshot(params: Params, dist: str):
    D, eta = draw(params, dist)
    K_R, K_F, K_M = solve_with_fcl(params, D, eta)
    x = residual(D, eta, K_R)
    d = np.minimum(np.maximum(K_F - x, 0.0), K_M)
    foss = np.minimum(np.maximum(x + d, 0.0), K_F)
    return {"K_R": K_R, "K_F": K_F, "K_M": K_M,
            "carbon": params.c * float(foss.mean()),
            "g_KF": F(K_F, D, eta, K_R),
            "g_KFmKM": F(max(K_F - K_M, 0.0), D, eta, K_R)}


def main():
    # (a) Adoption boundary in C_M
    rows_a = []
    Cbar = BASE.C_M_bar()
    for eps in [-0.30, -0.10, -0.02, 0.02, 0.10, 0.30]:
        p = replace(BASE, C_M=max(Cbar + eps, 0.1))
        if not p.assumption1_ok():
            rows_a.append({"eps": eps, "C_M": round(p.C_M, 3),
                           "note": "outside_A1"}); continue
        r = snapshot(p, "uniform")
        rows_a.append({"eps": eps, "C_M": round(p.C_M, 3),
                       **{k: round(v, 4) for k, v in r.items()}})
    pd.DataFrame(rows_a).to_csv(RES / "fragility_adoption_boundary.csv", index=False)

    # (b) Endpoint shift-ratio boundary along Beta(a, 5-a)
    rows_b = []
    for a in np.linspace(0.5, 4.5, 17):
        b = 5.0 - a
        name = _register(a, b)
        r = snapshot(BASE, name)
        rows_b.append({"a": round(a, 3), "b": round(b, 3),
                       **{k: round(v, 5) for k, v in r.items()},
                       "endpoint_gap": round(r["g_KF"] - r["g_KFmKM"], 5),
                       "endpoint_holds": r["g_KF"] >= r["g_KFmKM"]})
        DISTRIBUTIONS.pop(name, None)
    df = pd.DataFrame(rows_b)
    df.to_csv(RES / "fragility_endpoint_boundary.csv", index=False)

    # Locate the flip a*
    sign = np.sign(df["endpoint_gap"].values)
    flips = np.where(np.diff(sign) != 0)[0]
    a_star = float(df["a"].iloc[flips[0]]) if len(flips) else None
    summary = {"a_flip": a_star,
               "n_endpoint_holds": int(df["endpoint_holds"].sum()),
               "n_scenarios": int(len(df))}
    pd.DataFrame([summary]).to_csv(RES / "fragility_summary.csv", index=False)
    return rows_a, df, summary


if __name__ == "__main__":
    main()