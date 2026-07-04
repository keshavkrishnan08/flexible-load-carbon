# Role 3 — Week 3

Comparative statics of the carbon characterization, contract wedge,
robustness value, and fragility witnesses.

## Files
| File | Purpose |
|------|---------|
| `comparative_statics_characterization.py` | Bullet 1: signs ∂J/∂θ for θ ∈ {R, c, β, p, C_F, C_R, C_M}; boundary movement dC̄_M/dθ |
| `contract_comparative_statics.py`         | Bullet 2: wedge W = Carbon_myopic − Carbon_optimal; signs dW/dC_M, dW/dC_R; Beta(a, 5−a) shape sweep |
| `robustness_value.py`                     | Bullet 3: Wasserstein-1 Beta ambiguity set, price-of-robustness monotonicity, LR-path certificate |
| `fragility_map.py`                        | Bullet 4: adoption knife-edge (C_M around C̄_M) + endpoint shift-ratio check g(a) ≥ g(K_F*) |
| `run_week3.py`                            | Driver — runs all four, writes team memo |
| `writeup_week3.tex`                       | LaTeX writeup: Prop 1–4, Lemma, Theorem with proofs |
| `REPRODUCIBILITY.md`                      | Env, run command, verification table |
| `results/`                                | 9 CSVs + `week3_findings_memo.md` |

## Reproduce
```
cd role3/week3
python3 run_week3.py
```
Uses the shared solver in `../numerical_solver.py`.

## Headline numbers
- ∂J/∂R > 0, ∂J/∂c < 0, ∂J/∂C_F < 0, ∂J/∂C_R < 0, ∂J/∂C_M < 0: **8/8 distributions each**
- ∂J/∂β > 0: **7/8**; ∂J/∂p > 0: **5/8** (ambiguous, flagged)
- Wedge monotonicity: ∂W/∂C_M ≤ 0 in **7/8**, ∂W/∂C_R invariant sign 8/8
- LR-path sign invariance: **True**; max price of robustness: **0.125**
- Endpoint condition g(a) ≥ g(K_F*) (a = K_F*−K_M*) holds in **17/17** Beta(a, 5−a) scenarios; no flip (g non-increasing on this single-mode family)
- Adoption knife-edge witness: K_M* collapses from 0.16 → 0 across C̄_M

## Sync with Roles 1, 2, 4
- Bullet 1 signs feed directly into Role 1's characterization theorem.
- Bullet 2 wedge quantifies gap Role 2's optimal-contract solver targets.
- Bullet 3 confirms Role 1's minimax equality along the MLR deformation path.
- Bullet 4: the endpoint condition holds across the whole Beta(a, 5−a) family; the genuine regime boundary for Role 4 is the adoption knife-edge C_M = C̄_M.