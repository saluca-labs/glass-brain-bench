"""
hybrid_search_m2.py — PROPOSED drop-in for soul-svc/hybrid_search.py.

Replaces the M1 count-based pair (`_decay_factor` × `_recall_boost`) with the M2
retrievability factor computed from the stored per-memory `stability` and
`last_recall_at`. Reference only — not wired into the live service. The mechanism
is validated in ../tests/test_m2_spacing.py.

THREE CHANGES against the current file (line numbers as of 2026-06-11):

1. SELECT (hybrid_search.py:122) — also fetch the two new columns:
     .select("id,full_context,topics,created_at,recall_count,metadata,"
             "knowledge_tier,stability,last_recall_at")

2. SCORING (hybrid_search.py:295-304, Phase 4) — replace the two factor lines
     m["_score"] *= self._decay_factor(m.get("created_at"))
     m["_score"] *= self._recall_boost(m.get("recall_count") or 0)
   with a single retrievability factor:
     m["_score"] *= self._retrievability(m.get("stability"), m.get("last_recall_at"))
   (tier boosting and sort are unchanged.)

3. RECALL EVENT (wherever recall_count is incremented on access) — also update
   stability and last_recall_at via `apply_recall_update` below, atomically with
   the count increment. Prefer doing this server-side in the recall RPC so the
   read-modify-write is transactional; the Python here is the canonical spec.
"""

from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Optional

H0 = 48.0    # initial stability / half-life (hours) — must match the migration DEFAULT
F  = 3.0     # max corroboration strength factor


def _hours_since(ts_iso: Optional[str]) -> float:
    if not ts_iso:
        return 0.0
    try:
        ts = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
        return max(0.0, (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0)
    except Exception:
        return 0.0


# --- scoring side (read) -----------------------------------------------------

def _retrievability(stability: Optional[float], last_recall_at: Optional[str]) -> float:
    """Replaces `_decay_factor × _recall_boost`. Decay anchored to LAST RECALL,
    so a recalled memory is fresh again (testing effect); strength accumulated by
    prior recalls lives in `stability`, not in a count."""
    h = stability if (stability and stability > 0) else H0
    return 2.0 ** (-_hours_since(last_recall_at) / h)


# --- recall side (write) — canonical spec for the recall-increment handler ----

def apply_recall_update(stability: Optional[float], last_recall_at: Optional[str]):
    """Call at a recall event, alongside recall_count := recall_count + 1.
    Returns (new_stability, new_last_recall_at_iso). Gain is gated on
    retrievability-at-recall (∝ R·(1−R)); then the decay clock resets to now."""
    h = stability if (stability and stability > 0) else H0
    R = 2.0 ** (-_hours_since(last_recall_at) / h)
    new_stability = h * (1.0 + (F - 1.0) * R * (1.0 - R))
    return new_stability, datetime.now(timezone.utc).isoformat()
