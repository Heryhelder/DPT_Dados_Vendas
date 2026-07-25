# Implementation Plan: Pipeline Runner

**Branch**: `007-pipeline-runner` | **Date**: 2026-07-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-pipeline-runner/spec.md`

## Summary

Create a single `run_pipeline()` function that orchestrates all 5 ETL stages (extract → validate → prepare → analyze → store) with configurable input/output paths and processing summary logging.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: pandas >= 2.2 < 3, duckdb (latest) — all existing

**Storage**: DuckDB files (via existing `store_analytics()`)

**Testing**: pytest

**Target Platform**: Local/CLI (data pipeline)

**Project Type**: library (ETL pipeline module)

**Performance Goals**: N/A — batch pipeline, ~7k rows

**Constraints**: TDD mandatory per constitution; ruff linter; no new dependencies

**Scale/Scope**: 1 new function, 1 new file, ~50 lines of code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design (Phase 0)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. KISS/YAGNI | PASS | Single function, no abstractions, no new classes |
| II. DRY | PASS | Reuses all existing stage modules — no logic duplication |
| III. TDD | PASS | Tests written before implementation |
| IV. Reproducible Pipeline | PASS | Deterministic: same input → same output |
| V. Documentation | PASS | Logging provides observability per constitution |

### Post-Design (Phase 1) — Re-evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. KISS/YAGNI | PASS | Function is ~50 lines, no unnecessary abstractions |
| II. DRY | PASS | Zero new logic — pure orchestration of existing functions |
| III. TDD | PASS | Contract defined; quickstart validates scenarios |
| IV. Reproducible Pipeline | PASS | Idempotent: re-running overwrites output |
| V. Documentation | PASS | Logging + docstring + quickstart |

## Project Structure

### Documentation (this feature)

```text
specs/007-pipeline-runner/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── config.py            # DEFAULT_INPUT_PATH constant (new)
├── pipeline.py          # NEW: run_pipeline() orchestrator
├── extract.py           # Unchanged
├── validate.py          # Unchanged
├── prepare.py           # Unchanged
├── analyze.py           # Unchanged
├── store.py             # Unchanged
└── sql/                 # Unchanged

tests/
├── test_pipeline.py     # NEW: tests for run_pipeline()
└── (other test files unchanged)
```

**Structure Decision**: Single new file `src/pipeline.py` with one function. One new constant `DEFAULT_INPUT_PATH` in `config.py`. All existing modules unchanged.

## Complexity Tracking

No violations — the simplest possible orchestration.
