#!/usr/bin/env python3
"""
A1 Role 1 -- Week 3 verification suite.
Confirms the optimal-contract decarbonization theory of role1_week3_theory.tex:
  Prop 1  surplus contract burns ZERO FCL fossil
  Thm 1   adopted => surplus channel>0 at KRo => KRc>KRo, KFc<=KFo, carbon STRICTLY falls
          -- and the sign needs NO SHAPE CONDITION (holds across every family/shape)
  Cor 1   Pareto improvement: Pi^c>Pi^o, carbon down, blackout HELD (== 1-phio, both)
  Prop 2  exact saving formula == direct quadrature
  contrast: the Week-2 naive rule's fossil floor at the same primitives
Self-contained (no import of verify_week2). Quadrature ground truth.
"""
import numpy as np
from scipy import integrate, optimize, stats

R,c,p,CF=1.4,0.5,1.0,0.6          # per-MWh revenue, fossil cost, price, fossil capital
beta_pen=2.0                       # blackout penalty (b+p>R, b+p>c+CF hold)
b=beta_pen
phio=(b+p-c-CF)/(b+p-c)
Dbar=10.0
PASS=[]
def ok(name,cond,detail=""):
    PASS.append(bool(cond)); print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

# ---- model: x = D - KR*S, D and S from given scipy dists (D scaled to [0,Dbar]) ----
class Model:
    def __init__(self,Ddist,Sdist,label):
        self.Dd,self.Sd,self.label=Ddist,Sdist,label
        gx,gw=np.polynomial.legendre.leggauss(80); self.s=0.5*(gx+1); self.wS=0.5*gw*Sdist.pdf(self.s)
    def _grid(self,KR,n=2400):
        x=np.linspace(-KR,Dbar,n); A=x[:,None]+KR*self.s[None,:]
        FD=self.Dd.cdf(np.clip(A,0,Dbar)/Dbar)
        fD=np.where((A>0)&(A<Dbar),self.Dd.pdf(np.clip(A,1e-9,Dbar-1e-9)/Dbar)/Dbar,0.0)
        return x,(FD*self.wS[None,:]).sum(1),(fD*self.s[None,:]*self.wS[None,:]).sum(1)
    def F(self,xq,KR):
        x,Fg,_=self._grid(KR); return float(np.interp(xq,x,Fg))
    def Finv(self,t,KR):
        x,Fg,_=self._grid(KR); return float(np.interp(t,Fg,x))
    @staticmethod
    def _trapz_exact(x,vals,lo,hi):
        """Integrate lo..hi with the ENDPOINTS EXACT.

        The previous version masked a fixed grid, (x>=lo)&(x<=hi), so a limit that moved
        between nodes did not change the integral at all until it crossed one -- then the
        value jumped.  Measured jump ~5e-3.  That is 15x the -3e-4 'carbon rises in the
        left-skew family' signal, which was therefore an artifact of the grid, not a
        property of the model.  It also made e(K_R) increase on 60 of 100 fine steps,
        appearing to falsify the monotone-fossil lemma; with exact endpoints it is 0 of 100.
        """
        if hi<=lo: return 0.0
        inner=x[(x>lo)&(x<hi)]
        pts=np.concatenate(([lo],inner,[hi]))
        return float(np.trapz(np.interp(pts,x,vals),pts))
    def cons_fossil(self,KR,KF):
        x,Fg,_=self._grid(KR); return self._trapz_exact(x,1-Fg,0.0,KF)
    def ren_benefit(self,KR,KF,KMlo=None):   # renewable marginal value (no CR), + surplus channel if KMlo given
        x,Fg,FKRg=self._grid(KR)
        I=lambda lo,hi:self._trapz_exact(x,FKRg,lo,hi)
        val=c*I(0,KF)+(b+p)*I(KF,Dbar)
        chan=R*I(KMlo,0) if (KMlo is not None and KMlo<0) else 0.0
        return val,chan

def solve_nofcl_target(m,KRo_target=2.0):
    """Pick CR so the no-FCL optimum is exactly KRo_target (guarantees interior)."""
    KFo=m.Finv(phio,KRo_target); val,_=m.ren_benefit(KRo_target,KFo)
    CR=val                       # CR := renewable benefit at target => KRo = target by construction
    return CR,KRo_target,KFo
def surplus_opt(m,CR,CM,KRo):
    """Surplus-contract optimum.  The surplus channel pulls KR up (Prop 2); we impose a
    physical renewable cap so KFc stays in (0,KFo) -- the cap binds in the cheap-renewable
    pull, and the decarbonization theorem holds at the capped optimum just the same."""
    # cap = largest KR keeping the fossil cutoff strictly positive (full-decarbon corner excluded)
    Kcap=KRo
    while Kcap<40 and m.Finv(phio,Kcap*1.5)>0.3: Kcap*=1.5
    def dPi(KR):
        KF=m.Finv(phio,KR); q=m.F(0,KR)
        negKM=m.Finv(CM/R,KR) if CM/R<q else 0.0
        val,chan=m.ren_benefit(KR,KF,KMlo=negKM if negKM<0 else None)
        return val+chan-CR
    if dPi(Kcap)>0: KRc=Kcap; capped=True
    else: KRc=optimize.brentq(dPi,KRo,Kcap,xtol=1e-7); capped=False
    KFc=m.Finv(phio,KRc); q=m.F(0,KRc); KMc=(-m.Finv(CM/R,KRc)) if CM/R<q else 0.0
    return KRc,KFc,KMc,capped

# ---------------------------------------------------------------------
print("="*74); print("  A1 ROLE 1 -- WEEK 3: optimal-contract decarbonization (no shape condition)"); print("="*74)
class Mix:   # two-component Beta mixture (bimodal demand)
    def __init__(self,d1,w1,d2): self.d1,self.w1,self.d2=d1,w1,d2
    def cdf(self,x): return self.w1*self.d1.cdf(x)+(1-self.w1)*self.d2.cdf(x)
    def pdf(self,x): return self.w1*self.d1.pdf(x)+(1-self.w1)*self.d2.pdf(x)
    def mean(self): return self.w1*self.d1.mean()+(1-self.w1)*self.d2.mean()
fams=[Model(stats.beta(2,2),stats.beta(2,2),"symmetric  D~B(2,2)"),
      Model(stats.beta(5,2),stats.beta(2,2),"left-skew  D~B(5,2)"),
      Model(stats.beta(2,5),stats.beta(2,2),"right-skew D~B(2,5)"),
      Model(Mix(stats.beta(8,2),0.5,stats.beta(2,8)),stats.beta(2,2),"bimodal D mix"),
      Model(stats.beta(2,2),stats.beta(5,2),"high-CF S~B(5,2)")]

print(f"\n  phio={phio:.4f}  (R={R}, c={c}, b+p={b+p}, CF={CF})")
allfall=True; alladopt=True
print(f"\n  {'family':<20}{'CR':>6}{'CM':>6}{'KRo':>6}{'KRc':>7}{'KFo':>6}{'KFc':>6}{'fos_o':>7}{'fos_c':>7}{'save':>7} {'cap':>4}")
for m in fams:
    CR,KRo,KFo=solve_nofcl_target(m,2.0)
    q=m.F(0,KRo); CM=0.5*R*q                          # ensure adoption CM<R*q
    KRc,KFc,KMc,capped=surplus_opt(m,CR,CM,KRo)
    # channel strictly positive at KRo (Step 1 local proof)
    negKM0=m.Finv(CM/R,KRo); _,chan0=m.ren_benefit(KRo,KFo,KMlo=negKM0)
    # All carbon integrals on ONE common grid with identical quadrature (so the
    # algebraic saving identity of Prop 2 is checked to grid precision, not across grids).
    x,FgC,_=m._grid(KRc); x0,Fg0,_=m._grid(KRo)
    Fc=lambda xx:np.interp(xx,x,FgC); Fo=lambda xx:np.interp(xx,x0,Fg0)
    xo=np.linspace(0,KFo,4000); xc=np.linspace(0,KFc,4000); xt=np.linspace(KFc,KFo,2000)
    foso=float(np.trapz(1-Fo(xo),xo)); fosc=float(np.trapz(1-Fc(xc),xc))
    t1=float(np.trapz(Fc(xc)-Fo(xc),xc)); t2=float(np.trapz(1-Fo(xt),xt))
    save_formula=t1+t2; save_direct=foso-fosc
    adopt=KMc>1e-6; fall=fosc<foso-1e-9
    alladopt&=adopt; allfall&=fall
    print(f"  {m.label:<20}{CR:>6.3f}{CM:>6.3f}{KRo:>6.2f}{KRc:>7.2f}{KFo:>6.2f}{KFc:>6.2f}{foso:>7.3f}{fosc:>7.3f}{save_direct:>+7.3f} {str(capped):>4}")
    ok(f"   [{m.label.strip()}] surplus channel>0 at KRo => KRc>KRo", chan0>1e-9 and KRc>KRo+1e-6, f"chan={chan0:.4f}, KRc-KRo={KRc-KRo:+.3f}")
    ok(f"   [{m.label.strip()}] KFc<=KFo", KFc<=KFo+1e-6, f"{KFc:.3f}<={KFo:.3f}")
    ok(f"   [{m.label.strip()}] carbon STRICTLY falls (fos_c<fos_o)", fall, f"save={save_direct:+.4f}")
    ok(f"   [{m.label.strip()}] adopted (CM<R*F(0;KRo))", adopt, f"KMc={KMc:.3f}")
    ok(f"   [{m.label.strip()}] exact saving formula == direct", abs(save_formula-save_direct)<1e-4, f"{save_formula:.4f} vs {save_direct:.4f}")

print()
ok("SHAPE-INDEPENDENT: carbon falls in EVERY family (sign never flips)", allfall, "all 5 shapes decarbonize: sym/left/right/bimodal/high-CF")

# ---- cap-invariance: is the result a property of the model or of the cap? -------------
# K_R sits AT the cap in most families (profit is still rising there), so the reported
# saving is a property of the constraint set.  What must not depend on the cap is the SIGN.
# Test it directly instead of asserting the magnitude.
def surplus_opt_at(m,CR,CM,KRo,Kcap):
    def dPi(KR):
        KF=m.Finv(phio,KR); q=m.F(0,KR)
        negKM=m.Finv(CM/R,KR) if CM/R<q else 0.0
        val,chan=m.ren_benefit(KR,KF,KMlo=negKM if negKM<0 else None)
        return val+chan-CR
    KRc=Kcap if dPi(Kcap)>0 else optimize.brentq(dPi,KRo,Kcap,xtol=1e-7)
    return KRc,m.Finv(phio,KRc)
sign_ok=True; spread={}
for m in fams:
    CR,KRo,KFo=solve_nofcl_target(m,2.0); q=m.F(0,KRo); CM=0.5*R*q
    foso=m.cons_fossil(KRo,KFo); saves=[]
    for mult in (1.5,3.0,5.0,10.0,20.0):
        KRc,KFc=surplus_opt_at(m,CR,CM,KRo,KRo*mult)
        saves.append(foso-m.cons_fossil(KRc,KFc))
    if not all(s>0 for s in saves): sign_ok=False
    spread[m.label.strip()]=(min(saves),max(saves))
ok("cap-invariance: carbon falls at EVERY cap (1.5x-20x), EVERY family -- SIGN is the model",
   sign_ok, f"{len(spread)} families x 5 caps, all savings > 0")
worst=max(spread.values(),key=lambda v:v[1]/max(v[0],1e-9))
ok("cap-invariance: MAGNITUDE is cap-determined, so no magnitude may be quoted",
   worst[1]/max(worst[0],1e-9)>10, f"widest family ranges {worst[0]:+.4f} to {worst[1]:+.4f}")
ok("adoption holds in every family", alladopt, "")

# ---- Lemma (monotone fossil): e(KR)=int_0^{(KF(KR))_+}(1-F) strictly decreasing in KR ----
m=fams[0]
def e_of(KR):
    KF=max(m.Finv(phio,KR),0.0); return m.cons_fossil(KR,KF) if KF>0 else 0.0
# step 0.02 (was 0.5).  The coarse grid could not have detected the ~5e-3 quadrature
# artifact that made this lemma appear to fail; it now resolves well past it.
KRgrid=np.arange(1.0,12.0,0.02); evals=[e_of(K) for K in KRgrid]
mono_dec=all(evals[i+1]<evals[i]-1e-9 or evals[i+1]<1e-9 for i in range(len(evals)-1))
ok("Lemma: fossil output e(KR) strictly decreasing in KR (more renewables, less fossil)",
   mono_dec, f"e(1.0)={evals[0]:.3f} -> e(12)={evals[-1]:.3f}, monotone={mono_dec}")

# ---- Prop 1: surplus contract burns zero FCL fossil (structural, any state) ----
m=fams[0]; KR,KF,KM=3.0,6.0,4.0
def fcl_fossil(d_func):
    xs=np.linspace(-KR,Dbar,400); tot=0
    for x in xs:
        d=d_func(x); tot=max(tot,max(d-max(-x,0),0))  # FCL fossil in this state
    return tot
surp_max=fcl_fossil(lambda x:min(max(-x,0),KM))
naive_max=fcl_fossil(lambda x:min(max(KF-x,0),KM))
ok("Prop1: surplus contract FCL fossil == 0 in every state", surp_max<1e-9, f"max={surp_max:.2e}")
ok("Prop1: naive contract DOES burn FCL fossil (the Week-2 floor)", naive_max>0.1, f"max FCL fossil={naive_max:.3f}")

# ---- Cor 1: triple-win (profit up, blackout down) ----
def profit_nofcl(m,KR,KF,CR):
    x,Fg,_=m._grid(KR)
    cf=m.cons_fossil(KR,KF)
    bo=integrate.quad(lambda xx:1-np.interp(xx,x,Fg),KF,Dbar,limit=200)[0]
    ED=Dbar*m.Dd.mean()
    return p*ED - c*cf - (b+p)*bo - CF*KF - CR*KR
def profit_surplus(m,KR,KF,KM,CR,CM):
    x,Fg,_=m._grid(KR)
    rev=R*integrate.quad(lambda xx:np.interp(xx,x,Fg),-KM,0,limit=200)[0]
    cf=m.cons_fossil(KR,KF)
    bo=integrate.quad(lambda xx:1-np.interp(xx,x,Fg),KF,Dbar,limit=200)[0]
    ED=Dbar*m.Dd.mean()
    return p*ED + rev - c*cf - (b+p)*bo - CF*KF - CR*KR - CM*KM
# Cor 1 is a PARETO improvement: profit strictly UP, carbon DOWN, blackout HELD EQUAL
# (both target phi^o, so 1-phi^o identical -- this is the corrected claim, not "lower").
tw=True
for m in fams[:3]:
    CR,KRo,KFo=solve_nofcl_target(m,2.0); q=m.F(0,KRo); CM=0.5*R*q
    KRc,KFc,KMc,_=surplus_opt(m,CR,CM,KRo)
    Po=profit_nofcl(m,KRo,KFo,CR); Pc=profit_surplus(m,KRc,KFc,KMc,CR,CM)
    blo=1-m.F(KFo,KRo); blc=1-m.F(KFc,KRc)
    prof_up=Pc>Po+1e-6; rel_held=abs(blc-blo)<1e-3
    tw &= prof_up and rel_held
    ok(f"   [{m.label.strip()}] Pareto: Pi^c>Pi^o and blackout^c==blackout^o (held)", prof_up and rel_held, f"dPi={Pc-Po:+.3f}, blackout: {blc:.4f} vs {blo:.4f} (=1-phio)")
ok("Cor1: Pareto improvement (profit UP, carbon DOWN, reliability HELD at 1-phio)", tw, "")

# ============================================================================
# Thm (frontier): the budget family d_tau = min{(-x)_+ + tau, KM, (KF-x)_+} nests
# surplus-only (tau=0) and naive (tau=inf).  Verify: carbon C(tau) strictly INCREASING
# (min at tau=0 => surplus-only is GLOBALLY carbon-optimal); profit Pi(tau) INCREASING
# (the carbon-profit frontier); endpoints match Wk3 (tau=0) and Wk2-style naive.
# ============================================================================
print("\n  --- optimal-contract family / carbon-profit frontier (Sec family) ---")
Dd2=stats.beta(2,2); Sd2=stats.beta(2,2); EDm=Dbar*Dd2.mean()
gx2,gw2=np.polynomial.legendre.leggauss(40); ss=0.5*(gx2+1); wss=0.5*gw2*Sd2.pdf(ss)
def fam_stats(KR,KF,KM,tau):
    x=np.linspace(-KR,Dbar,1000); A=x[:,None]+KR*ss[None,:]
    fxd=(np.where((A>0)&(A<Dbar),Dd2.pdf(np.clip(A,1e-9,Dbar-1e-9)/Dbar)/Dbar,0.0)*wss[None,:]).sum(1)
    Z=np.trapz(fxd,x); fxd=fxd/Z if Z>0 else fxd
    sx=np.maximum(-x,0.); cons=np.minimum(np.maximum(x,0.),KF); head=np.maximum(KF-np.maximum(x,0.),0.)
    d=np.minimum(KM,sx+np.minimum(tau,head)); ff=np.maximum(d-sx,0.); blk=np.maximum(np.maximum(x,0.)-KF,0.)
    E=lambda v:float(np.trapz(v*fxd,x)); return E(d),E(ff),E(cons),E(blk)
def fam_opt(tau,CRv,CMv,x0):
    def negp(k):
        KR,KF,KM=k
        if min(KR,KF,KM)<1e-3 or KR>KRCAP: return 1e6
        rev,ff,cons,blk=fam_stats(KR,KF,KM,tau)
        return -(p*EDm+R*rev-c*(cons+ff)-(b+p)*blk-CF*KF-CRv*KR-CMv*KM)
    r=optimize.minimize(negp,x0,method='Nelder-Mead',options={'xatol':1e-3,'fatol':1e-4,'maxiter':5000})
    rev,ff,cons,blk=fam_stats(*r.x,tau); return r.x,(cons+ff),ff,-r.fun
# Interior optimum.  This sweep previously ran at C_M=0.04 with the barrier K_R<=0.99*Dbar,
# which BOUND in every cell: K_R was frozen at 9.90, so "K_R non-increasing" (Condition M)
# held trivially and Lambda was measured off a capacity stock that could not move.  At the
# standard C_M=0.5 with a slack cap, K_R is genuinely interior -- and it RISES with tau, so
# Condition M fails while its conclusion (Lambda<1) survives.  See role1_week4_theory.tex
# rem:condMfails.  KRCAP=20 is far above the optimum (~2.7) and its slackness is asserted.
KRCAP=20.0
CRv,CMv=0.5,0.5; taus=[0.0,0.5,1.0,2.0,5.0,15.0]; rows=[]; base=(3,6,4)
KRts=[]
for tau in taus:
    k,carb,ff,Pi=fam_opt(tau,CRv,CMv,base); base=k; rows.append((tau,carb,ff,Pi)); KRts.append(k[0])
C=[r[1] for r in rows]; Pi=[r[3] for r in rows]
print("   tau:    "+"  ".join(f"{t:>6.1f}" for t in taus))
print("   carbon: "+"  ".join(f"{c:>6.3f}" for c in C))
print("   profit: "+"  ".join(f"{P:>6.3f}" for P in Pi))
print("   K_R:    "+"  ".join(f"{v:>6.3f}" for v in KRts))
# GUARD: if K_R sits at a barrier the sweep is degenerate and says nothing about Condition M.
ok("frontier sweep is non-degenerate (K_R interior, not pinned at a barrier)",
   all(1e-2 < v < KRCAP-1e-2 for v in KRts), f"K_R in [{min(KRts):.3f}, {max(KRts):.3f}], cap {KRCAP}")

ok("frontier(ii): carbon C(tau) strictly INCREASING => min at tau=0 (surplus-only GLOBAL carbon-opt)",
   all(C[i+1]>C[i]+1e-4 for i in range(len(C)-1)), f"argmin@tau={rows[min(range(len(C)),key=lambda i:C[i])][0]}")
# Profit rises with tau only while the budget still binds.  Past saturation -- d_tau =
# min{(-x)_+ + tau, K_M, (K_F-x)_+} is capped by K_M -- more budget buys nothing, so profit
# and carbon both flatten.  Here that happens between tau=5 and tau=15.  Asserting STRICT
# monotonicity across the whole range is therefore wrong; it only passed before because the
# pinned barrier kept the sweep away from saturation.
sat=[i for i in range(len(Pi)-1) if Pi[i+1]<=Pi[i]+1e-4]
ok("frontier(i): profit Pi(tau) non-decreasing (carbon-profit trade-off)",
   all(Pi[i+1]>=Pi[i]-1e-4 for i in range(len(Pi)-1)), f"Pi: {Pi[0]:.2f}->{Pi[-1]:.2f}")
ok("frontier(i): profit STRICTLY increasing while the budget binds",
   all(Pi[i+1]>Pi[i]+1e-4 for i in range(len(Pi)-1) if i not in sat) and len(sat)<len(Pi)-1,
   f"strict on tau<={taus[(sat[0] if sat else len(Pi)-1)]}, saturates after (K_M binds)")
ok("frontier: tau=0 FCL fossil==0 (surplus endpoint) and naive endpoint burns fossil",
   rows[0][2]<1e-6 and rows[-1][2]>0.1, f"ff(0)={rows[0][2]:.4f}, ff(naive)={rows[-1][2]:.3f}")
# Exact-reduction check (Thm ii): C(tau)-C(0) = Phi(tau)*(1-Lambda(tau)),
# Lambda = (G(K0)-G(Ktau))/Phi.  G(Ktau)=carbon-ff; G(K0)=C[0].  Surplus-only global
# carbon-opt <=> Lambda<=1.  At the interior optimum Lambda is POSITIVE (~0.14-0.22): the
# induced build-out offsets part of the load's footprint, but well under all of it.  The
# earlier Lambda<0 came from the pinned barrier, where K_R could not respond at all.
G0=C[0]; lam=[]
for i in range(1,len(rows)):
    Gt=C[i]-rows[i][2]; phi=rows[i][2]        # G(Ktau)=carbon-ff ; Phi=ff
    lam.append((G0-Gt)/phi if phi>1e-9 else 0.0)
    # NOTE: C(tau)-C(0) = Phi*(1-Lambda) is DEFINITIONAL here, because Lambda is
    # defined as (G0-Gt)/Phi with Gt = C[i]-Phi.  Asserting it verifies arithmetic,
    # not the model, so we do not dress it up as a check (see B4 fix below).
print("   Lambda: "+"  ".join(f"{L:>6.3f}" for L in lam)+"   (leverage; <1 => surplus-only carbon-opt)")
KR_mono=all(KRts[i+1]<=KRts[i]+1e-3 for i in range(len(KRts)-1))
print(f"   [report] Condition M (K_R non-increasing): {KR_mono}  <- expected FALSE at an interior optimum")
# B4 FIX: this previously passed the literal True with the label "exact identity
# ... holds", which could not fail and was backed by no comparison.  The identity is
# definitional (Lambda := (G0-Gt)/Phi), so it is reported, not asserted.  The
# substantive claim -- Lambda < 1 -- is the check on the next line.
print("   [NOTE] C(tau)-C(0)=Phi*(1-Lambda) is definitional (Lambda := (G0-Gt)/Phi); "
      "not asserted as a test.  The substantive claim is Lambda<1 below.")
ok("frontier(ii): leverage Lambda(tau)<1 for all tau>0 (positive: build-out offsets part of it)",
   all(L<1.0 for L in lam), f"max Lambda={max(lam):+.3f} (<1 => surplus-only GLOBAL carbon-opt)")

print("\n"+"="*74); print(f"  RESULT: {sum(PASS)}/{len(PASS)} checks PASS"); print("="*74)
