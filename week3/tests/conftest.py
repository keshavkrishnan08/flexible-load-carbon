"""
Shared fixtures. `valid_params` is a hand-picked parameter set that
satisfies Assumption 1 (paper Section 3.1) *and* keeps the no-FCL and
with-FCL-given-K_R uniform solutions inside their respective regimes
(K_R^o > 0; K*_M > K*_R and K*_F < D_bar at the K_R values tests probe) --
finding this set is itself part of what test_closed_form_uniform.py checks
by construction (see its module docstring for the two parameter pitfalls
that were hit and fixed while building this).
"""
import pytest

from fcl_solver.model import Params


@pytest.fixture
def valid_params():
    p = Params(R=109, c=45, CF=10, CR=8, CM=56, beta=190, p=10, D_bar=100)
    p.check_assumption1()
    return p


@pytest.fixture
def valid_params_small():
    """A second, differently-scaled parameter set for cross-checking that
    results aren't an artifact of one specific set of numbers."""
    p = Params(R=60, c=22, CF=6, CR=4, CM=34, beta=140, p=8, D_bar=50)
    p.check_assumption1()
    return p
