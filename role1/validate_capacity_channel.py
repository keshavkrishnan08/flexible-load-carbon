"""Fast vectorized V2: K_R* vs K_R^o and the shift-ratio sign-law,
on Beta scale-mixtures x = D - K_R S.  Fixed-grid trapezoid integration."""
import numpy as np
from scipy import optimize
from scipy.stats import beta

class ScaleMix:
    def __init__(self, Dbar, ad,bd, as_,bs, ns=400):
        self.Dbar=Dbar; self.bD=beta(ad,bd)
        s=(np.arange(ns)+0.5)/ns; w=beta(as_,bs).pdf(s); self.s=s; self.w=w/w.sum()
    def _fD(self,d):
        z=np.clip(np.asarray(d)/self.Dbar,0,1)
        return np.where((d>=0)&(d<=self.Dbar), self.bD.pdf(np.clip(z,1e-9,1-1e-9))/self.Dbar,0.0)
    def _FD(self,d): return self.bD.cdf(np.clip(np.asarray(d)/self.Dbar,0,1))
    def F(self,x,KR):  return float(np.dot(self.w,self._FD(x+KR*self.s)))
    def f(self,x,KR):  return float(np.dot(self.w,self._fD(x+KR*self.s)))
    def FKR(self,x,KR):return float(np.dot(self.w,self.s*self._fD(x+KR*self.s)))
    # vectorized grid integrals of FKR over [a,b]
    def intFKR(self,a,b,KR,n=600):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*self.s[None,:]
        vals=(self._fD(X.ravel()).reshape(X.shape)*self.s[None,:]).dot(self.w)
        return np.trapz(vals,xs)
    def intF(self,a,b,KR,n=600):
        xs=np.linspace(a,b,n); X=xs[:,None]+KR*self.s[None,:]
        vals=self._FD(X.ravel()).reshape(X.shape).dot(self.w)
        return np.trapz(vals,xs)

def focs_with(d,P,v):
    KR,KF,KM=v; R,c,b,p,CF,CR,CM=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR'],P['CM']
    gM=(R-c)*d.F(KF-KM,KR)+c*d.F(-KM,KR)-CM
    Fk=d.F(KF,KR); Fg=d.F(KF-KM,KR)
    gF=R*(Fk-Fg)-c*(1-Fg)+(b+p)*(1-Fk)-CF
    gR=R*d.intFKR(KF-KM,KF,KR)+c*d.intFKR(-KM,KF-KM,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR
    return [gR,gF,gM]
def focs_no(d,P,v):
    KR,KF=v; R,c,b,p,CF,CR=P['R'],P['c'],P['beta'],P['p'],P['CF'],P['CR']
    e1=d.F(KF,KR)-(b+p-c-CF)/(b+p-c)
    e2=c*d.intFKR(0,KF,KR)+(b+p)*d.intFKR(KF,d.Dbar,KR)-CR
    return [e1,e2]

def study(d,P,tag):
    sw=optimize.fsolve(lambda v:focs_with(d,P,v),[3,5,6],full_output=True)
    KR,KF,KM=sw[0]; conv=sw[2]==1
    sn=optimize.fsolve(lambda v:focs_no(d,P,v),[3,6]); KRn=sn[0]
    h=3e-3
    KRp=optimize.fsolve(lambda v:focs_with(d,dict(P,CM=P['CM']+h),v),[KR,KF,KM])[0]
    KRm=optimize.fsolve(lambda v:focs_with(d,dict(P,CM=P['CM']-h),v),[KR,KF,KM])[0]
    dKR=(KRp-KRm)/(2*h)
    B=d.FKR(KF,KR)*d.f(KF-KM,KR)-d.FKR(KF-KM,KR)*d.f(KF,KR)
    eps=1e-12  # guard: f(KF)->0 at the upper endpoint for incr/left-skew densities
    glo=d.FKR(KF-KM,KR)/(d.f(KF-KM,KR)+eps); ghi=d.FKR(KF,KR)/(d.f(KF,KR)+eps)
    ok=(dKR<=1e-4)==(B<=1e-10)
    print(f"[{tag}]\n  KR*={KR:7.4f} KR^o={KRn:7.4f}  KR*>KR^o? {KR>KRn}  (conv={conv})")
    print(f"  g(KF-KM)={glo:.5f} g(KF)={ghi:.5f}  g non-incr? {glo>=ghi-1e-9}")
    print(f"  dKR*/dCM={dKR:+.4f}  B={B:+.3e}  sign-law {'HOLDS' if ok else 'FAILS'}\n")

P=dict(R=1.4,c=0.5,beta=4.0,p=1.0,CF=0.6,CR=0.5,CM=0.5,Dbar=10.0)
for (ad,bd,tag) in [(2,2,"D~Beta(2,2) symmetric"),(1,3,"D~Beta(1,3) decr-density"),
                    (3,1,"D~Beta(3,1) incr-density"),(2,5,"D~Beta(2,5) right-skew"),
                    (5,2,"D~Beta(5,2) left-skew"),(2,8,"D~Beta(2,8) strong right-skew")]:
    try: study(ScaleMix(10,ad,bd,2,2),P,tag)
    except Exception as e: print(f"[{tag}] ERR {e}\n")
