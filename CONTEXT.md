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

## Working conventions
Explain before changing; re-derive from the .txt rather than transcribe; trust
the paper over notes and flag discrepancies; write validation as real pytest
tests; use Role 2's solver (vendored in role4/fcl_backend) as the numerical
backend rather than reimplementing it.
