# A1 Week 3 Plan

## Role 1 (Optimal Contract and General Carbon Theory)

- **Characterize the optimal FCL dispatch-and-curtailment contract.** Replace the
  assumed rule with the full class of admissible state-contingent schedules plus a
  transfer. Solve for the firm-optimal contract and the carbon-optimal one, and
  characterize the optimizer.

- **Settle whether the optimal contract flips the carbon sign.** Prove whether a
  finite interior optimum exists where the carbon-optimal contract reduces carbon and
  the myopic rule cannot. Pin the wedge to the fossil floor.

- **Prove the exact carbon characterization (necessary and sufficient).** Build the
  carbon functional with sign-of-carbon equal to sign-of-functional, proved both ways.
  Identify the minimal decisive statistic of the distribution and prove no coarser one
  works, closing the keystone to an iff.

- **Solve the distributionally-robust capacity rule.** Over an ambiguity set around a
  nominal distribution, solve the worst-case carbon problem jointly with capacity
  choice. Characterize the saddle, prove the minimax equality, and give the robust
  capacities in closed form on the power-law family.

- **Draw the carbon phase diagram.** Partition the cost plane into carbon-up,
  carbon-neutral, and carbon-down regions with analytic boundaries. Establish
  connectedness and monotonicity.

- **Unify and self-contain.** Assemble the above into one classification theorem and
  make the deliverable standalone, restating and proving every imported Week-1/2 lemma
  in-file. Numerical companion mirrors each identity.

## Role 2 (Solver and Numerical Methods)

- **Build the optimal-contract solver.** Discretize the schedule space and solve the
  constrained carbon-minimization (variational optimal control with the profit-floor
  and IR multipliers), validating against Role 1's closed-form optimal contract on the
  uniform and power-law families to machine precision; recover the state-dependent
  curtailment cutoff and confirm the firm-optimal vs carbon-optimal wedge.

- **Build the distributionally-robust solver.** Implement the inner least-favorable-F
  search over the ambiguity set with the outer capacity optimization, and certify the
  saddle: verify minimax equals maximin numerically and that the inner optimizer
  matches Role 1's least-favorable distribution; map the robust optimum as the
  ambiguity radius grows.

- **Validate the characterization theorem at scale.** Evaluate the carbon functional
  across a large theory-tied distribution library (Beta scale-mixtures, bimodal,
  heavy-tailed) and confirm the sign match in every cell — one principled sweep that
  corroborates the iff or surfaces the counterexample; render the phase diagram
  numerically.

- **Certify the new optima.** Establish second-order conditions, uniqueness, and the
  boundary of the regularity region for the contract and robust problems (analytic
  Hessian / KKT certificates, not finite-difference noise), delivering a numerical map
  of where the Week-3 hypotheses hold.

## Role 3 (Comparative Statics and Robustness)

- **Sign the characterization comparative statics.** Via implicit-function and
  envelope identities, sign the derivative of the carbon functional and the movement
  of the carbon boundary for every primitive (R, c, beta, p, C_F, C_R, C_M), and prove
  the direction in which each cost shifts the carbon-down region.

- **Sign the optimal-contract comparative statics.** Characterize how the optimal
  curtailment schedule and its carbon output move with costs and with the shape of the
  distribution, in particular how the firm-optimal/carbon-optimal wedge responds to the
  adoption margin C_M and renewable cost C_R.

- **Quantify the value of robustness.** Prove monotonicity of the robust-minus-nominal
  carbon gap in the ambiguity radius, bound the price of robustness, and deliver a
  cross-distribution certificate along a likelihood-ratio / mean-preserving-spread
  deformation path so the robust verdict holds across the path, not just at the
  nominal.

- **Map fragility.** Identify where the new results are knife-edge — the boundary of
  the characterization and the saddle — and construct explicit witnesses on each side,
  the sharpness companions to Role 1's theorems.

## Role 4 (Theory Hardening and Regimes)

- **Extend the contract and characterization across regimes.** Carry the optimal
  contract and the characterization into the small-FCL regime and across the regime
  boundary; prove the schedule and the carbon functional stitch continuously, or locate
  and explain the discontinuity.

- **Harden the optimality and robust proofs.** Supply the measure-theoretic
  scaffolding the variational and minimax arguments need — existence and measurability
  of the optimal schedule, IC/IR constraint qualification, and a minimax theorem whose
  compactness and convexity hypotheses are verified for the ambiguity set. Stress-test
  Assumption 1 against each new result.

- **Regime-map the new objects.** Determine where the optimal contract changes form
  and where the phase-diagram boundaries cross regime lines; deliver the stitched
  carbon phase diagram over the full cost plane spanning both FCL regimes.

- **Reconcile the team.** Integrate the four roles' Week-3 outputs into one coherent
  statement, cross-check every shared object (the contract, the carbon functional, the
  robust optimum) for consistency across roles, and flag any divergence before it
  reaches the integrated paper.
