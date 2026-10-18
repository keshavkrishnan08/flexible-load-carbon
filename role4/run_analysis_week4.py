#!/usr/bin/env python3
"""Run the Role 4 Week-4 acceptance summary."""
from role4.params import Params
from role4 import week4


def main() -> None:
    P = Params(R=2.0, c=1.0, CF=1.0, CR=0.5, CM=0.3, beta=1.0, p=2.0, D_bar=100.0)
    out = week4.week4_summary(P)

    b1 = out["extend_functional_across_regimes"]
    b2 = out["harden_converse"]
    b3 = out["regime_map_classification"]
    b4 = out["reconcile_team"]

    print("=== Role 4 Week 4, Theory Hardening and Regimes ===")
    print("Bullet 1: functional sign = %s; carbon C1 across regime = %s; kink located in %s"
          % (b1["functional_sign"], b1["carbon_integral_C1"], b1["located_discontinuity"]))
    print("Bullet 2: measurable extremal schedule = %s; Sion saddle when compact = %s; carbon-window ill-posed = %s"
          % (b2["extremal_schedule_measurable"], b2["sion_saddle_when_compact"], b2["ill_posed_on_carbon_window"]))
    print("Bullet 3: carbon-down connected = %s; spans both regimes = %s; crossing = (%.3f, %.3f)"
          % (b3["carbon_down_connected"], b3["spans_both_regimes"],
             b3["regime_crossing"]["crossing_C_M"], b3["regime_crossing"]["crossing_C_R"]))
    print("Bullet 4: shared objects consistent = %s; flags = %s"
          % (b4["shared_objects_consistent"], ", ".join(b4["divergences"].keys())))


if __name__ == "__main__":
    main()
