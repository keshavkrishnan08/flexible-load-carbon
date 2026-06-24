"""
A1 EXTENSION verification: the CORRELATION comparative static.

Joint (D,S): D ~ Dbar*Beta(2,2);  S|D ~ Beta with mean m(D)=0.5 - rho*(D/Dbar-0.5)
(concentration nu).  rho>0  => S falls with D  => NEGATIVE corr(D,S).
Residual demand x = D - K_R*S.

Closed identities (derived in the memo), with s*=(d-x)/K_R:
  F(x;K_R)   = ∫ fD(d) [1 - F_{S|d}(s*)] dd
  f(x;K_R)   = ∫ fD(d)  f_{S|d}(s*)/K_R dd
  F_KR(x;K_R)= ∫ fD(d)  f_{S|d}(s*) * s*/K_R dd     => g(x)=F_KR/f = E[S | quantile x]

Predict: more negative corr(D,S) (higher rho) makes g(x) steeper-decreasing
(shift-ratio condition), so K*_R rises and the carbon margin improves:
  dK*_R/drho > 0,   d(carbon reduction)/drho > 0.
"""
import numpy as np
from scipy import integrate, optimize
from scipy.stats import beta as Beta

Dbar=10.0; nu=8.0
fD = lambda d: np.where((d>=0)&(d<=Dbar), Beta(2,2).pdf(np.clip(d/Dbar,1e-9,1-1e-9))/Dbar, 0.0)
def mS(d,rho): return np.clip(0.5 - rho*(d/Dbar-0.5), 0.05,0.95)
def fScond(s,d,rho):
    m=mS(d,rho); a=nu*m; b=nu*(1-m)
    return Beta(a,b).pdf(np.clip(s,1e-9,1-1e-9))
def FScond(s,d,rho):
    m=mS(d,rho); a=nu*m; b=nu*(1-m)
    return Beta(a,b).cdf(np.clip(s,0,1))

# grid over d for quadrature
DD=np.linspace(1e-3,Dbar-1e-3,400); wD=fD(DD); wD=wD/np.trapz(wD,DD)

def F(x,KR,rho):
    s=np.clip((DD-x)/KR,0,1); return np.trapz(wD*(1-FScond(s,DD,rho)),DD)
def fdens(x,KR,rho):
    s=(DD-x)/KR; inside=(s>=0)&(s<=1)
    return np.trapz(wD*np.where(inside,fScond(np.clip(s,0,1),DD,rho),0.0)/KR,DD)
def FKR(x,KR,rho):
    s=(DD-x)/KR; inside=(s>=0)&(s<=1)
    return np.trapz(wD*np.where(inside,fScond(np.clip(s,0,1),DD,rho)*s/KR,0.0),DD)

def gR(P,rho,KR,KF,KM):
    R,c,b,p,CR=P['R'],P['c'],P['beta'],P['p'],P['CR']
    xs1=np.linspace(KF-KM,KF,60); xs2=np.linspace(-KM,KF-KM,60); xs3=np.linspace(KF,Dbar,60)
    t1=np.trapz([FKR(x,KR,rho) for x in xs1],xs1)
    t2=np.trapz([FKR(x,KR,rho) for x in xs2],xs2)
    t3=np.trapz([FKR(x,KR,rho) for x in xs3],xs3)
    return R*t1+c*t2+(b+p)*t3-CR
def gM(P,rho,KR,KF,KM): return (P['R']-P['c'])*F(KF-KM,KR,rho)+P['c']*F(-KM,KR,rho)-P['CM']
def gF(P,rho,KR,KF,KM):
    R,c,b,p,CF=P['R'],P['c'],P['beta'],P['p'],P['CF']; Fk=F(KF,KR,rho); Fg=F(KF-KM,KR,rho)
    return R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
def solve_with(P,rho,x0):
    return optimize.fsolve(lambda v:[gR(P,rho,*v),gF(P,rho,*v),gM(P,rho,*v)],x0,xtol=1e-8)
def solve_no(P,rho,x0):
    R,c,b,p,CF,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR']
    def foc(v):
        KR,KF=v
        e1=F(KF,KR,rho)-(b+p-c-CF)/(b+p-c)
        xs1=np.linspace(0,KF,60); xs2=np.linspace(KF,Dbar,60)
        return [e1, c*np.trapz([FKR(x,KR,rho) for x in xs1],xs1)+(b+p)*np.trapz([FKR(x,KR,rho) for x in xs2],xs2)-CR]
    return optimize.fsolve(foc,x0,xtol=1e-8)
def Efossil(KR,KF,KM,rho):
    xs=np.linspace(-KM,KF-KM,120); return np.trapz([1-F(x,KR,rho) for x in xs],xs)

P=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.25,CM=0.45,Dbar=Dbar)
print(f"{'rho':>6} {'corr(D,S)':>9} {'KR*':>7} {'KR^o':>7} {'KR*>KRo':>7} {'carbonMargin(o-*)':>17}")
star=[3,5,6]
res=[]
for rho in [-0.4,-0.2,0.0,0.2,0.4]:
    # empirical corr(D,S)
    ds=np.random.default_rng(0).random((40000,)); # not used; compute corr analytically-ish via grid
    sgrid=np.linspace(0.01,0.99,50)
    ED=np.trapz(wD*DD,DD);
    EDS=np.trapz(wD*DD*mS(DD,rho),DD); ES=np.trapz(wD*mS(DD,rho),DD)
    VD=np.trapz(wD*(DD-ED)**2,DD);
    cov=EDS-ED*ES
    # var S approx (ignore conditional var for corr sign indicator)
    corr_sign=cov
    try:
        sw=solve_with(P,rho,star); KR,KF,KM=sw
        sn=solve_no(P,rho,[KR*0.6,KF]); KRn,KFn=sn
        if KM>1e-2: star=sw
        marg=Efossil(KRn,KFn,0.0,rho)-Efossil(KR,KF,KM,rho)
        print(f"{rho:6.2f} {cov:9.3f} {KR:7.3f} {KRn:7.3f} {str(KR>KRn):>7} {marg:17.4f}")
        res.append((rho,KR,KRn,marg))
    except Exception as e:
        print(f"{rho:6.2f}  ERR {e}")
import numpy as np
if len(res)>=3:
    KRs=[r[1] for r in res]; margs=[r[3] for r in res]
    print(f"\nK*_R increasing in rho (more neg corr)? {all(np.diff(KRs)>-1e-3)}")
    print(f"carbon margin increasing in rho?         {all(np.diff(margs)>-1e-3)}")
