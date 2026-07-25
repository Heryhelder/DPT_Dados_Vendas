# Research: Pipeline Runner

**Date**: 2026-07-25

## R1: Where to place the pipeline runner function

**Decision**: New file `src/pipeline.py` with a single function `run_pipeline()`.

**Rationale**: Keeps the orchestrator separate from individual stages. Each stage module stays focused on its single responsibility. KISS — one file, one function.

**Alternatives considered**:
- Adding `run_pipeline()` to `config.py` — rejected, config should hold constants only
- Adding `run_pipeline()` to `store.py` — rejected, store is the last stage, not the orchestrator
- Adding `__main__.py` entry point — deferred to future feature (CLI not in scope)

## R2: Default input file path

**Decision**: Add `DEFAULT_INPUT_PATH = "data/electronics_sales_raw.csv"` to `src/config.py`.

**Rationale**: Centralizes the default path alongside other configuration constants (`DEFAULT_DELIMITER`, `DEFAULT_ENCODING`). Consistent with existing pattern.

## R3: How to handle stage errors

**Decision**: Let exceptions propagate naturally — no try/except wrapping in the pipeline runner.

**Rationale**: Each stage already raises appropriate exceptions (`FileNotFoundError`, `ValueError`, etc.). Wrapping would add complexity without value. The caller can catch exceptions as needed. KISS.

## R4: Logging approach

**Decision**: Use the existing `logging` module with `logger.info()` for the processing summary. Log: input file, rows after extraction, rows after validation, total net revenue, number of files created, duration.

**Rationale**: Consistent with all other modules that already use `logging.getLogger(__name__)`. Constitution Principle V requires structured logging for observability.
