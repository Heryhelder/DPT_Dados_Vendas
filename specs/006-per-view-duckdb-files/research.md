# Research: Per-View DuckDB Files

**Date**: 2026-07-25

## R1: How to parse individual view definitions from SQL file

**Decision**: Use regex to split statements and extract view names — no new dependencies.

**Rationale**: The project constitution (KISS/YAGNI) prohibits adding unnecessary dependencies. `sqlparse` would be the "proper" tool, but is overkill for 5 known `CREATE OR REPLACE VIEW` statements in a controlled internal file.

**Alternatives considered**:
- `sqlparse.split()` — proper SQL parser, handles edge cases (embedded semicolons), but adds a dependency. Rejected per KISS.
- `str.split(';')` — simplest, but breaks on semicolons inside string literals. Acceptable for this controlled file but regex is only marginally more complex.

**Chosen approach**:
```python
import re

# Split into individual statements
statements = [s.strip() for s in re.split(r';\s*\n', sql_content) if s.strip()]

# Extract view names
view_names = re.findall(
    r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS',
    sql_content, re.IGNORECASE
)
```

## R2: DuckDB multi-statement execution

**Decision**: Confirmed that `duckdb.execute()` handles multiple semicolon-separated statements natively.

**Rationale**: The existing `store.py` already relies on this (lines 44-45). No changes needed to the execution model — we just need to execute each view statement against a separate DuckDB connection.

## R3: DuckDB reads DataFrames directly

**Decision**: Confirmed that `SELECT * FROM df` works in DuckDB when `df` is a Pandas DataFrame in scope.

**Rationale**: Existing code uses this pattern (line 42). Each per-view `.duckdb` file will use `CREATE TABLE sales AS SELECT * FROM df` to materialize the base table, then execute the single view DDL.

## R4: View name to filename mapping

**Decision**: Use view name directly as filename (e.g., `v_monthly_revenue` → `v_monthly_revenue.duckdb`).

**Rationale**: Simple, predictable, no mapping logic needed. View names already follow snake_case convention suitable for filenames.

## R5: `config.py` DUCKDB_PATH update

**Decision**: Change `DUCKDB_PATH` from `"output/data.duckdb"` to `"output"` (directory path).

**Rationale**: The `db_path` parameter now represents the output directory, not a single file. The constant name may be renamed to `DUCKDB_OUTPUT_DIR` for clarity, but this is optional — KISS favors keeping the name and just changing the value.
