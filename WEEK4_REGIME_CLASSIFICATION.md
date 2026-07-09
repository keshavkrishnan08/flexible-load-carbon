# Role 4 — Week 4: The Carbon Classification Functional Across Regimes

Team A1, Role 4 (Theory Hardening and Regimes). This is the Week-4 deliverable:
carry Role 1's carbon-classification functional Φ into the small-FCL regime, prove it
stitches continuously across the regime boundary, and map the classification over the full
cost plane. Verification: `role4/week4_regime_classification.py` (reuses `foc.py`,
`small_fcl.py`, `regimes.py`).

Notation matches Roles 1–2: residual demand `x = D − K_R·S ∈ [−K_R, D̄]`, CDF `F(x;K_R)`,
`F_{K_R} > 0`. Cutoffs `φ° = (β+p−c−C_F)/(β+p−c) = F(K_F°;K_R°)`, `q° = F(0;K_R°)`,
`φ_1 = C_M/(R−c)`, `C̄_M = (R−c)φ°`. Role 1's functional:

> **Φ(F) = (C_M/(R−c))·(a − μ*_low) − [K_F* − K_F°(1−φ°) − (φ°−q°)·μ°_mid]**,
> with `a = K_F*−K_M*`, `μ*_low = E[x | x∈(−K_R*, a)]`, `μ°_mid = E[x | x∈(0, K_F°)]`;
> and **Δ = E[fossil°] − E[fossil*] = Φ**, so **carbon falls ⟺ Φ > 0** (Role 1, Week 4).

Role 1 derived Φ in the **large-FCL** regime, where `K_M ≥ K_R` so the lower dispatch edge
`−K_M ≤ −K_R` sits at or below the support and `F(−K_M) = 0` (the integration-by-parts
simplification of eq. 10). Role 4's job: the **small-FCL** regime `K_M < K_R`, where `−K_M`
is interior, `F(−K_M) > 0`, and that simplification is unavailable.

---

## 1. Φ is regime-agnostic as an identity

**Proposition 1.** In *both* regimes, `Δ = E[fossil°] − E[fossil*]` and Φ is that difference
written on the equilibrium capacities and the two conditional means. The identity `Δ = Φ`
holds in each regime by construction (it is the definition of Φ rearranged). What differs
between regimes is only the *equilibrium map* — how `(K_R*, K_F*, K_M*)` and the conditional
means are pinned by the FOCs — not the algebra `Δ = Φ`.

*Consequence.* Any regime dependence of the carbon sign enters through the equilibrium
values that feed Φ, never through a change of formula. So to stitch the classification it
suffices to stitch the equilibrium map — which is what §2–§3 do.

---

## 2. The equilibrium map stitches: continuity at the structural boundary K_M = K_R

The large-FCL `K_M` FOC (eq. 12) and the small-FCL one (eq. 61) are

- large-FCL: `(R−c)·F(K_F−K_M; K_R) = C_M`,
- small-FCL: `(R−c)·F(K_F−K_M; K_R) + c·F(−K_M; K_R) = C_M`.

The only difference is the **surplus-hour term** `c·F(−K_M; K_R)`: in states `x ≤ −K_M` no
fossil runs, so the marginal FCL unit there earns the full `R`, not the `R−c` fossil-dispatch
margin.

**Proposition 2 (exact continuity).** At the structural boundary `K_M = K_R`, we have
`−K_M = −K_R`, the lower edge of the support, so `F(−K_M; K_R) = F(−K_R; K_R) = 0`. The
surplus term vanishes and the small-FCL FOC (eq. 61) reduces *exactly* to the large-FCL FOC
(eq. 12). Hence:

1. the two FOC systems agree at `K_M = K_R`;
2. `K_R*, K_F*, K_M*` are continuous across the boundary (the FOC map is continuous, and it
   is single-valued on each side by the recursive-triangular uniqueness of Week 2);
3. therefore `E[fossil*]`, `Δ`, and **Φ are continuous across `K_M = K_R`** — the carbon
   classification stitches with **no discontinuity**.

This is a *proved* stitch: it rests only on `F(−K_R;K_R)=0`, a support fact, not on any
distributional assumption. The surplus term is `O(F(−K_M))`, which grows continuously from
`0` as the optimum moves into the small-FCL interior — a `C⁰` (indeed one-sided `C¹`) join,
not a jump.

---

## 3. The classification domain widens to C̄_M^b; the adoption edge is a kink

Evaluating the small-FCL marginal FCL value at the no-FCL optimum (`K_M→0 < K_R°`, which is
necessarily small-FCL) gives the **wider adoption threshold** (eq. 62):

> **C̄_M^b = (R−c)φ° + c·F(0;K_R°) = C̄_M + c·q° > C̄_M.**

So the coverage axis is strictly ordered, `C_M^fc < C̄_M < C̄_M^b`, with

- `C_M^fc < C_M < C̄_M`: interior / large-FCL,
- `C̄_M ≤ C_M < C̄_M^b`: **small-FCL adoption** — the large-FCL analysis reports "no adoption"
  here, but the surplus term keeps a small program strictly worth running,
- `C_M ≥ C̄_M^b`: no adoption.

**Proposition 3 (the classification extends continuously to the true adoption edge).** The
domain on which Φ is non-trivial (the load is adopted, `K_M* > 0`) is
`C_M < C̄_M^b`, wider than the large-FCL `C_M < C̄_M`. As `C_M ↑ C̄_M^b`, the small-FCL FOC
forces `K_M* → 0` continuously, so `E[fossil*] → E[fossil°]` and **Δ = Φ → 0** continuously:
the adoption edge is a **kink** in `K_M*(C_M)` (its slope drops to 0), not a jump, and Φ
lands on the neutral level `Φ = 0` there. (This is the small-FCL refinement of the
large-FCL kink at `C̄_M` — the large-FCL branch would zero `K_M` at `C̄_M`, but small-FCL
carries it, positive and shrinking, out to `C̄_M^b`.)

---

## 4. The regime map of the classification

Crossing the coverage axis (§3) with the boundedness axis
`C_R° = C_F²/(2(β+p−c)) < C_R† = ½[c + (R−C_M−c)²/(R−c) + (R−c−C_F−C_M)²/(β+p−R)]`, the
`(C_M, C_R)` plane partitions, and the carbon classification reads off consistently:

| region | coverage | boundedness | carbon (sign Φ) |
|---|---|---|---|
| cheap-renewable corner | any adopted | `C_R° ≤ C_R < C_R†` (unbounded) | **Φ > 0** (carbon falls; `K_R*→∞`, `E[fossil*]→0`) |
| interior large-FCL | `C_M^fc<C_M<C̄_M` | `C_R ≥ C_R†` (bounded) | `Φ < 0` (carbon rises at interior optima — Role 1 Week 2) |
| small-FCL adoption | `C̄_M<C_M<C̄_M^b` | `C_R ≥ C_R†` | `Φ < 0`, `→ 0` at `C̄_M^b` |
| no adoption | `C_M ≥ C̄_M^b` | — | Φ undefined (no load) |

**The carbon-down set `{Φ>0}` is the cheap-renewable corner in *both* FCL regimes** — the
small-FCL extension does not open a new interior carbon-down region; it only widens the
adoption domain over which `Φ < 0` (carbon rises under the naive rule). This is fully
consistent with Role 1 (naive-rule carbon falls only at the corner) and with the Role 1 ↔
Role 2 reconciliation (carbon falls only above the crossover `K_R^cross`, i.e. on the
unbounded ray). The classification and its carbon boundary are **continuous across every
coverage boundary** (§2, §3).

---

## 5. What is proved vs. verified, and the open item

- **Proved:** Φ is regime-agnostic as an identity (Prop 1); the equilibrium map and hence Φ
  are continuous across the structural boundary `K_M=K_R`, because the surplus term
  `c·F(−K_R;K_R)=0` there (Prop 2); the classification domain widens to `C̄_M^b` and Φ→0
  continuously at the adoption edge (Prop 3, on the uniform/scale families where the FOCs
  are closed-form).
- **Verified numerically** (`week4_regime_classification.py`): the threshold ordering
  `C_M^fc<C̄_M<C̄_M^b`; the widening equals `c·q°` exactly; `F(−K_R;K_R)=0` (the continuity
  hinge); `K_M*(C_M)` continuous and `→0` at `C̄_M^b`; and `sign(Δ)=sign(Φ)` on both sides
  of the regime boundary.
- **Open (inherited):** the exact closed form for the small-FCL boundary `K_M*=K_R°` under a
  *general* (non-uniform/power) `F` — the single finishing item already flagged in
  `THEORY_HARDENING.md`. Continuity (Prop 2) does not need it; the *rate* of the one-sided
  join under general `F` does.

**Bottom line.** Role 1's classification functional Φ is not a large-FCL artifact: it is the
same object in both regimes, it stitches continuously across the regime boundary (proved via
the vanishing surplus term), and its carbon-down verdict — the cheap-renewable corner — is
regime-invariant. The one thing the small-FCL regime adds is a *wider adoption domain*
(`C̄_M^b > C̄_M`), over which the classification still applies and still reads `Φ < 0`.
