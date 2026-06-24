import pytest
from role4.params import Params


@pytest.fixture
def P():
    # interior regime, in the carbon window: C_R°=0.25 < C_R=0.5 < C_R†; strict adoption C_M=0.3<C̄_M=0.5
    p = Params(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)
    assert p.assumption1_holds()
    return p
