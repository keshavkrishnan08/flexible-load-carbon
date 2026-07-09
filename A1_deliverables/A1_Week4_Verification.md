# A1 Week 4 — Verification Evidence (all green)

Fresh verification run of every Week-4 deliverable. All checks pass.

## Role 1 — the carbon classification theorem  (`role1/verify_week4.py`)
Fresh run, **13/13 PASS** on the load-bearing checks:

- `Φ = Δ` and `sign(Δ) = sign(Φ)` in **every** distribution-library family (symmetric, left-skew, right-skew, mild-skew) — the classification identity, to ~1e-9 machine precision.
- `∂Φ/∂μ*_low < 0` and `∂Φ/∂μ°_mid > 0` (both means load-bearing).
- Each mean **alone** flips `sign(Φ)` at the representative optimum (`Φ∈[−3.33,+0.40]` and `[−5.27,+0.49]`).
- The per-mean **sharp iff**: `D_ℓ ⟺ (μ*_low sweep flips)` and `D_m ⟺ (μ°_mid sweep flips)`, both exact.
- Condition M (leverage bound): `K_R` non-increasing (const 9.90), `K_F` non-decreasing (3.40→5.28), `Λ(τ) < 0` throughout.
- Condition S (carbon boundary): `Φ(C_R)` monotone single-crossing (`+1.90 → −2.50`).

## Role 4 — the classification functional across regimes  (`role4/week4_regime_classification.py`)
Fresh run, **8/8 PASS**:

- Threshold ordering `C_M^fc < C̄_M < C̄_M^b` (0.300 < 0.780 < 0.880).
- Adoption widening equals `c·q°` exactly (0.1000).
- Continuity hinge `F(−K_R;K_R) = 0` at the structural boundary.
- `eq61(K_M=K_R) ≡ eq12(K_M=K_R)` — the small-FCL FOC reduces to the large-FCL one (|diff| = 0).
- `K_M*(C_M) → 0` continuously at the adoption edge (0.786 → 0.314 → 0.079 → 0.000) — a kink, no jump.
- Regime-map consistency (`unified_statement`).

## Role 2 — the carbon-functional evaluator  (independent review, `week4/`)
- The keystone functional `Ψ` is **mathematically identical** to Role 1's `Φ = Δ` — same closed form, same conditional-mean domains, same sign convention.
- Numerically self-consistent: `carbon_delta = −c·Ψ` reproduced to ~0.01–2% across uniform / power / lognormal cells.
- The sweep reports **0 sign mismatches** between the closed-form `Ψ` and the solver's direct carbon; corner cells excluded correctly; carbon-falls region is the cheap-renewable corner (consistent with Role 1).

## Role 3 — comparative statics and robustness  (`writeup_week4.tex`)
- Compiles clean (3pp).
- Two independent adversarial passes; every finding remediated. Endpoint inequality `g(a) ≥ g(K_F*)` (correct direction, shift ratio); envelope term `c(1−F(K_F*))·dK_F/dθ`; `dK_F*/dR > 0`; adoption boundary a continuous kink; price-of-robustness monotonicity proved by set inclusion; β sign correctly labeled ambiguous (5/7 distribution-free).

---

**Bottom line.** Every Week-4 deliverable verifies green: Role-1 13/13, Role-4 8/8, Role-2 keystone exact (0 mismatches), Role-3 clean and consistent. `Ψ` (Role 2) = `Φ = Δ` (Role 1); the classification stitches continuously across regimes (Role 4); all four are consistent and pushed.
