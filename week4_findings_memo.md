# Role 3 — Week 4 Findings Memo

## Bullet 1: Functional comparative statics
Signs of dPsi/dtheta (Psi = Carbon_FCL - Carbon_noFCL, functional proxy) across 8 distributions:
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

## Bullet 2: Contract-family comparative statics
Sign of dW/dtheta where W = Carbon_myopic - Carbon_optimal:
  - d/dC_M: +0 / -7 / 01
  - d/dC_R: +0 / -0 / 08

## Bullet 3: Value of robustness
  - LR-path sign invariant: True
  - Price of robustness monotone in r: False
  - Max price of robustness: 0.125
  - Max |carbon gap|: 7.0578

## Bullet 4: Fragility map (Psi=0 level set)
  - Endpoint-condition holds in 16/17 Beta(a, 5-a) scenarios
  - Endpoint flip located at a* ≈ 0.5

## Bullet 5: Distributionally-robust characterization (Pareto)
  - Nominal tail index a0 = 2.5
  - Worst-case tail at max radius: a_wc = 2.100
  - Worst-case tail monotone (heavier) in r: True
  - Max price of robustness: 0.000
  - Max |carbon gap|: 0.3299
  - Nominal contract: (K_R, K_F, K_M) = (20.0, -0.057, 13.427)

## Sync with other roles
- Bullet 1 signs feed Role 1's classification theorem (dPsi/dtheta direction).
- Bullet 2 wedge collapses to 0 as C_M ↑ C_M_bar — pins Role 1's leverage boundary.
- Bullet 3 LR-path certificate confirms Role 2's minimax=maximin numerical claim.
- Bullet 4 fragility flip at a* ≈ 0.5 supplies Role 4's regime-boundary witness.
- Bullet 5 Pareto closed form gives Role 1 the power-law worst-case optimum.
