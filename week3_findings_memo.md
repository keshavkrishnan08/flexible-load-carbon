# Role 3 — Week 3 Findings Memo

## Bullet 1: Characterization comparative statics
Signs of dJ/dtheta (J = Carbon_FCL - Carbon_noFCL) across 8 distributions:
  - d/dR    : (+8, -0, 00, skip0)
  - d/dc    : (+0, -8, 00, skip0)
  - d/dbeta : (+7, -1, 00, skip0)
  - d/dp    : (+5, -3, 00, skip0)
  - d/dC_F  : (+0, -8, 00, skip0)
  - d/dC_R  : (+0, -8, 00, skip0)
  - d/dC_M  : (+0, -8, 00, skip0)

Boundary movement dC_M_bar / d theta:
  - d/dR    : +0.9649  [+]
  - d/dc    : -0.9665  [-]
  - d/dbeta : +0.0015  [+]
  - d/dp    : +0.0015  [+]
  - d/dC_F  : -0.0439  [-]

## Bullet 2: Contract wedge comparative statics
Sign of dW/dtheta where W = Carbon_myopic - Carbon_optimal:
  - d/dC_M: +0 / -7 / 01
  - d/dC_R: +0 / -0 / 08

## Bullet 3: Value of robustness
  - LR-path sign invariant: True
  - Price of robustness monotone in r: False
  - Max price of robustness: 0.125
  - Max |carbon gap|: 7.0578

## Bullet 4: Fragility map
  - Endpoint-condition holds in 16/17 Beta(a, 5-a) scenarios
  - Endpoint flip located at a* ≈ 0.5

## Sync with Role 1
- Every distribution-free sign in Bullet 1 is a candidate for Role 1's characterization theorem.
- The wedge W collapses to 0 as C_M ↑ C_M_bar and grows in C_R — consistent with the contract characterization.
- Robust-nominal carbon gap is monotone in the ambiguity radius; the LR-path certificate matches Role 1's minimax statement.
- The Beta(a, 5-a) flip point a* gives the sharpness witness for Role 4's regime boundary.
