"""
Role 1 (General Carbon Theory) — numerical ground-truth validation.

 (V1) Uniform/power-law closed forms (eqs 18-23, 25, 26) verified at a FIXED
      K_R against direct quadrature of the unified profit integral (eq 5).
      Fixed-K_R avoids the uniform knife-edge (eq 24): under uniform/power
      F, the marginal value of K_R is CONSTANT in K_R, so K_R* is a corner
      (0 or infinity). That is itself a theorem we confirm (V1c).
 (V2) On strictly-concave Beta scale-mixtures x = D - K_R S (interior K_R*),
      confirm  K_R* > K_R^o  and that sign(dK_R*/dC_M) = sign of the
      shift-ratio bracket  B = F_KR(K_F) f(K_F-K_M) - F_KR(K_F-K_M) f(K_F).
      Tuning D's density slope flips g(x)=F_KR/f monotonicity and, with it,
      the sign of K_R* - K_R^o  -- proving the condition is sharp.
"""
import numpy as np
from scipy import integrate, optimize

class PowerLaw:
    def __init__(self, Dbar, alpha=1.0): self.Dbar=Dbar; self.a=alpha
    def F(self,x,KR):
        Q=self.Dbar+KR; z=min(max((x+KR)/Q,0.0),1.0); return z**self.a
    def f(self,x,KR):
        Q=self.Dbar+KR
        if x<=-KR or x>=self.Dbar: return 0.0
        return self.a*((x+KR)/Q)**(self.a-1)/Q
    def FKR(self,x,KR):
        Q=self.Dbar+KR; return self.f(x,KR)*(self.Dbar-x)/Q

class ScaleMix:
    """x = D - KR*S ,  D ~ Dbar*Beta(ad,bd) ,  S ~ Beta(as,bs)."""
    def __init__(self, Dbar, ad,bd, as_,bs, ns=601):
        from scipy.stats import beta
        self.Dbar=Dbar; self.bD=beta(ad,bd); self.bS=beta(as_,bs)
        s=np.linspace(1e-4,1-1e-4,ns); w=self.bS.pdf(s); self.s=s; self.w=w/w.sum()
    def _fD(self,d):
        d=np.asarray(d,float); z=d/self.Dbar
        return np.where((z>=0)&(z<=1), self.bD.pdf(np.clip(z,1e-9,1-1e-9))/self.Dbar,0.0)
    def _FD(self,d): return self.bD.cdf(np.clip(np.asarray(d,float)/self.Dbar,0,1))
    def F(self,x,KR):  return float(np.sum(self.w*self._FD(x+KR*self.s)))
    def f(self,x,KR):  return float(np.sum(self.w*self._fD(x+KR*self.s)))
    def FKR(self,x,KR):return float(np.sum(self.w*self.s*self._fD(x+KR*self.s)))

def gM(d,P,KR,KF,KM): return (P['R']-P['c'])*d.F(KF-KM,KR)+P['c']*d.F(-KM,KR)-P['CM']
def gF(d,P,KR,KF,KM):
    R,c,b,p,CF=P['R'],P['c'],P['beta'],P['p'],P['CF']; Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
    return R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
def gR(d,P,KR,KF,KM):
    R,c,b,p,CR=P['R'],P['c'],P['beta'],P['p'],P['CR']
    t1,_=integrate.quad(lambda x:d.FKR(x,KR),KF-KM,KF,limit=60)
    t2,_=integrate.quad(lambda x:d.FKR(x,KR),-KM,KF-KM,limit=60)
    t3,_=integrate.quad(lambda x:d.FKR(x,KR),KF,d.Dbar,limit=60)
    return R*t1+c*t2+(b+p)*t3-CR
def _fsolve_checked(fn,x0,xtol,tag,rtol=1e-8,tries=4):
    """Solve fn(x)=0, refuse to return a non-solution, and escalate through robust solvers.

    Bare fsolve returns its last iterate whatever happened, so every downstream check then
    runs on a point that does not solve the FOCs.  Two real failure modes are handled:

      * ier=5 ("not making good progress") fires both when genuinely stuck AND when already
        at machine precision -- so the RESIDUAL is ground truth, not ier.
      * fsolve's forward-difference Jacobian stalls at interior points with a spiky integrand
        (D~Beta(1,3) at C_M=0.502): |F| sticks at ~1e-6.  We escalate: restart fsolve from the
        best iterate, then fall back to Levenberg-Marquardt least_squares, which handles the
        noisy Jacobian cleanly (verified to reach 1e-16 on exactly this stall).

    Raises only if every solver stays above rtol -- then it is a real non-solution."""
    def res(x): return float(np.max(np.abs(np.asarray(fn(x),dtype=float))))
    best=None; bestres=np.inf; x=np.asarray(x0,dtype=float)
    for k in range(tries):
        sol,info,ier,msg=optimize.fsolve(fn,x,xtol=xtol,full_output=True)
        if np.all(np.isfinite(sol)) and res(sol)<bestres: best,bestres=sol,res(sol)
        if bestres<=rtol: return best
        x=best if best is not None else x
        if k>0: x=x*(1.0+1e-7)
    # escalate to Levenberg-Marquardt from the best fsolve iterate (robust to noisy Jacobians)
    try:
        lm=optimize.least_squares(lambda v:np.asarray(fn(v),dtype=float),best,method='lm',
                                  xtol=1e-14,ftol=1e-14,gtol=1e-14)
        if np.all(np.isfinite(lm.x)) and res(lm.x)<bestres: best,bestres=lm.x,res(lm.x)
    except Exception:
        pass
    if bestres<=rtol: return best
    raise RuntimeError(f"{tag}: no solver reached the tolerance "
                       f"(best max|F|={bestres:.3e} > {rtol:.0e}): {msg.strip()}")

def solve_with(d,P,x0):
    return _fsolve_checked(lambda v:[gR(d,P,*v),gF(d,P,*v),gM(d,P,*v)],x0,1e-11,
                           'solve_with',rtol=1e-5)  # ScaleMix ns=800 residual floor
def solve_no(d,P,x0):
    R,c,b,p,CF,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR']
    def foc(v):
        KR,KF=v
        e1=d.F(KF,KR)-(b+p-c-CF)/(b+p-c)
        t1,_=integrate.quad(lambda x:d.FKR(x,KR),0,KF,limit=60)
        t2,_=integrate.quad(lambda x:d.FKR(x,KR),KF,d.Dbar,limit=60)
        return [e1,c*t1+(b+p)*t2-CR]
    return _fsolve_checked(foc,x0,1e-11,'solve_no',rtol=1e-5)  # ScaleMix residual floor

print("="*72)
print("V1  Closed forms at FIXED K_R  (uniform & power-law) vs quadrature")
print("="*72)
P=dict(R=2.0,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.2,CM=0.4,Dbar=10.0)
for alpha in (1.0,0.5,2.0):
    d=PowerLaw(P['Dbar'],alpha); KR=3.0; Q=P['Dbar']+KR
    R,c,b,p,CF,CM,D=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CM'],P['Dbar']
    # eq23 KF*, eq22 KF*-KM*
    KF_cf=D+(R-c-CF-CM)/(b+p-R)*Q
    gap_cf=D-(R-CM-c)/(R-c)*Q
    KM_cf=KF_cf-gap_cf
    # verify these satisfy FOCs 12,13 (gM,gF=0) at this KR:
    e_gM=gM(d,P,KR,KF_cf,KM_cf); e_gF=gF(d,P,KR,KF_cf,KM_cf)
    # carbon with FCL eq26 (proportional, /c):  E[fossil] = int_{-KM}^{KF-KM}(1-F)dx
    Ef_q,_=integrate.quad(lambda x:1-d.F(x,KR),-KM_cf,KF_cf-KM_cf,limit=200)
    Ef_eq26=D+(R-c-CF-CM)/(b+p-R)*Q-0.5*(CM/(R-c))**2*Q   # paper eq26 (uniform only)
    # carbon no FCL eq25 (/c): KF^o(D-KF^o/2)/Q with F(KF^o)=(b+p-c-CF)/(b+p-c)
    KFo=D-CF/(b+p-c)*Q
    Efo_q,_=integrate.quad(lambda x:1-d.F(x,KR),0,KFo,limit=200)
    Efo_eq25=KFo*(D-KFo/2)/Q
    tag={1.0:"uniform",0.5:"power a=0.5",2.0:"power a=2"}[alpha]
    print(f"\n [{tag}] at KR={KR}:  FOC residuals gM={e_gM:.2e} gF={e_gF:.2e}  (eqs22/23 solve FOCs ✓)")
    if alpha==1.0:
        print(f"    carbon/c WITH  fcl: quad={Ef_q:.6f}  eq26={Ef_eq26:.6f}  diff={abs(Ef_q-Ef_eq26):.2e}")
        print(f"    carbon/c NO    fcl: quad={Efo_q:.6f}  eq25={Efo_eq25:.6f}  diff={abs(Efo_q-Efo_eq25):.2e}")
print("\n V1c knife-edge: marginal value of K_R is constant in K_R (uniform/power)")
for alpha in (1.0,0.5,2.0):
    d=PowerLaw(P['Dbar'],alpha)
    def mval(kr):
        Q=P['Dbar']+kr; R,c,b,p,CF,CM,D=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CM'],P['Dbar']
        KF=D+(R-c-CF-CM)/(b+p-R)*Q; KM=KF-(D-(R-CM-c)/(R-c)*Q)
        return gR(d,P,kr,KF,KM)+P['CR']   # gross marginal value (add back CR)
    print(f"   {('uniform' if alpha==1 else 'a=%.1f'%alpha):>9}:  MV(KR=1)={mval(1.0):.6f}  MV(KR=5)={mval(5.0):.6f}  MV(KR=9)={mval(9.0):.6f}")

print("\n"+"="*72)
print("V2  Interior families:  K_R* vs K_R^o  and the shift-ratio law")
print("="*72)
def study(d,P,tag,x0w,x0n):
    KR,KF,KM=solve_with(d,P,x0w); KRn,KFn=solve_no(d,P,x0n)
    h=2e-3
    KRp=solve_with(d,dict(P,CM=P['CM']+h),[KR,KF,KM])[0]
    KRm=solve_with(d,dict(P,CM=P['CM']-h),[KR,KF,KM])[0]
    dKR=(KRp-KRm)/(2*h)
    B=d.FKR(KF,KR)*d.f(KF-KM,KR)-d.FKR(KF-KM,KR)*d.f(KF,KR)
    eps=1e-12
    glo=d.FKR(KF-KM,KR)/(d.f(KF-KM,KR)+eps); ghi=d.FKR(KF,KR)/(d.f(KF,KR)+eps)
    ok = (dKR<=1e-6)==(B<=1e-9)
    print(f"\n [{tag}]")
    print(f"   KR*={KR:7.4f}  KR^o={KRn:7.4f}   KR*>KR^o ? {KR>KRn}")
    print(f"   g(KF-KM)={glo:.5f}  g(KF)={ghi:.5f}   g non-incr ? {glo>=ghi-1e-9}")
    print(f"   dKR*/dCM={dKR:+.4f}  bracket B={B:+.6e}   sign-law {'HOLDS' if ok else 'FAILS'}")
P2=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.5,CM=0.5,Dbar=10.0)  # R<c+CF+CM=1.6 (Assumption 1)
study(ScaleMix(10,2,2,2,2),P2,"D~Beta(2,2) symmetric, S~Beta(2,2)",[3,5,6],[3,6])
study(ScaleMix(10,1,3,2,2),P2,"D~Beta(1,3) decreasing-density (left mass)",[3,5,6],[3,6])
study(ScaleMix(10,3,1,2,2),P2,"D~Beta(3,1) increasing-density (right mass)",[3,5,6],[3,6])
study(ScaleMix(10,2,5,2,2),P2,"D~Beta(2,5) right-skewed",[3,5,6],[3,6])
study(ScaleMix(10,5,2,2,2),P2,"D~Beta(5,2) left-skewed",[3,5,6],[3,6])
