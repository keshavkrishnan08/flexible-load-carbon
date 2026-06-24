"""
Role 1 -- general existence of the carbon threshold C_R_dagger, the rigorous way.

Anchor (proven): as C_R -> infinity, no renewables are affordable (K_R*=K_R^o=0),
so the FCL world differs from no-FCL only by the utilization effect (FCL on spare
fossil) => E[fossil*] > E[fossil^o] => Delta < 0.  Combined with continuity and
Delta>0 at small C_R (capacity substitution), IVT gives a finite threshold.

Here: cold-start each C_R (no warm-start trap); clamp K_R>=0; treat a diverging
K_R* (>CAP) as the unbounded-renewables regime where E[fossil*]=0 (fossil ->0).
Show Delta is decreasing through a sign change, and Delta<0 at large C_R.
"""
import numpy as np
from scipy import optimize
from scipy.stats import beta as Beta
CAP=60.0

class ScaleMix:
    def __init__(s,Dbar,ad,bd,as_,bs,ns=500):
        s.Dbar=Dbar; s.bD=Beta(ad,bd)
        u=(np.arange(ns)+.5)/ns; w=Beta(as_,bs).pdf(u); s.s=u; s.w=w/w.sum()
    def _fD(s,d):
        d=np.asarray(d,float); z=np.clip(d/s.Dbar,1e-12,1-1e-12)
        return np.where((d>=0)&(d<=s.Dbar),s.bD.pdf(z)/s.Dbar,0.)
    def _FD(s,d): return s.bD.cdf(np.clip(np.asarray(d,float)/s.Dbar,0,1))
    def F(s,x,KR):  return float(s.w@s._FD(x+KR*s.s))
    def intFKR(s,a,b,KR,n=250):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*s.s[None,:]
        return np.trapz((s._fD(X.ravel()).reshape(X.shape)*s.s[None,:])@s.w,xs)
    def int1mF(s,a,b,KR,n=250):
        if b<=a: return 0.0
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*s.s[None,:]
        return np.trapz(1.0-(s._FD(X.ravel()).reshape(X.shape))@s.w,xs)

def solve_with(d,P):
    R,c,b,p,CF,CR,CM=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR'],P['CM']
    def foc(v):
        KR,KF,KM=np.maximum(v,[0,0,0])
        gM=(R-c)*d.F(KF-KM,KR)+c*d.F(-KM,KR)-CM
        Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
        gF=R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
        gR=R*d.intFKR(KF-KM,KF,KR)+c*d.intFKR(-KM,KF-KM,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR
        return [gR,gF,gM]
    for x0 in ([1.0,5.0,6.0],[0.2,4.0,5.0],[5.0,8.0,9.0]):
        s,info,ier,_=optimize.fsolve(foc,x0,full_output=True,xtol=1e-9)
        if ier==1 and s[0]>-0.5: return np.maximum(s,[0,0,0])
    return np.maximum(s,[0,0,0])
def solve_no(d,P):
    R,c,b,p,CF,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR']
    def foc(v):
        KR,KF=np.maximum(v,[0,0])
        e1=d.F(KF,KR)-(b+p-c-CF)/(b+p-c)
        return [e1, c*d.intFKR(0,KF,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR]
    for x0 in ([0.5,6.0],[0.0,5.0],[5.0,8.0]):
        s,info,ier,_=optimize.fsolve(foc,x0,full_output=True,xtol=1e-9)
        if ier==1 and s[0]>-0.5: return np.maximum(s,[0,0])
    return np.maximum(s,[0,0])

def Delta(d,P):
    KR,KF,KM=solve_with(d,P); KRn,KFn=solve_no(d,P)
    Ef = 0.0 if KR>CAP else ((KM-KR)+d.int1mF(-KR,KF-KM,KR) if KM>KR else d.int1mF(-KM,KF-KM,KR))
    Efo = 0.0 if KRn>CAP else d.int1mF(0,KFn,KRn)
    return Efo-Ef, KR, KRn

def run(d,P,tag):
    print(f"\n[{tag}]  (R={P['R']},C_M={P['CM']})")
    prev=None; crossed=None
    for CR in [0.25,0.35,0.5,0.7,0.9,1.2,1.6,2.2,3.0]:
        P['CR']=CR
        D,KR,KRn=Delta(d,P)
        tag2 = "  Delta<0" if D<0 else ""
        print(f"   C_R={CR:4.2f}  KR*={'unb' if KR>CAP else f'{KR:5.2f}':>5}  KR^o={KRn:5.2f}  Delta={D:+8.4f}{tag2}")
        if prev is not None and prev[1]>=0 and D<0: crossed=(prev[0],CR)
        prev=(CR,D)
    print(f"   => sign change (C_R_dagger) bracketed in {crossed}" if crossed else "   => no crossing in range")

# favorable: high R (strong capacity substitution), C_M small, right-skew helps
P=dict(R=1.55,c=0.5,beta=4.0,p=1.0,CF=0.6,CM=0.45,Dbar=10.0)  # R<c+CF+CM=1.55? boundary -> use 1.54
P['R']=1.54
for ad,bd,t in [(2,5,'D~Beta(2,5) right-skew'),(2,8,'D~Beta(2,8) strong right-skew'),(2,2,'D~Beta(2,2)')]:
    run(ScaleMix(10,ad,bd,2,2),dict(P),t)
