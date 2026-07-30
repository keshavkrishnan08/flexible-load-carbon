"""
Week 2 Task 4: map where the analytic Hessian's negative-definiteness
certificate (hessian.certify_negative_definite) holds versus fails, within
the class of residual-demand distributions admitted by this solver.

Two structurally DIFFERENT kinds of irregularity are documented and
tested here, deliberately kept separate because they are not the same
mathematical phenomenon:

1. DIVERGENCE (this file, PowerResidual(alpha<1)): dF/dK_R itself grows
   without bound approaching the support edge x=-K_R from inside, whenever
   alpha<1. The Hessian's H_RR entry is then not a finite number AT ALL
   once an integration range crosses that edge (K_R < K_M < K_F+K_R, the
   paper's "large-FCL" regime) -- there is no "negative definite or not"
   question to ask; the object doesn't exist. This is detected by checking
   the relevant boundary value GROWS without bound as the step shrinks,
   not by evaluating the Hessian (which would just silently return a
   large-but-finite floating-point number at any fixed step).

2. INDEFINITENESS (run_finite_optimum_sweep.py / test_finite_interior_optimum.py,
   lognormal-primitive family): the Hessian IS a finite, well-defined
   number, but at some (C_R, sigma) combinations the located stationary
   point's Hessian eigenvalues are not all negative -- a genuine saddle,
   not a maximum. See finite_optimum_sweep.py's "saddle" outcome category
   and finite_optimum_sweep_results.csv for the swept map. (a) is checked
   directly below; (b) is reported from the sweep's own results table
   rather than re-run here, since the full sweep is the expensive part.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from fcl_solver.distributions import PowerResidual, UniformResidual


@pytest.mark.parametrize("alpha", [0.3, 0.5, 0.8, 0.99])
def test_power_residual_FKR_diverges_at_edge_when_alpha_below_one(alpha):
    """dist.dcdf_dKR(-K_R+eps, K_R) must grow without bound as eps -> 0+
    whenever alpha<1 -- this is the mathematical fact behind why H_RR is
    undefined for these distributions once an integration range crosses
    x=-K_R (see hessian.py's docstring / README.md). Checked by confirming
    the value keeps increasing as eps shrinks across several orders of
    magnitude, not by asserting a specific numeric limit (there is none --
    the limit is +infinity).
    """
    dist = PowerResidual(D_bar=100, alpha=alpha)
    K_R = 15.0
    eps_values = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10]  # descending eps, factor of 100 apart
    values = [float(dist.dcdf_dKR(-K_R + eps, K_R)) for eps in eps_values]

    assert values == sorted(values), "value should keep GROWING as eps shrinks (ascending as eps descends)"
    # Precise check, not just "some growth": near the edge, dF/dK_R ~ u^(alpha-1)
    # with u=(x+K_R)/(D_bar+K_R) -> 0 linearly in eps, so a 100x reduction in
    # eps should grow the value by exactly 100^(1-alpha) (e.g. ~3.16x for
    # alpha=0.5, but only ~1.047x for alpha=0.99 -- still genuine divergence,
    # just a slow power law, which is why a fixed ">1.5x" threshold is wrong
    # for alpha close to 1 and this checks the actual predicted rate instead).
    expected_ratio = 100.0 ** (1.0 - alpha)
    ratios = [values[i + 1] / values[i] for i in range(len(values) - 1)]
    for r in ratios:
        assert r == pytest.approx(expected_ratio, rel=0.05), f"ratio {r} != predicted {expected_ratio}"


@pytest.mark.parametrize("alpha", [1.0, 1.5, 2.0, 5.0])
def test_power_residual_FKR_is_bounded_at_edge_when_alpha_at_or_above_one(alpha):
    """The contrasting, REGULAR case: alpha>=1 keeps dF/dK_R finite (alpha=1,
    i.e. Uniform) or drives it to exactly 0 (alpha>1) at the support edge --
    in both cases H_RR is a well-defined finite number there, and the
    Leibniz boundary-correction machinery in hessian.py applies cleanly
    (adding a finite, possibly-zero, correction term)."""
    dist = PowerResidual(D_bar=100, alpha=alpha)
    K_R = 15.0
    eps_values = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10]
    values = [dist.dcdf_dKR(-K_R + eps, K_R) for eps in eps_values]

    assert all(np.isfinite(v) for v in values)
    assert max(values) < 1e6, "should stay bounded, unlike the alpha<1 case"


def test_uniform_is_the_regular_boundary_case():
    """Uniform (=PowerResidual(alpha=1)) sits exactly at the regularity
    boundary in alpha: dF/dK_R jumps to a finite nonzero constant
    (1/(D_bar+K_R)) at the edge, rather than diverging (alpha<1) or
    vanishing (alpha>1). This is the case hessian.py's Leibniz boundary
    term was originally derived against (see test_hessian.py)."""
    dist = UniformResidual(D_bar=100)
    K_R = 15.0
    val = dist.dcdf_dKR(-K_R + 1e-9, K_R)
    assert val == pytest.approx(1.0 / (100.0 + K_R), rel=1e-6)


def test_regularity_classification_across_alpha_grid():
    """A small map (Task 4's "numerical map" deliverable, the
    closed-form-distribution half of it -- see
    finite_optimum_sweep_results.csv for the lognormal-primitive half):
    for each alpha, classify whether crossing into the large-FCL regime
    (K_M>K_R, so an integration range straddles x=-K_R) is regular or
    divergent, purely from the sign of (alpha-1)."""
    results = {}
    for alpha in [0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 3.0]:
        dist = PowerResidual(D_bar=100, alpha=alpha)
        K_R = 15.0
        v_loose, v_tight = dist.dcdf_dKR(-K_R + 1e-4, K_R), dist.dcdf_dKR(-K_R + 1e-9, K_R)
        diverges = v_tight > 10 * v_loose and v_tight > 1.0
        results[alpha] = "divergent" if diverges else "regular"

    assert results[0.2] == "divergent"
    assert results[0.5] == "divergent"
    assert results[0.8] == "divergent"
    assert results[1.0] == "regular"
    assert results[1.2] == "regular"
    assert results[1.5] == "regular"
    assert results[3.0] == "regular"
    # the boundary is exactly alpha=1 (Uniform) -- matches
    # PowerResidual's own docstring (footnote 6 of the paper: alpha<1 is
    # "right-skewed", more mass in deep surplus, alpha>1 "left-skewed").
