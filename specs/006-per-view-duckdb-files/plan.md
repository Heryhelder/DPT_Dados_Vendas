# Implementation Plan: Per-View DuckDB Files

**Branch**: `006-per-view-duckdb-files` | **Date**: 2026-07-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-per-view-duckdb-files/spec.md`

## Summary

Change the DuckDB persistence layer to generate one `.duckdb` file per analytical view instead of a single file containing all views. Each file contains the `sales` base table + exactly one view, enabling Tableau to connect to individual files without multi-view compatibility issues.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: pandas >= 2.2 < 3, duckdb (latest)

**Storage**: DuckDB files (one per view)

**Testing**: pytest

**Target Platform**: Local/CLI (data pipeline)

**Project Type**: library (ETL pipeline module)

**Performance Goals**: N/A — batch pipeline, ~7k rows

**Constraints**: TDD mandatory per constitution; ruff linter; no new dependencies

**Scale/Scope**: 5 views, ~7k rows, single-user pipeline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design (Phase 0)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. KISS/YAGNI | PASS | Simplest approach: loop over view definitions, create one file per view |
| II. DRY | PASS | Reuses existing `create_views.sql`; no logic duplication |
| III. TDD | PASS | Tests must be written before implementation (Red→Green→Refactor) |
| IV. Reproducible Pipeline | PASS | Idempotent per-file output; deterministic |
| V. Documentation | PASS | Views defined in SQL; pipeline documented via specs |

### Post-Design (Phase 1) — Re-evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. KISS/YAGNI | PASS | No new dependencies (`sqlparse` rejected); regex splitting is sufficient |
| II. DRY | PASS | Single source of view definitions in `create_views.sql`; no duplication |
| III. TDD | PASS | Contract defined in `contracts/store-analytics.md`; quickstart validates scenarios |
| IV. Reproducible Pipeline | PASS | Per-file validation (row count + revenue sum) ensures determinism |
| V. Documentation | PASS | data-model.md, contracts, quickstart.md all generated |

## Project Structure

### Documentation (this feature)

```text
specs/006-per-view-duckdb-files/
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
├── config.py            # Update DUCKDB_PATH to output directory
├── store.py             # Rewrite: per-view file generation
├── sql/
│   ├── create_views.sql # Unchanged (source of view definitions)
│   └── (no changes)
└── __init__.py

tests/
├── test_store.py        # Rewrite: test per-view file output
└── (other test files unchanged)
```

**Structure Decision**: Single project. Only `src/store.py` and `src/config.py` change. `src/sql/create_views.sql` is read but not modified. Tests in `tests/test_store.py` are rewritten.

## Complexity Tracking

No violations — the change is straightforward and KISS-compliant.
