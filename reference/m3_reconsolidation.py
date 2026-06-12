"""
m3_reconsolidation.py — prediction-error-gated in-place reconsolidation (PROPOSED).

The minimal mechanism that lets a stored memory be REVISED toward new evidence at
retrieval, gated nonmonotonically on prediction error (PE = mismatch between the
stored belief and what the reminder presents):
  - PE below PE_LOW : no destabilization (nothing to learn) -> no update.
  - moderate PE     : memory destabilizes and updates toward the new evidence.
  - PE above PE_HIGH: treated as NEW learning; the old memory is left intact.

IMPORTANT HONESTY NOTE: the windowed inverted-U below is the DESIGN, chosen to
match the documented boundary conditions of human reconsolidation —
  * prediction error is NECESSARY to destabilize  (Sevenster, Beckers & Kindt 2013)
  * too much mismatch tips retrieval into new learning, not update  (Sevenster 2014)
  * "incomplete reminders drive reconsolidation"  (Sinclair & Barense 2019)
It is NOT a discovered prediction. The benchmark's actual finding is the located
gap: SHI today (M1) and the M2 durability/spacing fix BOTH lack in-place revision
entirely — memory is append-only / strengthen-on-recall, with no way to correct a
stored belief when contradicting evidence arrives. Reconsolidation is therefore a
SEPARATE gap from forgetting/spacing, and M3 is the smallest thing that closes it.

Declared parameters, fixed before any fitting:
  PE_LOW, PE_HIGH  window boundaries; D_MAX  peak update fraction.
"""

from __future__ import annotations
import math

PE_LOW  = 0.10   # below this: no destabilization
PE_HIGH = 0.85   # above this: new learning, old memory untouched
D_MAX   = 0.80   # max update fraction at the window peak


def destabilization(pe: float) -> float:
    """Update fraction D(PE) in [0, D_MAX] — a windowed inverted-U: 0 at the
    boundaries, single peak in the middle of [PE_LOW, PE_HIGH]."""
    if pe <= PE_LOW or pe >= PE_HIGH:
        return 0.0
    x = (pe - PE_LOW) / (PE_HIGH - PE_LOW)        # 0..1 across the window
    return D_MAX * math.sin(math.pi * x) ** 2     # 0 at edges, peak at x=0.5


def m3_update(stored: float, observed: float):
    """Reconsolidation at retrieval: move the stored belief toward the observed
    value by D(PE). Returns (new_stored, update_fraction, formed_new_memory)."""
    pe = abs(observed - stored)
    d = destabilization(pe)
    new_stored = stored + d * (observed - stored)
    formed_new_memory = pe >= PE_HIGH             # too-much-mismatch -> new memory
    return new_stored, d, formed_new_memory


def m1_or_m2_update(stored: float, observed: float):
    """M1 (production) and the M2 fix: NO in-place content revision. A recall may
    strengthen (M2) or bump a count (M1), but the stored belief is never moved
    toward contradicting evidence. Returns (stored unchanged, 0.0, False)."""
    return stored, 0.0, False
