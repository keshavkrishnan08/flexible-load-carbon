# Role 3: Results

Outputs of `python run_all_experiments.py` (seed = 7, 40k Monte-Carlo samples).
All numbers reproduce bit-for-bit from a clean checkout.

## Files

| File | What it tests | Headline |
|------|---------------|----------|
| `proposition1_profit_blackout_carbon.csv` | Prop 1 (profit ↑, blackout ↓) + carbon sign across 8 distributions × 5 parameter grids | profit ↑ **16/16**, blackout ↓ **16/16** when `C_M < C̄_M`; carbon ↓ 10/40 (right-skew low-C_R region) |
| `case_c_short_run_carbon.csv` | Section 5.3 / eq. (30): both capacities fixed | ΔCarbon ≥ 0 in **96/96** |
| `role1_capacity_substitution.csv` | Capacity-substitution channel `K_R* > K_R°` (eq. 15) | **32/32**; carbon strictly ↓ in 2/32, all right-skew + low-C_R |
| `findings_summary_for_team.md` | Plain-English memo for the team sync with Role 1 | see file |

## Sync points (for Role 1)

1. Proposition 1 parts (i)-(ii) are **distribution-free** in every test whenever `C_M < C̄_M`: the proof's claim is numerically airtight.
2. Term II of the carbon decomposition (eq. 17, utilisation effect) is non-negative in 30/40 scenarios; flips sign only in the left-skew + high-`C_R` corner.
3. Candidate general carbon condition needs the qualifier *"under right-skewed F or sufficiently low `C_R`"*, matches Role 2's 210-scenario null and Role 4's partial-grid null.

## Regenerating

```bash
cd role3
python run_all_experiments.py
```