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

### aspirational fix (NOT BUILT)
Move the production model M1 → M2:
1. **Activation-gated corroboration.** Replace the count-only recall boost with a
   stability gain that depends on retrievability at recall time — larger gain when
   the memory was nearly forgotten (gain ∝ 1−R, realized with prob ≈ R).
2. **Recall resets/extends the decay clock.** Anchor decay to `last_recall`, not
   only `created_at`, and lengthen the half-life on each successful retrieval — the
   testing effect. Spacing then falls out of (1)+(2) together.
3. **Per-memory stability is stored and updated**, not recomputed from a count at
   query time, so the trajectory of a memory's strength is itself inspectable.

Open question before shipping: whether (1)+(2) at SHI's scale and access patterns
actually reproduce the human curves — to be **demonstrated** by re-running
benchmark 01 against real logs, not assumed.

### shipped code (NOT STARTED)
M2 implemented in the live memory layer; benchmark 01 re-run on production decay
traces; results published here next to the simulation.

## Backlog — benchmarks to add
- 02 reconsolidation / prediction-error update window (nonmonotonic mismatch).
- 03 retrieval-induced / active forgetting.
- 04 consolidation (tag-then-replay) selectivity vs salience function.
Each must obey the standard in `README.md`: declared params, controlled confounds,
honest negatives.
