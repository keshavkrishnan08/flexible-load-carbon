# Reproducibility: Role 3 Week 4

## Environment
- Python ≥ 3.10
- `pip install -r ../requirements.txt` (numpy, scipy, pandas, matplotlib)

## Run
```
python run_week4.py
```
Seed is fixed (`Params.seed = 7`, `n_samples = 40000`). Every CSV is
bit-for-bit stable across back-to-back runs.

## MD5 hashes (results/*.csv)
```
9f33dc4a5a02906074e98cd0c773f39c  characterization_boundary_movement.csv
db07b3ba2ba6c61e554203b44573ca10  characterization_comparative_statics.csv
ad1d39297419678334aa463aacdc324f  contract_wedge_by_shape.csv
ac378448e3fcb96d0e7d7ab1d5e5f650  contract_wedge_comparative_statics.csv
1147c8d2e5fda509499a6db4f936ee9b  dro_pareto_psi_curve.csv
c0b52848a374e5eab951e96237ecc746  dro_summary.csv
ef9a4ab42448b53bfdd721ee7f25bc10  dro_worst_case_and_robust_contract.csv
b6f77cbc56423bb39032d7e2defaf924  fragility_adoption_boundary.csv
c8eb88df644c8d1e89d5d95f2a841af9  fragility_endpoint_boundary.csv
4770d0d167a861ee674f42b75aad0759  fragility_summary.csv
330cd4316d8b981c5eb8540025806646  robustness_gap_vs_radius.csv
4666be517d0b219b6a58be2eb623ae4a  robustness_summary.csv
```
Verify with `md5sum results/*.csv`.