# Research: Analytical Data Preparation

**Date**: 2026-07-12

## Decisions

### 1. Time Column Extraction Method

**Decision**: Use pandas `dt` accessor after converting `order_date` to datetime.

**Rationale**: The `validate_sales` function already converts date columns to datetime using `pd.to_datetime(format="mixed", errors="coerce")`. Since `prepare_sales` receives validated data, `order_date` should already be datetime. However, for defensive coding, we'll handle both string and datetime inputs.

**Alternatives considered**:
- SQL via DuckDB: Rejected — this is a pandas pipeline stage, not an analytical query
- Manual string parsing: Rejected — error-prone and unnecessary with pandas

### 2. Quarter Calculation

**Decision**: Calendar year quarters (Q1=Jan-Mar through Q4=Oct-Dec).

**Rationale**: Standard for business analytics. Pandas `dt.quarter` returns exactly this.

**Alternatives considered**:
- Fiscal year (custom start month): Rejected per clarification — no fiscal year requirement

### 3. Dimension Standardization Format

**Decision**: Title case via `str.title()` with `str.strip()` for whitespace.

**Rationale**: Title case is standard for business reports and dashboards. Matches existing `validate.py` behavior for name columns. Consistent with constitution principle of simplicity.

**Alternatives considered**:
- Lowercase: Rejected — poor readability in reports
- Uppercase: Rejected — aggressive formatting, not standard for dimension labels
- Custom mapping: Rejected — unnecessary complexity for this use case

### 4. Null Handling Strategy

**Decision**: Preserve rows with NULL time/dimension columns (no row removal).

**Rationale**: Constitution principle IV states raw data is never modified. Preserving rows allows downstream consumers to handle NULLs as needed. Aligns with FR-010 and FR-011.

**Alternatives considered**:
- Remove rows with NULLs: Rejected — data loss, violates constitution
- Default sentinel values: Rejected — misleading in aggregations

### 5. Immutability Pattern

**Decision**: Return new DataFrame, never modify input.

**Rationale**: Constitution principle IV (reproducibility) and best practices for data pipelines. Input DataFrame should remain unchanged for debugging and re-execution.

**Alternatives considered**:
- In-place modification: Rejected — violates immutability principle, makes debugging harder

### 6. Logging Format

**Decision**: Structured logging with key=value pairs (same pattern as `validate.py`).

**Rationale**: Consistent with existing codebase. Structured logs enable easy parsing for monitoring.

**Alternatives considered**:
- JSON logging: Rejected — adds complexity without current need
- Plain text: Rejected — harder to parse programmatically

## Technology Choices

| Technology | Version | Justification |
|-----------|---------|---------------|
| Python | 3.14 | Constitution requirement |
| pandas | >= 2.2, < 3 | Constitution requirement |
| pytest | >= 8.0 | Existing test framework |
| ruff | >= 0.9 | Constitution linter |

## Integration Points

- **Input**: Output of `validate_sales()` — DataFrame with 25 columns, datetime types, validated data
- **Output**: DataFrame with 28 columns (25 original + month, year, quarter)
- **Next stage**: DuckDB SQL queries for metrics (Stage 4)
