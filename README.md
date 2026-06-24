# Team A1, Role 4 — Theory Hardening and Regimes

The Role 4 deliverable on the **FCL paper**, addressing the four task bullets:

1. **Re-verify the core proofs** — FOC derivations eqs (12), (13), (15) and the
   three-step Proposition 1 proof (Appendix B.1), with the one gap flagged.
2. **Complete the small-FCL regime** — Appendix G eqs (60)–(63) and the wider
   adoption threshold eq (62), `C̄_M^b = C̄_M + c·q° > C̄_M`.
3. **Reconcile the regime boundaries** — full-coverage (p25 digression
   `R ≥ c+C_F+C_M`), interior/large-FCL, and small-FCL in one consistent
   statement, ordered `C_M^fc < C̄_M < C̄_M^b`.
4. **Pressure-test Assumption 1** — each of the four conditions, what it guards,
   and what breaks if relaxed.

Read **`THEORY_HARDENING.md`** first — it is organized bullet-by-bullet, with
every claim cross-referenced to the test that backs it. It also resolves the
**Keshav (Role 1) vs Dhruv (Role 2)** carbon disagreement: they evaluate the
program below vs above a buildout crossover `K_R^cross`, and the with-FCL
program is unbounded exactly on the carbon-reduction window (`C_R < C_R†`).

## Setup & run
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q     # 17 passing
.venv/bin/python run_analysis.py         # regime_map.png, reconciliation.png/.csv
```

## Layout
```
role4/
  params.py         model primitives + the four Assumption-1 predicates
  foc.py            bullet 1A: eqs 11-15 cutoffs (Lemma 2), checked vs solver
  proposition1.py   bullet 1B: Prop 1 three steps + the flagged Step-3 gap
  small_fcl.py      bullet 2: Appendix G eqs 60-63 + eq 62 widening
  regimes.py        bullet 3: unified coverage + boundedness statement, crossover
  assumption1.py    bullet 4: four-condition necessity / what-breaks stress test
  reconcile.py      Role 1 vs Role 2 carbon reconciliation (uses the backend)
  fcl_backend/      Role 2's solver, vendored unchanged as the numerical backend
tests/              17 pytest cases, one file per bullet
run_analysis.py     figures + a four-bullet summary print
THEORY_HARDENING.md the writeup (start here)
FCL_Carbon_Paper.txt the source paper (equations intact)
archive_miner_side/  the earlier original-task miner-side work (old Bitcoin
                     paper, eqs 9-10 / App A) — kept for provenance, not part
                     of this task. See its proofs in derivations.md there.
```

## Numerical backend note
`role4/fcl_backend/` is Role 2's `fcl_solver`, copied in unchanged. Role 1
designates it the team validation backend; using it here means the
reconciliation runs against the *actual* numerical model that disagreed with
the theory, not a reimplementation.
