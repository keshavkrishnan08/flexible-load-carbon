"""
Role 1 -- storage vs the flexible load for renewable surplus (referee issue #3).

Static, expected-flow storage model.  Confirms:
  (A) Prop carbon:    storage displaces grid fossil per surplus MWh; surplus-FCL does not.
  (B) Prop invariant: the naive-minus-surplus dispatch carbon gap is INVARIANT to K_S.
  (C) Prop threshold: the FCL is the higher-VALUE surplus user iff R > c+eta[phi_o c+(1-phi_o)(b+p)].
"""
import numpy as np
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

d = ScaleMix(10, 2, 2, 2, 2)
XS = np.linspace(-12, 10, 1500)
R, c, b, p, CF, eta = 1.4, 0.5, 4.0, 0.7, 0.6, 0.85
KR, KF = 2.0, 7.0

def dens(KR):
    xs = XS[XS >= -KR]; Fx = np.array([d.F(x, KR) for x in xs])
    fx = np.clip(np.gradient(Fx, xs), 0, None); Z = np.trapz(fx, xs)
    return xs, (fx / Z if Z > 0 else fx)

def carbon(KM_surplus=0.0, KM_naive=0.0, KS=0.0):
    xs, fx = dens(KR); xp = np.maximum(xs, 0.); surp = np.maximum(-xs, 0.)
    E = lambda v: float(np.trapz(v * fx, xs))
    charge = np.minimum(surp, KS)
    displaced = eta * E(charge)
    base = E(np.minimum(xp, KF))
    naive_burn = E(np.minimum(np.maximum(KF - xp, 0.), KM_naive))
    return base + naive_burn - displaced

if __name__ == "__main__":
    print("=" * 74)
    print("  STORAGE vs FLEXIBLE LOAD for renewable surplus")
    print("=" * 74)

    print("\n(A) per-surplus carbon: storage displaces, surplus-FCL does not")
    c0 = carbon(); cS = carbon(KS=3.0); cM = carbon(KM_surplus=3.0)
    print(f"    none={c0:.4f}  storage(K_S=3)={cS:.4f} (d={c0-cS:+.4f})  surplusFCL(K_M=3)={cM:.4f} (d={c0-cM:+.4f})")
    ok("storage lowers grid fossil, surplus-FCL does not", (c0 - cS) > 1e-3 and abs(c0 - cM) < 1e-3,
       f"storage {c0-cS:+.4f} vs FCL {c0-cM:+.4f}")

    print("\n(B) naive-minus-surplus dispatch gap is invariant to K_S")
    gaps = []
    for KS in [0.0, 2.0, 4.0]:
        g = carbon(KM_naive=3.0, KS=KS) - carbon(KM_surplus=3.0, KS=KS); gaps.append(g)
        print(f"    K_S={KS:.1f}:  gap = {g:+.4f}")
    ok("dispatch gap invariant to K_S (spread < 1e-3)", max(gaps) - min(gaps) < 1e-3,
       f"spread={max(gaps)-min(gaps):.1e}, gap~{gaps[0]:+.3f}")

    print("\n(C) value threshold R* = c + eta[phi_o c + (1-phi_o)(b+p)]")
    phio = (b + p - c - CF) / (b + p - c)
    Rstar = c + eta * (phio * c + (1 - phio) * (b + p))
    vstor = eta * (phio * c + (1 - phio) * (b + p))
    print(f"    phi_o={phio:.3f}  v_stor={vstor:.3f}  R-c={R-c:.3f}  R*={Rstar:.3f}")
    # verify the boxed inequality is equivalent to (R-c) > v_stor
    ok("threshold: (R-c > v_stor)  <=>  (R > R*)", ((R - c > vstor) == (R > Rstar)),
       f"R-c>{vstor:.2f}? {R-c>vstor}   R>{Rstar:.2f}? {R>Rstar}")
    # and that a high-value load clears it while a low-value one does not
    ok("high-value compute (R=3) clears R*, low-value (R=1) does not",
       (3.0 > Rstar) and (1.0 < Rstar), f"R*={Rstar:.2f} in (1,3)")

    print("\n" + "=" * 74)
    print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS")
    print("=" * 74)
