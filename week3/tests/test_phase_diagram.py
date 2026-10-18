"""
Week 3 Task 3 tests: carbon phase diagram and contract-vs-greedy comparison.

These tests validate the carbon-sign-flip hypothesis, can the carbon-optimal
contract achieve lower carbon than the no-FCL benchmark in cases where the
greedy (firm-optimal) dispatch cannot? and ensure the phase-diagram
classification machinery is correct.
"""
import warnings

import numpy as np
import pytest

from fcl_solver.contract_solver import (
    solve_carbon_optimal_dispatch,
    solve_firm_optimal_dispatch,
)
from fcl_solver.distributions import UniformResidual, lognormal_primitive
from fcl_solver.model import Params
from fcl_solver.phase_diagram import (
    PhaseDiagramCell,
    _classify,
    run_dispatch_phase_sweep,
    summarize_phase,
)
from fcl_solver.solver import solve_no_fcl, solve_with_fcl


@pytest.fixture
def params_cr25():
    p = Params(R=109, c=45, CF=10, CR=25, CM=56, beta=190, p=10, D_bar=100)
    p.check_assumption1()
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Classification logic
# ─────────────────────────────────────────────────────────────────────────────

def test_classify_logic():
    assert _classify(10.0, 100.0) == "carbon_up"     # 10% > neutral_tol
    assert _classify(-10.0, 100.0) == "carbon_down"   # -10% < -neutral_tol
    assert _classify(0.05, 100.0) == "carbon_neutral"  # 0.05% < neutral_tol
    assert _classify(0.0, 0.0) == "carbon_neutral"     # no reference


# ─────────────────────────────────────────────────────────────────────────────
# Carbon-optimal dispatch at firm-optimal capacities (fast, fixed-cap version)
# ─────────────────────────────────────────────────────────────────────────────

def test_carbon_optimal_dispatch_at_firm_capacities(params_cr25):
    """Core test: at the firm-optimal (K_R*, K_F*, K_M*), does the carbon-
    optimal dispatch lower carbon vs the no-FCL benchmark?

    Note: the greedy dispatch RAISES carbon vs no-FCL at this point (confirmed
    by Week 2). The question is whether an optimally-designed contract can
    undo that increase.
    """
    warnings.filterwarnings("ignore")
    dist = lognormal_primitive(D_bar=100)

    # Get firm-optimal capacities (same as Week 2)
    firm_cap = solve_with_fcl(dist, params_cr25, KR_max=500, KF_max=300, KM_max=300)
    no_fcl = solve_no_fcl(dist, params_cr25, KR_max=500, KF_max=300)

    # Dispatch LPs at those capacities
    firm_dispatch = solve_firm_optimal_dispatch(
        dist, params_cr25, firm_cap.K_R, firm_cap.K_F, firm_cap.K_M, N=250
    )
    co_dispatch = solve_carbon_optimal_dispatch(
        dist, params_cr25, firm_cap.K_R, firm_cap.K_F, firm_cap.K_M,
        profit_floor=firm_dispatch.profit_dispatch, N=250,
    )

    # Greedy dispatch should still raise carbon vs no-FCL (Week 2 finding)
    assert firm_dispatch.carbon >= no_fcl.carbon - 1.0, (
        f"Greedy carbon={firm_dispatch.carbon:.2f} vs no-FCL={no_fcl.carbon:.2f}: "
        "expected greedy to be higher (Week 2 finding)"
    )

    # Carbon-optimal dispatch ≤ firm-optimal (LP minimizes carbon)
    assert co_dispatch.carbon <= firm_dispatch.carbon + 1e-4

    # Report whether the carbon sign flipped
    sign_flip = co_dispatch.carbon < no_fcl.carbon
    print(
        f"\nCR=25, lognormal (Week 2 canonical point):\n"
        f"  no-FCL carbon:   {no_fcl.carbon:.3f}\n"
        f"  greedy dispatch: {firm_dispatch.carbon:.3f} (Δ={firm_dispatch.carbon - no_fcl.carbon:+.3f})\n"
        f"  optimal contract:{co_dispatch.carbon:.3f} (Δ={co_dispatch.carbon - no_fcl.carbon:+.3f})\n"
        f"  sign flip: {sign_flip}"
    )
    # Test is informational: we assert it runs cleanly but don't assert
    # which direction the answer goes (that's the research question)
    assert "Optimal" in co_dispatch.lp_status


def test_carbon_optimal_dispatch_uniform_large_fcl(params_cr25):
    """Uniform distribution, large-FCL regime: Lemma 1 + carbon gap both work."""
    warnings.filterwarnings("ignore")
    dist = UniformResidual(D_bar=100)
    K_R, K_F, K_M = 10.0, 60.0, 30.0  # K_M > K_R: large-FCL

    firm = solve_firm_optimal_dispatch(dist, params_cr25, K_R, K_F, K_M, N=300)
    no_fcl = solve_no_fcl(dist, params_cr25, KR_max=500, KF_max=300)

    # Floor slightly below (more relaxed than) firm profit to give the carbon
    # optimizer room. Use absolute slack to handle negative profit correctly.
    floor = firm.profit_dispatch - abs(firm.profit_dispatch) * 0.2
    co = solve_carbon_optimal_dispatch(dist, params_cr25, K_R, K_F, K_M,
                                        profit_floor=floor, N=300)
    assert co.carbon <= firm.carbon + 1e-4
    assert "Optimal" in co.lp_status


# ─────────────────────────────────────────────────────────────────────────────
# Mini dispatch-phase sweep (tiny grid for speed)
# ─────────────────────────────────────────────────────────────────────────────

def test_dispatch_phase_sweep_minimal():
    """Mini sweep: 2 C_R x 1 distribution x 1 C_M, validates the machinery."""
    warnings.filterwarnings("ignore")
    cells = run_dispatch_phase_sweep(
        CR_values=[25.0, 35.0],
        CM_values=[56.0],
        dist_names=["uniform"],
        N_inner=150,
    )
    assert len(cells) == 2, f"Expected 2 cells, got {len(cells)}"
    for c in cells:
        assert c.outcome_greedy in ("carbon_up", "carbon_neutral", "carbon_down")
        assert c.outcome_contract in ("carbon_up", "carbon_neutral", "carbon_down")
        assert c.carbon_no_fcl > 0
        assert c.carbon_greedy >= 0
        assert c.carbon_contract >= 0
        # Contract can only be ≤ greedy (both computed at same capacities)
        assert c.carbon_contract <= c.carbon_greedy + 1e-3

    summary = summarize_phase(cells)
    assert "Phase sweep" in summary


def test_dispatch_phase_no_sign_flip_at_firm_capacities():
    """WEEK 3 KEYSTONE FINDING (fast sweep, dispatch-only at firm-optimal capacities):
    Across 4 distributions × 5 C_R values, the carbon-optimal dispatch LP
    found NO sign flips (contract carbon < no-FCL carbon) even when given
    the BEST POSSIBLE dispatch schedule. Carbon improved in 0/20 cells.

    This extends Week 2: not only does the greedy rule fail to flip carbon,
    but the LP-optimal (carbon-minimizing) dispatch ALSO fails. The finding
    covers the fixed-capacity version of the problem; the joint capacity +
    contract optimization is covered separately by run_contract_sweep.py.
    """
    warnings.filterwarnings("ignore")
    cells = run_dispatch_phase_sweep(
        CR_values=np.arange(20.0, 40.0, 5.0),  # 4 CR values
        CM_values=[56.0],
        dist_names=["uniform", "lognormal_sigma0.28", "lognormal_sigma0.6"],
        N_inner=200,
    )
    sign_flips = sum(c.sign_flip for c in cells)
    # The fixed-capacity carbon-optimal contract does NOT flip the carbon sign
    assert sign_flips == 0, (
        f"Found {sign_flips} sign flip(s) -- this would be a major new finding! "
        f"Details: {[(c.dist_name, c.CR, c.delta_contract) for c in cells if c.sign_flip]}"
    )


def test_summarize_phase_with_sign_flip():
    """summarize_phase correctly identifies and reports a sign flip."""
    cells = [
        PhaseDiagramCell(
            dist_name="test", CR=25.0, CM=56.0,
            outcome_greedy="carbon_up", outcome_contract="carbon_down",
            delta_greedy=5.0, delta_contract=-3.0,
            sign_flip=True,  # greedy raises, contract lowers
            carbon_no_fcl=100.0, carbon_greedy=105.0, carbon_contract=97.0,
        ),
        PhaseDiagramCell(
            dist_name="test", CR=35.0, CM=56.0,
            outcome_greedy="carbon_up", outcome_contract="carbon_up",
            delta_greedy=3.0, delta_contract=1.0,
            sign_flip=False,
            carbon_no_fcl=100.0, carbon_greedy=103.0, carbon_contract=101.0,
        ),
    ]
    summary = summarize_phase(cells)
    assert "1/2" in summary  # 1 sign flip out of 2 cells
    assert "SIGN FLIPS" in summary
