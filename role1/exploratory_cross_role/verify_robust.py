"""
A1 EXTENSION verification: distributionally ROBUST emission certificate.

Claim (Thm R1): within the shape class U = {F : density non-increasing on the
FCL dispatch zone, non-decreasing on the no-FCL fossil zone}, the UNIFORM is the
least-favorable distribution for carbon -- it MINIMIZES the net carbon saving at
common cutoff probabilities. Hence the closed-form uniform condition (C_R<=C_R^dag)
certifies emission reduction for the entire (infinite-dimensional) class U.

Engine (Cor 2): on the FCL zone the conditional mean mu*_low <= midpoint, with
equality iff uniform; on the no-FCL zone mu^o_mid >= midpoint, equality iff uniform.
A larger mu*_low and a smaller mu^o_mid both SHRINK the carbon saving, so uniform
(midpoints) is the worst case. We verify the two extremal facts directly over a
large random sample of monotone-density distributions.
"""
import numpy as np
rng=np.random.default_rng(1)

def cond_mean_noninc(a,b,shape):
    """E[X | X in (a,b)] for a NON-INCREASING density on (a,b), parametrized by
    f(t) prop exp(-shape*(t-a)) (shape>=0 => non-increasing; shape=0 => uniform)."""
    t=np.linspace(a,b,4000); w=np.exp(-shape*(t-a)); w/=np.trapezoid(w,t)
    return np.trapezoid(w*t,t)

def cond_mean_nondec(a,b,shape):
    """E[X|X in (a,b)] for NON-DECREASING density f(t) prop exp(shape*(t-a))."""
    t=np.linspace(a,b,4000); w=np.exp(shape*(t-a)); w/=np.trapezoid(w,t)
    return np.trapezoid(w*t,t)

print("Thm R1 engine: uniform is extremal for the conditional means.")
a,b=-3.0,5.0; mid=(a+b)/2
bad=0; worst_low=-1
for _ in range(3000):
    sh=rng.uniform(0,3)
    m=cond_mean_noninc(a,b,sh)         # non-increasing density
    if m>mid+1e-9: bad+=1              # must be <= midpoint
    worst_low=max(worst_low,m)
print(f"  FCL zone: non-increasing-density mean <= midpoint in {3000-bad}/3000;"
      f"  sup mean={worst_low:.4f} -> midpoint={mid:.4f} (uniform attains it)")

a2,b2=0.0,6.0; mid2=(a2+b2)/2
bad2=0; worst_mid=1e9
for _ in range(3000):
    sh=rng.uniform(0,3)
    m=cond_mean_nondec(a2,b2,sh)       # non-decreasing density
    if m<mid2-1e-9: bad2+=1            # must be >= midpoint
    worst_mid=min(worst_mid,m)
print(f"  no-FCL zone: non-decreasing-density mean >= midpoint in {3000-bad2}/3000;"
      f"  inf mean={worst_mid:.4f} -> midpoint={mid2:.4f} (uniform attains it)")

# Direct: net carbon saving at FIXED capacities/cutoffs as a function of shape.
# saving ∝ (CM/(R-c))(KF-KM-mu_low) - [KF - KFo(1-phi) - (phi-q)mu_mid] ; larger mu_low
# and smaller mu_mid both reduce saving -> uniform (shape 0) is the minimizer.
R,c,CM=1.4,0.5,0.5; KF,KM,KR=6.0,5.0,2.0; KFo,phi,q=4.0,0.8667,0.2
def saving(shape):
    mu_low=cond_mean_noninc(-KR,KF-KM,shape)
    mu_mid=cond_mean_nondec(0,KFo,shape)
    util=(CM/(R-c))*((KF-KM)-mu_low)
    netcap=KF-KFo*(1-phi)-(phi-q)*mu_mid
    return util-netcap
shapes=np.linspace(0,3,25); svals=[saving(s) for s in shapes]
print(f"\n  net carbon saving vs shape (0=uniform): min at shape={shapes[int(np.argmin(svals))]:.2f}"
      f"  (uniform={svals[0]:.4f}, max-shape={svals[-1]:.4f})")
print(f"  uniform is the MINIMIZER (least-favorable)? {np.argmin(svals)==0}")
