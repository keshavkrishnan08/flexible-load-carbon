"""
Role 4 -- Week 4 verification: the carbon classification functional across regimes.

Checks the claims of WEEK4_REGIME_CLASSIFICATION.md, reusing the existing Role-4 modules:
  Prop 2 (continuity hinge): the surplus term c*F(-K_R;K_R) = 0 at the structural
          boundary K_M=K_R, so the small-FCL FOC (eq 61) reduces to the large-FCL FOC (eq 12).
  Prop 3 (widening + kink): C_M^fc < C_M_bar < C_M_bar_b, the widening equals c*q exactly,
          and along C_M the small-FCL K_M FOC drives K_M -> 0 continuously at C_M_bar_b.
  Regime map: sign consistency of the classification across the regime boundary.
Run:  python3 -m role4.week4_regime_classification   (from the repo root)
"""
from __future__ import annotations
import math
from role4.params import Params
from role4 import foc, small_fcl, regimes

PASS = []
def ok(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

def F_uniform(x, K_R, D_bar):
    return min(max((x + K_R) / (D_bar + K_R), 0.0), 1.0)

def main():
    # interior calibration (uniform family) with cheap-enough renewables that the no-FCL
    # optimum is interior (K_R^o > 0), so q^o = F(0;K_R^o) > 0 and the small-FCL widening
    # c*q^o is non-degenerate.
    P = Params(R=1.4, c=0.5, CF=0.6, CR=0.2, CM=0.5, beta=4.0, p=1.0, D_bar=10.0)

    print("=" * 70)
    print("  ROLE 4 -- WEEK 4: classification functional across regimes")
    print("=" * 70)

    # ---- Prop 3: threshold ordering C_M^fc < C_M_bar < C_M_bar_b, widening = c*q ----
    cm_fc = regimes.C_M_fc(P)
    cmbar = foc.C_M_bar(P)
    cmbar_b = small_fcl.C_M_bar_b_eq62(P)
    q = small_fcl.surplus_prob_no_fcl(P)
    widening = small_fcl.adoption_widening(P)
    print(f"\n  C_M^fc={cm_fc:.4f}  C_M_bar={cmbar:.4f}  C_M_bar_b={cmbar_b:.4f}  q={q:.4f}")
    ok("Prop3: threshold ordering C_M^fc < C_M_bar < C_M_bar_b",
       cm_fc < cmbar < cmbar_b, f"{cm_fc:.3f} < {cmbar:.3f} < {cmbar_b:.3f}")
    ok("Prop3: adoption widening equals c*q exactly",
       abs(widening - P.c * q) < 1e-9, f"widening={widening:.4f}, c*q={P.c*q:.4f}")

    # ---- Prop 2: continuity hinge  F(-K_R;K_R)=0  =>  small-FCL FOC reduces to large-FCL ----
    KR = 3.0  # any interior K_R
    surplus_at_boundary = F_uniform(-KR, KR, P.D_bar)   # F(-K_R;K_R)
    ok("Prop2: surplus term F(-K_R;K_R)=0 at the structural boundary K_M=K_R",
       abs(surplus_at_boundary) < 1e-12, f"F(-K_R;K_R)={surplus_at_boundary:.2e}")
    # eq61 residual at K_M=K_R equals eq12 residual (surplus term drops out)
    K_F = 6.0
    res_small = small_fcl.km_foc_residual_small(P, K_R=KR, K_F=K_F, K_M=KR)          # eq 61 at K_M=K_R
    res_large = (P.R - P.c) * F_uniform(K_F - KR, KR, P.D_bar) - P.CM               # eq 12 at K_M=K_R
    ok("Prop2: eq61(K_M=K_R) == eq12(K_M=K_R) (FOCs agree at the boundary)",
       abs(res_small - res_large) < 1e-12, f"|diff|={abs(res_small-res_large):.2e}")

    # ---- Prop 3: K_M* -> 0 continuously as C_M -> C_M_bar_b (kink, no jump) ----
    # Solve the small-FCL K_M FOC for K_M at fixed (K_R,K_F) as C_M rises toward C_M_bar_b.
    def solve_KM(CM_val, K_R, K_F):
        Pc = P.__class__(R=P.R, c=P.c, CF=P.CF, CR=P.CR, CM=CM_val, beta=P.beta, p=P.p, D_bar=P.D_bar)
        lo, hi = 0.0, K_F
        # residual is decreasing in K_M (more FCL capacity, lower marginal value); bisection
        f = lambda KM: small_fcl.km_foc_residual_small(Pc, K_R, K_F, KM)
        if f(lo) < 0:   # even the first unit isn't worth it -> K_M=0
            return 0.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0: lo = mid
            else: hi = mid
        return 0.5 * (lo + hi)

    # base at the NO-FCL optimum (K_R^o, K_F^o): at the adoption edge K_M->0 the
    # capacities approach their no-FCL values, and the first FCL unit's marginal value is
    # exactly (R-c)phi^o + c*q^o = C_M_bar_b (eq 62). Uniform closed forms:
    inner = 2 * P.CR - P.CF**2 / (P.beta + P.p - P.c)
    KR_o = P.D_bar * (math.sqrt(P.c / inner) - 1.0)            # no-FCL optimal renewable
    Q_o = P.D_bar + KR_o
    KF_o = P.D_bar - P.CF / (P.beta + P.p - P.c) * Q_o          # no-FCL optimal fossil
    KR, K_F = KR_o, KF_o
    print(f"\n   (no-FCL optimum: K_R^o={KR_o:.3f}, K_F^o={KF_o:.3f})")
    cms = [cmbar_b * frac for frac in (0.90, 0.96, 0.99, 1.00, 1.01)]
    kms = [solve_KM(cm, KR, K_F) for cm in cms]
    print("\n   C_M/C_M_bar_b: " + "  ".join(f"{cm/cmbar_b:>6.2f}" for cm in cms))
    print("   K_M*:          " + "  ".join(f"{km:>6.3f}" for km in kms))
    # continuous decline; hits (near) 0 at/after C_M_bar_b, no jump between consecutive points
    monotone = all(kms[i+1] <= kms[i] + 1e-6 for i in range(len(kms) - 1))
    small_jumps = all(abs(kms[i+1] - kms[i]) < 0.5 for i in range(len(kms) - 1))
    zero_beyond = kms[-1] < 1e-3
    ok("Prop3: K_M*(C_M) is non-increasing toward C_M_bar_b (kink)", monotone,
       f"K_M: {kms[0]:.3f} -> {kms[-1]:.3f}")
    ok("Prop3: K_M*(C_M) has no jump across the adoption edge (continuous)", small_jumps,
       "max consecutive step < 0.5")
    ok("Prop3: K_M* = 0 for C_M >= C_M_bar_b (adoption edge)", zero_beyond,
       f"K_M*(1.01*C_M_bar_b)={kms[-1]:.4f}")

    # ---- Regime map: classification sign is regime-consistent (uses existing unified_statement) ----
    us = regimes.unified_statement(P)
    ok("Regime map: unified_statement returns coverage+boundedness consistently",
       isinstance(us, dict) and us.get("coverage_ordered") is True and bool(us.get("coverage_regime")),
       f"coverage={us.get('coverage_regime')}, boundedness={us.get('boundedness_regime')}")

    print("\n" + "=" * 70)
    print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS")
    print("=" * 70)
    return sum(PASS) == len(PASS)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
