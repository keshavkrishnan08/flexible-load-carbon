# CONTEXT.md — Team A1, Role 4 (Theory Hardening and Regimes)

## Task (verbatim, the updated Role 4 assignment)
Role 4 (Theory Hardening and Regimes), on the FCL paper:
1. Re-verify the core proofs. Walk the Proposition 1 proof in Appendix B.1 and
   the three FOC derivations (eqs 12, 13, 15), flagging any gap.
2. Complete the small-FCL regime. Finish the small-FCL case in Appendix G and
   confirm the wider adoption threshold in eq 62.
3. Reconcile the regime boundaries. Make the large-FCL, small-FCL, and
   full-coverage cases (the R >= c + C_F + C_M digression on p25) fit together
   in one consistent statement.
4. Pressure-test Assumption 1. Check the four parameter conditions are
   necessary where claimed and note what breaks if each is relaxed.

## Why this exists
Keshav's theoretical model (Role 1) and Dhruv's numerical model (Role 2)
disagreed on carbon: Role 1 proves it falls; Role 2 found it never does across
210 scenarios and that the model wants infinite capacity. Role 4 hardens the
theory and maps the regimes so the two reconcile.

## Source / paper
`FCL_Carbon_Paper.txt` — "Flexible Computing Loads, Electricity Grid
Resilience, and Carbon Emission Reduction." Equation numbers in the task match
this file (Assumption 1 §3.1; eqs 11-15 §4.1; Prop 1 + proof App. B.1; small-FCL
eqs 60-63 and eq 62 App. G; p25 full-coverage digression).

## Key results (all verified; see THEORY_HARDENING.md)
- FOCs 12/13/15 re-derived; cutoffs match Role 2's solver to ≤1e-3.
- Prop 1 Steps 1-2 fully general; Step 3 (carbon) general only for uniform/
  power — gap flagged, closed by Role 1's shift ratio + the buildout crossover.
- Small-FCL eq 62: C̄_M^b = C̄_M + c·q° > C̄_M (adoption widens by c·q°).
- Regimes ordered C_M^fc < C̄_M < C̄_M^b; full-coverage = p25 digression.
- Assumption 1: A1/A3/A4 strictly necessary (relaxing breaks an interior
  optimum / flips a sign); A2 necessary only for the interior regime (relaxing
  lands in full coverage, not a contradiction).
- Reconciliation: with-FCL unbounded iff C_R < C_R†; carbon falls only past the
  buildout crossover K_R^cross. Both Role 1 and Role 2 correct.

## How I want Claude Code to work
Explain before changing; re-derive from the .txt rather than transcribe; trust
the paper over notes and flag discrepancies; write validation as real pytest
tests; use Role 2's solver (vendored in role4/fcl_backend) as the numerical
backend rather than reimplementing it.

---

## Week 2 — Mechanism Design and Regimes (additive)

### Task (verbatim, the Week 2 Role 4 assignment)
1. Prove a single per-MWh price R (not a state-contingent transfer) uniquely
   implements the dispatch d* and pins the capacity vector; characterize when
   the price instrument is rich enough.
2. Compose the C_M coverage axis and the C_R boundedness axis into one regime
   theorem, and pin the small-/large-FCL crossover as the locus K_M* = K_R°
   (left open in Week 1).
3. Upgrade the Assumption-1 pressure-test to a necessity proof for each of the
   four conditions, and characterize the regime obtained when each is relaxed.
4. Introduce private information the principal cannot infer from observed
   demand — the agent privately knows the renewable factor S, only D is
   observed — and derive the second-best screening contract and how its
   information rent shifts emissions vs the full-information benchmark.

### Key results (all verified; see MECHANISM_REGIMES.md)
- Bullet 1: flat R implements d* (Lemma 1, served-MWh payoff) and the capacity
  FOCs pin (K_R*,K_F*,K_M*); rich enough iff c < R < β+p (implied by A1 and A4);
  an unrestricted state-contingent transfer adds zero value.
- Bullet 2: closes the Week-1 open item — C_M^cross = (R−c)[D̄(β+p−c−C_F)+
  K_R°(R−c−C_F)]/[(D̄+K_R°)(β+p−c)] (sympy-derived, = numeric locus); three-axis
  unified theorem with consistent labels.
- Bullet 3: each condition's guarded g(slack) is strictly monotone and hits its
  validity edge at slack 0 (a proof, not a nudge); {A1,A3,A4} strictly
  necessary, A2 necessary only for interiority.
- Bullet 4: private S ⇒ second-best d^SB ≤ d^FB (none-at-top); rent leaks,
  lowering effective FCL revenue R_eff < R, which shrinks the carbon-reduction
  window C_R < C_R† (read off the threshold since uniform K_R is a corner). A
  force against the carbon leg of the triple win, absent in the transparent-R
  Bitcoin case (Section 8 / Remark 8 made precise).

### Week 2 files (additive)
- role4/instrument.py, role4/unified_regime.py, role4/necessity.py,
  role4/screening.py
- tests/test_instrument.py, tests/test_unified_regime.py,
  tests/test_necessity.py, tests/test_screening.py
- run_analysis_week2.py, MECHANISM_REGIMES.md
- Full suite: 41 passing (17 Week 1 + 24 Week 2). Week 1 modules untouched.
