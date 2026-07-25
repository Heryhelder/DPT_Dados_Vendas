# Feature Specification: Pipeline Runner

**Feature Branch**: `007-pipeline-runner`

**Created**: 2026-07-25

**Status**: Draft

**Input**: User description: "gere um método que irá rodar todo o pipeline que criamos. Esse método deve carregar o arquivo electronics_sales_raw.csv, rodar todo o processamento em cima desse arquivo e gerar as views no final"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Full Pipeline End-to-End (Priority: P1)

As a data analyst, I want to run a single command that loads the raw CSV, processes it through all pipeline stages, and generates the per-view DuckDB files, so that I can produce analytical outputs without manually calling each stage.

**Why this priority**: This is the core deliverable — a single entry point that orchestrates the entire 5-stage pipeline (extract → validate → prepare → analyze → store).

**Independent Test**: Can be fully tested by calling the pipeline function and verifying that 5 `.duckdb` files exist in the output directory with correct data.

**Acceptance Scenarios**:

1. **Given** the raw CSV file exists at `data/electronics_sales_raw.csv`, **When** the pipeline runner is called, **Then** 5 `.duckdb` files are created in the output directory.
2. **Given** the pipeline has completed, **When** the `sales` table is queried in any output file, **Then** it contains valid analytical data (row count > 0, `SUM(net_revenue)` > 0).
3. **Given** the pipeline has completed, **When** each view is queried, **Then** it returns results without errors.

---

### User Story 2 - Configurable Input and Output Paths (Priority: P2)

As a developer, I want the pipeline runner to accept custom input file and output directory paths, so that it can be used with different datasets or output locations without modifying source code.

**Why this priority**: Enables flexibility for testing, different environments, and future datasets.

**Independent Test**: Can be tested by calling the pipeline with custom paths and verifying output appears in the specified location.

**Acceptance Scenarios**:

1. **Given** the pipeline runner is called with a custom input path, **When** it completes, **Then** the output is generated from the specified file.
2. **Given** the pipeline runner is called with a custom output directory, **When** it completes, **Then** the `.duckdb` files appear in that directory.

---

### User Story 3 - Pipeline Reports Processing Summary (Priority: P3)

As a data analyst, I want the pipeline to log a summary of what was processed (row counts, metrics), so that I can quickly verify the output without manually querying each file.

**Why this priority**: Improves observability and trust in the pipeline output.

**Independent Test**: Can be tested by running the pipeline and checking that log output includes row count and revenue summary.

**Acceptance Scenarios**:

1. **Given** the pipeline has completed, **When** log output is reviewed, **Then** it includes the number of rows processed and total net revenue.
2. **Given** the pipeline has completed, **When** log output is reviewed, **Then** it includes the number of `.duckdb` files created and processing duration.

---

### Edge Cases

- What happens when the input CSV file does not exist? The pipeline MUST raise a clear error indicating the file was not found.
- What happens when the input CSV is empty or contains only invalid rows? The pipeline MUST raise a ValueError (from the store stage).
- What happens when the output directory already contains `.duckdb` files from a previous run? The pipeline MUST overwrite them (idempotent behavior).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single function that runs all 5 pipeline stages sequentially: extract, validate, prepare, analyze, store.
- **FR-002**: The pipeline runner MUST load `data/electronics_sales_raw.csv` by default.
- **FR-003**: The pipeline runner MUST accept an optional input file path parameter to override the default.
- **FR-004**: The pipeline runner MUST accept an optional output directory path parameter (default: `"output"`).
- **FR-005**: The pipeline runner MUST call each stage in order: `extract_csv()` → `validate_sales()` → `prepare_sales()` → `analyze_sales()` → `store_analytics()`.
- **FR-006**: The pipeline runner MUST propagate errors from any stage — if a stage fails, the pipeline stops and reports the error.
- **FR-007**: The pipeline runner MUST log a processing summary after completion: rows processed, total net revenue, number of files created, duration.
- **FR-008**: The pipeline runner MUST return the output directory path for programmatic use.

### Key Entities

- **Pipeline Runner**: A function that orchestrates the 5-stage ETL pipeline from CSV input to DuckDB output.
- **Pipeline Stages**: extract → validate → prepare → analyze → store (existing modules, no changes needed).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the pipeline runner produces 5 `.duckdb` files in the output directory.
- **SC-002**: The pipeline runner completes without errors for the default input file.
- **SC-003**: The pipeline runner processes all valid rows from the input CSV (row count matches extraction output).
- **SC-004**: The pipeline runner logs a summary with row count and revenue within 5 seconds of completion.
- **SC-005**: The pipeline runner can be called with custom input/output paths and produces correct output.

## Assumptions

- The 5 pipeline stages (`extract`, `validate`, `prepare`, `analyze`, `store`) are already implemented and working.
- The default input file is `data/electronics_sales_raw.csv` (approximately 7,000 rows).
- The default output directory is `"output"`.
- The pipeline runner is a Python function, not a CLI script (CLI can be added later).
- The `analyze_sales()` function uses default COGS rules and tax rate (no custom parameters needed for v1).
- The pipeline runner does not need to handle concurrent executions.
