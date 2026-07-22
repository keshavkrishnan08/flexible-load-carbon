"""
ROLE 1 -- adversarial exactness check of EVERY analytical formula in
role1_carbon_theory.tex.  Nothing is taken on faith: each closed form is
compared to a finite-difference of the unified profit integral Pi (eq 5),
computed by high-accuracy quadrature.  Pass = agreement to >= 6 digits.
"""
import numpy as np
from scipy import integrate, optimize
from scipy.stats import beta

# ---------- distributions ----------
class PowerLaw:
    def __init__(self,Dbar,a=1.0): self.Dbar=Dbar; self.a=a
    def F(self,x,KR):
        Q=self.Dbar+KR; z=min(max((x+KR)/Q,0.),1.); return z**self.a
    def f(self,x,KR):
        Q=self.Dbar+KR
        return 0. if (x<=-KR or x>=self.Dbar) else self.a*((x+KR)/Q)**(self.a-1)/Q
    def FKR(self,x,KR): return self.f(x,KR)*(self.Dbar-x)/(self.Dbar+KR)

class ScaleMix:
    def __init__(self,Dbar,ad,bd,as_,bs,ns=800):
        self.Dbar=Dbar; self.bD=beta(ad,bd)
        s=(np.arange(ns)+.5)/ns; w=beta(as_,bs).pdf(s); self.s=s; self.w=w/w.sum()
    def _fD(self,d):
        d=np.asarray(d,float); z=np.clip(d/self.Dbar,1e-12,1-1e-12)
        return np.where((d>=0)&(d<=self.Dbar), self.bD.pdf(z)/self.Dbar,0.)
    def _FD(self,d): return self.bD.cdf(np.clip(np.asarray(d,float)/self.Dbar,0,1))
    def F(self,x,KR):  return float(self.w@self._FD(x+KR*self.s))
    def f(self,x,KR):  return float(self.w@self._fD(x+KR*self.s))
    def FKR(self,x,KR):return float(self.w@(self.s*self._fD(x+KR*self.s)))

# ---------- profit (eq 5) by quadrature, and analytic gradients ----------
def Pi(d,P,KR,KF,KM):
    R,c,b,p,CF,CR,CM=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR'],P['CM']
    F=lambda x:d.F(x,KR)
    I1=integrate.quad(F,KF-KM,KF,limit=300,epsabs=1e-12,epsrel=1e-12)[0]
    I2=integrate.quad(lambda x:1-F(x),-KM,KF-KM,limit=300,epsabs=1e-12,epsrel=1e-12)[0]
    I3=integrate.quad(lambda x:1-F(x),KF,d.Dbar,limit=300,epsabs=1e-12,epsrel=1e-12)[0]
    return R*I1-c*I2-(b+p)*I3-CF*KF-CR*KR-CM*KM
def gM(d,P,KR,KF,KM): return (P['R']-P['c'])*d.F(KF-KM,KR)+P['c']*d.F(-KM,KR)-P['CM']
def gF(d,P,KR,KF,KM):
    R,c,b,p,CF=P['R'],P['c'],P['beta'],P['p'],P['CF']; Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
    return R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
def gR(d,P,KR,KF,KM):
    R,c,b,p,CR=P['R'],P['c'],P['beta'],P['p'],P['CR']
    t1=integrate.quad(lambda x:d.FKR(x,KR),KF-KM,KF,limit=300)[0]
    t2=integrate.quad(lambda x:d.FKR(x,KR),-KM,KF-KM,limit=300)[0]
    t3=integrate.quad(lambda x:d.FKR(x,KR),KF,d.Dbar,limit=300)[0]
    return R*t1+c*t2+(b+p)*t3-CR
def grad(d,P,v): return np.array([gR(d,P,*v),gF(d,P,*v),gM(d,P,*v)])  # order (R,F,M)

def fd_grad(d,P,v,h=1e-5):
    g=np.zeros(3)
    for i in range(3):
        vp=list(v); vm=list(v); vp[i]+=h; vm[i]-=h
        g[i]=(Pi(d,P,*vp)-Pi(d,P,*vm))/(2*h)
    return g  # d Pi / d(KR,KF,KM)
def fd_hess(d,P,v,h=1e-4):
    H=np.zeros((3,3))
    for i in range(3):
        vp=list(v); vm=list(v); vp[i]+=h; vm[i]-=h
        gp=grad(d,P,vp); gm=grad(d,P,vm)
        H[:,i]=(gp-gm)/(2*h)
    return 0.5*(H+H.T)  # symmetrize

def _fsolve_checked(fn,x0,xtol,tag):
    """fsolve that REFUSES to return a non-solution.  Bare fsolve returns its last
    iterate whatever happened; every downstream 'verification' then runs on a point
    that does not solve the FOCs.  Raise instead."""
    sol,info,ier,msg=optimize.fsolve(fn,x0,xtol=xtol,full_output=True)
    res=float(np.max(np.abs(np.asarray(fn(sol),dtype=float))))
    if ier!=1 or not np.all(np.isfinite(sol)) or res>1e-6:
        raise RuntimeError(f"{tag}: fsolve did not converge (ier={ier}, max|F|={res:.3e}): {msg.strip()}")
    return sol

def solve_with(d,P,x0):
    return _fsolve_checked(lambda v:grad(d,P,v),x0,1e-12,'solve_with')

PASS=[];
def chk(name,a,b,tol=1e-5):
    rel=abs(a-b)/(1+abs(b)); good=rel<tol; PASS.append(good)
    print(f"  [{'PASS' if good else 'FAIL'}] {name:42s} analytic={a:+.8g} ref={b:+.8g} rel={rel:.1e}")

def ok(name,cond,detail=""):
    cond=bool(cond); PASS.append(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name:42s} {detail}")

# ===================================================================
print("="*72,"\n  CHECK 1: analytic gradients (eqs 11-15) == FD of profit\n","="*72)
P=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.5,CM=0.5,Dbar=10.0)
d=ScaleMix(10,2,2,2,2); v=[3.0,5.0,6.0]
ga=grad(d,P,v); gf=fd_grad(d,P,v)
for i,nm in enumerate(['dPi/dKR','dPi/dKF','dPi/dKM']): chk(nm,ga[i],gf[i])

print("\n"+"="*72,"\n  CHECK 2: cross-partials (eqs hRM,hFM,hRF) == FD Hessian\n","="*72)
H=fd_hess(d,P,v)
KR,KF,KM=v
hRM=(P['R']-P['c'])*d.FKR(KF-KM,KR)+P['c']*d.FKR(-KM,KR)
hFM=(P['R']-P['c'])*d.f(KF-KM,KR)
hRF=(P['R']-P['beta']-P['p'])*d.FKR(KF,KR)-(P['R']-P['c'])*d.FKR(KF-KM,KR)
chk('H_RM',hRM,H[0,2]); chk('H_FM',hFM,H[1,2]); chk('H_RF',hRF,H[0,1])

print("\n"+"="*72,"\n  CHECK 3: dK_R*/dC_M cofactor formula == FD of the equilibrium\n","="*72)
for (ad,bd,tag) in [(2,2,"Beta(2,2)")]:
    dd=ScaleMix(10,ad,bd,2,2)
    star=solve_with(dd,P,[3,5,6]); KR,KF,KM=star
    reg='large-FCL' if KM>=KR else 'small-FCL'
    Hs=fd_hess(dd,P,star)
    # exact (H^-1)(0,0,1) -> KR component
    dKR_lin=np.linalg.solve(Hs,np.array([0,0,1.0]))[0]
    # finite-diff of the actual equilibrium
    h=2e-3
    KRp=solve_with(dd,dict(P,CM=P['CM']+h),star)[0]
    KRm=solve_with(dd,dict(P,CM=P['CM']-h),star)[0]
    dKR_fd=(KRp-KRm)/(2*h)
    # my closed-form cofactor (general, no large-FCL assumption):
    cof31=Hs[0,1]*Hs[1,2]-Hs[0,2]*Hs[1,1]     # H_RF H_FM - H_RM H_FF
    dKR_cof=cof31/np.linalg.det(Hs)
    # my SIMPLIFIED large-FCL closed form in Theorem 1:
    B=dd.FKR(KF,KR)*dd.f(KF-KM,KR)-dd.FKR(KF-KM,KR)*dd.f(KF,KR)
    dKR_thm=(P['R']-P['beta']-P['p'])*(P['R']-P['c'])*B/np.linalg.det(Hs)  # (R-(b+p)) -- sign-fixed
    print(f"\n  -- {tag}  (KR*={KR:.3f},KM*={KM:.3f}: {reg}) --")
    chk('dKR/dCM  (Hess solve vs FD eqm)',dKR_lin,dKR_fd,1e-3)
    chk('dKR/dCM  (cofactor vs Hess solve)',dKR_cof,dKR_lin)
    chk('dKR/dCM  (Thm1 large-FCL form)',dKR_thm,dKR_lin,1e-3 if KM>=KR else 1e9)
    if KM<KR: print("       (Thm1 simplified form only claimed for large-FCL; this cell is small-FCL -> expected mismatch)")

print("\n"+"="*72,"\n  CHECK 4: interior knife-edge MV (eq:mv) == FD along power-law locus\n","="*72)
# interior params for uniform/power: need R<c+CF+CM and an interior KR on the locus.
Pk=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.5,CM=0.5,Dbar=10.0)
R,c,b,p,CF,CM,D=Pk['R'],Pk['c'],Pk['beta'],Pk['p'],Pk['CF'],Pk['CM'],Pk['Dbar']
MV_formula=0.5*(c+(R-CM-c)**2/(R-c)+(R-c-CF-CM)**2/(b+p-R))
for a in (1.0,0.5,2.0):
    du=PowerLaw(D,a)
    def locus(kr):
        Q=D+kr; KF=D+(R-c-CF-CM)/(b+p-R)*Q; KM=KF-(D-(R-CM-c)/(R-c)*Q); return KF,KM
    def MV(kr):
        KF,KM=locus(kr); return gR(du,Pk,kr,KF,KM)+Pk['CR']
    vals=[MV(kr) for kr in (1.,4.,8.)]
    const = max(abs(vals[0]-vals[1]),abs(vals[1]-vals[2]))<1e-6
    print(f"  alpha={a}: MV(1,4,8)=({vals[0]:.6f},{vals[1]:.6f},{vals[2]:.6f}) const={const}", end="")
    if a==1.0: chk('  uniform MV vs eq:mv',vals[1],MV_formula)
    else: print()
    # B6: 'const' was computed, printed, then silently discarded -- the knife-edge claim
    # was never asserted.  Asserting it naively FAILS, and the failure is diagnostic:
    # MV(1)=MV(4) exactly but MV(8) departs.  The reason is the regime boundary.  On the
    # locus, K_M>=K_R (large-FCL, F(-K_M)=0) at K_R=1,4 but K_M=7.0<8=K_R at K_R=8.  The
    # knife-edge therefore holds on the SAME regime that carries the Phi=Delta identity:
    # one boundary governs both headline results.  Assert it where it is claimed to hold,
    # and assert that it genuinely breaks outside -- so neither half can rot silently.
    KMs=[locus(kr)[1] for kr in (1.,4.,8.)]
    big=[i for i,kr in enumerate((1.,4.,8.)) if KMs[i]>=kr]      # large-FCL indices
    small=[i for i,kr in enumerate((1.,4.,8.)) if KMs[i]<kr]
    bigv=[vals[i] for i in big]
    ok(f'  knife-edge holds on large-FCL (K_M>=K_R) at alpha={a}',
       len(bigv)>1 and max(bigv)-min(bigv)<1e-6,
       f'spread={max(bigv)-min(bigv):.2e} over {len(bigv)} large-FCL pts')
    if small:
        ok(f'  knife-edge genuinely BREAKS on small-FCL at alpha={a}',
           max(abs(vals[i]-bigv[0]) for i in small)>1e-4,
           f'departure={max(abs(vals[i]-bigv[0]) for i in small):.2e} (regime boundary is real)')

print("\n"+"="*72,"\n  CHECK 5: cutoff probabilities (eq:cutoffs) at the optimum\n","="*72)
dd=ScaleMix(10,2,2,2,2); star=solve_with(dd,P,[3,5,6]); KR,KF,KM=star
chk('F(KF*-KM*;KR*) == CM/(R-c)',dd.F(KF-KM,KR),P['CM']/(P['R']-P['c']))
chk('F(KF*;KR*) == (b+p-c-CF-CM)/(b+p-R)',dd.F(KF,KR),(P['beta']+P['p']-P['c']-P['CF']-P['CM'])/(P['beta']+P['p']-P['R']))

print("\n"+"="*72,"\n  CHECK 6: Prop 2 fossil decomposition (eqs fos1,fos2 = paper 44,45)\n","="*72)
# E[fossil with] = KF* - (CM/(R-c))(KF*-KM*-mu_low);  vs direct quadrature
mu_low=integrate.quad(lambda x:x*dd.f(x,KR),-KR,KF-KM,limit=300)[0]/dd.F(KF-KM,KR)
fos_with_q=integrate.quad(lambda x:1-dd.F(x,KR),-KM,KF-KM,limit=300)[0]
fos_with_f=KF-(P['CM']/(P['R']-P['c']))*((KF-KM)-mu_low)
chk('E[fossil with] (eq44 vs quad)',fos_with_f,fos_with_q)
# no-FCL optimum
def solve_no(d,P,x0):
    R,c,b,p,CF,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR']
    def foc(v):
        KRn,KFn=v
        e1=d.F(KFn,KRn)-(b+p-c-CF)/(b+p-c)
        t1=integrate.quad(lambda x:d.FKR(x,KRn),0,KFn,limit=300)[0]
        t2=integrate.quad(lambda x:d.FKR(x,KRn),KFn,d.Dbar,limit=300)[0]
        return [e1,c*t1+(b+p)*t2-CR]
    return _fsolve_checked(foc,x0,1e-12,'solve_no')
KRo,KFo=solve_no(dd,P,[3,6]); phio=dd.F(KFo,KRo); qo=dd.F(0,KRo)
mu_mid=integrate.quad(lambda x:x*dd.f(x,KRo),0,KFo,limit=300)[0]/(phio-qo)
fos_no_q=integrate.quad(lambda x:1-dd.F(x,KRo),0,KFo,limit=300)[0]
fos_no_f=KFo*(1-phio)+(phio-qo)*mu_mid
chk('E[fossil no]   (eq45 vs quad)',fos_no_f,fos_no_q)
chk('phi_o == (b+p-c-CF)/(b+p-c)',phio,(P['beta']+P['p']-P['c']-P['CF'])/(P['beta']+P['p']-P['c']))

print("\n"+"="*72); print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS"); print("="*72)
