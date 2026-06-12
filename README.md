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

## The trajectory

This repo exists to move, in public and in order:

1. **here is the gap** — benchmark 01, done.
2. **here is the aspirational fix** — M2: gate the corroboration increment on
   retrievability at recall, and let a successful recall reset/extend the decay
   clock (testing effect). The spacing effect falls out. *Not yet built in
   production.* See `STATUS.md`.
3. **here is the code that closes it** — the M2 mechanism shipped into the live
   memory layer, re-run against this benchmark on real data, demonstrated not
   asserted.

## Run

```
pip install -r requirements.txt
python benchmarks/forgetting_spacing.py     # writes results/forgetting_spacing.png
```

## License

TODO — choose before public release (the essay's ethos favors an open,
permissive license so the standard can be adopted freely).
