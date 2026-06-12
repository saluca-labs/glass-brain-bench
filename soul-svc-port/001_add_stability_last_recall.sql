-- soul-svc migration (PROPOSED — not yet applied): M2 activation-gated memory.
--
-- Adds the two columns the M2 model needs on _memories:
--   stability       per-memory half-life (hours), updated on each recall
--   last_recall_at  anchor for decay (the testing effect: decay measured from
--                   the last recall, not from creation)
--
-- DO NOT run against production until validated on staging and reviewed.
-- See ./README.md for the full deploy + validation checklist.

ALTER TABLE _memories
  ADD COLUMN IF NOT EXISTS stability      double precision NOT NULL DEFAULT 48.0,  -- = H0 (half-life hrs)
  ADD COLUMN IF NOT EXISTS last_recall_at timestamptz;

-- Seed decay anchor for existing rows.
UPDATE _memories SET last_recall_at = created_at WHERE last_recall_at IS NULL;

-- Non-destructive backfill: approximate stability from existing recall_count so
-- ranking is roughly preserved at deploy time. Monotonic in count; TUNABLE — the
-- constants below should be re-derived against real decay traces, not assumed.
UPDATE _memories
  SET stability = 48.0 * (1.0 + 0.5 * ln(1.0 + recall_count))
  WHERE recall_count > 0;

-- NOTE: a forward decision is required at the recall-increment site (wherever
-- recall_count is bumped on access). That handler must ALSO, atomically:
--   R := pow(2, -extract(epoch from (now() - last_recall_at))/3600 / stability);
--   stability      := stability * (1 + (F-1) * R * (1 - R));   -- F = 3.0
--   last_recall_at := now();
-- i.e. gate the stability gain on retrievability-at-recall, then reset the clock.
-- See ./hybrid_search_m2.py for the reference Python equivalents.
