"""
test_hsam.py — benchmark 02: HSAM (age-independent recall) is reachable under
M2 + spaced rehearsal, and NOT under M1 (the production rule).

Runnable: pytest tests/   or   python tests/test_hsam.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.hsam_rehearsal import (
    m2_rehearsed, m1_rehearsed, rehearsal_schedule, YEAR_H,
)

YOUNG = 1.0              # 1 hour
OLD   = 3 * YEAR_H       # 3 years


def test_m2_rehearsal_is_age_independent():
    """The HSAM hallmark: a 3-year-old rehearsed memory is as retrievable as a
    fresh one. Ratio should be ~1 (flat)."""
    r_young = m2_rehearsed(YOUNG)[0]
    r_old   = m2_rehearsed(OLD)[0]
    ratio = r_old / r_young
    assert ratio > 0.9, f"M2+rehearsal should be age-independent; 3y/1h ratio={ratio:.3f}"
    assert r_old > 0.5, f"M2+rehearsal old retrievability too low: {r_old:.3f}"


def test_m1_cannot_sustain_hsam():
    """Production M1 cannot reach HSAM: identical rehearsal, but creation-anchored
    decay (never reset by recall) drags old memories to ~0."""
    r_old_m1 = m1_rehearsed(OLD)
    r_old_m2 = m2_rehearsed(OLD)[0]
    assert r_old_m1 < 1e-6, f"M1+rehearsal should fade old memories; got {r_old_m1:.2e}"
    assert r_old_m1 / r_old_m2 < 1e-6, "M1 must be vastly worse than M2 at HSAM"


def test_hsam_rehearsal_is_efficient():
    """HSAM-like total recall needs only sparse, well-timed rehearsal under the
    expanding schedule — not thousands of reps. (Subjects describe revisiting,
    not endless drilling.)"""
    _, n = rehearsal_schedule(OLD)
    assert n < 30, f"expanding-schedule rehearsals over 3y should be log-few; got {n}"
    assert n > 5, f"sanity: should need more than a handful over 3y; got {n}"


if __name__ == "__main__":
    tests = [test_m2_rehearsal_is_age_independent,
             test_m1_cannot_sustain_hsam,
             test_hsam_rehearsal_is_efficient]
    failed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
