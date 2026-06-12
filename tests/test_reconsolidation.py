"""
test_reconsolidation.py — benchmark 03.

Asserts (a) the located gap: M1 (production) and M2 do no in-place revision; and
(b) M3's PE-gated update has the documented window shape (nonmonotonic; zero at
both boundaries — necessary-PE lower bound and too-much-PE upper bound).

NOTE: the window shape is DESIGNED to match known boundary conditions, so (b) is a
consistency check on the mechanism, not a discovered prediction. (a) is the result.

Runnable: pytest tests/   or   python tests/test_reconsolidation.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reference.m3_reconsolidation import (
    destabilization, m3_update, m1_or_m2_update, PE_LOW, PE_HIGH,
)


def test_m1_m2_have_no_reconsolidation():
    """The located gap: across the whole PE range, M1/M2 never move the belief."""
    for pe in [0.0, 0.2, 0.475, 0.7, 1.0]:
        new, d, _ = m1_or_m2_update(0.3, 0.3 + pe * 0.7)
        assert d == 0.0 and new == 0.3, f"M1/M2 must not revise; PE-proxy {pe} gave d={d}, new={new}"


def test_m3_window_is_nonmonotonic():
    """Zero update at PE=0 and PE=1, a single interior peak in between."""
    grid = [i / 200 for i in range(201)]
    vals = [destabilization(pe) for pe in grid]
    assert vals[0] == 0.0 and vals[-1] == 0.0, "update must be 0 at PE=0 and PE=1"
    peak_i = vals.index(max(vals))
    peak_pe = grid[peak_i]
    assert 0.0 < peak_pe < 1.0, f"peak must be interior; got {peak_pe}"
    # single-peaked: monotone up to the peak, monotone down after
    assert all(vals[i] <= vals[i + 1] + 1e-12 for i in range(peak_i)), "must rise to the peak"
    assert all(vals[i] >= vals[i + 1] - 1e-12 for i in range(peak_i, len(vals) - 1)), "must fall after the peak"


def test_m3_window_boundaries_match_known_bounds():
    """Lower bound (PE necessary) and upper bound (too much -> new learning)."""
    assert destabilization(PE_LOW) == 0.0, "no destabilization below PE_low"
    assert destabilization(PE_HIGH) == 0.0, "no update at/above PE_high"
    # too-much-mismatch forms a new memory and leaves the old one intact
    _, d, formed_new = m3_update(0.0, 0.95)   # PE=0.95 > PE_HIGH
    assert d == 0.0 and formed_new, "high PE must form a new memory, not overwrite"
    # moderate mismatch revises in-place
    _, d_mid, formed_mid = m3_update(0.0, (PE_LOW + PE_HIGH) / 2)
    assert d_mid > 0.0 and not formed_mid, "moderate PE must revise in-place"


if __name__ == "__main__":
    tests = [test_m1_m2_have_no_reconsolidation,
             test_m3_window_is_nonmonotonic,
             test_m3_window_boundaries_match_known_bounds]
    failed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
