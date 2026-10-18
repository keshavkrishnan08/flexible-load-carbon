"""Week 3 Bullet 1, Sign the characterization comparative statics.

For each primitive theta in {R, c, beta, p, C_F, C_R, C_M} we compute the
central-difference derivative of the carbon *functional* J(theta) at the
joint optimum:

    J(theta) = Carbon_FCL(theta) - Carbon_noFCL(theta)

and the movement of the carbon boundary along the C_M axis (the adoption
threshold C_M_bar and the effective carbon-sign flip point).

Signs are computed across every distribution in the registry so we can
claim a distribution-free direction whenever it holds unanimously.
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
    Params, DISTRIBUTIONS, draw, solve_no_fcl, solve_with_fcl, outcomes,
)

RES = HERE / "results"; RES.mkdir(exist_ok=True)

BASE = Params(R=55.0, c=30.0, p=100.0, beta=500.0,
              C_F=20.0, C_R=10.0, C_M=8.0)
PRIMS = ["R", "c", "beta", "p", "C_F", "C_R", "C_M"]
STEP = {"R": 1.0, "c": 0.5, "beta": 10.0, "p": 2.0,
        "C_F": 0.5, "C_R": 0.5, "C_M": 0.25}


def carbon_gap(params: Params, dist: str) -> float:
    D, eta = draw(params, dist)
    K_R0, K_F0 = solve_no_fcl(params, D, eta)
    K_R1, K_F1, K_M1 = solve_with_fcl(params, D, eta)
    c_no = outcomes(params, D, eta, K_R0, K_F0, 0.0)["carbon"]
    c_yes = outcomes(params, D, eta, K_R1, K_F1, K_M1)["carbon"]
    return c_yes - c_no


def sign(x: float, tol: float = 1e-4) -> str:
    return "+" if x > tol else "-" if x < -tol else "0"


def main():
    rows = []
    for dist in DISTRIBUTIONS:
        for theta in PRIMS:
            h = STEP[theta]
            p_plus = replace(BASE, **{theta: getattr(BASE, theta) + h})
            p_minus = replace(BASE, **{theta: getattr(BASE, theta) - h})
            if not (p_plus.assumption1_ok() and p_minus.assumption1_ok()):
                rows.append({"distribution": dist, "theta": theta,
                             "dJ_dtheta": None, "sign": "skip"}); continue
            j_plus = carbon_gap(p_plus, dist)
            j_minus = carbon_gap(p_minus, dist)
            deriv = (j_plus - j_minus) / (2 * h)
            rows.append({"distribution": dist, "theta": theta,
                         "dJ_dtheta": round(deriv, 5), "sign": sign(deriv)})

    df = pd.DataFrame(rows)
    df.to_csv(RES / "characterization_comparative_statics.csv", index=False)

    # Boundary movement: C_M_bar and empirical carbon-flip C_M*(theta)
    boundary = []
    for theta in ["R", "c", "beta", "p", "C_F"]:
        h = STEP[theta]
        p_plus = replace(BASE, **{theta: getattr(BASE, theta) + h})
        p_minus = replace(BASE, **{theta: getattr(BASE, theta) - h})
        dCM_bar = (p_plus.C_M_bar() - p_minus.C_M_bar()) / (2 * h)
        boundary.append({"theta": theta, "d_C_M_bar_d_theta": round(dCM_bar, 5),
                         "sign": sign(dCM_bar)})
    pd.DataFrame(boundary).to_csv(RES / "characterization_boundary_movement.csv",
                                  index=False)
    return rows, boundary


if __name__ == "__main__":
    main()