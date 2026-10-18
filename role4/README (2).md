# Team A1, Role 4: Theory Hardening and Regimes

## Week 4: Final Role 4 layer

Read **`WEEK4_ROLE4_DELIVERABLE.md`** first. The Week-4 acceptance wrapper is
`role4/week4.py`; it checks the four Week-4 bullets from the plan in one place:

1. extend the classification functional across small-/large-FCL regimes;
2. harden the converse with measurability, compactness, CQ, and minimax scaffolding;
3. regime-map the carbon-up/neutral/down classification over the full cost plane;
4. reconcile the shared objects and flag divergences before integration.

```bash
python -m pytest -q          # 71 passing
python run_analysis_week4.py # one-screen Week-4 certificate
```

Week-4 additive files:
```
role4/week4.py
tests/test_week4.py
run_analysis_week4.py
WEEK4_ROLE4_DELIVERABLE.md
```


> **Week 2 (Mechanism Design and Regimes) is now included**: see
> **`MECHANISM_REGIMES.md`** and the four new modules
> (`instrument.py`, `unified_regime.py`, `necessity.py`, `screening.py`),
> 24 new tests, and `run_analysis_week2.py`. Week 2 is purely additive; Week 1
> below is unchanged. Full suite after the Week-4 patch: **71 passing**.

The Role 4 deliverable on the **FCL paper**, addressing the four task bullets:

1. **Re-verify the core proofs**: FOC derivations eqs (12), (13), (15) and the
   three-step Proposition 1 proof (Appendix B.1), with the one gap flagged.
2. **Complete the small-FCL regime**: Appendix G eqs (60)-(63) and the wider
   adoption threshold eq (62), `C̄_M^b = C̄_M + c·q° > C̄_M`.
3. **Reconcile the regime boundaries**: full-coverage (p25 digression
   `R ≥ c+C_F+C_M`), interior/large-FCL, and small-FCL in one consistent
   statement, ordered `C_M^fc < C̄_M < C̄_M^b`.
4. **Pressure-test Assumption 1**: each of the four conditions, what it guards,
   and what breaks if relaxed.

Read **`THEORY_HARDENING.md`** first, it is organized bullet-by-bullet, with
every claim cross-referenced to the test that backs it. It also resolves the
**Keshav (Role 1) vs Dhruv (Role 2)** carbon disagreement: they evaluate the
program below vs above a buildout crossover `K_R^cross`, and the with-FCL
program is unbounded exactly on the carbon-reduction window (`C_R < C_R†`).

## Setup & run
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q            # 71 passing
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
                     paper, eqs 9-10 / App A) - kept for provenance, not part
                     of this task. See its proofs in derivations.md there.
```

## Numerical backend note
`role4/fcl_backend/` is Role 2's `fcl_solver`, copied in unchanged. Role 1
designates it the team validation backend; using it here means the
reconciliation runs against the *actual* numerical model that disagreed with
the theory, not a reimplementation.

## Week 2: Mechanism Design and Regimes
Read **`MECHANISM_REGIMES.md`** (organized bullet-by-bullet, every claim
cross-referenced to its test, same conventions as `THEORY_HARDENING.md`):

1. **A single per-MWh price implements the optimum**: a scalar `R` (not a
   state-contingent transfer) uniquely implements dispatch `d*` and pins the
   capacity vector; rich enough iff `c < R < β+p` (`role4/instrument.py`).
2. **Unified regime theorem**: composes coverage(`C_M`), boundedness(`C_R`),
   and FCL-scale axes into one statement, and **closes Week 1's open item** with
   the closed-form crossover `K_M*=K_R°` (`role4/unified_regime.py`).
3. **Necessity of Assumption 1, proven**: each condition's guarded quantity is
   a strictly monotone `g(slack)` hitting its validity edge exactly at slack 0;
   `{A1,A3,A4}` strictly necessary, `A2` interior-only (`role4/necessity.py`).
4. **Second-best contract under a private renewable factor**: the principal
   observes `D` but not `S`, so residual demand is private; the screening
   contract distorts dispatch downward (none at the top) and the information
   rent shrinks the carbon-reduction window `C_R<C_R†` (`role4/screening.py`).

```bash
.venv/bin/python -m pytest tests/ -q          # 41 passing (17 + 24)
.venv/bin/python run_analysis_week2.py        # crossover.png/.csv, screening.png
```

Week 2 layout (additive to the Week 1 tree above):
```
role4/
  instrument.py      Week-2 bullet 1: single-price implementation + richness window
  unified_regime.py  Week-2 bullet 2: unified theorem + K_M*=K_R° crossover (closed form)
  necessity.py       Week-2 bullet 3: Assumption-1 necessity proofs (slack certificates)
  screening.py       Week-2 bullet 4: second-best contract under private S
tests/               +4 files (test_instrument/unified_regime/necessity/screening)
run_analysis_week2.py figures + a four-bullet Week-2 summary print
MECHANISM_REGIMES.md  the Week-2 writeup (start here for Week 2)
```

## Week 3: Theory Hardening and Regimes (across regimes)
Read **`REGIME_STITCHING.md`** (organized bullet-by-bullet, every claim
cross-referenced to its test):

1. **Contract & carbon functional stitch across the FCL regime boundary**,
   `d*` is regime-free and the carbon functional is `C¹` across `K_M=K_R`; the
   only non-smoothness is a *located* kink in `∂²Π/∂K_M²` of size `c/(D̄+K_R)`
   as the small-FCL surplus term switches on (`role4/regime_stitch.py`).
2. **Measure-theoretic hardening**: existence (Weierstrass on the compact box),
   measurability of `d*`, IC/IR constraint qualification, and the Sion minimax
   for the ambiguity set; existence and the saddle need `C_R ≥ C_R†`, not just
   Assumption 1 (`role4/hardening.py`).
3. **Stitched carbon phase diagram**: one *connected* carbon-down region
   spanning both FCL regimes, smooth boundary `C_R†(C_M)` (convex, min at `C̄_M`)
   crossed once by the regime-form line `C_M^cross` (`role4/regime_phase.py`).
4. **Reconcile the team**: the contract, carbon functional, and robust optimum
   cross-checked against Role 1 and the backend; the ill-posed-robust-on-the-
   carbon-window divergence flagged (`role4/reconcile_week3.py`).

```bash
.venv/bin/python -m pytest tests/ -q          # 41 passing here (17 + 24);
                                              # 66 with Week 2 in place (17+25+24)
.venv/bin/python run_analysis_week3.py        # regime_stitch.png, phase_full.png/.csv
```

Week 3 layout (additive):
```
role4/
  regime_stitch.py    Week-3 bullet 1: contract + carbon functional across K_M=K_R
  hardening.py        Week-3 bullet 2: existence/measurability/IC-IR CQ/Sion minimax
  regime_phase.py     Week-3 bullet 3: stitched carbon phase diagram (both regimes)
  reconcile_week3.py  Week-3 bullet 4: cross-role reconciliation + divergence flags
tests/                +4 files (test_regime_stitch/hardening/regime_phase/reconcile_week3)
run_analysis_week3.py figures + a four-bullet Week-3 summary print
REGIME_STITCHING.md   the Week-3 writeup (start here for Week 3)
```
