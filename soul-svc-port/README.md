# soul-svc-port — the M2 fix, staged for production

This directory is the **proposed** production change that moves SHI's live memory
layer from M1 (count-based, no spacing) to M2 (activation-gated, testing-effect).
It is **not deployed**. The mechanism is validated in `../tests/test_m2_spacing.py`;
deployment to the live `_memories` table and re-validation on real decay traces is
the remaining step (the repo's "shipped code" milestone, see `../STATUS.md`).

## Files
- `001_add_stability_last_recall.sql` — schema migration (adds `stability`,
  `last_recall_at`; seeds + backfills, non-destructively).
- `hybrid_search_m2.py` — the three changes against `soul-svc/hybrid_search.py`:
  the `SELECT`, the Phase-4 scoring factor, and the recall-event update spec.

## Why this is staged, not hot-applied
The integrity standard this whole project runs on is *demonstrate, don't assert*.
M2 is demonstrated in simulation (the test passes), but **whether it reproduces
the human curves at SHI's real scale and access patterns has not been shown** —
that requires running it against production logs, which is exactly the claim we
refuse to assert in advance. Hot-editing the live memory the assistant depends on,
and declaring victory, would be the failure mode the essay is about.

## Deploy + validation checklist (the path to "here's the code")
1. Apply `001_*.sql` on **staging**; confirm backfill preserves current ranking
   within tolerance on a sample of queries.
2. Wire the three changes from `hybrid_search_m2.py`; put the new retrievability
   factor behind an independently-toggleable flag (matching the existing
   `decay`/`hyde`/`rerank` flags) so it can be A/B'd and rolled back.
3. Move the recall-event update **server-side** into the recall RPC so the
   read-modify-write of `stability` + `last_recall_at` is transactional.
4. Re-run `benchmarks/forgetting_spacing.py`-style analysis **against real
   production decay traces** (not the simulation). Publish the result here.
5. Only if it reproduces the spacing effect on real data does the repo's status
   line move from *aspirational* to *here's the code*. If it does not, that is a
   published negative, not a quiet rollback.

## Parameters
`H0 = 48 h` (initial half-life), `F = 3.0` (max corroboration factor). These are
placeholders carried over from the benchmark; before production they must be
re-derived against real retention data, with the fit reported.
