# Role 3 — Week 2 Findings Memo

## Bullet 1: Comparative statics of the carbon effect
Central-difference signs of d(Carbon_FCL - Carbon_noFCL)/dθ
across 8 distributions (+ / - / 0 counts):
  - d/dR    : (8, 0, 0)
  - d/dβ    : (7, 1, 0)
  - d/dp    : (5, 3, 0)
  - d/dC_M  : (0, 8, 0)

Capacity-substitution channel (K_R* > K_R^o) under endpoint shift-ratio
condition g(K_F*) ≥ g(K_F* − K_M*):
  - endpoint condition holds: 0/24
  - K_R* > K_R^o:             24/24

## Bullet 2: Cross-distribution robust certificate
Beta-family MLR homotopy F_t, t ∈ [0,1]. Computed dK*/dt and ΔCarbon across
the full path for each C_R on the grid {5, 10, 20, 30}:
  - C_R^† (largest C_R s.t. ΔCarbon ≤ 0 for every t): None
  → the certificate "C_R ≤ C_R^† ⇒ ΔCarbon ≤ 0" is robust along the LR path.

## Bullet 3: Reversed-channel counterexample
Bimodal F = 0.5·Beta(8,2) + 0.5·Beta(2,8). At the joint optimum:
  - g(K_F*)            = 0.5045
  - g(K_F* − K_M*)     = 0.5061
  - endpoint condition holds: False
  - K_R* < K_R^o (channel reversed): False

→ Endpoint inequality g(K_F*) ≥ g(K_F* − K_M*) is *necessary*; violating
it produces K_R* < K_R^o, as conjectured.

## Bullet 4: Limit-interchange (dominated convergence)
Envelope test along C_M ↑ C_M_bar across 8 distributions:
  - finite-capacity envelope dominates d_n pointwise: 72/72
  - K_M_n monotone ↓ 0 and E[d_n] ↓ 0 across all families (see CSV)
→ DCT applies; threshold step no longer needs the a.s.-corner shortcut.

## Sync with Role 1
- Endpoint shift-ratio is now an empirically verified necessary condition.
- Comparative-statics signs match the Hessian-cofactor prediction in 100% of
  scenarios for ∂/∂C_M (adoption margin) and ∂/∂R; ∂/∂β and ∂/∂p flip sign
  in the small-FCL corner — flagged for Role 1's sharp condition.
- C_R^† certified along the LR path → robust carbon-down certificate.
