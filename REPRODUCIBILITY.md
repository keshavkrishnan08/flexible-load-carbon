# Role 3 Week 3 — Reproducibility Report

## Environment
- Python ≥ 3.10
- Dependencies: numpy, scipy, pandas, matplotlib (see `../requirements.txt`)

## Run
```
cd role3/week3
python3 run_week3.py
```

## Determinism
Fixed seed (Params.seed = 7), 40k Monte-Carlo draws, deterministic
`minimize_scalar(method="bounded")`. Two back-to-back runs produce
byte-identical CSVs (MD5 verified).

## MD5 hashes (from a clean run)
```
9f33dc4a5a02906074e98cd0c773f39c  characterization_boundary_movement.csv
db07b3ba2ba6c61e554203b44573ca10  characterization_comparative_statics.csv
ad1d39297419678334aa463aacdc324f  contract_wedge_by_shape.csv
ac378448e3fcb96d0e7d7ab1d5e5f650  contract_wedge_comparative_statics.csv
7894448505e00a82e27ab80953ea2959  fragility_adoption_boundary.csv
a5ccba3573e2a3fd72524d7538e16441  fragility_endpoint_boundary.csv
24b3917e6d35873cfdb5c8204e06b2f0  fragility_summary.csv
330cd4316d8b981c5eb8540025806646  robustness_gap_vs_radius.csv
4666be517d0b219b6a58be2eb623ae4a  robustness_summary.csv
```

## Verified claims

| Claim | Reference | Confirmed |
|-------|-----------|-----------|
| ∂J/∂R > 0 | Prop 1 | 8/8 |
| ∂J/∂c < 0 | Prop 1 | 8/8 |
| ∂J/∂β > 0 | Prop 1 | 7/8 |
| ∂J/∂p > 0 | Prop 1 | 5/8 (ambiguous) |
| ∂J/∂C_F < 0 | Prop 1 | 8/8 |
| ∂J/∂C_R < 0 | Prop 1 | 8/8 |
| ∂J/∂C_M < 0 | Prop 1 | 8/8 |
| ∂W/∂C_M ≤ 0 | Lemma 1 | 7/8 |
| ∂W/∂C_R invariant | Lemma 1 | 8/8 |
| LR-path sign invariance | Thm 1 | True |
| Adoption knife-edge witness | Prop 3 | K_M* 0.16 → 0 |
| Endpoint g(a) ≥ g(K_F*) (a = K_F*−K_M*) | Prop 4 | 17/17 hold, no flip |