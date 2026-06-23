"""
Task 4 regression test: a small, fast version of run_sweep.py's grid,
pinning down the headline finding (see fcl_solver/sweep.py's docstring)
so a future change to the solver that accidentally "fixes" or breaks this
result gets caught immediately, without re-running the full sweep.
"""
import numpy as np

from fcl_solver.sweep import run_sweep


def test_profit_and_blackout_robust_carbon_is_not():
    cells = run_sweep(
        CR_values=np.geomspace(0.5, 20, 4),
        KR_cap_multiples=[1, 3],
        dist_names=["uniform", "power_alpha_0.5", "power_alpha_2.0"],
    )
    assert len(cells) == 4 * 2 * 3

    assert all(c.profit_higher for c in cells), "profit should improve in every cell"
    assert all(c.blackout_lower for c in cells), "blackout probability should fall in every cell"
    # The headline finding: not a single cell shows a carbon improvement
    # for this parameter family. If this assertion ever fails, that is
    # GOOD news worth flagging to the team -- it would mean a carbon-
    # improving region was found (see sweep.py for the full context).
    assert not any(c.carbon_lower for c in cells), (
        "found a carbon-improving cell -- this contradicts the documented sweep "
        "finding in fcl_solver/sweep.py and should be reported, not silently accepted"
    )
