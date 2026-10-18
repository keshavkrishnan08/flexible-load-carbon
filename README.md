# Team A1: Flexible Computing Loads, Grid Resilience, and Carbon Emissions

**Workstream A1: General Carbon/Contracting Theory and Numerical Methods.**

When do flexible computing loads, Bitcoin mining, AI training, *lower* a grid's
carbon emissions, and when do they *raise* them? This repository is Team A1's
answer: one general theory of the carbon sign, the optimal dispatch contract that
flips it, and a numerical backend that verifies every closed form to machine
precision. It is built on the group's source paper (§3 model, §4 baseline,
Appendix B.1, Appendix G, Proposition 4).

> **What's here, and what isn't.** This repo holds the **theory, the numerical
> methods, and all verified results**. The assembled manuscript is maintained
> separately and is deliberately not tracked here. A1 owns the theory (general
> distributions, the carbon condition, the contract, the main-model
> re-derivation) and the numerical methods; it does **not** cover empirical
> calibration with real data (A2), reliability/welfare/social-vs-private pricing
> (B1), the storage/multi-grid/dynamics continuum (B2), or regulatory lag (B3).

---

## The result, in one paragraph

A regulated utility (or, in the main model, a competitive market of third-party
miners paying a tariff) jointly chooses renewable `K_R`, fossil `K_F`, and
flexible-load `K_M` capacity under stochastic residual demand `x = D − K_R·S`.
Three equilibrium cutoffs are **distribution-free**: pure ratios of prices and
costs that hold for *every* demand shape. The net carbon change admits an **exact
closed form** `Φ`. Under the naive "run whenever it pays" rule a load large enough
to matter **always raises** emissions (`Φ` certifies the backfire); the **surplus
contract**, run computing only on otherwise-curtailed renewable energy, is the
carbon-optimal dispatch and is what turns the sign. The whole capacity-and-carbon
theory holds in the paper's main third-party-miner model, where the fossil and
load cutoffs *decouple* (a separation principle the utility-operated model hides).

---

## The four roles

| Role | Owns | Key deliverables | Verification |
|------|------|------------------|--------------|
| **Role 1**: General Carbon Theory & Optimal Contract | `role1/` | distribution-free cutoffs; the exact carbon classifier `Φ`; the optimal surplus contract; the **double-margin main-model re-derivation** (cutoffs + exact `Φ` coefficient + separation principle); storage as the competing surplus user; prices-vs-quantities; calibration theory | `role1/verify_*.py`, `validate_*.py`, 11 suites, all green |
| **Role 2**: Numerical solver & validator | `fcl_solver/`, `role2/`, `week2-4/` | the FOC solver for the joint capacity problem; per-week numerical validation against the closed forms | `pytest` (see `role2/`) |
| **Role 3**: Comparative statics & results | `role3/`, root `writeup_week*.tex` | Monte-Carlo comparative statics across 8 distributions × parameter grids; Proposition-1 profit/blackout/carbon signs | `role3/run_all_experiments.py` (seed-fixed, bit-reproducible) |
| **Role 4**: Theory hardening & regimes | `role4/`, `archive_miner_side/` | regime classification (small- vs large-FCL), hardening proofs, reconciliation against Role 2's solver (vendored unchanged) | `pytest role4/tests/` |

Cross-role consistency (shared notation, shared closed forms, no contradictions)
is certified in [`INTEGRATION.md`](INTEGRATION.md).

---

## Team and paper

ASSIP 2026 Team A1 at George Mason University (Costello College of Business), advised by
Dr. Jiasun Li: Keshav Krishnan, Ronit Mazumdar, Shreyas Kondapuram, and Dhruv Kamath. The work
was published as *The Carbon Effect of Flexible Computing Loads: A Distribution-Free Theory of
Dispatch, Investment, and Optimal Contracts* in the Journal of Student-Scientists' Research
(2026), [doi:10.13021/jssr2026.5665](https://doi.org/10.13021/jssr2026.5665).

This repository carries the team's full commit history, including the four role branches, from
[dhruvkamath-dev/team-a1](https://github.com/dhruvkamath-dev/team-a1).

---

## Reproduce everything

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
bash run_all.sh          # runs every role's verification; prints ALL A1 DELIVERABLES REPRODUCE.
```

Role-1 suites can also be run individually, e.g.:

```bash
cd role1
python3 verify_exact.py           # 21/21 - every analytic formula vs finite-difference of the profit integral
python3 verify_double_margin.py   #  9/9  - the cutoffs + exact Φ coefficient in the paper's main model
python3 verify_storage.py         #  6/6  - storage vs the flexible load for renewable surplus
```

---

## Repository layout

```
role1/            General carbon theory, optimal contract, main-model re-derivation (+ verifiers)
role2/  fcl_solver/  week2-4/   Numerical FOC solver and per-week validation
role3/            Comparative-statics experiments + results (CSVs, figures)
role4/  archive_miner_side/     Regime classification and theory hardening
A1_deliverables/  Results summaries, per-week findings, next-role handoff notes
tests/            Shared solver tests
writeup_week*.tex Per-week theory write-ups (Role 3)
run_all.sh        One-command reproducibility across all four roles
INTEGRATION.md    Cross-role consistency certificate
*_findings_memo.md, SCOPE.md, THEORY_HARDENING.md, REPRODUCIBILITY.md
```

## Scope of claims and honest limitations

Each role documents exactly what it proves, under what hypotheses, and what it
does not claim, see `role1/ROLE1_SCOPE.md`, `THEORY_HARDENING.md`, and the
per-role `REPRODUCIBILITY.md` files. Notable honestly-stated boundaries: the
carbon "classifier" `Φ` certifies a *rise* on its valid (large-FCL) domain rather
than exhibiting a two-sided flip there; the storage treatment is static
expected-flow, not a dynamic state-of-charge model; and the calibration's tariff
`p` is an assumption pending A2's empirical rebuild.
