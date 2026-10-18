"""
Role 3 Week 2, Bullet 2: Cross-distribution robust certificate.

One-parameter MLR-monotone deformation within Beta family:
  F_t(x) = Beta(alpha(t), beta(t)) * D_bar,   t in [0, 1]
with alpha(t) = 0.8 + 2.4 t,  beta(t) = 4.0 - 2.0 t.
At t=0 strongly right-skewed; at t=1 nearly symmetric. The family is ordered
by likelihood ratio: density ratio f_{t1}/f_{t0} is monotone in x for t1>t0.

We sweep t and record (K_R*, K_F*, K_M*, dCarbon) so we can sign
  dK*/dt   and verify   C_R <= C_R^dagger  =>  dCarbon <= 0
holds *uniformly* along the homotopy.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numerical_solver import (Params, outcomes, solve_no_fcl, solve_with_fcl,
                              DISTRIBUTIONS, _sampler_beta)

ROOT = Path(__file__).parent
RES = ROOT / "results"; RES.mkdir(exist_ok=True)


def beta_path_sampler(t):
    a = 0.8 + 2.4 * t
    b = 4.0 - 2.0 * t
    return _sampler_beta(a, b), (a, b)


def main():
    ts = np.linspace(0.0, 1.0, 11)
    C_R_grid = [1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 30.0]
    base = Params(R=55, c=30, p=100, beta=500, C_F=20, C_M=8)

    rows = []
    for C_R in C_R_grid:
        p = Params(**{**base.__dict__, "C_R": C_R})
        if not p.assumption1_ok(): continue
        for t in ts:
            sampler, (a, b) = beta_path_sampler(t)
            rng = np.random.default_rng(p.seed)
            D, eta = sampler(p.n_samples, p.D_bar, rng)
            K_R0, K_F0 = solve_no_fcl(p, D, eta)
            K_R, K_F, K_M = solve_with_fcl(p, D, eta)
            no = outcomes(p, D, eta, K_R0, K_F0, 0.0)
            yes = outcomes(p, D, eta, K_R, K_F, K_M)
            rows.append({"C_R": C_R, "t": round(float(t), 3),
                         "alpha": round(a, 3), "beta_shape": round(b, 3),
                         "K_R_no_fcl": round(K_R0, 4), "K_R_fcl": round(K_R, 4),
                         "K_F_fcl": round(K_F, 4), "K_M_fcl": round(K_M, 4),
                         "carbon_no_fcl": round(no["carbon"], 5),
                         "carbon_fcl":    round(yes["carbon"], 5),
                         "delta_carbon":  round(yes["carbon"] - no["carbon"], 5)})
    _write_csv(RES / "robust_certificate_homotopy.csv", rows)

    # Find C_R^dagger: largest C_R such that dCarbon <= 0 for every t on the path
    by_cr = {}
    for r in rows: by_cr.setdefault(r["C_R"], []).append(r)
    cert = []
    for C_R, rs in sorted(by_cr.items()):
        all_neg = all(r["delta_carbon"] <= 1e-6 for r in rs)
        dKR_t = [rs[i+1]["K_R_fcl"] - rs[i]["K_R_fcl"] for i in range(len(rs)-1)]
        cert.append({"C_R": C_R,
                     "all_t_carbon_down": bool(all_neg),
                     "min_delta_carbon": round(min(r["delta_carbon"] for r in rs), 5),
                     "max_delta_carbon": round(max(r["delta_carbon"] for r in rs), 5),
                     "dK_R_dt_min": round(min(dKR_t), 5),
                     "dK_R_dt_max": round(max(dKR_t), 5)})
    _write_csv(RES / "robust_certificate_summary.csv", cert)
    return rows, cert


def _write_csv(path, rows):
    if not rows: path.write_text(""); return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    rows, cert = main()
    print(f"homotopy rows: {len(rows)}")
    for c in cert:
        print(f"  C_R={c['C_R']:>4}: all_t carbon down = {c['all_t_carbon_down']}, "
              f"dCarbon in [{c['min_delta_carbon']}, {c['max_delta_carbon']}]")
    feasible = [c["C_R"] for c in cert if c["all_t_carbon_down"]]
    if feasible:
        print(f"C_R_dagger (robust certificate upper bound) = {max(feasible)}")
    else:
        print("No C_R on grid certifies; obstruction documented in writeup.")
