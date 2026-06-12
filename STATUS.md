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

## Benchmark 02 — HSAM via rehearsal (DONE, 2026-06-11)
Age-independent recall (the HSAM hallmark) is the behavioral limit of M2 + spaced
rehearsal over a lossless store. `benchmarks/hsam_rehearsal.py` + `tests/test_hsam.py`
(3/3): M2+rehearsal flat across 3 years (3y/1h ratio = 1.00) with only ~13
rehearsals; M1+rehearsal collapses to ~5e-12 (creation-anchored decay, never reset).
Reachable under M2, unreachable under production M1 — a second confirmation of the
benchmark-01 gap. No production change needed beyond the M2 deploy already staged;
an optional "HSAM tier" (non-decaying / heavily-rehearsed autobiographical tier)
is a deliberate trade, not a default (forgetting is adaptive).

## Benchmark 03 — reconsolidation / prediction-error window (DONE, 2026-06-11)
Located gap: M1 (production) AND the M2 fix have NO in-place belief revision —
update fraction = 0 across all prediction error. The system can only append
corrections, never correct a stored memory in place when contradicting evidence
arrives. `benchmarks/reconsolidation.py` + `tests/test_reconsolidation.py` (3/3).
M3 (`reference/m3_reconsolidation.py`) is the minimal fix: a prediction-error-gated
update, nonmonotonic (necessary PE to destabilize; too much PE → new memory). The
inverted-U is DESIGNED to match known bounds (Sevenster 2013/2014; Sinclair &
Barense 2019), so the window shape is a consistency check, not a discovery — the
result is the gap. NOT yet in `soul-svc-port/` (needs a content/embedding PE
comparison at retrieval); tracked as future work, a distinct change from the M2
durability deploy.

## Backlog — benchmarks to add
- 04 retrieval-induced / active forgetting.
- 05 consolidation (tag-then-replay) selectivity vs salience function.
- port: M3 (in-place reconsolidation) into soul-svc — separate, larger change.
Each must obey the standard in `README.md`: declared params, controlled confounds,
honest negatives.
