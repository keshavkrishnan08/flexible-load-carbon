# Role 3 — Week 2

Comparative statics, robust certificate, reversed-channel witness, and
limit-interchange proof for the FCL / Bitcoin-Mining carbon paper.

## Files
| File | Purpose |
|------|---------|
| `comparative_statics.py` | Bullet 1: signs ∂(ΔCarbon)/∂θ for θ ∈ {R, β, p, C_M}; verifies K_R* > K_R° under endpoint shift-ratio condition |
| `robust_certificate.py`  | Bullet 2: Beta-family MLR homotopy F_t, sweeps C_R, computes C_R^† |
| `reversed_channel.py`    | Bullet 3: bimodal F (0.5·Beta(8,2)+0.5·Beta(2,8)) where endpoint condition fails |
| `limit_interchange_test.py` | Bullet 4: dominated-convergence envelope check, K_M_n ↓ 0, E[d_n] ↓ 0 |
| `run_week2.py`           | Driver — runs all four and writes the team memo |
| `writeup_week2.tex`      | LaTeX writeup with full proofs (Prop, Lemma, Theorem, Corollary) |
| `REPRODUCIBILITY.md`     | Environment + run command + MD5 hashes + verification table |
| `results/`               | CSV outputs + `week2_findings_memo.md` |

## Reproduce
```
cd role3/week2
python3 run_week2.py
```
Reads the shared solver in `../numerical_solver.py`.

## Headline numbers
- ∂ΔC/∂R    > 0 in **8/8** distributions
- ∂ΔC/∂β    > 0 in **7/8**
- ∂ΔC/∂p    > 0 in **5/8** (flips in small-FCL corner)
- ∂ΔC/∂C_M  < 0 in **8/8**
- K_R* > K_R° in **24/24** scenarios (endpoint condition is sufficient,
  but not necessary on this grid → sync with Role 1)
- Robust-certificate obstruction: no positive C_R on the tested grid
  certifies ΔCarbon ≤ 0 uniformly along the Beta LR path
- Reversed-channel: endpoint condition fails by 1.6e-3; K_R* = K_R°
  (degenerate boundary, strict reversal deferred to Week 3)
- Dominated-convergence envelope: **72/72** pointwise dominations
