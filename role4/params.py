"""
Shared model primitives for the updated Role 4 (FCL paper, Section 3-4).

Residual demand x = D - K_R*S. The utility chooses renewable K_R, fossil
K_F, and flexible-computing-load K_M. Per-MWh: R fcl revenue, c fossil
variable cost, p retail price, beta blackout penalty. Amortized per-MW
capital: C_R, C_F, C_M. Demand support upper bound D_bar.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Params:
    R: float
    c: float
    CF: float
    CR: float
    CM: float
    beta: float
    p: float
    D_bar: float

    @property
    def bp(self) -> float:
        return self.beta + self.p

    # --- Assumption 1, the four conditions, named individually (bullet 4) ---
    def A1(self) -> bool:  # computing profitable enough to run on existing fossil
        return self.R > self.c + self.CM

    def A2(self) -> bool:  # but not enough to justify NEW fossil (interior regime)
        return self.R < self.c + self.CF + self.CM

    def A3(self) -> bool:  # worth building fossil backup to avoid blackout
        return self.bp > self.c + self.CF

    def A4(self) -> bool:  # not worth blacking out users to support computing
        return self.bp > self.R

    def assumption1_holds(self) -> bool:
        return self.A1() and self.A2() and self.A3() and self.A4()

    def with_(self, **kw) -> "Params":
        return replace(self, **kw)
