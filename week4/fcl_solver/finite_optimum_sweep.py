"""
Week 2 Task 2 (keystone) + Task 4: a single sweep over (C_R, lognormal
shape sigma) that serves both tasks at once, because they ask about the
same three checks from finite_optimum.find_finite_interior_optimum from
two different angles:

  - Task 2 asks: at points where a genuine finite interior optimum EXISTS,
    does carbon fall?
  - Task 4 asks: across the admitted distribution class, WHERE does that
    existence (in particular, Hessian negative-definiteness) fail?

Outcome categories (mutually exclusive):
  "runaway"          -- no finite optimum at all (Week 1's failure mode;
                         see finite_optimum.py's module docstring: this
                         persists under the lognormal-primitive family too
                         for small enough C_R -- it is not distribution-
                         specific, it is a property of the cost structure).
  "corner_zero"       -- collapsed to a zero-capacity corner (C_R too high).
  "optimizer_stalled"  -- the solver settled somewhere with a non-vanishing
                         gradient at the largest bound scale tried -- a
                         numerical (optimizer) issue, reported separately
                         from the two genuine mathematical categories below
                         so it doesn't get conflated with either.
  "saddle"            -- a genuine stationary point (gradient ~0) whose
                         Hessian is NOT negative definite -- Task 4's
                         target category: the model has a finite critical
                         point here, but it is not a maximum.
  "genuine_optimum"   -- finite, interior, regular: Task 2's target
                         category, where the carbon question is well-posed.

Separately, PowerResidual(alpha<1) crossing K_M>K_R is a DIFFERENT,
sharper irregularity than "saddle": the Hessian's K_R-direction second
derivative is not even a finite number there (dF/dK_R diverges at the
support edge -- see distributions.py's PowerResidual docstring and
tests/test_hessian.py's NOTE). That case is documented and tested
separately (test_hessian.py) rather than swept numerically here, since
"the Hessian does not exist" cannot be detected by evaluating it.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from .distributions import ResidualDemand, lognormal_primitive
from .finite_optimum import FiniteOptimumResult, find_finite_interior_optimum
from .model import Params


@dataclass
class SweepCell:
    CR: float
    sigma: float
    outcome: str
    regime: str | None = None  # "small" (K_M<=K_R) or "large" (K_M>K_R), if found
    shift_ratio_condition: bool | None = None
    KR_increased: bool | None = None
    carbon_lower: bool | None = None
    carbon_change: float | None = None
    grad_norm: float | None = None
    min_eigenvalue: float | None = None


def classify(dist: ResidualDemand, params: Params, **kwargs) -> tuple[str, FiniteOptimumResult]:
    """Map find_finite_interior_optimum's free-text `reason` onto one of
    the five mutually-exclusive outcome categories documented above."""
    result = find_finite_interior_optimum(dist, params, **kwargs)
    if result.found:
        return "genuine_optimum", result
    if "no finite optimum" in result.reason:
        return "runaway", result
    if "corner" in result.reason:
        return "corner_zero", result
    if "Hessian not negative definite" in result.reason:
        return "saddle", result
    if "gradient did not vanish" in result.reason:
        return "optimizer_stalled", result
    return "unknown:" + result.reason, result


def run_sweep(
    CR_values=None,
    sigma_values=None,
    R=109.0, c=45.0, CF=10.0, CM=56.0, beta=190.0, p=10.0, D_bar=100.0,
) -> list[SweepCell]:
    """Sweep (C_R, sigma) classifying the outcome at each grid point, for
    the lognormal-primitive family at the given (R,c,CF,CM,beta,p,D_bar).
    """
    if CR_values is None:
        CR_values = np.arange(8.0, 45.0, 1.0)
    if sigma_values is None:
        sigma_values = [0.2, 0.28, 0.4, 0.6]

    cells = []
    for sigma in sigma_values:
        dist = lognormal_primitive(D_bar=D_bar, sigma=sigma)
        for CR in CR_values:
            params = Params(R=R, c=c, CF=CF, CR=float(CR), CM=CM, beta=beta, p=p, D_bar=D_bar)
            try:
                params.check_assumption1()
            except AssertionError:
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                outcome, result = classify(dist, params)
            cell = SweepCell(CR=float(CR), sigma=sigma, outcome=outcome, grad_norm=result.grad_norm)
            if result.found:
                cell.regime = "large" if result.with_fcl.K_M > result.with_fcl.K_R else "small"
                cell.shift_ratio_condition = result.shift_ratio_condition_holds
                cell.KR_increased = result.KR_increased
                cell.carbon_lower = result.carbon_lower
                cell.carbon_change = result.carbon_change
            if result.certificate is not None:
                cell.min_eigenvalue = float(np.min(result.certificate.eigenvalues))
            cells.append(cell)
    return cells


def summarize(cells: list[SweepCell]) -> str:
    n = len(cells)
    by_outcome: dict[str, int] = {}
    for cell in cells:
        by_outcome[cell.outcome] = by_outcome.get(cell.outcome, 0) + 1

    genuine = [c for c in cells if c.outcome == "genuine_optimum"]
    n_carbon_lower = sum(1 for c in genuine if c.carbon_lower)

    lines = [f"Swept {n} (C_R, sigma) cells."]
    for outcome, count in sorted(by_outcome.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {outcome}: {count}/{n} ({100*count/n:.0f}%)")
    lines.append(
        f"Among {len(genuine)} genuine (finite, regular, interior) optima found: "
        f"carbon_lower in {n_carbon_lower}/{len(genuine)}."
    )
    if genuine and n_carbon_lower == 0:
        lines.append(
            "  Carbon NEVER fell at a genuine finite interior optimum in this sweep -- "
            "the Week 1 finding survives the move to a well-posed optimum (Week 2's reframe)."
        )
    return "\n".join(lines)
