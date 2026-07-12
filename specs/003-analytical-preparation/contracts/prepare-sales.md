# Contract: prepare_sales

**Date**: 2026-07-12

## Function Signature

```python
def prepare_sales(df: pd.DataFrame) -> pd.DataFrame:
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| df | pd.DataFrame | Yes | Validated DataFrame with 25 columns from `validate_sales()` |

### Input Requirements

- Must contain all 25 columns listed in `src/validate.py` → `REQUIRED_COLUMNS`
- `order_date` should be datetime64 (after validation), but string dates are handled via `pd.to_datetime(errors="coerce")`
- Dimension columns (region, sales_rep, category, sales_channel, customer_type) should be strings

### Input Validation

| Condition | Error | Message |
|-----------|-------|---------|
| DataFrame is empty | ValueError | "DataFrame de entrada está vazio" |

## Output

| Type | Description |
|------|-------------|
| pd.DataFrame | New DataFrame with 28 columns (25 input + 3 time columns) |

### Output Columns

All 25 input columns preserved, plus:

| Column | Type | Range | Null Handling |
|--------|------|-------|---------------|
| month | float64 | 1-12 | NaN if order_date invalid |
| year | float64 | 1900-2100 | NaN if order_date invalid |
| quarter | float64 | 1-4 | NaN if order_date invalid |

### Output Guarantees

- Input DataFrame is never modified (immutability)
- All original columns preserved in original order
- Time columns appended after original columns
- Dimension values converted to title case with trimmed whitespace
- NULL values preserved (no row removal)

## Side Effects

| Effect | Scope | Description |
|--------|-------|-------------|
| Logging | `src.prepare` logger | INFO level: rows_processed, columns_added, dimensions_standardized, null_dates |

## Usage Example

```python
from src.validate import validate_sales
from src.prepare import prepare_sales

# Stage 2: Validate
df_validated = validate_sales(df_raw)

# Stage 3: Prepare (this contract)
df_analytics = prepare_sales(df_validated)

# df_analytics has 28 columns, ready for DuckDB queries
```

## Error Conditions

| Error Type | Condition | Recovery |
|------------|-----------|----------|
| ValueError | Empty DataFrame | Check upstream pipeline |
| AttributeError | Missing dimension column | Ensure validate_sales ran first |
| TypeError | Non-string dimension values | Cast to string before calling |
