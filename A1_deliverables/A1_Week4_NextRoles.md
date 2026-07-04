# A1 Week 4 Plan

## Role 1 (Optimal Contract and General Carbon Theory)

- **Prove the carbon classification theorem.** Construct a single distributional
  functional of the residual-demand law, and prove the sign of the net-carbon effect
  equals the sign of that functional -- both directions. This turns the Week-2 sufficient
  conditions and numerical resolution into one closed-form if-and-only-if: exactly when,
  and why, a flexible load reduces carbon, for every distribution. It is the headline
  result, and it must be airtight to the most adversarial reviewer.

- **Pin the minimal decisive statistic.** Week 2 proved the carbon sign is not decidable
  from the distribution-free cutoffs, so the functional must live in the right
  conditional-moment space. Identify that minimal sufficient statistic and prove the
  converse -- no coarser statistic of the distribution decides the sign -- so the
  characterization is not just sufficient but sharp.

- **Close the frontier leverage condition to a theorem.** The Week-3 extension reduced
  global carbon-optimality of the surplus contract to a single leverage condition,
  verified but not proved. Prove it -- or characterize exactly the class of distributions
  and costs on which it holds and the boundary where it fails -- completing the
  optimal-contract-family result.

- **Give the distributionally-robust characterization.** Combine the functional with an
  ambiguity set of demand laws: characterize the worst-case distribution and the
  robust-optimal contract in terms of the functional, with a closed form on the power-law
  family and a price of robustness.

- **Draw the carbon phase diagram from the functional.** Partition the primitive space
  (costs and distribution shape) into carbon-up, carbon-neutral, and carbon-down regions
  whose analytic boundaries are the level sets of the functional and the viability
  threshold; establish the topology (each region connected, boundaries monotone).

- **Unify and self-contain.** Assemble the above into one classification theorem and make
  the deliverable standalone, restating and proving every imported lemma in-file. The
  numerical companion mirrors every identity and confirms sign of carbon equals sign of
  the functional in every cell.

## Role 2 (Solver and Numerical Methods)

- **Build the classification-functional evaluator.** Compute the functional across a large
  theory-tied distribution library (Beta scale-mixtures, bimodal, heavy-tailed) and
  confirm the sign of the net-carbon effect matches the sign of the functional in every
  cell, to machine precision -- one principled sweep that corroborates the if-and-only-if
  or surfaces the counterexample.

- **Map the phase diagram numerically.** Trace the level sets of the functional and the
  viability threshold across the primitive space, rendering the carbon-up / neutral /
  down partition and certifying the boundaries (not finite-difference noise).

- **Certify the leverage and the robust saddle.** Verify the leverage condition and its
  boundary numerically, and certify the distributionally-robust saddle (worst-case
  distribution matches the inner problem; minimax equals maximin).

- **Delimit the regularity region.** Establish the boundary of where the characterization's
  hypotheses hold (analytic Hessian / KKT certificates), delivering a numerical map of
  where the Week-4 theory applies.

## Role 3 (Comparative Statics and Robustness)

- **Sign the functional's comparative statics.** Via implicit-function and envelope
  identities, sign the derivative of the classification functional and the movement of the
  carbon boundary for every primitive, and prove the direction in which each cost shifts
  the carbon-down region.

- **Quantify the value of robustness through the functional.** Prove monotonicity of the
  robust-minus-nominal carbon gap in the ambiguity radius, bound the price of robustness,
  and deliver a cross-distribution certificate along a likelihood-ratio / mean-preserving
  spread path so the verdict holds across the path.

- **Map fragility of the boundary.** Identify where the characterization is knife-edge --
  the level set of the functional at zero -- and construct explicit witnesses on each
  side, the sharpness companions to Role 1's theorem.

- **Sign the contract-family comparative statics.** Characterize how the optimal budget
  and the leverage move with costs and with the shape of the distribution, in particular
  near the boundary where surplus-only ceases to be globally optimal.

## Role 4 (Theory Hardening and Regimes)

- **Extend the functional across regimes.** Carry the classification functional into the
  small-FCL regime and across the regime boundary; prove the functional and the carbon
  boundary stitch continuously, or locate and explain the discontinuity.

- **Harden the converse.** Supply the measure-theoretic scaffolding the necessity half
  needs -- existence and measurability of the extremal laws, constraint qualification for
  the minimal-statistic argument, and the class of admissible distributions on which the
  converse is tight.

- **Regime-map the classification.** Determine where the carbon regions and their
  boundaries cross regime lines; deliver the stitched phase diagram over the full cost
  plane spanning both FCL regimes.

- **Reconcile the team.** Integrate the four roles' Week-4 outputs into one coherent
  statement, cross-check every shared object (the functional, the boundary, the robust
  optimum) for consistency across roles, and flag any divergence before it reaches the
  integrated paper.
