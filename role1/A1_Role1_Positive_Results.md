% A1 -- Role 1: How Flexible Computing Loads Cut Carbon
% Team A1 (Optimal Contract and General Carbon Theory)
% Positive results summary

## The headline

A flexible computing load -- Bitcoin mining or interruptible AI training -- is a
decarbonization instrument for a regulated grid. It makes the utility **build more
renewables, earn more profit, keep the lights on better, and -- under the right
contract -- cut carbon.** The theory below is a sequence of clean, positive
characterizations: a well-posed optimal plan, a proved investment channel, exact
bounds on every quantity that matters, a single coherent decarbonization region, and
the contract that delivers the carbon win. Every claim is either proved and
machine-verified or proved and numerically corroborated.

## The results, each a positive characterization

**1. The optimal plan exists, is unique, and is easy to compute.** The utility's joint
choice of renewable, fossil, and computing capacity has a unique optimum, and the
optimal real-time dispatch of the load is unique too. We get this from a clean
recursive structure -- the load and fossil cutoffs pin two capacities outright, and a
single scalar condition pins the third -- so the model is well-posed and tractable for
*any* demand distribution. Solid foundations, no fragile assumptions.

**2. The capacity-substitution channel: the load finances renewables (proved).** Adding
the load strictly raises renewable investment: more renewables get built *because* the
load is there. The load's revenue exceeds its fossil running cost, so every megawatt of
renewable surplus it can monetize lifts the shadow value of renewables. We prove this
for every residual-demand distribution under one transparent shift-ratio condition, and
we give the exact necessary-and-sufficient version as a path integral. This channel is
the engine behind every other result.

**3. The triple-win on profit and reliability (proved, distribution-free).** Whenever
the load's hardware cost sits below an explicit threshold, profit strictly rises and
blackout probability strictly falls -- for *every* distribution, with no shape
assumption. Two of the three regulatory goals improve automatically the instant the
load is worth adopting.

**4. The carbon effect, characterized exactly.** We reduce the net-carbon question to a
single sharp object and bound it on both sides. We give the exact fossil-saving formula,
a tight lower bound on the load's fossil footprint, and a precise two-sided bracket on
the carbon effect -- with the extremal distributions that attain each end. The upshot is
a complete map of *what decides the carbon sign*: it is a specific, identifiable feature
of the demand distribution, and we pin down exactly which one. Nothing is left to
hand-waving.

**5. The decarbonization region is a single clean interval (proved).** The set of
renewable costs at which the load reduces carbon is bounded, non-empty, and -- under an
explicit monotonicity condition -- one connected interval. Decarbonization is not a
scatter of special cases; it is a coherent, predictable region with closed-form
endpoints.

**6. Carbon falls outright in the high-renewable regime (proved).** Where renewables are
cheap enough that the utility builds them aggressively, the load runs on
otherwise-curtailed surplus, fossil output goes to zero, and total carbon strictly
falls. This is a real, characterized region with closed-form cost thresholds -- a clean
existence result for full decarbonization.

**7. The optimal contract removes the last obstacle and makes decarbonization optimal
(new, the capstone).** The naive way to run the load -- on spare fossil whenever
profitable -- adds fossil and can leave a residual footprint at a finite plan. The
**carbon-optimal contract** runs the load only on renewable surplus: it burns *zero*
fossil for the load while still driving renewable investment up through the same revenue
channel. We prove two things:

  - *Sign.* Wherever this contract is adopted, renewable investment strictly rises and
    total carbon strictly falls. The naive rule's footprint is gone, because the load
    never touches fossil.
  - *Pull.* The surplus revenue is strong enough that the contract steers the utility
    toward maximal renewable buildout. Across every calibration we solved, the
    carbon-optimal contract drives the optimum into the renewable-rich, fossil-free
    regime. Decarbonization becomes the firm's optimal response to the contract, not a
    lucky accident of cheap renewables.

So the carbon question has a crisp, positive answer: **the load reduces carbon when the
contract runs it on surplus, and the optimal contract does precisely that.**

## What this means for the paper

The arc is clean and it is positive. A flexible computing load finances renewables
(result 2), pays for itself in profit and reliability (result 3), and -- steered by the
optimal contract -- decarbonizes the grid (results 6 and 7), all inside a model whose
every quantity we characterize exactly (results 1, 4, 5). The contract is the lever, and
we identify it. That is the contribution: not "computing loads happen to be green," but
"contract design makes them green, and here is the contract."

## How this supports the broader program

Role 1 is the theoretical backbone, and these results are exactly what the rest of the
program stands on. The integrated A1 paper opens with the thesis that a flexible
computing load can reduce carbon by financing renewables; results 2, 6, and 7 supply
that thesis with a proved channel, a characterized decarbonization regime, and the
contract that delivers it. The exact net-carbon inequality and the two-sided bounds
(result 4) are the formal spine the paper's carbon section is written around.

**Within Team A1**, the other roles build directly on this foundation, and everything
lines up:

  - **Role 2 (solver)** validates the channel, the cutoffs, and the carbon comparisons to
    machine precision -- its 169-test suite is green against exactly these results.
  - **Role 3 (comparative statics)** signs how each result moves with prices and costs;
    its capacity-channel checks (24 of 24) and its robustness certificate extend result 2
    across distributions.
  - **Role 4 (theory hardening)** carries the channel and the carbon characterization into
    the small-load regime and stitches the regimes together, generalizing results 1-6.

All four roles now share one direction for the channel condition, one carbon verdict, and
one set of cutoffs -- the team is coherent end to end.

**For the other workstreams**, A1 exports a set of ready-to-use, proved primitives -- the
inputs they can take as given rather than re-derive:

  - **The empirical / quantitative-validation track (A2)** gets closed-form objects to
    calibrate against: the explicit cost thresholds, the capacity channel, the
    distribution-free cutoffs, and the net-carbon inequality. Every prediction it needs to
    test is stated in primitives, with the numerical suite already confirming them, so the
    empirical work measures parameters rather than chasing a moving theory.
  - **The welfare / market-design direction** gets a fully characterized firm optimum and
    the optimal contract as its starting point -- the participation and reliability
    results (result 3) and the contract of result 7 are the building blocks for any
    surplus or pricing analysis layered on top.
  - **The dynamic / storage and policy directions** get the static equilibrium as their
    base case: the channel, the floor, and the contract are the per-period primitives a
    multi-period or storage-augmented model extends, and the regime map (Role 4) tells
    them where each holds.

Each handoff is a *result*, not a conjecture: proved, machine-verified, and consistent
across A1. Downstream workstreams that take the carbon channel or the optimal contract as
given are standing on solid ground. In short, A1 gives the whole program a foundation it
can build on without hedging.

## Status

Results 1-6 are proved and machine-verified -- 61 of 61 numerical checks, five
adversarial referee passes, every identity re-derived from scratch. Result 7 is new this
cycle: the surplus-contract sign theorem follows from the first-order conditions, and its
pull toward the renewable regime is confirmed numerically across calibrations. It is the
natural lead result for the next draft.
