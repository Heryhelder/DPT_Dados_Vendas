# Feature Specification: Per-View DuckDB Files

**Feature Branch**: `006-per-view-duckdb-files`

**Created**: 2026-07-25

**Status**: Draft

**Input**: User description: "precisamos fazer com que cada view se torne um arquivo duckdb para evitar problemas no Tableau. Ao invés de salvarmos um único arquivo com todas as views, precisamos separar cada view em um arquivo individual"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Individual DuckDB Files Per View (Priority: P1)

As a data analyst, I want each analytical view to be saved as a separate `.duckdb` file so that Tableau can connect to each view independently without compatibility issues caused by multiple views in a single database file.

**Why this priority**: This is the core motivation for the feature. Tableau has known issues when connecting to a DuckDB file containing multiple views — separating them eliminates these problems entirely and is the primary deliverable.

**Independent Test**: Can be fully tested by running the storage stage and verifying that 5 individual `.duckdb` files exist in the output directory, each containing exactly one view and one underlying table.

**Acceptance Scenarios**:

1. **Given** the analytical pipeline has produced a DataFrame, **When** the storage stage completes, **Then** 5 separate `.duckdb` files are created in the output directory (one per view: `v_monthly_revenue.duckdb`, `v_store_performance.duckdb`, `v_category_sales.duckdb`, `v_top_products.duckdb`, `v_sales_summary.duckdb`).
2. **Given** a `.duckdb` file for a specific view, **When** Tableau connects to it, **Then** it can read the view data without errors.
3. **Given** one of the per-view `.duckdb` files, **When** queried, **Then** it contains both the `sales` base table and exactly one view.

---

### User Story 2 - Backward-Compatible Storage Interface (Priority: P2)

As a developer, I want the storage function to maintain a clean interface that accepts a DataFrame and output path, so that existing pipeline code requires minimal changes to adopt the new per-file strategy.

**Why this priority**: Ensures the change integrates smoothly with the existing 5-stage pipeline without breaking the current contract between `analyze.py` and `store.py`.

**Independent Test**: Can be tested by calling the storage function with the same signature as today and verifying the new output structure is produced.

**Acceptance Scenarios**:

1. **Given** the existing `store_analytics(df, db_path)` function, **When** called with the same arguments as today, **Then** it produces the per-view `.duckdb` files instead of a single file, without raising errors.
2. **Given** the storage function output, **When** inspected, **Then** each `.duckdb` file is independently queryable.

---

### User Story 3 - Data Integrity Across All View Files (Priority: P3)

As a data analyst, I want every per-view `.duckdb` file to contain identical underlying `sales` data, so that metrics are consistent regardless of which file Tableau connects to.

**Why this priority**: Consistency across files is critical for trustworthy reporting. If different files contain different data, analysts would get conflicting numbers.

**Independent Test**: Can be tested by querying the `sales` table in each `.duckdb` file and verifying that `COUNT(*)` and `SUM(net_revenue)` are identical across all files.

**Acceptance Scenarios**:

1. **Given** 5 per-view `.duckdb` files have been generated, **When** the `sales` table is queried in each file, **Then** the row count and `SUM(net_revenue)` are identical across all files.
2. **Given** a per-view `.duckdb` file, **When** the view is queried, **Then** the results match the expected output of the corresponding SQL view definition.

---

### Edge Cases

- What happens when the output directory does not exist? The storage stage MUST create it automatically (`mkdir -p`).
- What happens when a `.duckdb` file already exists from a previous run? The storage stage MUST overwrite it completely (idempotent behavior via `CREATE OR REPLACE`).
- What happens when the DataFrame is empty? The storage stage MUST still create all `.duckdb` files with the correct schema (0-row table and empty view results).
- What happens when the `src/sql/create_views.sql` file contains a view definition that references a missing column? The storage stage MUST raise a clear error identifying the problematic view.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create one `.duckdb` file per analytical view defined in `src/sql/create_views.sql`.
- **FR-002**: Each `.duckdb` file MUST contain the `sales` base table (required for the view to be queryable) and exactly one view.
- **FR-003**: The view name MUST be used as the `.duckdb` filename (e.g., `v_monthly_revenue` → `v_monthly_revenue.duckdb`).
- **FR-004**: Each `.duckdb` file MUST be independently queryable — no cross-file dependencies.
- **FR-005**: The `sales` table data MUST be identical across all generated `.duckdb` files.
- **FR-006**: The storage stage MUST remain idempotent — re-running with the same data produces identical `.duckdb` files.
- **FR-007**: System MUST verify data integrity (row count and `SUM(net_revenue)`) for each generated `.duckdb` file against the source DataFrame.
- **FR-008**: The existing `store_analytics(df, db_path)` function signature MUST remain compatible — `db_path` now refers to the output directory rather than a single file path.
- **FR-009**: System MUST create the output directory if it does not exist.
- **FR-010**: Each `.duckdb` file MUST contain both the `sales` table and the corresponding view so that Tableau can connect and read data directly.

### Key Entities

- **Per-View DuckDB File**: An individual DuckDB database file containing the `sales` base table and one analytical view. Named after the view (e.g., `v_monthly_revenue.duckdb`).
- **Sales Table**: The base analytical table with 34 columns (product, sales, financial metrics). Duplicated across all per-view files to ensure independence.
- **Analytical View**: A virtual SQL view over the `sales` table, defined in `src/sql/create_views.sql`. Each view groups and aggregates data for a specific analytical purpose.
- **View Definitions**: The 5 SQL view definitions currently in `src/sql/create_views.sql`: `v_monthly_revenue`, `v_store_performance`, `v_category_sales`, `v_top_products`, `v_sales_summary`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After running the storage stage, exactly 5 `.duckdb` files exist in the output directory (one per view).
- **SC-002**: Each `.duckdb` file can be opened independently in Tableau without errors.
- **SC-003**: All 5 `.duckdb` files contain identical `sales` table data (verified by matching row count and `SUM(net_revenue)`).
- **SC-004**: The storage stage completes without errors for valid input DataFrames.
- **SC-005**: Re-running the storage stage with the same data produces the same output (idempotency).

## Assumptions

- Tableau's DuckDB connector can read individual `.duckdb` files without issues — the per-file approach is specifically motivated by known Tableau compatibility problems with multiple views in a single file.
- The 5 views defined in `src/sql/create_views.sql` are the complete and final set of views to be separated.
- The `sales` base table schema (34 columns) remains unchanged.
- Each `.duckdb` file containing the full `sales` table is acceptable in terms of disk space (the dataset is relatively small — ~7,000 rows).
- The output directory path (`db_path` parameter) is the parent directory where per-view files will be created, replacing the current single-file path semantics.
- The `config.py` `DUCKDB_PATH` constant may need updating to reflect the new directory-based output.
