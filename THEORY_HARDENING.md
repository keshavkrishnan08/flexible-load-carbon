# Theory Hardening and Regimes: Role 4 (Team A1)

Against the **FCL paper** (`FCL_Carbon_Paper.txt`, §3-4, Appendix B.1, Appendix
G). This document is organized by the four bullets of the Role 4 task. Each
analytical claim is backed by a check in `tests/` (run `pytest tests/ -q`, 17
passing) and, where it's a comparison, by Role 2's solver, vendored unchanged
in `role4/fcl_backend/`. Notation: residual demand `x = D − K_R·S`; capacities
`K_R` renewable, `K_F` fossil, `K_M` flexible computing load; `R, c, p, β` and
capital costs `C_R, C_F, C_M`.

---

## Bullet 1: Re-verify the core proofs (eqs 12, 13, 15; Prop 1 / App. B.1)

**The three FOCs**, re-derived from the interior-regime profit (eq. 10) by
Leibniz differentiation (`role4/foc.py`):

- **eq (12), `∂Π/∂K_M = 0`:** `F(K_F*−K_M*;K_R*) = C_M/(R−c)`. The RHS lies in
  `(0,1)` precisely under A1 (`R>c+C_M`), so a cutoff exists.
- **eq (13), `∂Π/∂K_F = 0`:** `F(K_F*;K_R*) = (β+p−c−C_F−C_M)/(β+p−R)`. RHS in
  `(0,1)` under A2 and A4; gives blackout prob `1−F* = (c+C_F+C_M−R)/(β+p−R)`
  (eq 14).
- **eq (15), `∂Π/∂K_R = 0`:** the marginal value of renewables weights the FCL
  dispatch band `(K_F−K_M, K_F)` by `R` and the rest by `c`; since `R>c`, this
  is the capacity-substitution force that pushes `K_R* > K_R°`.

All three cutoffs match Role 2's solver to ≤1e-3 (`tests/test_foc.py`:
`F(K_F*−K_M*)=0.300`, `F(K_F*)=0.700` at the worked params).

**Proposition 1, three steps** (`role4/proposition1.py`):

- **Step 1 (profit, distribution-free).** Revealed preference gives `Π* ≥ Π°`;
  strict iff `K_M*>0`. The marginal profit of the first FCL unit at the no-FCL
  optimum is `(R−c)φ° − C_M = C̄_M − C_M`, positive **iff `C_M < C̄_M`**.
  Verified: analytic sign matches the solver's `Π*>Π°`.
- **Step 2 (blackout, distribution-free).** `(1−F*)−(1−F°)` has numerator
  `C_M(β+p−c) − (R−c)(β+p−c−C_F)`, negative **iff `C_M < C̄_M`**. Verified
  against the solver's blackout probabilities.
- **Step 3 (carbon).** `E[fossil with FCL]` (eq 42) vs `E[fossil without]`
  (eq 43). The **utilization effect** raises fossil in every state (verified
  positive, distribution-free); the **capacity-substitution effect**
  (`K_R*>K_R°`) lowers it.

**GAP FLAGGED.** Step 3's *net* sign is established in Appendix B.1 only for the
uniform (and, via footnote 6, power-law) family, through eqs 25-26. For a
general `F`, B.1 *asserts* the capacity channel dominates "when `C_R` is
sufficiently small" but does not prove it, the carbon part of the triple win
is the conditional "may." Two things close it: (a) Role 1's shift-ratio
condition `g(x)=F_{K_R}/f` non-increasing makes `K_R*≥K_R°` general; (b) Role
4's Bullet-3 analysis shows the dominance only bites once buildout passes the
crossover `K_R^cross` (below it the utilization effect wins, see the
reconciliation). Steps 1-2 are airtight and general; Step 3 is not, by design.

---

## Bullet 2: Complete the small-FCL regime (Appendix G) and confirm eq (62)

In the small-FCL regime `K_M < K_R`, so `−K_M` sits inside the support and the
eq-(10) integration-by-parts simplification is unavailable; profit is the
eq-(60) form (`role4/small_fcl.py`). The `K_M` FOC gains a surplus-hour term
relative to eq (12):

> **eq (61):** `(R−c)F(K_F−K_M;K_R) + c·F(−K_M;K_R) = C_M`.

The extra `c·F(−K_M;K_R) > 0` is the marginal *pure-renewable-surplus* hour: in
states `x ≤ −K_M` no fossil runs, so the marginal FCL unit earns the full `R`,
not the `R−c` fossil-dispatch margin. Evaluating the first FCL unit at the
no-FCL optimum (`K_M→0 < K_R°`, necessarily small-FCL) gives the **wider
adoption threshold**:

> **eq (62):** `C̄_M^b = (R−c)φ° + c·F(0;K_R°) = C̄_M + c·q° > C̄_M`,

with `q° = F(0;K_R°)` the no-FCL surplus probability. **Confirmed**
(`tests/test_small_fcl.py`): `C̄_M^b > C̄_M`, the widening equals `c·q°` exactly,
and the eq-61 marginal value exceeds the large-FCL one by precisely that
surplus term. So on `(C̄_M, C̄_M^b)` the large-FCL analysis says "no adoption"
but a small-FCL program is still strictly worth running. Worked instance:
`C̄_M = 0.500 → C̄_M^b = 0.793` (widened by `c·q° = 0.293`).

---

## Bullet 3: Reconcile the regime boundaries (one consistent statement)

Two axes, stitched in `role4/regimes.py::unified_statement`.

**Coverage axis (in `C_M`), strictly ordered** (`thresholds_ordered`, verified):

> `C_M^fc = R−c−C_F  <  C̄_M = (R−c)φ°  <  C̄_M^b = C̄_M + c·q°`.

- `C_M ≤ C_M^fc` ⇔ the **p25 digression** `R ≥ c+C_F+C_M`: marginal value of
  fossil is `≥0` even at `K_F=D̄`, so the utility builds `≥ D̄` fossil and
  blackout prob is 0, the **full-coverage** regime (degenerate but favorable;
  adoption `C_M < C̄_M` is automatic since `C_M ≤ R−c−C_F < C̄_M`).
- `C_M^fc < C_M < C̄_M`: **interior / large-FCL** (the paper's main regime).
- `C̄_M ≤ C_M < C̄_M^b`: **small-FCL adoption** (Bullet 2).
- `C_M ≥ C̄_M^b`: **no adoption**.

**Boundedness axis (in `C_R`)**: the hardening that reconciles Role 1 vs Role 2
(next section): `C_R° = C_F²/(2(β+p−c))` (no-FCL bound) and
`C_R† = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]` (with-FCL bound),
with `C_R° < C_R†`. The with-FCL program is finite iff `C_R ≥ C_R†`; on
`C_R° ≤ C_R < C_R†` it is unbounded.

These compose into one statement: a parameter point has a coverage label *and*
a boundedness label, and `unified_statement` returns both consistently.

---

## Bullet 4: Pressure-test Assumption 1

For each of the four conditions: the object it guards, and what breaks if
relaxed (`role4/assumption1.py`, all verified in `tests/test_assumption1.py` by
nudging each parameter just past its boundary and watching the guarded quantity
leave its valid range).

| Cond | Statement | Guards | If relaxed |
|---|---|---|---|
| **A1** | `R > c + C_M` | eq-12 RHS `C_M/(R−c) < 1` ⇒ interior `K_M` exists | `≥1`: no FCL adoption ever (paper's own fallback) |
| **A2** | `R < c + C_F + C_M` | eq-13 RHS in `(0,1)` ⇒ interior `K_F ∈ (0,D̄)` | full-coverage corner (`K_F≥D̄`, blackout 0); strict ⇒ infinite fossil ("dedicated provider", out of scope) |
| **A3** | `β+p > c + C_F` | `φ° = (β+p−c−C_F)/(β+p−c) > 0` ⇒ fossil backup built | `φ°≤0`: no backup, grid tolerates blackouts |
| **A4** | `β+p > R` | eq-13 denominator `β+p−R > 0` ⇒ `F*∈(0,1)` | denom `≤0`: `F*` ill-defined; utility curtails users to serve FCL (perverse) |

So A1, A3, A4 are genuinely *necessary* (relaxing any one breaks an interior
optimum or flips an economic sign), while A2 is necessary only for the
*interior* regime, relaxing it lands in the well-defined full-coverage regime,
not a contradiction. That asymmetry is the precise content of the pressure
test, and it lines up with the p25 digression.

---

## The Role 1 ↔ Role 2 reconciliation (cross-cutting Bullets 1 & 3)

Keshav's theory (carbon falls) and Dhruv's numerics (carbon never falls; the
model wants infinite capacity) **do not conflict**. On the carbon-reduction
window `C_R° ≤ C_R < C_R†` the with-FCL program is *unbounded* in `K_R`
(`profile slope = C_R† − C_R > 0`; `eq24_constant = 2(C_R†−C_R)`, matched to
Role 2's own constant). Carbon only drops below the no-FCL benchmark once
buildout passes a crossover `K_R^cross` (≈ 4× the no-FCL scale in the worked
case): below it the utilization effect dominates (Dhruv's 0/210); above it the
capacity-substitution channel does (Keshav). `role4/reconcile.py` and
`reconciliation.png` show carbon rising then falling while profit rises without
bound. **Hardened takeaway:** Assumption 1 alone does not guarantee a finite
optimum, it needs `C_R ≥ C_R†`; the unboundedness is a corner-at-infinity, not
a local-curvature failure (the local Hessian stays negative-definite).

---

## Single open finishing item

The exact closed form for the small-FCL boundary `K*_M = K°_R` under a *general*
`F` (Role 1's residual) is located numerically here but not forced into a
general closed form, flagged, not asserted.
