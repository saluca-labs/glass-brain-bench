"""
Benchmark 01 — Forgetting curve + spacing effect.

Tests whether a memory-decay rule reproduces two of the most robust phenomena
in human memory: the Ebbinghaus forgetting curve, and the spacing effect.

TESTING STANDARD (see ../README.md):
  - Declared parameter count, fixed BEFORE looking at the human data.
  - Recency controlled in the spacing design (a fixed retention interval RI
    separates the last review from the test, so only the inter-study GAP varies).
  - Two models with the SAME parameter count, differing ONLY in the update rule,
    so any difference is attributable to the mechanism, not parameter freedom.
  - Honest negatives are results. A rule that fails is a located gap, not a
    failure of the harness.

MODELS:
  M1 "count-based": a corroboration multiplies stability by a fixed factor,
     independent of the memory's current state.  h <- f * h
  M2 "activation-gated": the stability gain depends on retrievability at review,
     weighted by retrieval success — expected gain ∝ R*(1-R).
     h <- h * (1 + (f-1)*R*(1-R))

STATUS (2026-06-11): SHI's production memory model (soul-svc/hybrid_search.py)
was read and found to be M1 — retrievability = exp(-λ·age_since_encoding) ×
(1 + ln(1+recall_count)/10); the recall term is a function of COUNT alone. So the
production system, as built, is the flat (no-spacing) curve in Panel B. M2 is the
aspirational target (see ../STATUS.md).
"""

import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

# --- Ebbinghaus (1885) savings %, classic forgetting-curve reference points ---
ebb_t = np.array([0.33, 1.0, 8.8, 24.0, 48.0, 144.0, 744.0])     # hours
ebb_r = np.array([58.2, 44.2, 35.8, 33.7, 27.8, 25.4, 21.1]) / 100.0

def exp_decay(t, h):              # 1 param
    return 2.0 ** (-t / h)

def pow_decay(t, S, beta):        # 2 params
    return (1.0 + t / S) ** (-beta)

p_exp, _ = curve_fit(exp_decay, ebb_t, ebb_r, p0=[24.0],
                     bounds=(0.01, 5000.0), maxfev=10000)
p_pow, _ = curve_fit(pow_decay, ebb_t, ebb_r, p0=[1.0, 0.2],
                     bounds=([0.01, 0.01], [5000.0, 3.0]), maxfev=10000)

def rmse(f, p):
    return float(np.sqrt(np.mean((f(ebb_t, *p) - ebb_r) ** 2)))

rmse_exp, rmse_pow = rmse(exp_decay, p_exp), rmse(pow_decay, p_pow)

# --- Spacing. Same params for both models; recency (RI) held fixed. ----------
H0 = 48.0      # initial half-life (hours), declared
F  = 3.0       # corroboration strength factor, declared
RI = 96.0      # fixed retention interval between last review and test
gaps = np.linspace(0.0, 240.0, 400)

def m1_count_based(gap):
    return 2.0 ** (-RI / (H0 * F))         # stability = H0*F regardless of timing

def m2_activation_gated(gap):
    R = 2.0 ** (-gap / H0)                  # retrievability when the review occurs
    h_final = H0 * (1.0 + (F - 1.0) * R * (1.0 - R))
    return 2.0 ** (-RI / h_final)

m1 = np.array([m1_count_based(g) for g in gaps])
m2 = np.array([m2_activation_gated(g) for g in gaps])
m1_rel, m2_rel = m1 / m1[0], m2 / m2[0]     # normalize to own massed baseline
opt_gap = gaps[int(np.argmax(m2_rel))]
best = m2_rel.max()
improve = 100.0 * (best - 1.0)

# --- Figure -----------------------------------------------------------------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.8))

tt = np.linspace(0.2, 744, 500)
axA.scatter(ebb_t, ebb_r, color="black", zorder=5, label="Ebbinghaus 1885 (savings)")
axA.plot(tt, exp_decay(tt, *p_exp), "--", color="#c0392b",
         label=f"exponential, 1 param (RMSE {rmse_exp:.3f})")
axA.plot(tt, pow_decay(tt, *p_pow), "-", color="#2c7fb8",
         label=f"power-law, 2 params (RMSE {rmse_pow:.3f})")
axA.set_xscale("log")
axA.set_xlabel("retention interval (hours, log)")
axA.set_ylabel("retention")
axA.set_title("A  Forgetting curve — fits, but does not discriminate")
axA.legend(fontsize=8, loc="upper right")
axA.grid(alpha=0.3)

axB.plot(gaps, m1_rel, "-", color="#c0392b", lw=2,
         label="M1 count-based (= SHI production) — flat: no spacing")
axB.plot(gaps, m2_rel, "-", color="#2c7fb8", lw=2,
         label="M2 activation-gated (aspirational) — spacing + optimal lag")
axB.axhline(1.0, color="#888", ls="--", lw=0.8)
axB.axvline(opt_gap, color="#2c7fb8", ls=":", alpha=0.7)
axB.annotate(f"optimal gap ≈ {opt_gap:.0f} h (R≈0.5)\n+{improve:.0f}% vs massed",
             xy=(opt_gap, best), xytext=(opt_gap + 25, best - 0.12),
             fontsize=8, arrowprops=dict(arrowstyle="->", color="#2c7fb8"))
axB.set_xlabel(f"inter-study gap (hours)   [recency held fixed: RI = {RI:.0f} h]")
axB.set_ylabel("retention at test (relative to massed practice)")
axB.set_title("B  Spacing — the discriminating test (same param count)")
axB.legend(fontsize=8, loc="upper right")
axB.grid(alpha=0.3)

fig.suptitle("Confidence-weighted decay, simulated: reproduces forgetting, "
             "but spacing needs activation-gating", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.96])
out_png = OUT / "forgetting_spacing.png"
fig.savefig(out_png, dpi=150)

print(f"exp fit: half-life h={p_exp[0]:.2f} h, RMSE={rmse_exp:.4f}")
print(f"pow fit: S={p_pow[0]:.3f}, beta={p_pow[1]:.3f}, RMSE={rmse_pow:.4f}")
print(f"M1 count-based spacing range (normalized): {m1_rel.max()-m1_rel.min():.2e}  (= flat, no spacing)")
print(f"M2 activation-gated: optimal gap={opt_gap:.1f} h (=H0), "
      f"peak/massed={best:.3f}x, improvement=+{improve:.1f}% vs massed")
print(f"saved: {out_png}")
