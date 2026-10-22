# AGENTS.md

Instructions for AI coding agents working in this repository.

## What this is

Three runnable benchmarks that hold synthetic-memory update rules to memory-lab standards, with
reference models for the proposed fixes. It is a simulation harness: every result is a fact about a
simulated rule, not about biology and not a measurement of a deployed system.

## Read in this order

1. `README.md`: the standard, the "How it works" diagram, what is in this repo and what is not, and
   the three findings.
2. `STATUS.md`: where each claim sits (gap, reference fix, shipped code) and the backlog.
3. `reference/m2_memory.py` and `reference/m3_reconsolidation.py`: the M2 and M3 models.
4. `benchmarks/`: the three benchmark scripts; `tests/` holds 3 tests per benchmark.
5. `soul-svc-port/README.md`: the staged, undeployed production change for M2.

## What you can and cannot see

- You can run and check everything in `benchmarks/`, `reference/`, `tests/` and `soul-svc-port/`.
- The production memory service the findings describe (`soul-svc/hybrid_search.py`, the M1 rule)
  is in a private repository. Its code is quoted in README.md and STATUS.md; you cannot check
  those quotes from here.
- `soul-svc-port/` is written against that private service. Nothing in this repo imports it and
  no test covers it.
- `benchmarks/forgetting_spacing.py` has its own inline copy of the M1 and M2 equations; it does
  not import `reference/m2_memory.py`. `tests/test_m2_spacing.py` tests the reference model.

## The only numbers to trust

- Declared parameters: `H0_DEFAULT` and `F_DEFAULT` in `reference/m2_memory.py`; `H0`, `F` and `RI`
  in `benchmarks/forgetting_spacing.py`; `PE_LOW`, `PE_HIGH` and `D_MAX` in
  `reference/m3_reconsolidation.py`; `LAMBDA` and `TARGET_R` in `benchmarks/hsam_rehearsal.py`.
- Benchmark results: what a fresh run of each script prints. The README quotes the 2026-10-22 run;
  the checked-in figures in `results/` are the published record of each benchmark.
- Test count: `python -m pytest -v tests` (9 on 2026-10-22).

## Quickstart

```bash
python benchmarks/forgetting_spacing.py     # prints the fits and the spacing result
```

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt pytest
```

## Test

```bash
python -m pytest -v tests
```

Passing looks like `9 passed` (3 per benchmark on 2026-10-22). CI (`.github/workflows/tests.yml`)
runs the same command on Python 3.12.

## Conventions

- Every benchmark obeys the standard in README.md: parameter count declared before looking at the
  human data, confounds controlled by design, the same parameter count across compared models, and
  failures published as results.
- A new benchmark comes with tests that would fail if the claimed effect were absent.
- Dependencies stay numpy, scipy, matplotlib (and pytest for tests).
- If an import between `reference/`, `benchmarks/` and `tests/` changes, update the README diagram
  in the same change.
- No em-dashes in docs. If README.md, STATUS.md or soul-svc-port/README.md changes, regenerate
  `llms-full.txt` in the same change.

## Do not

- Commit a regenerated figure in `results/` unless the benchmark that draws it changed. The figures
  are the published record of each run.
- Tune a parameter after looking at the human data, or describe a simulated result as a finding
  about biology or about a deployed system.
- Describe `soul-svc-port/` as deployed. It is staged until STATUS.md says otherwise.
- Commit secrets, hostnames, internal paths or personal emails. The benchmarks print an absolute
  output path; never paste that line into docs.

## Done means

`python -m pytest -v tests` passes, each changed benchmark runs and prints its numbers, and any
number quoted in README.md or STATUS.md matches a fresh run.
