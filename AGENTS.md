# AGENTS.md

Instructions for AI coding agents working in this repository.

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
- No em-dashes in docs. If README.md, STATUS.md or soul-svc-port/README.md changes, regenerate
  `llms-full.txt` in the same change.

## Do not

- Commit a regenerated figure in `results/` unless the benchmark that draws it changed. The figures
  are the published record of each run.
- Tune a parameter after looking at the human data, or describe a simulated result as a finding
  about biology or about a deployed system.
- Commit secrets, hostnames, internal paths or personal emails. The benchmarks print an absolute
  output path; never paste that line into docs.

## Done means

`python -m pytest -v tests` passes, each changed benchmark runs and prints its numbers, and any
number quoted in README.md or STATUS.md matches a fresh run.
