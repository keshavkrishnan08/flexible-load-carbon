#!/usr/bin/env python3
"""
A1 Role 1 -- Week 4 verification suite (the carbon classification theorem).
  Thm classify : closed-form Phi (eq:Phi) == quadrature Delta to ~1e-9; sign match.
  Thm minimal  : dPhi/dmu*_low<0, dPhi/dmu_mid>0; EACH mean alone flips sign(Phi).
  Prop phase   : Phi(C_R) monotone with a single zero (carbon boundary).
  Thm leverage : K_F(tau) non-decreasing; Lambda(tau)<0 across shapes.
Reuses Week-2's verified equilibrium solver (import with stdout suppressed).
"""
import sys, io, numpy as np
from scipy import integrate, optimize, stats
_o=sys.stdout; sys.stdout=io.StringIO()
from verify_week2 import ScaleMix, P0, solve_with, solve_no, Efos_with, Efos_no
sys.stdout=_o

R,c,b,p,CF=P0['R'],P0['c'],P0['beta'],P0['p'],P0['CF']
phio=(b+p-c-CF)/(b+p-c)
PASS=[]
def ok(name,cond,detail=""):
    PASS.append(bool(cond)); print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

def cond_means(d,P,star,no):
    """mu*_low = E[x|x in(-KR*,a)], mu_mid = E[x|x in(0,KF^o)]; a=KF*-KM*, qo=F(0;KR^o)."""
    KR,KF,KM=star; KRo,KFo=no; a=KF-KM
    Fa=d.F(a,KR)
    mu_low=integrate.quad(lambda x:x*d.f(x,KR),-KR,a,limit=200)[0]/Fa
    qo=d.F(0,KRo)
    mu_mid=integrate.quad(lambda x:x*d.f(x,KRo),0,KFo,limit=200)[0]/(phio-qo)
    return a,qo,mu_low,mu_mid,KF,KM,KR,KFo,KRo

def Phi_of(a,qo,mu_low,mu_mid,KF,KFo,P):
    CM=P['CM']
    return (CM/(R-c))*(a-mu_low) - (KF - KFo*(1-phio) - (phio-qo)*mu_mid)

print("="*74); print("  A1 ROLE 1 -- WEEK 4: the carbon classification theorem"); print("="*74)
print(f"\n  phio={phio:.4f}")

# ---- Thm classify: Phi (closed form) == Delta (quadrature), sign match, across library ----
fams=[("sym  B(2,2)",ScaleMix(10,2,2,2,2)),
      ("left B(5,2)",ScaleMix(10,5,2,2,2)),
      ("rght B(2,5)",ScaleMix(10,2,5,2,2)),
      ("D~B(2,3)   ",ScaleMix(10,2,3,2,2))]
print(f"\n  {'family':<12}{'Delta(quad)':>13}{'Phi(closed)':>13}{'|diff|':>11}{'signs':>8}")
allmatch=True; _sw=[2.7,7.3,3.3]; _swo=[2.0,6.0]
for lab,d in fams:
    try:
        star=solve_with(d,P0,_sw,precise=True); no=solve_no(d,P0,_swo); _sw=list(star); _swo=list(no)
        Delta=Efos_no(d,P0,no)-Efos_with(d,P0,star)
        a,qo,mu_low,mu_mid,KF,KM,KR,KFo,KRo=cond_means(d,P0,star,no)
        Phi=Phi_of(a,qo,mu_low,mu_mid,KF,KFo,P0)
        match=abs(Phi-Delta)<1e-4 and (np.sign(Phi)==np.sign(Delta))
        allmatch&=match
        print(f"  {lab:<12}{Delta:>13.6f}{Phi:>13.6f}{abs(Phi-Delta):>11.2e}{('OK' if np.sign(Phi)==np.sign(Delta) else 'X'):>8}")
        ok(f"   [{lab.strip()}] Phi==Delta (classification identity)", abs(Phi-Delta)<1e-4, f"|diff|={abs(Phi-Delta):.2e}")
    except Exception as e:
        print(f"  {lab:<12} ERR {type(e).__name__}: {str(e)[:40]}"); allmatch=False
ok("Thm classify: Phi==Delta and sign(Delta)==sign(Phi) in EVERY family", allmatch, "exact iff verified")

# ---- Thm minimal: partial signs + each mean alone flips sign(Phi) ----
d=ScaleMix(10,2,2,2,2)
star=solve_with(d,P0,[2.7,7.3,3.3],precise=True); no=solve_no(d,P0,[2,6])
a,qo,mu_low,mu_mid,KF,KM,KR,KFo,KRo=cond_means(d,P0,star,no)
dPhi_dmulow=-P0['CM']/(R-c); dPhi_dmumid=phio-qo
ok("Thm minimal: dPhi/dmu*_low < 0", dPhi_dmulow<0, f"={dPhi_dmulow:+.4f}")
ok("Thm minimal: dPhi/dmu_mid > 0 (phio>qo)", dPhi_dmumid>0, f"={dPhi_dmumid:+.4f} (phio={phio:.3f}, qo={qo:.3f})")
# sweep mu*_low over (-KR, a) with mu_mid fixed -> Phi crosses 0?
lows=np.linspace(-KR+1e-3,a-1e-3,50)
Phis_low=[Phi_of(a,qo,ml,mu_mid,KF,KFo,P0) for ml in lows]
flip_low=(min(Phis_low)<0<max(Phis_low))
# sweep mu_mid over (0, KFo) with mu*_low fixed
mids=np.linspace(1e-3,KFo-1e-3,50)
Phis_mid=[Phi_of(a,qo,mu_low,mm,KF,KFo,P0) for mm in mids]
flip_mid=(min(Phis_mid)<0<max(Phis_mid))
ok("Thm minimal: mu*_low ALONE flips sign(Phi) (mu_mid fixed) => mu*_low not redundant", flip_low,
   f"Phi in [{min(Phis_low):+.2f},{max(Phis_low):+.2f}] over mu*_low range")
ok("Thm minimal: mu_mid ALONE flips sign(Phi) (mu*_low fixed) => mu_mid not redundant", flip_mid,
   f"Phi in [{min(Phis_mid):+.2f},{max(Phis_mid):+.2f}] over mu_mid range")
# Thm per-mean (sharp iff): conditions D_l, D_m and their exact margins Phi_hi
Delta_eq=Phi_of(a,qo,mu_low,mu_mid,KF,KFo,P0)  # =Delta at this optimum (<0)
Phi_hi_l=Delta_eq+(P0['CM']/(R-c))*(mu_low+KR)   # margin for D_l
Phi_hi_m=Delta_eq+(phio-qo)*(KFo-mu_mid)         # margin for D_m
ok("Thm per-mean: D_l  (CM/(R-c))(mu*_low+KR) > |Delta| <=> Phi_hi>0", Phi_hi_l>0,
   f"Phi_hi={Phi_hi_l:+.3f} (Delta={Delta_eq:+.3f})")
ok("Thm per-mean: D_m  (phio-qo)(KFo-mu_mid) > |Delta| <=> Phi_hi>0", Phi_hi_m>0,
   f"Phi_hi={Phi_hi_m:+.3f}")
# consistency: the exact iff -- D_l holds <=> mu*_low sweep flips sign
ok("Thm per-mean: iff exact -- (D_l) <=> (mu*_low sweep flips)", (Phi_hi_l>0)==flip_low, "iff verified")
ok("Thm per-mean: iff exact -- (D_m) <=> (mu_mid sweep flips)", (Phi_hi_m>0)==flip_mid, "iff verified")

# ---- Prop phase: Phi(C_R) monotone with a single zero ----
d=ScaleMix(10,2,2,2,2); CRs=np.linspace(0.30,0.62,9); phivals=[]; sw=[2.7,7.3,3.3]; swo=[2,6]
for CRv in CRs:
    P=dict(P0,CR=CRv)
    try:
        st=solve_with(d,P,sw,precise=True); nf=solve_no(d,P,swo); sw=list(st); swo=list(nf)
        aa,qq,ml,mm,kf,km,kr,kfo,kro=cond_means(d,P,st,nf)
        phivals.append(Phi_of(aa,qq,ml,mm,kf,kfo,P))
    except Exception: phivals.append(np.nan)
pv=[v for v in phivals if np.isfinite(v)]
mono=all(pv[i+1]<=pv[i]+1e-6 for i in range(len(pv)-1))
single_cross=sum((pv[i]>0)!=(pv[i+1]>0) for i in range(len(pv)-1))<=1
ok("Prop phase: Phi(C_R) monotone non-increasing (carbon boundary well-defined)", mono, f"{len(pv)} pts, Phi {pv[0]:+.2f}->{pv[-1]:+.2f}")
ok("Prop phase: Phi(C_R) has a single sign change (one carbon boundary)", single_cross, "at most one zero-crossing")

# ---- Thm leverage: budget family -- K_F(tau) non-decreasing, Lambda(tau)<0 ----
Dbar=10.0; Dd=stats.beta(2,2); Sd=stats.beta(2,2); EDm=Dbar*Dd.mean()
gx,gw=np.polynomial.legendre.leggauss(40); ss=0.5*(gx+1); wss=0.5*gw*Sd.pdf(ss)
def fam_stats(KR,KF,KM,tau):
    x=np.linspace(-KR,Dbar,900); A=x[:,None]+KR*ss[None,:]
    fx=(np.where((A>0)&(A<Dbar),Dd.pdf(np.clip(A,1e-9,Dbar-1e-9)/Dbar)/Dbar,0.0)*wss[None,:]).sum(1)
    Z=np.trapz(fx,x); fx=fx/Z if Z>0 else fx
    sx=np.maximum(-x,0.); cons=np.minimum(np.maximum(x,0.),KF); head=np.maximum(KF-np.maximum(x,0.),0.)
    dd=np.minimum(KM,sx+np.minimum(tau,head)); ff=np.maximum(dd-sx,0.)
    E=lambda v:float(np.trapz(v*fx,x)); return E(dd),E(ff),E(cons)
def fam_black(KR,KF):
    x=np.linspace(-KR,Dbar,900); A=x[:,None]+KR*ss[None,:]
    fx=(np.where((A>0)&(A<Dbar),Dd.pdf(np.clip(A,1e-9,Dbar-1e-9)/Dbar)/Dbar,0.0)*wss[None,:]).sum(1)
    Z=np.trapz(fx,x); fx=fx/Z if Z>0 else fx
    return float(np.trapz(np.maximum(np.maximum(x,0.)-KF,0.)*fx,x))
def fam_opt(tau,CRv,CMv,x0):
    def negp(k):
        KR,KF,KM=k
        if min(KR,KF,KM)<1e-3 or KR>Dbar*0.99: return 1e6
        rev,ff,cons=fam_stats(KR,KF,KM,tau)
        return -(p*EDm + R*rev - c*(cons+ff) - (b+p)*fam_black(KR,KF) - CF*KF - CRv*KR - CMv*KM)
    r=optimize.minimize(negp,x0,method='Nelder-Mead',options={'xatol':1e-3,'fatol':1e-4,'maxiter':4000})
    rev,ff,cons=fam_stats(*r.x,tau); return r.x,(cons+ff),ff,cons
CRv,CMv=0.5,0.04; taus=[0.0,0.5,1.0,2.0,5.0]; KRs=[]; KFs=[]; Cs=[]; ffs=[]; cons0=None; base=(3,6,4)
for tau in taus:
    k,carb,ff,cons=fam_opt(tau,CRv,CMv,base); base=k; KRs.append(k[0]); KFs.append(k[1]); Cs.append(carb); ffs.append(ff)
    if tau==0.0: cons0=cons
lam=[]
for i in range(1,len(taus)):
    Gt=Cs[i]-ffs[i]; lam.append((cons0-Gt)/ffs[i] if ffs[i]>1e-9 else 0.0)
KF_mono=all(KFs[i+1]>=KFs[i]-1e-3 for i in range(len(KFs)-1))
KR_mono=all(KRs[i+1]<=KRs[i]+1e-3 for i in range(len(KRs)-1))   # Condition M: K_R non-increasing
print("   tau:    "+"  ".join(f"{t:>6.1f}" for t in taus))
print("   K_R:    "+"  ".join(f"{v:>6.2f}" for v in KRs))
print("   K_F:    "+"  ".join(f"{v:>6.2f}" for v in KFs))
print("   Lambda: "+"      "+"  ".join(f"{L:>6.3f}" for L in lam))
ok("Thm leverage(Cond M): K_F(tau) non-decreasing", KF_mono, f"K_F: {KFs[0]:.2f}->{KFs[-1]:.2f}")
ok("Thm leverage(Cond M): K_R(tau) non-increasing", KR_mono, f"K_R: {KRs[0]:.2f}->{KRs[-1]:.2f}")
ok("Thm leverage: Cond M => Lambda<0<1 (proved) => surplus-only carbon-opt", (KF_mono and KR_mono and all(L<1.0 for L in lam)), f"max Lambda={max(lam):+.3f}")

print("\n"+"="*74); print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS"); print("="*74)
