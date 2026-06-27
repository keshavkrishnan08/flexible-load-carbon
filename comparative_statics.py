"""
Role 3 Week 2 — Bullet 1: Comparative statics of the carbon effect.

Signs the partial derivatives
    d(Carbon_FCL - Carbon_noFCL) / d theta     for theta in {R, beta, p, C_M}
via central finite differences on the joint optimum (eqs 12, 13, 15), and
confirms the capacity-substitution claim K_R* > K_R^o under the endpoint
shift-ratio condition  g(K_F*) >= g(K_F* - K_M*),
where g(x) = F_{K_R}(x) / f(x) at the realised thresholds.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numerical_solver import (DISTRIBUTIONS, Params, draw, outcomes,
                              solve_no_fcl, solve_with_fcl, residual)

ROOT = Path(__file__).parent
RES = ROOT / "results"; RES.mkdir(exist_ok=True)


def carbon_gap(p, dist):
    D, eta = draw(p, dist)
    K_R0, K_F0 = solve_no_fcl(p, D, eta)
    K_R, K_F, K_M = solve_with_fcl(p, D, eta)
    a = outcomes(p, D, eta, K_R0, K_F0, 0.0)["carbon"]
    b = outcomes(p, D, eta, K_R,  K_F,  K_M)["carbon"]
    return b - a


def shift_ratio_g(D, eta, K_R, x, h=0.02):
    """g(x) = dF/dK_R / f(x) via central differences on the empirical CDF."""
    def F(KR, xq):
        return float(np.mean(residual(D, eta, KR) <= xq))
    dF_dKR = (F(K_R + h, x) - F(K_R - h, x)) / (2 * h)
    f_x   = (F(K_R, x + h) - F(K_R, x - h)) / (2 * h)
    if abs(f_x) < 1e-8: return float("nan")
    return dF_dKR / f_x


def central_diff(theta_name, base, dist, rel_h=0.02):
    val = getattr(base, theta_name)
    h = max(abs(val) * rel_h, 1e-3)
    plus  = Params(**{**base.__dict__, theta_name: val + h})
    minus = Params(**{**base.__dict__, theta_name: val - h})
    if not (plus.assumption1_ok() and minus.assumption1_ok()):
        return None
    return (carbon_gap(plus, dist) - carbon_gap(minus, dist)) / (2 * h)


def main():
    base = Params(R=55, c=30, p=100, beta=500, C_F=20, C_R=10, C_M=8)
    assert base.assumption1_ok()
    thetas = ["R", "beta", "p", "C_M"]
    rows_cs = []
    for dist in DISTRIBUTIONS:
        for th in thetas:
            d = central_diff(th, base, dist)
            if d is None: continue
            rows_cs.append({"distribution": dist, "theta": th,
                             "d_carbon_gap_d_theta": round(d, 6),
                             "sign": "+" if d > 1e-6 else ("-" if d < -1e-6 else "0")})
    _write_csv(RES / "comparative_statics_signs.csv", rows_cs)

    rows_sub = []
    for dist in DISTRIBUTIONS:
        for C_R in [5.0, 10.0, 20.0]:
            p = Params(**{**base.__dict__, "C_R": C_R})
            if not p.assumption1_ok(): continue
            D, eta = draw(p, dist)
            K_R0, K_F0 = solve_no_fcl(p, D, eta)
            K_R, K_F, K_M = solve_with_fcl(p, D, eta)
            g_hi = shift_ratio_g(D, eta, K_R, K_F)
            g_lo = shift_ratio_g(D, eta, K_R, K_F - K_M)
            endpoint_ok = (not np.isnan(g_hi) and not np.isnan(g_lo)
                            and g_hi >= g_lo - 1e-4)
            rows_sub.append({"distribution": dist, "C_R": C_R,
                              "K_R_no_fcl": round(K_R0, 4),
                              "K_R_fcl":    round(K_R, 4),
                              "K_R_higher": bool(K_R > K_R0 - 1e-4),
                              "g_at_K_F":   round(g_hi, 4) if not np.isnan(g_hi) else "nan",
                              "g_at_K_F_minus_K_M": round(g_lo, 4) if not np.isnan(g_lo) else "nan",
                              "endpoint_condition_holds": bool(endpoint_ok)})
    _write_csv(RES / "capacity_substitution_endpoint.csv", rows_sub)
    return rows_cs, rows_sub


def _write_csv(path, rows):
    if not rows: path.write_text(""); return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    cs, sub = main()
    print(f"comparative statics rows: {len(cs)}")
    for th in ["R","beta","p","C_M"]:
        signs = [r["sign"] for r in cs if r["theta"]==th]
        print(f"  d/d{th}: + {signs.count('+')} / - {signs.count('-')} / 0 {signs.count('0')}")
    print(f"capacity-substitution rows: {len(sub)}")
    ok = sum(r["endpoint_condition_holds"] for r in sub)
    up = sum(r["K_R_higher"] for r in sub)
    print(f"  endpoint condition holds: {ok}/{len(sub)};  K_R*>K_R^o: {up}/{len(sub)}")
