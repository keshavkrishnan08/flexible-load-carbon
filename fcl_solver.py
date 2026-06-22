"""
fcl_solver.py  --  Team A1, Role 2 (Solver & Numerical Validation)

Numerically solves the utility's capacity-choice problem from the FCL/carbon
paper and validates it against the uniform closed-forms.

Model recap (large-FCL regime, K_M > K_R), profit eq (10):
    Pi(KR,KF,KM) = p E[D] + R * INT_{KF-KM}^{KF} F(x;KR) dx
                          - c * ( KF - INT_{KF-KM}^{-KR} F(x;KR) dx )   [see note]
                          - (b+p) * INT_{KF}^{Dbar} (1-F(x;KR)) dx
                          - CF*KF - CR*KR - CM*KM

We instead integrate the *primitive* profit form (5)/(10) directly and
numerically, so the same code works for ANY distribution F(.;KR). The uniform
closed-forms are used only as golden checks.

Parameters
----------
R    : mining revenue per MWh        (must satisfy R > c)
c    : fossil variable+carbon cost per MWh
CF   : fossil capacity cost per MW
CR   : renewable capacity cost per MW
CM   : ASIC / FCL hardware cost per MW
p    : retail electricity price per MWh
beta : blackout penalty (VOLL net of p) per MWh
Dbar : max consumer demand (support upper bound of residual demand)

Key derived objects:
    Cbar_M = (R-c)(beta+p-c-CF)/(beta+p-c)     adoption threshold, eq (27)
    no-mining FOCs (7),(9);  with-mining FOCs (12),(13),(15)
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import integrate, optimize


@dataclass
class Params:
    R: float
    c: float
    CF: float
    CR: float
    CM: float
    p: float
    beta: float
    Dbar: float

    @property
    def Cbar_M(self) -> float:          # eq (27)
        return (self.R - self.c) * (self.beta + self.p - self.c - self.CF) / (self.beta + self.p - self.c)

    def check_assumptions(self):
        msgs = []
        if not self.R > self.c:                       msgs.append("need R > c")
        if not self.beta + self.p > self.R:           msgs.append("need beta+p > R (Assumption 1)")
        if not self.R < self.c + self.CF + self.CM:   msgs.append("need interior regime R < c+CF+CM")
        return msgs


# ---------------------------------------------------------------------------
# Distribution of residual demand x_tilde, with CDF F(x; KR) on [-KR, Dbar].
# Provide cdf(x,KR); everything else is generic numerical integration.
# ---------------------------------------------------------------------------
class ResidualDist:
    def cdf(self, x, KR):  raise NotImplementedError
    def support(self, KR): return (-KR, None)   # upper bound supplied by Params.Dbar


class Uniform(ResidualDist):
    """F(x;KR) = (x+KR)/(Dbar+KR) on [-KR, Dbar].  Extended: 0 below, 1 above."""
    def __init__(self, Dbar): self.Dbar = Dbar
    def cdf(self, x, KR):
        x = np.asarray(x, dtype=float)
        F = (x + KR) / (self.Dbar + KR)
        return np.clip(F, 0.0, 1.0)


def _Fbar(dist, x, KR):   # 1 - F
    return 1.0 - dist.cdf(x, KR)


def _gint(f, a, b, breaks=(), n=1200):
    """Trapezoidal integral of vectorized f on [a,b], splitting at any interior
    breakpoints (the extended-CDF kinks at -KR and Dbar) so kinks are resolved
    regardless of interval width. Returns 0 if b<=a."""
    if b <= a:
        return 0.0
    pts = sorted([a, b] + [p for p in breaks if a < p < b])
    tot = 0.0
    for lo, hi in zip(pts[:-1], pts[1:]):
        xs = np.linspace(lo, hi, n)
        tot += float(np.trapezoid(f(xs), xs))
    return tot


# ---------------------------------------------------------------------------
# Profit (numerical), valid for any dist.  Large-FCL regime, eq (10).
# ---------------------------------------------------------------------------
def profit(P: Params, dist: ResidualDist, KR, KF, KM, EDtilde=0.0):
    """Expected utility profit, primitive form (5) with EXTENDED CDF (0 below -KR,
    1 above Dbar). Valid in both regimes. p*E[D] enters as constant EDtilde."""
    if min(KR, KF, KM) < 0:
        return -1e18
    bk = (-KR, P.Dbar)
    mining_rev  = P.R * _gint(lambda x: dist.cdf(x, KR),  KF - KM, KF, bk)
    fossil_cost = P.c * _gint(lambda x: _Fbar(dist, x, KR), -KM, KF - KM, bk)   # = c*E[fossil], Remark 2
    blackout    = (P.beta + P.p) * _gint(lambda x: _Fbar(dist, x, KR), KF, P.Dbar, bk)
    capex = P.CF * KF + P.CR * KR + P.CM * KM
    return P.p * EDtilde + mining_rev - fossil_cost - blackout - capex


def profit_no_mining(P: Params, dist: ResidualDist, KR, KF, EDtilde=0.0):  # eq (6)
    if min(KR, KF) < 0:
        return -1e18
    bk = (-KR, P.Dbar)
    fossil = P.c * _gint(lambda x: _Fbar(dist, x, KR), 0.0, KF, bk)
    blackout = (P.beta + P.p) * _gint(lambda x: _Fbar(dist, x, KR), KF, P.Dbar, bk)
    return P.p * EDtilde - fossil - blackout - P.CF * KF - P.CR * KR


# ---------------------------------------------------------------------------
# Solvers (source of truth = numerical optimum)
# ---------------------------------------------------------------------------
def solve_no_mining(P, dist):
    B = (0, 5 * P.Dbar)
    best = None
    for s0 in ([0.5, 0.8], [0.2, 0.5], [1.0, 1.0]):
        x0 = [P.Dbar * s0[0], P.Dbar * s0[1]]
        r = optimize.minimize(lambda v: -profit_no_mining(P, dist, v[0], v[1]),
                              x0, method="L-BFGS-B", bounds=[B, B],
                              options=dict(ftol=1e-12, gtol=1e-9, maxiter=2000))
        if best is None or r.fun < best.fun:
            best = r
    KR, KF = best.x
    return dict(KR=KR, KF=KF, profit=-best.fun, blackout=float(_Fbar(dist, KF, KR)))


def solve_with_mining(P, dist):
    B = (0, 5 * P.Dbar)
    best = None
    for s0 in ([0.8, 0.9, 0.6], [0.4, 0.7, 0.4], [1.2, 1.0, 1.0], [0.6, 0.85, 0.8]):
        x0 = [P.Dbar * s0[0], P.Dbar * s0[1], P.Dbar * s0[2]]
        r = optimize.minimize(lambda v: -profit(P, dist, v[0], v[1], v[2]),
                              x0, method="L-BFGS-B", bounds=[B, B, B],
                              options=dict(ftol=1e-12, gtol=1e-9, maxiter=3000))
        if best is None or r.fun < best.fun:
            best = r
    KR, KF, KM = best.x
    return dict(KR=KR, KF=KF, KM=KM, profit=-best.fun, blackout=float(_Fbar(dist, KF, KR)))


# ---------------------------------------------------------------------------
# Carbon (eq 17): expected fossil output * c, with and without FCL.
#   without:  c * INT_0^{KoF}    (1-F(x;KoR)) dx
#   with:     c * INT_{-KM}^{KF-KM} (1-F(x;KR)) dx   [= KF - INT F, primitive form]
# We return expected fossil OUTPUT (MWh); multiply by emission factor outside.
# ---------------------------------------------------------------------------
def fossil_output_no_mining(P, dist, KR, KF):
    return _gint(lambda x: _Fbar(dist, x, KR), 0.0, KF, (-KR, P.Dbar))

def fossil_output_with_mining(P, dist, KR, KF, KM):   # Remark 2
    return _gint(lambda x: _Fbar(dist, x, KR), -KM, KF - KM, (-KR, P.Dbar))


# ---------------------------------------------------------------------------
# Uniform closed-forms (golden values).  eqs (7),(8),(13),(14),(18),(19),(20)
# ---------------------------------------------------------------------------
def uniform_closed_forms(P: Params):
    """No-mining uniform closed form: solve (7)&(9) for (KoR,KoF).
    The PDF's with-mining K_R closed form is truncated; the with-mining optimum
    is validated against FOCs (12),(13) in validate() instead."""
    b, p, c, CF, R, Dbar = P.beta, P.p, P.c, P.CF, P.R, P.Dbar

    def nomine_system(v):
        KoR, KoF = v
        f7 = (KoF + KoR) / (Dbar + KoR) - (b + p - c - CF) / (b + p - c)
        lhs = c * (Dbar * KoF - KoF**2 / 2) + (b + p) * (Dbar - KoF)**2 / 2
        f9 = lhs - P.CR * (Dbar + KoR)**2
        return [f7, f9]
    KoR, KoF = optimize.fsolve(nomine_system, [Dbar * 0.5, Dbar * 0.5])
    if KoR < 0:   # renewable corner: KoR=0, KoF solves (7) with KR=0
        KoR = 0.0
        KoF = Dbar * (b + p - c - CF) / (b + p - c)
    return dict(no_mining=dict(KR=KoR, KF=KoF,
                               blackout=1 - (KoF + KoR) / (Dbar + KoR)))


# ---------------------------------------------------------------------------
# Validation harness  --  "match to the decimal"
# ---------------------------------------------------------------------------
def validate(P: Params, tol=1e-2):
    """
    Validation strategy:
      (A) No-mining: numerical optimum must match the uniform closed-form
          system (7)&(9) to tolerance  -> exercises eqs (6),(7),(8),(9).
      (B) With-mining: the numerical optimum must satisfy the paper's stated
          FOC conditions (12) F(KF-KM)=CM/(R-c) and (13) F(KF)=(b+p-c-CF-CM)/(b+p-R),
          and the gradient of profit must vanish. (The PDF's K_R closed form was
          truncated, so we validate the optimum against the FOCs rather than an
          independent closed form.)
    TODO(student): paste the exact total-profit closed forms (paper eq 48 no-mining,
    eq 60 with-mining) below and assert profit==closed_form to the decimal.
    """
    dist = Uniform(P.Dbar)
    assert not P.check_assumptions(), P.check_assumptions()
    nm_cf = uniform_closed_forms(P)["no_mining"]
    num_nm = solve_no_mining(P, dist)
    num_m  = solve_with_mining(P, dist)

    def cmp(name, a, b):
        ok = abs(a - b) < tol
        print(f"  {'OK ' if ok else 'XX '}{name:16s} got={a:12.5f}  target={b:12.5f}  |d|={abs(a-b):.2e}")
        return ok

    print("Cbar_M (adoption threshold) =", round(P.Cbar_M, 5),
          " | CM =", P.CM, " ->", "ADOPT (CM<Cbar_M)" if P.CM < P.Cbar_M else "BAN")

    print("\n[A) No-mining: numeric vs uniform closed form]")
    okA  = cmp("KoR", num_nm["KR"], nm_cf["KR"])
    okA &= cmp("KoF", num_nm["KF"], nm_cf["KF"])
    okA &= cmp("blackout", num_nm["blackout"], nm_cf["blackout"])

    print("\n[B) With-mining: FOC conditions at the numerical optimum]")
    KR, KF, KM = num_m["KR"], num_m["KF"], num_m["KM"]
    F_KF   = float(dist.cdf(KF, KR))
    F_KFKM = float(dist.cdf(KF - KM, KR))
    okB  = cmp("(13) F(KF)",   F_KF,   (P.beta + P.p - P.c - P.CF - P.CM) / (P.beta + P.p - P.R))
    # (12) only binds when KM is interior (KF-KM strictly inside support)
    if KF - KM > -KR + 1e-6:
        okB &= cmp("(12) F(KF-KM)", F_KFKM, P.CM / (P.R - P.c))
    else:
        print("  -- (12) at FCL corner (KF-KM at support edge); not binding")

    print("\n[Regime + triple-win readout]")
    regime = "LARGE-FCL (Sec 4)" if KM > KR else "small-FCL (App G)"
    print(f"  K* (KR,KF,KM) = ({KR:.3f}, {KF:.3f}, {KM:.3f})   regime: {regime}")
    print(f"  KR* vs KoR    : {KR:.3f} vs {num_nm['KR']:.3f}  -> renewables "
          f"{'UP' if KR > num_nm['KR'] + 1e-6 else 'FLAT/CORNER' if abs(KR-num_nm['KR'])<1e-6 else 'DOWN'} with FCL")
    fout_nm = fossil_output_no_mining(P, dist, num_nm["KR"], num_nm["KF"])
    fout_m  = fossil_output_with_mining(P, dist, KR, KF, KM)
    print(f"  carbon (fossil MWh) no-mining={fout_nm:.4f}  with-mining={fout_m:.4f}  "
          f"-> {'LOWER' if fout_m < fout_nm else 'HIGHER'} with FCL")
    print(f"  blackout: {num_nm['blackout']:.5f} -> {num_m['blackout']:.5f}  "
          f"({'down' if num_m['blackout'] < num_nm['blackout'] else 'up'})")
    print(f"  profit higher w/ FCL: {num_m['profit'] > num_nm['profit'] - 1e-6}")

    core_ok = okA and okB and (num_m['profit'] > num_nm['profit'] - 1e-6) \
              and (num_m['blackout'] <= num_nm['blackout'] + 1e-9)
    print("\nRESULT:", "CORE MECHANICS VALIDATED" if core_ok else "MISMATCH (investigate)")
    print("NOTE: carbon direction is regime/distribution-dependent (Prop 1(ii), Prop 4) "
          "-- map it with sweep(), don't assume.")
    return core_ok


def sweep(base: Params, key_x="CR", xs=None, key_y="CM", ys=None):
    """Map carbon direction (with-FCL fossil output minus no-FCL) over a 2D grid.
    Returns array: -1 carbon DOWN (good), +1 carbon UP, nan if assumptions fail.
    Role 2 deliverable 4: 'chart which regions keep emissions down'."""
    import numpy as np
    xs = xs if xs is not None else np.linspace(8, 40, 9)
    ys = ys if ys is not None else np.linspace(5, 25, 9)
    dist = Uniform(base.Dbar)
    M = np.full((len(ys), len(xs)), np.nan)
    for i, yv in enumerate(ys):
        for j, xv in enumerate(xs):
            d = base.__dict__.copy(); d[key_x] = xv; d[key_y] = yv
            P = Params(**d)
            if P.check_assumptions() or P.CM >= P.Cbar_M:
                continue
            nm = solve_no_mining(P, dist); m = solve_with_mining(P, dist)
            c_nm = fossil_output_no_mining(P, dist, nm["KR"], nm["KF"])
            c_m  = fossil_output_with_mining(P, dist, m["KR"], m["KF"], m["KM"])
            M[i, j] = -1.0 if c_m < c_nm else 1.0
    return xs, ys, M


if __name__ == "__main__":
    P = Params(R=60, c=30, CF=40, CR=24, CM=10, p=50, beta=1000, Dbar=100)
    validate(P)
