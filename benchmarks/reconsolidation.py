"""
Benchmark 03 — reconsolidation: the prediction-error update window.

Human memory updates a stored belief at retrieval only within a window of
prediction error: none if the reminder matches (nothing to learn), maximal at
moderate mismatch, and none again if the mismatch is so large the reminder is
treated as a new event (Sevenster 2013/2014; Sinclair & Barense 2019).

WHAT THIS BENCHMARK ACTUALLY SHOWS (read ../reference/m3_reconsolidation.py):
the inverted-U is DESIGNED to match those boundary conditions, so reproducing it
is not a discovery. The finding is the located GAP — SHI today (M1) and the M2
durability/spacing fix BOTH have NO in-place revision: a recall never moves a
stored belief toward contradicting evidence. So neither can reconsolidate; M3 is
the minimal added mechanism (a PE-gated update) that can. This is a distinct,
consequential gap: without it, wrong/stale memories are never corrected in place —
the system can only pile on new ones.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reference.m3_reconsolidation import (
    destabilization, m3_update, m1_or_m2_update, PE_LOW, PE_HIGH, D_MAX,
)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out = Path(__file__).resolve().parent.parent / "results"
    out.mkdir(parents=True, exist_ok=True)

    pes = np.linspace(0.0, 1.0, 400)
    d_m3 = np.array([destabilization(pe) for pe in pes])
    d_m12 = np.zeros_like(pes)                         # M1 and M2: no revision

    # Belief trajectory: stored belief starts at 0.0; a reminder presents value = PE.
    stored0 = 0.0
    belief_m3 = np.array([m3_update(stored0, pe)[0] for pe in pes])
    belief_m12 = np.array([m1_or_m2_update(stored0, pe)[0] for pe in pes])
    observed = pes                                    # the evidence presented

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.8))

    axA.plot(pes, d_m3, "-", color="#2c7fb8", lw=2.4, label="M3 (proposed) — PE-gated update")
    axA.plot(pes, d_m12, "-", color="#c0392b", lw=2.4, label="M1 (production) & M2 — no revision")
    axA.axvspan(PE_LOW, PE_HIGH, color="#2c7fb8", alpha=0.06)
    axA.axvline(PE_LOW, color="#888", ls=":", lw=1); axA.axvline(PE_HIGH, color="#888", ls=":", lw=1)
    axA.text(PE_LOW, -0.07, "PE_low", fontsize=7, ha="center")
    axA.text(PE_HIGH, -0.07, "PE_high\n(→new learning)", fontsize=7, ha="center")
    axA.set_xlabel("prediction error at retrieval (mismatch)")
    axA.set_ylabel("update fraction D(PE)")
    axA.set_title("A  The reconsolidation window (inverted-U)")
    axA.legend(fontsize=8, loc="upper right")
    axA.grid(alpha=0.3)

    axB.plot(pes, observed, "--", color="#888", lw=1.2, label="evidence presented")
    axB.plot(pes, belief_m3, "-", color="#2c7fb8", lw=2.4, label="M3 — belief revised in-place")
    axB.plot(pes, belief_m12, "-", color="#c0392b", lw=2.4, label="M1 & M2 — belief never moves")
    axB.set_xlabel("prediction error at retrieval (mismatch)")
    axB.set_ylabel("stored belief after the reminder")
    axB.set_title("B  Only M3 corrects the memory (and only in the window)")
    axB.legend(fontsize=8, loc="upper left")
    axB.grid(alpha=0.3)

    fig.suptitle("Benchmark 03 — reconsolidation: SHI (M1) and the M2 fix lack "
                 "in-place revision; M3 adds the PE-gated update (window is designed, not discovered)",
                 fontsize=9.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_png = out / "reconsolidation.png"
    fig.savefig(out_png, dpi=150)

    peak_i = int(d_m3.argmax())
    print(f"M3 window: PE_low={PE_LOW}, PE_high={PE_HIGH}, peak at PE={pes[peak_i]:.3f} (D={d_m3[peak_i]:.3f})")
    print(f"  D(0.0)={destabilization(0.0):.3f}  D(1.0)={destabilization(1.0):.3f}  (both 0: necessary + upper bound)")
    print(f"M1/M2 update fraction across all PE: max={d_m12.max():.3f}  (= no reconsolidation, ever)")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()
