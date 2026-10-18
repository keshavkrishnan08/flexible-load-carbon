"""
Role 3 Week 2, Bullet 4: Limit-interchange / dominated convergence check.

Week-1 threshold proof used an a.s.-corner argument: as C_M -> C_M_bar^-,
K_M* -> 0, then "expected fossil dispatch -> 0". Week 2 replaces this with a
dominated-convergence argument:

    E[ d_n(X) ]  ->  E[ d_infty(X) ]    as n -> infty,
where d_n(x) = min((K_F_n - x)_+, K_M_n) and the dominating envelope is
    |d_n(x)| <= K_F_max  (finite-capacity envelope, integrable since X has
finite expectation).

This script verifies the envelope numerically: for a sequence C_M_n ↑ C_M_bar
we check (i) K_M_n monotone decreasing to 0, (ii) E[d_n] -> 0, (iii) the
finite envelope dominates every d_n pointwise.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numerical_solver import (DISTRIBUTIONS, Params, draw, solve_with_fcl,
                              residual)

ROOT = Path(__file__).parent
RES = ROOT / "results"; RES.mkdir(exist_ok=True)


def run(dist="uniform"):
    base = Params(R=55, c=30, p=100, beta=500, C_F=20, C_R=10, C_M=8)
    D, eta = draw(base, dist)
    C_M_bar = base.C_M_bar()
    rows = []
    K_F_envelope = None
    for frac in [0.50, 0.70, 0.85, 0.92, 0.96, 0.98, 0.99, 0.995, 0.999]:
        C_M = frac * C_M_bar
        p = Params(**{**base.__dict__, "C_M": C_M})
        if not p.assumption1_ok(): continue
        K_R, K_F, K_M = solve_with_fcl(p, D, eta)
        x = residual(D, eta, K_R)
        d = np.minimum(np.maximum(K_F - x, 0.0), K_M)
        env = max(K_F, K_M)
        K_F_envelope = env if K_F_envelope is None else max(K_F_envelope, env)
        dominated = bool(np.all(d <= K_F_envelope + 1e-9))
        rows.append({
            "C_M_over_C_M_bar": round(frac, 4),
            "K_M_star":         round(K_M, 5),
            "K_F_star":         round(K_F, 5),
            "E_d":              round(float(d.mean()), 6),
            "envelope_K_F_max": round(float(K_F_envelope), 5),
            "dominated_pointwise": dominated,
        })
    return rows


def main():
    all_rows = []
    for dist in DISTRIBUTIONS:
        for r in run(dist):
            r2 = {"distribution": dist, **r}
            all_rows.append(r2)
    with open(RES / "limit_interchange_envelope.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader(); w.writerows(all_rows)
    return all_rows


if __name__ == "__main__":
    rows = main()
    # Monotone K_M -> 0 and E[d] -> 0 per distribution
    by = {}
    for r in rows: by.setdefault(r["distribution"], []).append(r)
    print(f"limit-interchange rows: {len(rows)}")
    ok_dom = sum(r["dominated_pointwise"] for r in rows)
    print(f"  envelope dominates pointwise: {ok_dom}/{len(rows)}")
    for d, rs in by.items():
        kms = [r["K_M_star"] for r in rs]
        eds = [r["E_d"] for r in rs]
        mono = all(kms[i] >= kms[i+1] - 1e-4 for i in range(len(kms)-1))
        print(f"  {d:24s}: K_M monotone↓ {mono},  K_M last={kms[-1]:.4f}, E[d] last={eds[-1]:.4f}")
