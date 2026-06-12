# glass-brain-bench

Open testing standards for synthetic-memory claims, companion to the essay
**"The Glass Brain"** (Saluca, 2026).

The essay argues something deliberately small: a legible, fully-instrumented
synthetic memory *could* be a cheap hypothesis-generator for the science of
memory — **only if** its claims are held to the same standard a memory lab would
hold them to. This repository is where that standard is enforced in runnable
code, so the claims can be re-run, attacked, and extended by anyone, rather than
taken on the author's word.

## The standard

Every benchmark here obeys the same rules. They exist to stop a memory model
from looking better than it is.

1. **Declared parameter count, fixed before looking at the human data.** No
   fitting a model to a phenomenon and then calling the fit a prediction.
2. **Confounds controlled by design, not by hope.** Spacing tests hold recency
   fixed; otherwise a "spacing effect" is just a recency effect in disguise.
3. **Same parameter count across compared models**, differing only in the
   mechanism, so any difference is attributable to the mechanism and not to one
   model having more freedom.
4. **Honest negatives are results.** A rule that fails a benchmark has *located a
   gap* in the artifact. That is the point. We publish the failures.
5. **No borrowed credibility.** A result inside a simulated artifact is a fact
   about the artifact, never evidence about biology, until a wet lab confirms it.

## Benchmarks

| # | file | tests | status |
|---|------|-------|--------|
| 01 | `benchmarks/forgetting_spacing.py` | Ebbinghaus forgetting curve + spacing effect | **run** — see finding below |
| 02 | `benchmarks/hsam_rehearsal.py` | HSAM: age-independent recall via rehearsal | **run** — M2-only, see finding below |
| 03 | `benchmarks/reconsolidation.py` | reconsolidation: prediction-error update window | **run** — located gap, see finding below |

### Benchmark 01 finding (2026-06-11)

Two models, same two parameters, differing only in the update rule:

- **M1 "count-based"** — a corroboration multiplies stability by a fixed factor,
  independent of the memory's current state.
- **M2 "activation-gated"** — the gain from a corroboration depends on how
  retrievable the memory was when it was corroborated (expected gain ∝ R·(1−R)).

Result: a flexible decay fits the forgetting curve (not discriminating; a single
exponential actually *fails* the heavy tail, a power-law fits). The discriminating
test is spacing, with recency controlled: **M1 produces no spacing effect at all**
(stability depends on corroboration *count*, not timing); **only M2 produces the
spacing effect and its nonmonotonic optimal lag.**

This is what the production system does. SHI's live memory model
(`soul-svc/hybrid_search.py`) scores retrievability as

```
score = exp(-λ · age_since_encoding) × (1 + ln(1 + recall_count) / 10) × tier
```

— a single fixed-timescale decay anchored to encoding, times a recall term that
is a function of **count alone**. That is M1, literally. So the production system,
as built, reproduces neither the spacing effect nor the shape of the forgetting
curve. The benchmark located a real, confirmed gap in the artifact.

> Scope: this is a memory-*retrieval ranking* function, engineered for search
> relevance, not built to model human retention. The claim is not "SHI tried to be
> brain-like and failed." The claim is narrower: the documented rule
> ("persistence is a function of corroboration") is, in code, literally a function
> of corroboration *count*, and that rule does not reproduce these phenomena.

### Benchmark 02 finding (2026-06-11)

Motivated by the 60 Minutes "Endless Memory" segment on HSAM (people who recall
essentially every day of their life, *age-independently*). The claim under test:
HSAM is not special storage — it is the behavioral limit of **M2 + chronic
rehearsal** over a lossless store, because under M2 each recall resets the decay
clock and grows stability, so a memory rehearsed on a spaced schedule becomes
permanently retrievable.

Result (`tests/test_hsam.py`, 3/3): under M2, a rehearsed memory's retrievability
is **age-independent** — a 3-year-old memory scores the same as a fresh one (3y/1h
ratio = 1.00) — and it takes only **~13 well-timed rehearsals over 3 years**
(an expanding/spaced schedule), not thousands. The same rehearsal under **M1
(production)** decays to ~5e-12 at 3 years: because M1's decay is anchored to
*encoding* and never reset by recall, rehearsal cannot sustain old memories. So
HSAM-like total recall is reachable under M2 and unreachable under the live rule —
which both demonstrates the claim and re-confirms the production gap from a second
angle.

Scope: this mimics the *coverage* (age-independent retrievability), not the
reconstructive re-living human HSAM subjects describe — and forgetting is adaptive,
so a non-decaying tier is a deliberate trade, not a free upgrade.

### Benchmark 03 finding (2026-06-11)

Human memory revises a stored belief at retrieval only within a *window* of
prediction error: none if the reminder matches (nothing to learn), maximal at
moderate mismatch, and none again if the mismatch is large enough to be treated as
a new event (Sevenster 2013/2014; Sinclair & Barense 2019).

The honest finding here is **not** "we reproduced the inverted-U" — that curve is
*designed* into M3 to match those boundary conditions. The finding is the **located
gap**: SHI today (M1) **and** the M2 durability/spacing fix have **no in-place
revision at all** (`tests/test_reconsolidation.py`, 3/3 — M1/M2 update fraction = 0
across the entire PE range). A recall may strengthen a memory (M2) or bump a count
(M1), but it never moves a stored belief toward contradicting evidence. So the
system can only *append* corrections, never *correct in place* — stale or wrong
memories persist. Reconsolidation is a distinct gap from forgetting/spacing, and
M3 (`reference/m3_reconsolidation.py`) is the minimal mechanism that closes it: a
prediction-error-gated update, nonmonotonic as biology requires (necessary PE to
destabilize; too much PE → new memory, old one intact).

This one is **not yet in `soul-svc-port/`** — it is a larger change (it needs a
content/embedding comparison at retrieval to compute PE), tracked as future work.

## The trajectory

This repo exists to move, in public and in order:

1. **here is the gap** — benchmark 01, done.
2. **here is the aspirational fix** — M2: gate the corroboration increment on
   retrievability at recall, and let a successful recall reset/extend the decay
   clock (testing effect). The spacing effect falls out. **Reference
   implementation built and validated** (`reference/m2_memory.py`, `tests/` —
   3/3 passing); production deploy **staged** in `soul-svc-port/`, *not yet
   applied*. See `STATUS.md`.
3. **here is the code that closes it** — the M2 mechanism shipped into the live
   memory layer, re-run against this benchmark on **real data**, demonstrated not
   asserted. Not done.

## Run

```
pip install -r requirements.txt
python benchmarks/forgetting_spacing.py     # writes results/forgetting_spacing.png
```

## License

Apache License 2.0 — Copyright 2026 Saluca Labs, LLC. See `LICENSE` and `NOTICE`.

Apache-2.0 is chosen deliberately over a more minimal license: its explicit
patent grant lets anyone adopt and build on this testing standard without
ambiguity about Saluca's patent portfolio. The standard is only useful if it is
genuinely free to take.
