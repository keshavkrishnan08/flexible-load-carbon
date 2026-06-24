# Exploratory — NOT the Role 1 deliverable (candidate handoffs to Role 3 / Role 4)

Per the **A1 Week 1 Plan**, Role 1 is **General Carbon Theory** and is exactly four
tasks: re-derive eqs 25/26, generalize the net carbon-reduction condition, prove
`K*_R > K°_R`, and write the draft + gap memo. The Role 1 deliverable lives in the
parent folder (`role1_carbon_theory.tex`, `gap_memo.md`).

The material **in this folder is out of Role 1 scope.** It was built under a broader
"general contracting theory" framing and overlaps other roles. It is kept here —
labeled, not deleted — as a candidate handoff. **It is not part of Role 1's
deliverable and should not be counted as such.**

| File | What it is | Belongs to |
|---|---|---|
| `role1_contract_theory.tex` | Optimal demand-response contract `d*(x)`: existence / uniqueness / characterization over the full policy space (generalizes paper Lemma 1); principal–agent mechanism. | **Role 4** (Theory Hardening — "re-verify the core proofs"); mechanism design is beyond the Week-1 plan. |
| `role1_robust_contract.tex` | Distributionally robust (least-favorable = uniform) + detail-free (Wilson-doctrine) implementation. | Beyond the Week-1 plan (group-level contracting). |
| `verify_contract.py` | Verifies `d*` optimality (0/21,600 feasible policies beat it). | supports the contract doc |
| `verify_correlation.py` | Carbon sign vs `corr(D,S)` across a joint family — "map the carbon sign across distributions." | **Role 3** (Comparative Statics) |
| `verify_robust.py` | Least-favorable-distribution check. | supports the robust doc |

**Note on the correlation result.** The *theoretical* statement that the carbon
sign is governed by the demand–supply correlation (via the shift ratio
`g = E[S|x̃=x]`) is the interpretation of Role 1's general condition; but the
*numerical mapping of the carbon sign across distributions* is squarely Role 3's
task. The clean Role 1 statement (the general condition itself) stays in the
parent `role1_carbon_theory.tex`; the cross-distribution charting is here for Role 3.

These compile/run standalone; nothing in the Role 1 deliverable depends on them.
