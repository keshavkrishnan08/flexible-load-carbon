"""
Demand-response programs: how induced mining demand d(D, S) is shaped.

Two programs appear in the paper:

  Clean program (Section 3.6.3, used with the full-grid oligopoly):
      d(D, S) = S*k - D      if S*k >= D   (mining soaks up renewable surplus)
              = delta        if S*k <  D   (a chosen positive floor on fossil)
  Here delta (>=0) is the lever; delta = 0 is the no-mining benchmark.

  Adapted program (Appendix A, eq. 69, used in the partial grid):
      d(D, S) = min{S*k - D, nR/(2 Po)}   if S*k - D >= 0
              = d_floor                    if S*k - D <  0
  The surplus branch is CLIPPED at nR/(2 Po) because, with bounded
  inducement, a profit-seeking grid never sets P below Po/2 and so never
  induces more than n R/(2 Po) of surplus mining. The Remark in the paper
  explains why min{., nR/Po} (the naive cap) would instead penalize k.

These map a residual situation (D, S, k) to a mining quantity; Role 1/Role 3
feed that into the regulator's emission objective. emissions.py uses the
adapted program to check whether emission reduction survives the partial grid.
"""
from __future__ import annotations


def clean_program(D: float, S: float, k: float, delta: float = 0.0) -> float:
    """Section 3.6.3 program. delta is the fossil-fed mining floor."""
    surplus = S * k - D
    return surplus if surplus >= 0 else delta


def adapted_program(D: float, S: float, k: float, R: float, n: int, Po: float,
                    d_floor: float = 0.0) -> float:
    """Appendix A eq. (69) program, with the surplus branch clipped at nR/(2Po).

    d_floor (the `d` in eq. 69, with d <= nR/Po) is the fossil-fed mining
    quantity when renewables fall short; default 0 recovers "no mining when
    short."
    """
    surplus = S * k - D
    clip = n * R / (2.0 * Po)
    if surplus >= 0:
        return min(surplus, clip)
    return d_floor
