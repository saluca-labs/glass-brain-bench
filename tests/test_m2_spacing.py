"""
test_m2_spacing.py — demonstrates the M2 reference implementation actually does
what the essay claims the fix would do, and that M1 does not.

Runnable two ways:
  pytest tests/
  python tests/test_m2_spacing.py     # prints PASS/FAIL summary

The standard (../README.md): same parameter count across compared models;
recency controlled in the spacing design; honest pass/fail.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reference.m2_memory import M2Memory, m1_count_based_score, H0_DEFAULT

H0 = H0_DEFAULT          # 48 h
RI = 96.0                # fixed retention interval (recency held constant)


def m2_two_presentation_retention(gap_h: float) -> float:
    """P1 = initial encoding at t=0; P2 = one corroboration at t=gap; test at
    t = gap + RI (so recency from the last recall is fixed at RI for every gap)."""
    m = M2Memory(stability=H0, last_recall_h=0.0)   # encoded at t=0
    m.recall(now_h=gap_h)                            # corroborated at t=gap
    return m.retrievability_at(now_h=gap_h + RI)     # tested RI after last recall


def m1_two_presentation_retention(gap_h: float) -> float:
    """M1 has no stored stability and never resets decay. After two presentations
    recall_count = 1 (one corroboration); decay runs from creation (t=0) to the
    test at t = gap + RI. Compare at the SAME total age so recency is matched to
    M2's design as closely as the count-based rule allows."""
    age_at_test = gap_h + RI
    return m1_count_based_score(recall_count=1, age_h=age_at_test)


def test_m1_shows_no_spacing():
    gaps = [0.0, 12.0, 24.0, 48.0, 96.0, 168.0]
    vals = [m1_two_presentation_retention(g) for g in gaps]
    # M1's recall term is count-only (=1 for all gaps); the only gap-dependence is
    # the decay-from-creation recency term, which MONOTONICALLY falls with gap and
    # has no interior optimum — i.e. no spacing benefit (no peak at an intermediate
    # gap). Assert strict monotonic decrease.
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)), \
        f"M1 should be monotonic in gap (no spacing peak); got {vals}"


def test_m2_shows_spacing_with_optimal_lag():
    gaps = [g / 4.0 for g in range(0, 4 * 240)]      # 0..240 h, fine grid
    vals = [m2_two_presentation_retention(g) for g in gaps]
    massed = vals[0]
    peak = max(vals)
    peak_gap = gaps[vals.index(peak)]
    # (a) spaced beats massed by a clear margin
    assert peak > massed * 1.2, f"M2 spacing benefit too small: peak {peak:.4f} vs massed {massed:.4f}"
    # (b) the optimum is INTERIOR (nonmonotonic) — the spacing/lag effect
    assert 0.0 < peak_gap < 240.0, f"M2 optimum should be interior; got {peak_gap}"
    # (c) the optimum sits where retrievability at review ≈ 0.5, i.e. gap ≈ H0
    assert abs(peak_gap - H0) < H0 * 0.15, f"M2 optimal lag should be ≈H0={H0}; got {peak_gap}"


def test_m2_testing_effect_resets_decay():
    """A recall must reset the decay clock: retrievability right after recall is
    1.0 regardless of how decayed it was before (M1 never does this)."""
    m = M2Memory(stability=H0, last_recall_h=0.0)
    assert m.retrievability_at(H0) == 0.5            # decayed to half before recall
    m.recall(now_h=H0)                               # recall at the half-life point
    assert m.retrievability_at(H0) == 1.0            # clock reset: full retrievability
    assert m.stability > H0                          # and stability increased


if __name__ == "__main__":
    tests = [test_m1_shows_no_spacing,
             test_m2_shows_spacing_with_optimal_lag,
             test_m2_testing_effect_resets_decay]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
