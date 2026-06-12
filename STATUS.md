# STATUS

Where each claim sits on the gap → aspirational fix → shipped code trajectory.

## Benchmark 01 — forgetting curve + spacing

### gap (DONE, 2026-06-11)
SHI production memory (`soul-svc/hybrid_search.py`) is M1 (count-based). Confirmed
by reading the code, not just by simulation:
- `DECAY_LAMBDA = 0.001` /hr → single fixed half-life ~693 h (~29 d), decay measured
  from `created_at` (encoding), never reset by recall.
- `_recall_boost(recall_count) = 1 + log1p(recall_count)/10` — recall contribution
  is a function of **count alone**.
- `tkhr.py` topic salience: flat `+0.05` nudge per access (count-based), with
  saturating caps. No activation-gated path anywhere in the memory-strength model.
- `storage.py`: no separate consolidation/stability increment.

Consequence: no spacing effect, and a single-timescale decay that cannot match the
heavy-tailed forgetting curve. Retrieval also does not reinstate the trace (no
testing effect).

### reference implementation (BUILT + VALIDATED, 2026-06-11)
M2 is implemented and its behavior demonstrated, not asserted:
- `reference/m2_memory.py` — the activation-gated, testing-effect model:
  1. **Activation-gated corroboration** — stability gain ∝ R·(1−R) (max at R=0.5).
  2. **Recall resets/extends the decay clock** — decay anchored to `last_recall_at`
     (the testing effect); spacing falls out of (1)+(2) together.
  3. **Per-memory stability stored and updated**, not recomputed from a count.
- `tests/test_m2_spacing.py` — **3/3 passing**: M1 shows no spacing (monotonic in
  gap), M2 shows spacing with an interior optimal lag at gap ≈ H0 (R≈0.5), and a
  recall resets retrievability to 1.0 while increasing stability.

### production deploy (STAGED, NOT APPLIED)
`soul-svc-port/` holds the proposed change against `soul-svc/hybrid_search.py`:
the migration (`001_add_stability_last_recall.sql`) and the three-point drop-in
(`hybrid_search_m2.py` — SELECT, Phase-4 scoring factor, recall-event update).
**Not deployed.** Whether M2 reproduces the human curves at SHI's real scale and
access patterns is unproven until re-run against production decay traces — see the
deploy + validation checklist in `soul-svc-port/README.md`. The status line moves
from *aspirational* to *here's the code* only after that real-data demonstration,
and a failure there is published, not rolled back quietly.

## Backlog — benchmarks to add
- 02 reconsolidation / prediction-error update window (nonmonotonic mismatch).
- 03 retrieval-induced / active forgetting.
- 04 consolidation (tag-then-replay) selectivity vs salience function.
Each must obey the standard in `README.md`: declared params, controlled confounds,
honest negatives.
