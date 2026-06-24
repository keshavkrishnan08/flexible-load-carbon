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
def solve_with(d,P,x0): return optimize.fsolve(lambda v:grad(d,P,v),x0,xtol=1e-11)
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
    star=[3,5,6]
    for CM in [0.77,0.70,0.60,0.50,0.40,0.30]:
        P=dict(R=R,c=c,beta=b,p=p,CF=CF,CR=0.5,CM=CM,Dbar=10.0)
        star=solve_with(dd,P,star); KR,KF,KM=star
        h=2e-3
        KRp=solve_with(dd,dict(P,CM=CM+h),star)[0]; KRm=solve_with(dd,dict(P,CM=CM-h),star)[0]
        dKR=(KRp-KRm)/(2*h)
        eig=np.linalg.eigvalsh(fd_hess(dd,P,star))
        print(f"{CM:6.2f} {KR:7.3f} {KM:7.3f} {'large' if KM>=KR else 'small':>7} "
              f"{dKR:9.3f} {str(bool(np.all(eig<0))):>7}  {np.round(eig,3)}")
