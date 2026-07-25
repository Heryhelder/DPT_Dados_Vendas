# Contract: store_analytics Function Interface

**Date**: 2026-07-25

## Function Signature

```python
def store_analytics(df: pd.DataFrame, db_path: str | Path) -> None:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | Analytical DataFrame with 34 columns (output of `analyze_sales()`) |
| `db_path` | `str \| Path` | **Output directory** where per-view `.duckdb` files will be created |

### Behavior

1. Creates `db_path` directory if it does not exist
2. For each view defined in `src/sql/create_views.sql`:
   - Creates `{db_path}/{view_name}.duckdb`
   - Each file contains:
     - `sales` table (34 columns, populated from `df`)
     - One view (the corresponding `CREATE OR REPLACE VIEW` statement)
3. Validates each generated `.duckdb` file:
   - Row count matches `len(df)`
   - `SUM(net_revenue)` matches `df["net_revenue"].sum()` (tolerance: 0.01)

### Raises

| Exception | Condition |
|-----------|-----------|
| `ValueError` | `df` is empty |
| `ValueError` | Row count mismatch between DataFrame and any `.duckdb` file |
| `ValueError` | Revenue sum mismatch between DataFrame and any `.duckdb` file |

### Side Effects

- Creates/overwrites `.duckdb` files in the output directory
- Creates the output directory if it does not exist

### Idempotency

Re-running with the same `df` and `db_path` produces identical output files.

## Example Usage

```python
from src.store import store_analytics

# Output directory — creates 5 .duckdb files inside
store_analytics(analytical_df, "output")
# Result:
#   output/v_monthly_revenue.duckdb
#   output/v_store_performance.duckdb
#   output/v_category_sales.duckdb
#   output/v_top_products.duckdb
#   output/v_sales_summary.duckdb
```
