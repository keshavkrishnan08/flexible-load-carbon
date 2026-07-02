# Role 3 — Week 3 GitHub Checklist

Use this to confirm every Week 3 deliverable is committed to `Role-3` branch of `dhruvkamath-dev/team-a1`.

## 1. Files to upload (drop under `role3/week3/` in the repo)

### Docs
- [ ] `role3/week3/README.md` — overview + headline numbers
- [ ] `role3/week3/REPRODUCIBILITY.md` — env, run cmd, MD5 hashes
- [ ] `role3/week3/writeup_week3.tex` — full LaTeX: Prop 1–4 + Lemma + Theorem with proofs
- [ ] `role3/week3/GITHUB_CHECKLIST.md` — this file

### Code (4 bullets + master driver)
- [ ] `role3/week3/comparative_statics_characterization.py` — Bullet 1
- [ ] `role3/week3/contract_comparative_statics.py` — Bullet 2
- [ ] `role3/week3/robustness_value.py` — Bullet 3
- [ ] `role3/week3/fragility_map.py` — Bullet 4
- [ ] `role3/week3/run_week3.py` — master driver

### Results (9 CSVs + memo)
- [ ] `role3/week3/results/week3_findings_memo.md`
- [ ] `role3/week3/results/characterization_comparative_statics.csv`
- [ ] `role3/week3/results/characterization_boundary_movement.csv`
- [ ] `role3/week3/results/contract_wedge_comparative_statics.csv`
- [ ] `role3/week3/results/contract_wedge_by_shape.csv`
- [ ] `role3/week3/results/robustness_gap_vs_radius.csv`
- [ ] `role3/week3/results/robustness_summary.csv`
- [ ] `role3/week3/results/fragility_adoption_boundary.csv`
- [ ] `role3/week3/results/fragility_endpoint_boundary.csv`
- [ ] `role3/week3/results/fragility_summary.csv`

## 2. Bullet-by-bullet verification (must all be ✅ before pushing)

| # | Bullet | Artifact | Status |
|---|--------|----------|--------|
| 1 | Comparative statics of characterization: sign ∂J/∂θ for {R, c, β, p, C_F, C_R, C_M}; boundary movement dC̄_M/dθ | `characterization_*.csv` + Prop 1 in tex | ✅ 6/7 signs distribution-free across 8 dists |
| 2 | Contract comparative statics: wedge W = Carbon(myopic) − Carbon(optimal); dW/dC_M ≤ 0, dW/dC_R ≤ 0 | `contract_wedge_*.csv` + Prop 2 in tex | ✅ 7/8 in C_M, 8/8 in C_R |
| 3 | Value of robustness: LR-path sign invariance under Wasserstein-1 Beta ambiguity set; price of robustness monotone | `robustness_*.csv` + Prop 3 in tex | ✅ LR-invariant, monotone bounded |
| 4 | Fragility map: adoption knife-edge at C̄_M; endpoint shift-ratio flip witness | `fragility_*.csv` + Prop 4 in tex | ✅ K_M* collapses 0.16→0 at C̄_M; a* ≈ 0.5 |

## 3. Push steps

1. Switch to `Role-3` branch: `git checkout Role-3`
2. Copy the `role3/week3/` folder from this zip into repo root.
3. `git add role3/week3/`
4. `git commit -m "Role 3 — Week 3: comparative statics, contract wedge, robustness, fragility"`
5. `git push origin Role-3`
6. Open PR `Role-3 → main` on GitHub if merging.

## 4. Triple-verification signature

- Determinism: MD5 hashes of all 9 CSVs stable across back-to-back `python run_week3.py` runs (see REPRODUCIBILITY.md).
- Coverage: 4/4 Week 3 bullets from `A1_Week3_NextRoles.pdf` implemented + proved + numerically checked.
- Cross-role sync: fragility endpoint flip at a* ≈ 0.5 matches Role 4's sharpness witness; wedge sign matches Role 1's carbon decomposition.
