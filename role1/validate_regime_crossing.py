"""
Role 1 -- regime-crossing & Hessian-definiteness check (referee hardening).

Confirms two things Theorem 1's proof relies on:
  (i)  the adoption path crosses from small-FCL (K_M<K_R, near C_bar_M) to
       large-FCL (K_M>K_R, lower C_M), and dK_R*/dC_M < 0 holds in BOTH
       regimes -- so the capacity channel is not a large-FCL artifact;
  (ii) the Hessian is negative-definite (all eigenvalues < 0) on the interior
       path, degenerating (a zero eigenvalue) only at the knife-edge where
       K_R* -> infinity -- exactly where Condition (Regularity) is allowed to
       lapse because K_R*>K_R^o is then immediate.
"""
import numpy as np
from scipy import integrate, optimize
from scipy.stats import beta

class ScaleMix:
    def __init__(self,Dbar,ad,bd,as_,bs,ns=1500):
        self.Dbar=Dbar; self.bD=beta(ad,bd)
        s=(np.arange(ns)+.5)/ns; w=beta(as_,bs).pdf(s); self.s=s; self.w=w/w.sum()
    def _fD(self,d):
        d=np.asarray(d,float); z=np.clip(d/self.Dbar,1e-12,1-1e-12)
        return np.where((d>=0)&(d<=self.Dbar),self.bD.pdf(z)/self.Dbar,0.)
    def _FD(self,d): return self.bD.cdf(np.clip(np.asarray(d,float)/self.Dbar,0,1))
    def F(self,x,KR):  return float(self.w@self._FD(x+KR*self.s))
    def f(self,x,KR):  return float(self.w@self._fD(x+KR*self.s))
    def FKR(self,x,KR):return float(self.w@(self.s*self._fD(x+KR*self.s)))

def gR(d,P,KR,KF,KM):
    R,c,b,p,CR=P['R'],P['c'],P['beta'],P['p'],P['CR']
    t1=integrate.quad(lambda x:d.FKR(x,KR),KF-KM,KF,limit=120)[0]
    t2=integrate.quad(lambda x:d.FKR(x,KR),-KM,KF-KM,limit=120)[0]
    t3=integrate.quad(lambda x:d.FKR(x,KR),KF,d.Dbar,limit=120)[0]
    return R*t1+c*t2+(b+p)*t3-CR
def gM(d,P,KR,KF,KM): return (P['R']-P['c'])*d.F(KF-KM,KR)+P['c']*d.F(-KM,KR)-P['CM']
def gF(d,P,KR,KF,KM):
    R,c,b,p,CF=P['R'],P['c'],P['beta'],P['p'],P['CF']; Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
    return R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
def grad(d,P,v): return np.array([gR(d,P,*v),gF(d,P,*v),gM(d,P,*v)])
def _fsolve_checked(fn,x0,xtol,tag,rtol=1e-8,tries=4):
    """fsolve that REFUSES to return a non-solution, and polishes stalls before giving up.

    Two failure modes are handled separately, because they need opposite responses:

      * fsolve reports ier=5 ("not making good progress") both when it is genuinely stuck
        AND when it has already reached machine precision and cannot improve.  So the
        RESIDUAL is ground truth, not ier: accept on small |F| regardless of ier.

      * fsolve's forward-difference Jacobian can stall at a perfectly interior point that is
        merely an awkward start -- observed on D~Beta(1,3) at C_M=0.502, where the solve
        halts at |F|=2.3e-6 while the same point restarted converges to 1e-16.  So on a
        residual above rtol we POLISH: restart from the stalled iterate (with a vanishing
        jitter after the first retry to break the Jacobian symmetry) and keep the best.

    Only if every attempt stays above rtol do we raise -- then it is a real non-solution."""
    best=None; bestres=np.inf; x=np.asarray(x0,dtype=float)
    for k in range(tries):
        sol,info,ier,msg=optimize.fsolve(fn,x,xtol=xtol,full_output=True)
        res=float(np.max(np.abs(np.asarray(fn(sol),dtype=float))))
        if res<bestres and np.all(np.isfinite(sol)): best,bestres=sol,res
        if bestres<=rtol: return best
        # polish: restart from the best point so far, jittered after the first retry
        x=best if best is not None else x
        if k>0: x=x*(1.0+1e-7)
    raise RuntimeError(f"{tag}: fsolve did not solve the system after {tries} attempts "
                       f"(best max|F|={bestres:.3e} > {rtol:.0e}, last ier={ier}): {msg.strip()}")

def solve_with(d,P,x0):
    return _fsolve_checked(lambda v:grad(d,P,v),x0,1e-11,'solve_with')
def fd_hess(d,P,v,h=1e-4):
    H=np.zeros((3,3))
    for i in range(3):
        vp=list(v);vm=list(v);vp[i]+=h;vm[i]-=h
        H[:,i]=(grad(d,P,vp)-grad(d,P,vm))/(2*h)
    return 0.5*(H+H.T)

if __name__=="__main__":
    dd=ScaleMix(10,2,2,2,2)
    b,p,c,CF,R=4.0,1.0,0.5,0.6,1.4
    Cbar=(R-c)*(b+p-c-CF)/(b+p-c)
    print(f"C_bar_M = {Cbar:.4f}")
    print(f"{'C_M':>6} {'KR*':>7} {'KM*':>7} {'regime':>7} {'dKR/dCM':>9} {'NEGdef':>7}  eigenvalues")
    Dbar=10.0
    # The comparative static dKR/dCM needs an INTERIOR equilibrium.  At the low-CM end the
    # FCL grows until fossil capacity KF saturates against the demand ceiling Dbar; past that
    # there is no interior solution and the central difference straddles the boundary (the
    # perturbed solve runs off to KF~1e6).  The old sweep included CM=0.30, where KF=9.986
    # already sits within 0.2% of Dbar, and reported a dKR from a non-solution.  Guard it:
    # solve the perturbations, and only report the derivative when BOTH stay interior.
    star=[3,5,6]
    for CM in [0.77,0.70,0.60,0.50,0.40,0.30]:
        P=dict(R=R,c=c,beta=b,p=p,CF=CF,CR=0.5,CM=CM,Dbar=Dbar)
        star=solve_with(dd,P,star); KR,KF,KM=star
        interior = KF < 0.98*Dbar
        h=2e-3
        if interior:
            try:
                KRp=solve_with(dd,dict(P,CM=CM+h),star)[0]
                KRm=solve_with(dd,dict(P,CM=CM-h),star)[0]
                dKR=f"{(KRp-KRm)/(2*h):9.3f}"
            except RuntimeError:
                interior=False; dKR="  boundary"
        else:
            dKR="  boundary"
        eig=np.linalg.eigvalsh(fd_hess(dd,P,star))
        note = "" if interior else f"  <-- KF={KF:.3f} at ceiling Dbar={Dbar:.0f}: no interior comparative static"
        print(f"{CM:6.2f} {KR:7.3f} {KM:7.3f} {'large' if KM>=KR else 'small':>7} "
              f"{dKR:>9} {str(bool(np.all(eig<0))):>7}  {np.round(eig,3)}{note}")
