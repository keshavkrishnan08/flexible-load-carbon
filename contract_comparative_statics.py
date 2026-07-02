"""Week 3 Bullet 2 — Optimal-contract comparative statics.

We compare two dispatch contracts on the same (K_R, K_F, K_M):

  Myopic (firm-optimal):  d_M(x) = min(max(K_F - x, 0), K_M)
  Carbon-optimal:         d_C(x) = min(max(x, 0), K_M)   (dispatch when any
                          fossil is about to run — max fossil substitution)

The wedge W(C_M, C_R) = Carbon_M - Carbon_C  ≥ 0 measures how much a
socially-set contract could remove vs the myopic rule. Signs of dW/dC_M
and dW/dC_R across the 8 distributions test the claim that the wedge
shrinks in C_M (adoption margin) and grows in C_R (dirty on the margin).
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
    Params, DISTRIBUTIONS, draw, solve_with_fcl, residual,
)

RES = HERE / "results"; RES.mkdir(exist_ok=True)
BASE = Params(R=55.0, c=30.0, p=100.0, beta=500.0,
              C_F=20.0, C_R=10.0, C_M=8.0)


def carbons(params: Params, dist: str):
    D, eta = draw(params, dist)
    K_R, K_F, K_M = solve_with_fcl(params, D, eta)
    x = residual(D, eta, K_R)
    d_M = np.minimum(np.maximum(K_F - x, 0.0), K_M)
    d_C = np.minimum(np.maximum(x, 0.0), K_M)   # max substitution
    foss_M = np.minimum(np.maximum(x + d_M, 0.0), K_F)
    foss_C = np.minimum(np.maximum(x + d_C, 0.0), K_F)
    return {"K_R": K_R, "K_F": K_F, "K_M": K_M,
            "carbon_myopic":  params.c * float(foss_M.mean()),
            "carbon_optimal": params.c * float(foss_C.mean()),
            "wedge": params.c * float((foss_M - foss_C).mean())}


def sign(x, tol=1e-4):
    return "+" if x > tol else "-" if x < -tol else "0"


def main():
    rows = []
    for dist in DISTRIBUTIONS:
        base = carbons(BASE, dist)
        for theta, h in [("C_M", 0.5), ("C_R", 0.5)]:
            p_plus = replace(BASE, **{theta: getattr(BASE, theta) + h})
            p_minus = replace(BASE, **{theta: getattr(BASE, theta) - h})
            if not (p_plus.assumption1_ok() and p_minus.assumption1_ok()):
                continue
            w_plus = carbons(p_plus, dist)["wedge"]
            w_minus = carbons(p_minus, dist)["wedge"]
            dw = (w_plus - w_minus) / (2 * h)
            rows.append({"distribution": dist, "theta": theta,
                         "wedge_base": round(base["wedge"], 4),
                         "dW_dtheta": round(dw, 5), "sign": sign(dw)})

    pd.DataFrame(rows).to_csv(RES / "contract_wedge_comparative_statics.csv",
                              index=False)

    # Distribution-shape sensitivity along the Beta(a, 5-a) family
    shape_rows = []
    for a in [0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 4.5]:
        b = 5.0 - a
        name = f"beta_a{a}_b{b}"
        DISTRIBUTIONS[name] = _beta_sampler(a, b)
        try:
            r = carbons(BASE, name)
            shape_rows.append({"a": a, "b": b, **{k: round(v, 4)
                                                  for k, v in r.items()}})
        finally:
            DISTRIBUTIONS.pop(name, None)
    pd.DataFrame(shape_rows).to_csv(RES / "contract_wedge_by_shape.csv",
                                    index=False)
    return rows, shape_rows


def _beta_sampler(a, b):
    def f(n, D_bar, rng):
        D = rng.beta(a, b, n) * D_bar
        eta = rng.uniform(0, 1, n)
        return D, eta
    return f


if __name__ == "__main__":
    main()