"""
m2_memory.py — the M2 fix as a reference implementation.

This is the activation-gated, testing-effect memory-strength model the essay
marks "aspirational." It is the code that would replace SHI's count-based rule
(soul-svc/hybrid_search.py `_decay_factor` × `_recall_boost`). It is validated
here against benchmark 01 (see ../tests/test_m2_spacing.py); it is NOT yet
deployed to the production memory layer — see ../soul-svc-port/README.md.

PRODUCTION CONTRAST
  M1 (live):  retrievability ≈ exp(-λ·age_since_created) × (1 + ln(1+recall_count)/10)
              — decay anchored to creation; recall contributes by COUNT only.
  M2 (here):  retrievability  = 2^(-(now - last_recall_at)/stability)
              — decay anchored to LAST RECALL (testing effect); each recall
                updates a stored per-memory `stability`, gated on how retrievable
                the memory was at that recall (desirable difficulty).

Two declared parameters, fixed before looking at any human data:
  H0  initial stability (half-life, hours)
  F   maximum corroboration strength factor
"""

from __future__ import annotations
from dataclasses import dataclass

H0_DEFAULT = 48.0   # initial half-life (hours)
F_DEFAULT  = 3.0    # max corroboration strength factor


def retrievability(stability_h: float, hours_since_last_recall: float) -> float:
    """Probability-like retrievability: 1.0 at the moment of recall, halving
    every `stability_h` hours since the last recall."""
    if stability_h <= 0:
        return 0.0
    return 2.0 ** (-max(0.0, hours_since_last_recall) / stability_h)


def stability_after_recall(stability_h: float,
                           hours_since_last_recall: float,
                           f: float = F_DEFAULT) -> float:
    """Activation-gated stability update applied AT a recall event.

    Expected gain ∝ R·(1−R): you must retrieve it (≈prob R) and you gain more
    the harder it was (≈1−R). Gain is therefore maximal at R = 0.5 — the
    desirable-difficulty sweet spot — and near zero for a massed recall (R≈1)
    or a fully-forgotten one (R≈0). This is what produces the spacing effect
    and its nonmonotonic optimal lag. The caller also sets last_recall_at = now.
    """
    R = retrievability(stability_h, hours_since_last_recall)
    return stability_h * (1.0 + (f - 1.0) * R * (1.0 - R))


@dataclass
class M2Memory:
    """Reference per-memory state. In production these two fields are columns on
    `_memories` (stability double precision, last_recall_at timestamptz), updated
    on every recall and read at scoring time."""
    stability: float = H0_DEFAULT       # half-life (hours)
    last_recall_h: float = 0.0          # hours (test clock); prod: last_recall_at

    def retrievability_at(self, now_h: float) -> float:
        return retrievability(self.stability, now_h - self.last_recall_h)

    def recall(self, now_h: float, f: float = F_DEFAULT) -> None:
        """Apply a recall/corroboration at time now_h: gate the stability gain on
        current retrievability, then reset the decay clock (the testing effect)."""
        self.stability = stability_after_recall(
            self.stability, now_h - self.last_recall_h, f)
        self.last_recall_h = now_h     # decay clock resets on successful recall


# --- M1 reference (the current production rule), for head-to-head testing ----

def m1_count_based_score(recall_count: int, age_h: float,
                         decay_lambda: float = 0.001) -> float:
    """Mirror of soul-svc/hybrid_search.py: exp(-λ·age_since_created) ×
    (1 + ln(1+recall_count)/10). Decay never resets; recall is count-only."""
    import math
    return math.exp(-decay_lambda * age_h) * (1.0 + math.log1p(recall_count) / 10.0)
