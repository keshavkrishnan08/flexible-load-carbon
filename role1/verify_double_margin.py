"""
Role 1 -- double-margin (third-party-miner) cutoffs, the paper's MAIN model.

Confirms, against the solved utility equilibrium on Beta scale mixtures:
  (1) miner FCL cutoff       F(K_F-K_M) = C_M/(R-p)              [Prop. phi1]
  (2) fossil cutoff          F(K_F)     = (b+p-c-C_F)/b          [Thm. phiodm]
  (3) DECOUPLING             F(K_F) is invariant to C_M          [Cor. decouple]

Physical dispatch is identical to the utility-operated model; only who collects which margin
differs (miner R-p, utility p-c). Miners enter by free entry (R-p)F(K_F-K_M)=C_M; the utility
chooses K_R,K_F internalizing the entry response dK_M/dK_F=1.
"""
import numpy as np
from scipy import optimize
from scipy.stats import beta as spbeta

class ScaleMix:
    def __init__(s, Dbar, ad, bd, as_, bs, ns=400):
        s.Dbar = Dbar; s.bD = spbeta(ad, bd)
        u = (np.arange(ns) + .5) / ns; w = spbeta(as_, bs).pdf(u)
        s.s = u; s.w = w / w.sum()
    def _fD(s, dd):
        dd = np.asarray(dd, float); z = np.clip(dd / s.Dbar, 1e-12, 1 - 1e-12)
        return np.where((dd >= 0) & (dd <= s.Dbar), s.bD.pdf(z) / s.Dbar, 0.)
    def _FD(s, dd): return s.bD.cdf(np.clip(np.asarray(dd, float) / s.Dbar, 0, 1))
    def F(s, x, KR): return float(s.w @ s._FD(x + KR * s.s))

PASS = []
def ok(name, cond, detail=""):
    cond = bool(cond); PASS.append(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name:52s} {detail}")

def solve_dm(d, P):
    """Utility equilibrium in the double margin. Returns (K_R,K_F,K_M)."""
    R, p, c, b, CF, CR, CM, Dbar = (P[k] for k in ['R','p','c','beta','CF','CR','CM','Dbar'])
    phi1 = CM / (R - p)
    def Finv(KR, t): return optimize.brentq(lambda z: d.F(z, KR) - t, -KR + 1e-9, Dbar - 1e-9, xtol=1e-10)
    XS = np.linspace(-Dbar, Dbar, 1400)
    def profit(KR, KF, KM):
        xs = XS[XS >= -KR]; Fx = np.array([d.F(x, KR) for x in xs])
        fx = np.clip(np.gradient(Fx, xs), 0, None); Z = np.trapz(fx, xs); fx = fx / Z if Z > 0 else fx
        xp = np.maximum(xs, 0.)
        miner = np.minimum(np.maximum(KF - xp, 0.), KM)
        fcons = np.minimum(xp, KF); out = np.maximum(xp - KF, 0.)
        E = lambda v: float(np.trapz(v * fx, xs))
        return (p - c) * E(miner) - c * E(fcons) - (b + p) * E(out) - CF * KF - CR * KR
    def obj(k):
        KR, KF = k
        if KR < 0.05 or KF < 0.5 or KF > Dbar * 0.99: return 1e6
        try: KM = KF - Finv(KR, phi1)
        except Exception: return 1e6
        return -profit(KR, KF, max(KM, 1e-3))
    r = optimize.minimize(obj, (2.0, 7.0), method='Nelder-Mead',
                          options={'xatol': 2e-4, 'fatol': 2e-5, 'maxiter': 2500})
    KR, KF = r.x
    return KR, KF, max(KF - Finv(KR, phi1), 1e-3)

if __name__ == "__main__":
    d = ScaleMix(10, 2, 2, 2, 2)
    print("=" * 74)
    print("  DOUBLE-MARGIN CUTOFFS  (third-party miners, tariff p)")
    print("=" * 74)
    PARAMS = [dict(R=1.4, p=0.70, c=0.5, beta=4.0, CF=0.6, CR=0.5, CM=0.30, Dbar=10.0),
              dict(R=1.6, p=0.80, c=0.5, beta=4.0, CF=0.6, CR=0.5, CM=0.40, Dbar=10.0),
              dict(R=1.5, p=0.75, c=0.4, beta=3.5, CF=0.5, CR=0.5, CM=0.35, Dbar=10.0)]
    for P in PARAMS:
        R, p, c, b, CF, CM = P['R'], P['p'], P['c'], P['beta'], P['CF'], P['CM']
        phi1 = CM / (R - p); phio_dm = (b + p - c - CF) / b
        KR, KF, KM = solve_dm(d, P)
        reg = 'large-FCL' if KM >= KR else 'small-FCL'
        print(f"\n  R-p={R-p:.2f} p-c={p-c:.2f}  eq: K_R={KR:.3f} K_F={KF:.3f} K_M={KM:.3f} ({reg})")
        ok(f"  miner cutoff  F(KF-KM)=C_M/(R-p)={phi1:.4f}",
           abs(d.F(KF - KM, KR) - phi1) < 1e-3, f"F={d.F(KF-KM,KR):.4f} err={abs(d.F(KF-KM,KR)-phi1):.1e}")
        ok(f"  fossil cutoff F(KF)=(b+p-c-CF)/b={phio_dm:.4f}",
           abs(d.F(KF, KR) - phio_dm) < 3e-3, f"F={d.F(KF,KR):.4f} err={abs(d.F(KF,KR)-phio_dm):.1e}")

    # decoupling: F(K_F) invariant to C_M
    print("\n  --- decoupling: F(K_F)=phi_o_DM invariant to C_M ---")
    Pb = dict(R=1.4, p=0.70, c=0.5, beta=4.0, CF=0.6, CR=0.5, CM=0.30, Dbar=10.0)
    phio_dm = (Pb['beta'] + Pb['p'] - Pb['c'] - Pb['CF']) / Pb['beta']
    fkfs = []
    for CM in [0.20, 0.30, 0.40, 0.50]:
        KR, KF, KM = solve_dm(d, dict(Pb, CM=CM)); fkfs.append(d.F(KF, KR))
        print(f"    C_M={CM:.2f}: F(KF)={d.F(KF,KR):.4f}  (target {phio_dm:.4f})")
    ok("decoupling: F(KF) invariant to C_M (spread < 3e-3)",
       max(fkfs) - min(fkfs) < 3e-3, f"spread={max(fkfs)-min(fkfs):.1e} over C_M in [0.2,0.5]")

    # --- carbon classification carries over: naive dispatch raises carbon in the DM model ---
    print("\n  --- Phi=Delta carries over: naive dispatch raises carbon in the main model ---")
    from scipy import integrate
    Pc = dict(R=1.4, p=0.70, c=0.5, beta=4.0, CF=0.6, CR=0.5, CM=0.30, Dbar=10.0)
    def _dens(KR):
        import numpy as _np
        xs = _np.linspace(-KR, Pc['Dbar'], 1200); Fx = _np.array([d.F(x, KR) for x in xs])
        fx = _np.clip(_np.gradient(Fx, xs), 0, None); Z = _np.trapz(fx, xs)
        return xs, (fx / Z if Z > 0 else fx)
    def _q(fn, a, bb): return integrate.quad(fn, a, bb, limit=200)[0]
    KRn, KFn, KMn = solve_dm(d, Pc)
    # no-load benchmark
    R_, p_, c_, b_, CF_, CR_ = (Pc[k] for k in ['R','p','c','beta','CF','CR'])
    def _prof_no(k):
        KR, KF = k
        if KR < 0.05 or KF < 0.5 or KF > Pc['Dbar']*0.99: return 1e6
        xs, fx = _dens(KR); xp = np.maximum(xs, 0.)
        E = lambda v: float(np.trapz(v*fx, xs))
        return -(-c_*E(np.minimum(xp, KF)) - (b_+p_)*E(np.maximum(xp-KF, 0.)) - CF_*KF - CR_*KR)
    ro = optimize.minimize(_prof_no, (2., 7.), method='Nelder-Mead',
                           options={'xatol':3e-4,'fatol':3e-5,'maxiter':2000})
    KRo, KFo = ro.x
    Ef_naive = _q(lambda x: 1 - d.F(x, KRn), -KMn, KFn - KMn)   # large-FCL naive fossil
    Ef_no = _q(lambda x: 1 - d.F(x, KRo), 0, KFo)
    Delta = Ef_no - Ef_naive
    print(f"    DM naive eq K_R={KRn:.3f} K_F={KFn:.3f} K_M={KMn:.3f}; Delta={Delta:+.3f}")
    ok("carbon classification carries over: naive dispatch raises carbon (Delta<0)",
       Delta < -0.5, f"Delta={Delta:+.3f} (carbon UP in the main model too)")

    # --- EXACT coefficient: Delta == Phi_dm (not just the sign) ---
    a = KFn - KMn
    fden = lambda x, KR: float(d.w @ d._fD(x + KR * d.s))       # analytic mixture density
    phio = (b_ + p_ - c_ - CF_) / (b_ + p_ - c_)
    qo = d.F(0, KRo)
    mu_low = _q(lambda x: x * fden(x, KRn), -KMn, a) / _q(lambda x: fden(x, KRn), -KMn, a)
    mu_mid = _q(lambda x: x * fden(x, KRo), 0, KFo) / _q(lambda x: fden(x, KRo), 0, KFo)
    Phi_dm = (Pc['CM'] / (R_ - p_)) * (a - mu_low) - (KFn - KFo * (1 - phio) - (phio - qo) * mu_mid)
    print(f"    Phi_dm(formula, CM/(R-p) coeff) = {Phi_dm:+.4f}   Delta(quad) = {Delta:+.4f}")
    ok("EXACT: Delta == Phi_dm  (full carbon coefficient in the main model)",
       abs(Delta - Phi_dm) < 3e-3, f"|Delta - Phi_dm| = {abs(Delta-Phi_dm):.1e} (equilibrium-solve limited)")

    print("\n" + "=" * 74)
    print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS")
    print("=" * 74)
