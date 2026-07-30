# Role 3 — Reproducibility Report

## Environment
- Python >= 3.10
- Dependencies (see `requirements.txt`): numpy, scipy, pandas, matplotlib
- Install: `pip install -r requirements.txt`

## How to reproduce
From the `role3/` directory:
```
python3 run_all_experiments.py
```
Outputs are written to:
- `role3/results/proposition1_profit_blackout_carbon.csv`
- `role3/results/case_c_short_run_carbon.csv`
- `role3/results/role1_capacity_substitution.csv`
- `role3/results/findings_summary_for_team.md`
- `role3/figures/triple_win_heatmap.png`
- `role3/figures/carbon_by_skew.png`

## Determinism
The solver uses a fixed RNG seed (`numpy.random.default_rng(0)` in
`numerical_solver.draw`) and deterministic root-finders
(`scipy.optimize.brentq`, `minimize_scalar`). Running
`run_all_experiments.py` three times in a row produces byte-identical
CSVs and identical stdout:

```
md5(proposition1_profit_blackout_carbon.csv) = 5789890fe58da37da6992bd96f83b96a
md5(case_c_short_run_carbon.csv)             = 15e04a414f8a5151d00f1aa5d7d97620
md5(role1_capacity_substitution.csv)         = b40ee5ed41c5c11999ddcee250458f04
md5(stdout across 3 runs)                    = 6d92b35f636a55f82ed9cc3ef5377f67
```

## Verified results (triple-checked, identical across 3 runs)

| Claim (paper reference)                              | Scenarios | Confirmed |
|------------------------------------------------------|-----------|-----------|
| Prop 1 (i): profit up with FCL when C_M < C_M_bar    | 16        | 16/16     |
| Prop 1 (ii): blackout prob down when C_M < C_M_bar   | 16        | 16/16     |
| Capacity substitution K_R* >= K_R^o (eq 15 channel)  | 32        | 32/32     |
| Case C short-run (eq 30): dCarbon >= 0, fixed K's    | 96        | 96/96     |
| Utilisation Term II of eq 17 has predicted sign      | 40        | 40/40     |

Sync point with Role 1: in the long-run joint optimum the carbon sign
flips only under left-skewed F + high C_R, matching footnote 6 of the
paper.

## File map
- `numerical_solver.py` — FOC solver for eqs (10), (12), (13), (15) and Case C (eq 30).
- `run_all_experiments.py` — Bullets 1-4 driver; writes CSVs + figures + memo.
- Formal proofs (Prop 1, capacity substitution, eq 17 decomposition, Case C
  corollary) live in the assembled manuscript, which is maintained outside this
  repository; the reproducible sources are the per-week write-ups
  (`writeup_week2.tex`, `writeup_week3.tex`, `writeup_week4.tex`) at the repo root.
- `results/` — CSV outputs + team sync memo.
- `figures/` — heatmap and skew plot used in the writeup.
