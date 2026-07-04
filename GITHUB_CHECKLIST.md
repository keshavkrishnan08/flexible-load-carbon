# Role 3 — Week 3 GitHub Checklist

Target: `Role-3` branch of `dhruvkamath-dev/team-a1`, under `role3/week3/`.

## Sync with past weeks
- **Week 1 dependency**: all Bullet 1–4 scripts `from numerical_solver import (...)` — that module lives at `role3/numerical_solver.py` (Week 1). This zip includes a copy inside `week3/` so it runs standalone; in the repo, keep the canonical copy at `role3/numerical_solver.py` and delete the duplicate.
- **Week 2 dependency**: none at import time. Week 3 reuses the same `K_R_max=20.0` saturation fix introduced in Week 2 (already in `numerical_solver.py`).
- **Cross-role sync**:
  - Bullet 1 distribution-free signs feed Role 1's characterization theorem.
  - Bullet 2 wedge sign matches Role 1's carbon decomposition.
  - Bullet 3 LR-path certificate matches Role 1's minimax statement.
  - Bullet 4: endpoint condition g(a) ≥ g(K_F*) holds across the whole Beta(a,5−a) family (no flip); the genuine knife-edge for Role 4 is the adoption boundary C̄_M.

## Files to upload

### Docs
- [ ] `role3/week3/README.md`
- [ ] `role3/week3/REPRODUCIBILITY.md`
- [ ] `role3/week3/writeup_week3.tex` — Prop 1–4 + Lemma + Theorem with proofs
- [ ] `role3/week3/GITHUB_CHECKLIST.md` (this file)

### Code
- [ ] `role3/week3/comparative_statics_characterization.py` — Bullet 1
- [ ] `role3/week3/contract_comparative_statics.py` — Bullet 2
- [ ] `role3/week3/robustness_value.py` — Bullet 3
- [ ] `role3/week3/fragility_map.py` — Bullet 4
- [ ] `role3/week3/run_week3.py` — master driver
- [ ] `role3/numerical_solver.py` — already present from Week 1; do NOT re-commit the bundled copy inside `week3/`

### Results
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

## Bullet verification
| # | Bullet | Status |
|---|--------|--------|
| 1 | Sign ∂J/∂θ for {R,c,β,p,C_F,C_R,C_M}; boundary movement | ✅ 6/7 signs distribution-free across 8 dists |
| 2 | Wedge W monotone: dW/dC_M ≤ 0, dW/dC_R ≤ 0 | ✅ 7/8 in C_M, 8/8 in C_R |
| 3 | Wasserstein Beta ambiguity: LR-path sign invariant | ✅ invariant; max price of robustness = 0.125 |
| 4 | Adoption knife-edge at C̄_M; endpoint shift-ratio check | ✅ K_M*: 0.16→0 at C̄_M; g(a) ≥ g(K_F*) holds 17/17, no flip |

## Push steps
1. `git checkout Role-3`
2. Copy `week3/` into `role3/week3/` in the repo. Delete `role3/week3/numerical_solver.py` (bundled copy) — the canonical one at `role3/numerical_solver.py` is already on the branch from Week 1.
3. `git add role3/week3/`
4. `git commit -m "Role 3 — Week 3: comparative statics, contract wedge, robustness, fragility"`
5. `git push origin Role-3`

## Triple-verification signature
- Determinism: MD5 hashes of all 9 CSVs stable across back-to-back `python run_week3.py` (see REPRODUCIBILITY.md).
- Coverage: 4/4 Week 3 bullets from `A1_Week3_NextRoles.pdf`.
- Standalone: `run_week3.py` executes end-to-end from this zip after unzip.
