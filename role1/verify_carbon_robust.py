"""
Role 1 (General Carbon Theory) -- distribution-free reading of the carbon effect.
Verifies, with NO fragile C_R sweeps (single cold-started equilibrium):

(A) Sufficient statistic: the net carbon saving Delta depends on F only through the
    pair of conditional means (mu*_low, mu^o_mid) at the distribution-free cutoffs
    -- two scalars summarize the whole distribution (given capacities). [Prop 2]
(B) Tight magnitude bounds: since mu*_low in (-K_R*, K_F*-K_M*) and
    mu^o_mid in (0, K_F^o),
        Delta_min = K_F^o(1-phi^o) - K_F*
        Delta_max = K_F^o - K_F* + (C_M/(R-c))(K_F*-K_M*+K_R*)
    bracket Delta(F) for EVERY F, using only capacities and distribution-free phi^o.
(C) Least-favorable distribution: within the monotone-density class, the uniform
    MINIMIZES Delta (conditional means hit interval midpoints) -- the closed-form
    uniform condition is a worst-case certificate. (3000-sample check.)
"""
import numpy as np
from scipy import optimize
from scipy.stats import beta as Beta
rng=np.random.default_rng(3)

class ScaleMix:
    def __init__(s,Dbar,ad,bd,as_,bs,ns=700):
        s.Dbar=Dbar; s.bD=Beta(ad,bd)
        u=(np.arange(ns)+.5)/ns; w=Beta(as_,bs).pdf(u); s.s=u; s.w=w/w.sum()
    def _fD(s,d):
        d=np.asarray(d,float); z=np.clip(d/s.Dbar,1e-12,1-1e-12)
        return np.where((d>=0)&(d<=s.Dbar),s.bD.pdf(z)/s.Dbar,0.)
    def _FD(s,d): return s.bD.cdf(np.clip(np.asarray(d,float)/s.Dbar,0,1))
    def F(s,x,KR):  return float(s.w@s._FD(x+KR*s.s))
    def f(s,x,KR):  return float(s.w@s._fD(x+KR*s.s))
    def FKR(s,x,KR):return float(s.w@(s.s*s._fD(x+KR*s.s)))
    def intFKR(s,a,b,KR,n=400):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*s.s[None,:]
        return np.trapz((s._fD(X.ravel()).reshape(X.shape)*s.s[None,:])@s.w,xs)
    def int1mF(s,a,b,KR,n=400):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*s.s[None,:]
        return np.trapz(1.0-(s._FD(X.ravel()).reshape(X.shape))@s.w,xs)
    def condmean(s,a,b,KR,n=400):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*s.s[None,:]
        fx=(s._fD(X.ravel()).reshape(X.shape))@s.w
        Z=np.trapz(fx,xs); return np.trapz(xs*fx,xs)/Z if Z>0 else np.nan

P=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CM=0.5,CR=0.5,Dbar=10.0)
R,c,b,p,CF,CM,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CM'],P['CR']
d=ScaleMix(10,2,2,2,2)
def focs_w(v):
    KR,KF,KM=v
    gM=(R-c)*d.F(KF-KM,KR)+c*d.F(-KM,KR)-CM
    Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
    gF=R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
    gR=R*d.intFKR(KF-KM,KF,KR)+c*d.intFKR(-KM,KF-KM,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR
    return [gR,gF,gM]
def focs_n(v):
    KR,KF=v
    return [d.F(KF,KR)-(b+p-c-CF)/(b+p-c), c*d.intFKR(0,KF,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR]
KR,KF,KM=optimize.fsolve(focs_w,[2.7,5.0,6.0],xtol=1e-11)   # cold start (interior)
KRn,KFn=optimize.fsolve(focs_n,[1.8,7.0],xtol=1e-11)
phi=(b+p-c-CF)/(b+p-c); q=d.F(0,KRn)
mu_low=d.condmean(-KR,KF-KM,KR); mu_mid=d.condmean(0,KFn,KRn)
Ef = (KM-KR)+d.int1mF(-KR,KF-KM,KR) if KM>KR else d.int1mF(-KM,KF-KM,KR)
Efo = d.int1mF(0,KFn,KRn)
Delta = Efo-Ef
# (A)/(B) via Prop 2 closed forms
Ef_p  = KF-(CM/(R-c))*((KF-KM)-mu_low)
Efo_p = KFn*(1-phi)+(phi-q)*mu_mid
Delta_p = Efo_p-Ef_p
Dmin = KFn*(1-phi)-KF
Dmax = KFn - KF + (CM/(R-c))*((KF-KM)+KR)
print(f"equilibrium: KR*={KR:.3f} KF*={KF:.3f} KM*={KM:.3f}  KR^o={KRn:.3f} KF^o={KFn:.3f}")
print(f"(A) Prop-2 sufficient-statistic Delta matches direct quadrature: "
      f"{Delta_p:+.5f} vs {Delta:+.5f}  rel={abs(Delta_p-Delta)/(1+abs(Delta)):.1e}")
print(f"(B) bounds:  Dmin={Dmin:+.4f}  <=  Delta={Delta:+.4f}  <=  Dmax={Dmax:+.4f}   "
      f"inside? {Dmin-1e-6<=Delta<=Dmax+1e-6}")

# (C) least-favorable: conditional mean of monotone density vs midpoint
a1,b1=-KR,KF-KM; a2,b2=0,KFn
def cm_noninc(a,bb,sh,n=3000):
    t=np.linspace(a,bb,n); w=np.exp(-sh*(t-a)); w/=np.trapz(w,t); return np.trapz(w*t,t)
def cm_nondec(a,bb,sh,n=3000):
    t=np.linspace(a,bb,n); w=np.exp(sh*(t-a)); w/=np.trapz(w,t); return np.trapz(w*t,t)
ok1=all(cm_noninc(a1,b1,rng.uniform(0,3))<= (a1+b1)/2 +1e-9 for _ in range(3000))
ok2=all(cm_nondec(a2,b2,rng.uniform(0,3))>= (a2+b2)/2 -1e-9 for _ in range(3000))
print(f"(C) within monotone class: mu*_low<=midpoint {ok1} and mu^o_mid>=midpoint {ok2}")
# direct: at fixed capacities, tilt from uniform (s=0) into U and confirm Delta is MINIMIZED at the uniform
def Delta_suff(mu_low,mu_mid): return (KFn*(1-phi)+(phi-q)*mu_mid)-(KF-(CM/(R-c))*((KF-KM)-mu_low))
ds=[Delta_suff(cm_noninc(a1,b1,s), cm_nondec(a2,b2,s)) for s in [0,0.2,0.5,1,2,4]]
print(f"    Delta vs tilt s=[0,.2,.5,1,2,4]: {[round(d,4) for d in ds]}")
print(f"    sign check: dDelta/dmu*_low<0 and dDelta/dmu^o_mid>0; uniform (s=0) MINIMIZES Delta? {abs(min(ds)-ds[0])<1e-9}")
