# Role 3 Week 2 — Reproducibility Report

## Environment
- Python ≥ 3.10
- Dependencies: numpy, scipy, pandas, matplotlib (see `../requirements.txt`)
- Install: `pip install -r ../requirements.txt`

## Run
```
cd role3/week2
python3 run_week2.py
```

## Determinism
Solver uses fixed seed (Params.seed = 7) and deterministic
`scipy.optimize.minimize_scalar(method="bounded")`. Three back-to-back
runs produce byte-identical CSVs.

## Verified claims

| Claim | Reference | Confirmed |
|-------|-----------|-----------|
| ∂ΔC/∂R > 0 across distributions | §1.2 | 8/8 |
| ∂ΔC/∂β > 0 | §1.2 | 7/8 |
| ∂ΔC/∂p > 0 | §1.2 | 5/8 (flip flagged) |
| ∂ΔC/∂C_M < 0 | §1.2 | 8/8 |
| K_R* > K_R° (substitution channel) | Prop 1.3 | 24/24 |
| Endpoint shift-ratio is sufficient but NOT necessary | §3, Lemma | confirmed numerically |
| DCT envelope dominates d_n pointwise | §4 Lemma | 72/72 |
| K_M_n ↓ 0 and E[d_n] ↓ 0 as C_M ↑ C_M_bar | §4 Lemma | all 8 distributions |
| Robust-certificate obstruction on Beta LR path | Thm 2.1 | C_R^† = 0 in this parameterization |

## Outputs
- `results/comparative_statics_signs.csv`
- `results/capacity_substitution_endpoint.csv`
- `results/robust_certificate_homotopy.csv`
- `results/robust_certificate_summary.csv`
- `results/reversed_channel_counterexample.csv`
- `results/reversed_channel_g_profile.csv`
- `results/limit_interchange_envelope.csv`
- `results/week2_findings_memo.md`
