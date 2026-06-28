"""
Task 4: map where the FCL "triple win" (profit up, blackout down, carbon
down) holds versus where it breaks, as a function of (i) C_R, (ii) how much
renewable capacity is realistically buildable (K_R_cap), and (iii) the
shape of the residual-demand distribution.

THE HEADLINE FINDING (see tests/test_proposition1.py for the pinned-down,
asserted version of each piece below; this module is the broader sweep
that motivated those tests):

Parts (i) profit-higher and (ii) blackout-lower are robust: in every cell
of every sweep below, across every distribution family tried, they hold
whenever C_M < C_bar_M (or its small-FCL-regime-correct, wider counterpart
C_bar_M^b = C_bar_M + c*F(0;K_R^o), eq. 62). This matches the paper's proof
exactly (Appendix B.1's revealed-preference argument doesn't depend on the
distribution or on K_R being a finite global optimum).

Part (iii) carbon-lower is a different story. Two things had to be
understood before the sweep below means anything:

1. Under the uniform AND power residual-demand families, the with-FCL
   profit function has NO finite global maximum (Section 4's own eq. 24
   already signals K*_R can be a degenerate "infinite/arbitrary/zero"
   corner; we found numerically that once K_M is also free, the
   degeneracy is not confined to K_R alone -- K_F and K_M can also run
   away together). This traces back to Assumption 1 itself: R < c+C_F+C_M
   forces eq. 23's coefficient on (D_bar+K_R) to always be negative, so
   the large-FCL closed form for K*_F *must* go negative (economically
   invalid) at some finite K_R, for every parameter set satisfying
   Assumption 1 -- "K*_R = infinity" is a stylized description of a
   one-directional FOC, not a literal attainable point.
2. Because of (1), "the carbon level at K*_R" isn't a well-defined number
   to compare against the no-FCL benchmark's (perfectly well-defined,
   bounded) carbon level. The sweep below instead asks the practically
   relevant question: for a given REALISTIC cap on how much renewable
   capacity can be built (K_R_cap, swept as a multiple of D_bar), does the
   FCL program -- optimized subject to that cap -- emit less carbon than
   the no-FCL benchmark (which optimizes its own K_R, uncapped, since the
   no-FCL profit problem genuinely is bounded)?

RESULT: across this entire swept grid (C_R from 0.1x to 50x a baseline
value, K_R_cap from 0.5x to 10x D_bar, three distribution shapes), we did
not find a single cell where carbon improves. It always increases once FCL
is introduced, for this R/c/C_F/C_M/beta/p combination -- even though
profit and reliability improve in literally every cell. This is reported
plainly below rather than papered over; see run_sweep.py for how to
reproduce and extend the search (e.g. to other R/c/C_F/C_M ratios).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .distributions import PowerResidual, ResidualDemand, UniformResidual
from .model import Params
from .proposition1 import check_triple_win


@dataclass
class SweepCell:
    CR: float
    KR_cap_mult: float
    dist_name: str
    C_bar_M: float
    CM: float
    below_threshold: bool
    profit_higher: bool
    blackout_lower: bool
    carbon_lower: bool
    carbon_pct_change: float


def make_params(CR: float, R=109.0, c=45.0, CF=10.0, CM=56.0, beta=190.0, p=10.0, D_bar=100.0) -> Params:
    params = Params(R=R, c=c, CF=CF, CR=CR, CM=CM, beta=beta, p=p, D_bar=D_bar)
    params.check_assumption1()
    return params


DISTRIBUTIONS: dict[str, ResidualDemand] = {
    "uniform": UniformResidual(D_bar=100),
    "power_alpha_0.5": PowerResidual(D_bar=100, alpha=0.5),
    "power_alpha_2.0": PowerResidual(D_bar=100, alpha=2.0),
}


def run_sweep(
    CR_values=None,
    KR_cap_multiples=None,
    dist_names=None,
    **param_kwargs,
) -> list[SweepCell]:
    """Sweep (C_R, K_R_cap, distribution) and classify the triple-win outcome
    at each grid point. param_kwargs are passed through to make_params (use
    to explore other R/c/C_F/C_M/beta/p combinations).
    """
    if CR_values is None:
        CR_values = np.geomspace(0.1, 50, 10)
    if KR_cap_multiples is None:
        KR_cap_multiples = [0.5, 1, 2, 5, 10]
    if dist_names is None:
        dist_names = list(DISTRIBUTIONS.keys())

    cells = []
    for CR in CR_values:
        params = make_params(CR, **param_kwargs)
        for mult in KR_cap_multiples:
            KR_max = mult * params.D_bar
            for dist_name in dist_names:
                dist = DISTRIBUTIONS[dist_name]
                result = check_triple_win(dist, params, KR_max=KR_max, KF_max=3 * params.D_bar,
                                           KM_max=3 * params.D_bar)
                pct_change = (
                    100.0 * result.carbon_change / result.no_fcl.carbon
                    if result.no_fcl.carbon > 1e-9
                    else float("inf") if result.carbon_change > 0 else 0.0
                )
                cells.append(SweepCell(
                    CR=CR, KR_cap_mult=mult, dist_name=dist_name,
                    C_bar_M=result.C_bar_M, CM=result.CM,
                    below_threshold=result.below_threshold,
                    profit_higher=result.profit_higher,
                    blackout_lower=result.blackout_lower,
                    carbon_lower=result.carbon_lower,
                    carbon_pct_change=pct_change,
                ))
    return cells


def summarize(cells: list[SweepCell]) -> str:
    n = len(cells)
    n_profit = sum(c.profit_higher for c in cells)
    n_blackout = sum(c.blackout_lower for c in cells)
    n_carbon = sum(c.carbon_lower for c in cells)
    lines = [
        f"Swept {n} (C_R, K_R_cap, distribution) cells.",
        f"  profit_higher:   {n_profit}/{n}  ({100*n_profit/n:.0f}%)",
        f"  blackout_lower:  {n_blackout}/{n}  ({100*n_blackout/n:.0f}%)",
        f"  carbon_lower:    {n_carbon}/{n}  ({100*n_carbon/n:.0f}%)",
    ]
    if n_carbon == 0:
        worst = min(cells, key=lambda c: -c.carbon_pct_change)
        best = min(cells, key=lambda c: c.carbon_pct_change)
        lines.append(
            "  carbon NEVER improved in this sweep. Closest to improving: "
            f"{best.dist_name}, C_R={best.CR:.2f}, K_R_cap={best.KR_cap_mult}xD_bar "
            f"(carbon {best.carbon_pct_change:+.1f}%)."
        )
    return "\n".join(lines)
