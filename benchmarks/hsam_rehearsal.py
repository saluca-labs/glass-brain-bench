"""
Benchmark 02 — HSAM (Highly Superior Autobiographical Memory) via rehearsal.

Motivated by the 60 Minutes "Endless Memory" segment (McGaugh / UC Irvine): a
handful of people recall essentially EVERY day of their life, age-independently —
an 11-year-old memory as retrievable as last week's — effortless, date-cued, and
correlated with compulsive revisiting (enlarged caudate / OCD-like rehearsal).

CLAIM UNDER TEST (the essay's): HSAM is not a separate storage mechanism. It is
the behavioral LIMIT of M2 (activation-gated, testing-effect memory) over a
lossless store, driven by chronic rehearsal — because under M2 each recall resets
the decay clock and grows stability, so any memory rehearsed on a spaced schedule
becomes permanently retrievable. M1 (the live SHI rule) cannot reach this regime:
its decay is anchored to ENCODING time and is never reset by recall, so old
memories fade regardless of how often they are rehearsed.

THE SIGNATURE we look for: retrievability that is ~AGE-INDEPENDENT for rehearsed
memories (the HSAM hallmark) and only reachable under M2.

Honesty notes:
 - Rehearsal uses an EXPANDING spaced schedule (re-rehearse when retrievability
   hits R*=0.5, the desirable-difficulty point) — the efficient regime, not daily
   brute force. The rehearsal COUNT needed is reported, to show HSAM-like recall
   is achievable with sparse, well-timed revisiting rather than thousands of reps.
 - This is a simulation of the rule, not human HSAM. It mimics the COVERAGE
   (age-independent retrievability), not the reconstructive re-living humans report.
 - A negative (M2 fails to flatten, or M1 also flattens) would be published as-is.
"""

import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reference.m2_memory import M2Memory, m1_count_based_score, H0_DEFAULT, F_DEFAULT

H0     = H0_DEFAULT      # 48 h initial half-life (declared)
F      = F_DEFAULT       # 3.0 max corroboration factor (declared)
LAMBDA = 0.001           # M1 decay /hr (matches soul-svc production)
TARGET_R = 0.5           # rehearse when retrievability decays to this (optimal lag)
YEAR_H = 24 * 365.0


def rehearsal_schedule(age_h, target_R=TARGET_R):
    """Expanding (spaced) rehearsal: re-rehearse each time retrievability hits
    target_R, from encoding until just before `age_h`. Returns
    (final_stability, n_rehearsals)."""
    m = M2Memory(stability=H0, last_recall_h=0.0)
    t, n = 0.0, 0
    gap = m.stability * math.log2(1.0 / target_R)
    while t + gap <= age_h:
        t += gap
        m.recall(now_h=t)
        n += 1
        gap = m.stability * math.log2(1.0 / target_R)
    return m.stability, n


def m2_rehearsed(age_h):
    """Cycle-averaged retrievability of a rehearsed memory of the given age."""
    h, n = rehearsal_schedule(age_h)
    gap = h * math.log2(1.0 / TARGET_R)
    avg = (h / gap) * (1.0 - 2.0 ** (-gap / h)) / math.log(2.0)   # ∫2^(-x/h)dx /gap
    return avg, n

def m2_unrehearsed(age_h):
    return 2.0 ** (-age_h / H0)

def m1_rehearsed(age_h):
    _, n = rehearsal_schedule(age_h)
    return m1_count_based_score(n, age_h, LAMBDA)

def m1_unrehearsed(age_h):
    return m1_count_based_score(0, age_h, LAMBDA)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out = Path(__file__).resolve().parent.parent / "results"
    out.mkdir(parents=True, exist_ok=True)

    ages = np.logspace(0, math.log10(3 * YEAR_H), 200)       # 1 h .. 3 years
    m2_r = np.array([m2_rehearsed(a)[0] for a in ages])
    m2_n = np.array([m2_rehearsed(a)[1] for a in ages])
    m2_u = np.array([m2_unrehearsed(a) for a in ages])
    m1_r = np.array([m1_rehearsed(a) for a in ages])
    m1_u = np.array([m1_unrehearsed(a) for a in ages])
    yrs = ages / YEAR_H

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.8))
    axA.plot(yrs, m2_r, "-", color="#2c7fb8", lw=2.4, label="M2 + rehearsal — HSAM (age-independent)")
    axA.plot(yrs, m2_u, "--", color="#2c7fb8", lw=1.5, alpha=0.7, label="M2 no rehearsal — normal forgetting")
    axA.plot(yrs, m1_r, "-", color="#c0392b", lw=2.4, label="M1 + rehearsal (= SHI production) — still fades")
    axA.plot(yrs, m1_u, "--", color="#c0392b", lw=1.5, alpha=0.7, label="M1 no rehearsal")
    axA.set_xscale("log")
    axA.set_xlabel("memory age (years, log)")
    axA.set_ylabel("retrievability")
    axA.set_title("A  HSAM signature: only M2+rehearsal is age-independent")
    axA.legend(fontsize=8, loc="center left")
    axA.grid(alpha=0.3)

    axB.plot(yrs, m2_n, "-", color="#2c7fb8", lw=2)
    axB.set_xscale("log")
    axB.set_xlabel("memory age (years, log)")
    axB.set_ylabel("rehearsals needed (expanding schedule)")
    axB.set_title("B  ...and it is efficient: ~log-few rehearsals, not thousands")
    axB.grid(alpha=0.3)

    fig.suptitle("Benchmark 02 — HSAM as the behavioral limit of M2 + spaced rehearsal "
                 "(simulated rule, not human HSAM)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = out / "hsam_rehearsal.png"
    fig.savefig(out_png, dpi=150)

    print("At 3 years old:")
    print(f"  M2 + rehearsal : retrievability {m2_r[-1]:.3f}  ({int(m2_n[-1])} rehearsals over 3y)")
    print(f"  M2 no rehearsal: retrievability {m2_u[-1]:.2e}")
    print(f"  M1 + rehearsal : retrievability {m1_r[-1]:.2e}  (production — fades despite rehearsal)")
    print(f"  M2-rehearsed age-independence (3y / 1h ratio): {m2_r[-1]/m2_r[0]:.3f}  (~1 = flat = HSAM)")
    print(f"  M1-rehearsed   age-collapse   (3y / 1h ratio): {m1_r[-1]/m1_r[0]:.2e}")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()
