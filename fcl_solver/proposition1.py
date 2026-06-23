"""
Proposition 1 ("mining preference condition and triple win", paper p.30-31)
as a reusable check, for any residual-demand distribution (Task 3).

Proposition 1 claims, for C_M < C_bar_M = (R-c)*phi_o where
phi_o = F(K_F^o; K_R^o) is the no-FCL reliability:
  (i)   profit strictly higher with the FCL program            [any distribution, Assumption 1]
  (ii)  blackout probability strictly lower with the program    [any distribution, Assumption 1]
  (iii) carbon emissions MAY be lower (not guaranteed in general -- needs
        extra distributional conditions, e.g. uniform F with C_R small
        enough, or Corollary 2's concave/convex density conditions).

(i) and (ii) are distribution-free and should hold for *any* F satisfying
Assumption 1 -- that is the main thing to stress-test across distribution
families (Task 3). (iii) is expected to hold only sometimes -- mapping
where it holds/breaks is Task 4 (sweep.py).
"""
from __future__ import annotations

from dataclasses import dataclass

from .distributions import ResidualDemand
from .model import Params, blackout_probability
from .solver import SolveResult, solve_no_fcl, solve_with_fcl


def C_bar_M(params: Params, no_fcl: SolveResult) -> float:
    """C_bar_M = (R-c) * phi_o, eq. 27, using the no-FCL benchmark's
    realized reliability phi_o = F(K_F^o; K_R^o) = 1 - blackout_prob^o."""
    phi_o = 1.0 - no_fcl.blackout_prob
    return (params.R - params.c) * phi_o


@dataclass
class TripleWinResult:
    no_fcl: SolveResult
    with_fcl: SolveResult
    C_bar_M: float
    CM: float
    below_threshold: bool          # C_M < C_bar_M ?
    profit_higher: bool            # part (i)
    blackout_lower: bool           # part (ii)
    carbon_lower: bool             # part (iii), distribution-dependent
    carbon_change: float           # with_fcl.carbon - no_fcl.carbon (negative = improvement)

    def __repr__(self):
        return (
            f"TripleWin(C_M={self.CM:.3f} {'<' if self.below_threshold else '>='} "
            f"C_bar_M={self.C_bar_M:.3f} | profit_higher={self.profit_higher} "
            f"blackout_lower={self.blackout_lower} carbon_lower={self.carbon_lower} "
            f"d_carbon={self.carbon_change:+.4f})"
        )


def check_triple_win(dist: ResidualDemand, params: Params, **solver_kwargs) -> TripleWinResult:
    """Solve both benchmarks and report which parts of Proposition 1 hold."""
    no_fcl = solve_no_fcl(dist, params, **{k: v for k, v in solver_kwargs.items() if k in ("KR_max", "KF_max")})
    with_fcl = solve_with_fcl(dist, params, **solver_kwargs)

    cbar = C_bar_M(params, no_fcl)
    below = params.CM < cbar

    return TripleWinResult(
        no_fcl=no_fcl,
        with_fcl=with_fcl,
        C_bar_M=cbar,
        CM=params.CM,
        below_threshold=below,
        profit_higher=with_fcl.profit > no_fcl.profit,
        blackout_lower=with_fcl.blackout_prob < no_fcl.blackout_prob,
        carbon_lower=with_fcl.carbon < no_fcl.carbon,
        carbon_change=with_fcl.carbon - no_fcl.carbon,
    )
