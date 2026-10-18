# Role 4 derivations: miner-side theory and demand-response inducement

Team A1, Role 4. Built against `Bitcoin_Mining_for_Carbon_Emission_Reduction.txt`
(Li, Ren, Bellos; the authored Feb 28 2026 draft). Every result below is
also checked numerically in `miner_demand/` + `tests/`: the test name that
guards each is noted in brackets.

Notation follows the paper: `R` total dollar block reward in a period, `n`
in-grid miners, `P` price charged to in-grid miners, `d = Σ_i d_i` aggregate
in-grid mining demand, `m` out-of-grid miners at price `Po`.

---

## Lemma 1 (equilibrium mining demand, Task 1 / eqs 9-10)

**Claim.** With `n ≥ 2` symmetric miners each solving eq. (9),
`max_{d_i} R d_i/(d_i + Σ_{j≠i} d_j) − d_i P`, the unique interior Nash
equilibrium has aggregate demand

> **d = (1 − 1/n) · R / P.**   (eq. 10)

**Proof.** Write `D = Σ_j d_j`. Miner *i*'s payoff is `R d_i/D − d_i P`.
Its derivative in `d_i` (holding rivals fixed, so `∂D/∂d_i = 1`) is
`R (D − d_i)/D² − P`. The second derivative is `−2R(D − d_i)/D³ < 0` for
`d_i < D`, so the payoff is strictly concave and the first-order condition
is necessary and sufficient:

> `R (D − d_i)/D² = P.`   (the eq. between (9) and (10))

By symmetry `d_i = d/n` and `D = d`, so `D − d_i = d(1 − 1/n)`. Substituting,
`R d(1 − 1/n)/d² = P`, i.e. `R(1 − 1/n)/d = P`, giving `d = (1 − 1/n)R/P`. ∎

**Corollary 1a (inducement).** The map `P ↦ d` is a continuous, strictly
decreasing bijection from `(0, ∞)` onto `(0, ∞)`. Hence for any target
`d* > 0` the regulator implements it with the unique price
`P* = (1 − 1/n) R / d*`. This is the paper's "reverse-engineer the price to
produce any pattern of mining demand."
[`test_oligopoly.py::test_inducement_is_a_bijection`,
`::test_closed_form_matches_best_response_iteration`]

**Corollary 1b (participation).** In equilibrium each miner earns
`R/n − P d_i = R/n − (1−1/n)R/n = R/n² ≥ 0`, independent of `P`. So no price
in `(0, ∞)` drives a miner out, and the inducement of Cor. 1a is
unconstrained by participation.
[`test_oligopoly.py::test_participation_profit_nonnegative_and_price_free`]

---

## Proposition 2 (revenue exogeneity ⇒ duality, Task 2)

**Claim.** Utility revenue from miners is the constant

> **P · d = (1 − 1/n) · R,**

independent of `P` and of every utility decision (`k`, generation mix).
Consequently the revenue term in the utility's profit problem (eq. 6) is a
constant and profit-maximization collapses to the cost-minimization problem
of Section 3.5.

**Proof.** Multiply eq. (10) by `P`: `P d = (1 − 1/n)R`. `R` is fixed by
Bitcoin's protocol and price (the `ξ` of eqs 6-7), and `n` is market
structure; neither responds to the utility's choices, and `P` has cancelled.
Substituting a constant into the `argmax` over `k` leaves the maximizer
unchanged, so only the cost terms remain, the Section 3.5 problem. ∎

**Where it breaks (the boundary, as the plan asks).**
1. *Grid large enough to move the global game*: if the focal grid's price
   shifts total hashrate or the Bitcoin price, `R` is no longer exogenous to
   `P` and the cancellation fails. Exogeneity is a small-open-grid assumption.
2. *Mobile miners*: Proposition 3 below: once miners can leave for `Po`,
   `P d` is no longer constant.
3. *Endogenous entry*: if `n` responds to `P`, the `(1 − 1/n)` factor moves.
[`test_exogeneity.py` (all three tests)]

---

## Proposition 3 (partial grid, Task 3 / Appendix A eqs 61-68)

**Setup.** `n` in-grid miners pay `P`, `m` out-of-grid miners pay `Po`, all
`n + m` split the same `R` (eqs 61-62).

**Claim (eq. 68).** In-grid aggregate demand is

> **d = n (m + n − 1) R · [m Po − (m − 1) P] / (n P + m Po)².**

**Proof.** Summing all `n + m` FOCs gives `Σ_{M∪N} d_j = (m+n−1)R/(nP+mPo)`
(eq. 65; call it `T`). Summing only the `n` in-grid FOCs gives
`R[(n−1)Σ_N + nΣ_M]/T² = nP` (eq. 66). Write `Σ_M = T − Σ_N`, so the bracket
is `nT − Σ_N`; then `R(nT − Σ_N)/T² = nP` gives
`Σ_N = nT(1 − PT/R)`. Since `PT/R = P(m+n−1)/(nP+mPo)`,
`1 − PT/R = [mPo − (m−1)P]/(nP+mPo)`, and substituting `T` yields the claim. ∎
[`test_partial_grid.py::test_eq68_matches_two_price_best_response`,
`::test_total_demand_eq65`]

**Corollary 3a (small-grid limit, `m ≫ n`, `Po` fixed).**
`d → (nR/Po)(1 − P/Po)` and `P d → nR (P/Po)(1 − P/Po)`.
[`::test_small_grid_limit_is_approached`]

**Corollary 3b (exogeneity breaks).** `P d` in Cor. 3a is a concave parabola
in `P`, **not** a constant. It is maximized at `P = Po/2` with value
`nR/4`. Hence:
- the duality of Prop. 2 fails: profit-max ≠ cost-min in the partial grid;
- demand is non-negative iff `P ≤ Po` (else miners leave);
- the largest inducible demand is `nR/Po` (at `P → 0`), but a profit-seeking
  grid never sets `P < Po/2`, so **usable** inducement is capped at
  `d = nR/(2Po)`. This is exactly the clip in the adapted demand-response
  program eq. (69).
[`::test_revenue_peak_is_nR_over_4_at_Po_over_2`,
`::test_demand_nonnegative_iff_price_below_Po`, `::test_inducement_bounds`,
`::test_revenue_exogeneity_BREAKS_in_partial_grid`]

**Remark (a small correction to flag).** The paper says `P d` is
"approximately exogenous if `P` is not too far from `Po`." Numerically this
holds only loosely near the revenue peak `Po/2`; as `P → Po` the in-grid
demand collapses, so `P d` is in fact steeply varying in that tail. The
"approximately exogenous" reading is safe around `Po/2`, not near `Po`
itself. Worth confirming with the authors.

---

## Proposition 4 (emissions under the adapted program: probe, for Role 1 sync)

Under the uniform case (Section 3.6.2) with the adapted program eq. (69) and
shortfall floor `d_floor`, fossil output is
`fossil(D,S,k) = max(D − Sk, 0) + d_floor·1{Sk < D}` (surplus mining draws
only renewables; the floor adds fossil-fed mining when short). A cost-
minimizing utility picks `k` to minimize `c·E[fossil] + C·k`.

**Numerical finding.** Across 756 parameter cells, emissions under the
adapted program never fall below the no-mining benchmark. The reason is
Prop. 3: in the partial grid the surplus-absorbing channel is *bounded*
(`≤ nR/(2Po)`), so it cannot do the heavy lifting, while the only other
lever, the fossil-fed floor, adds emissions directly and only weakly
induces extra renewable capacity. **This does not contradict the paper:** the
paper's Appendix-A reduction is derived from the grid's *profit* problem
(eq. 70), not cost-minimization, precisely because Prop. 3 says cost-min is
no longer valid here. So the faithful emissions test must couple this
miner-side result to Role 1's regulator/profit optimization. Flagging for
sync.
[`test_emissions.py`, `run_sims.py` sweep → `emissions_sweep.csv`]
