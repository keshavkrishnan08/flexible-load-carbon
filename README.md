# Role 3 — Week 4 Bundle (5 bullets, functional-based)

Week 4 centres on Role 1's **classification functional** Ψ(F; θ).
Role 3 signs its comparative statics, quantifies robustness, maps
fragility, signs the contract-family, and delivers the full
distributionally-robust characterization on the Pareto family.

## Bullets

1. **Functional comparative statics** — `comparative_statics_characterization.py`
   → `results/characterization_comparative_statics.csv`,
     `results/characterization_boundary_movement.csv`
2. **Contract-family comparative statics** — `contract_comparative_statics.py`
   → `results/contract_wedge_comparative_statics.csv`,
     `results/contract_wedge_by_shape.csv`
3. **Value of robustness (LR/MPS-path certificate)** — `robustness_value.py`
   → `results/robustness_gap_vs_radius.csv`,
     `results/robustness_summary.csv`
4. **Fragility map (Ψ=0 level set + witnesses)** — `fragility_map.py`
   → `results/fragility_adoption_boundary.csv`,
     `results/fragility_endpoint_boundary.csv`,
     `results/fragility_summary.csv`
5. **Distributionally-robust characterization (Pareto)** — `dro_characterization.py`
   → `results/dro_worst_case_and_robust_contract.csv`,
     `results/dro_pareto_psi_curve.csv`,
     `results/dro_summary.csv`

## Run

```bash
pip install -r ../requirements.txt
python run_week4.py
```

Writes `results/week4_findings_memo.md` with headline numbers.

## Headline results

- **Bullet 1**: 8/8 distributions give ∂Ψ/∂R>0, ∂Ψ/∂c<0, ∂Ψ/∂C_F<0, ∂Ψ/∂C_R<0, ∂Ψ/∂C_M<0. 7/8 have ∂Ψ/∂β>0.
- **Bullet 2**: 7/8 have ∂W/∂C_M≤0, 8/8 have ∂W/∂C_R sign-invariant.
- **Bullet 3**: LR-path sign invariance = True; max price of robustness = 0.125.
- **Bullet 4**: adoption knife-edge witness collapses 0.16→0 at C̄_M; endpoint flip at a*≈0.5.
- **Bullet 5**: worst-case tail index monotone-decreasing in ambiguity radius (heavier tail wins); Pareto closed-form Ψ(a) = (R-c)(K_F-K_M)^{-a} - C_M matched numerically.

## Cross-role sync

- Bullets 1 & 5 feed Role 1's classification theorem and DRO capstone.
- Bullet 3 confirms Role 2's minimax = maximin.
- Bullet 4 supplies Role 4's regime-boundary sharpness witness a*≈0.5.