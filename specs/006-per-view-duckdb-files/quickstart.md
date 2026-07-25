# Quickstart: Per-View DuckDB Files

**Date**: 2026-07-25

## Prerequisites

- Python environment with `pandas`, `duckdb` installed
- Valid analytical DataFrame (output of `analyze_sales()`)

## Validation Scenarios

### Scenario 1: Generate per-view files

```bash
# From project root
python -c "
import pandas as pd
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales
from src.store import store_analytics

df = extract_csv('data/electronics_sales_raw.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
store_analytics(df, 'output')
"
```

**Expected outcome**: 5 `.duckdb` files in `output/` directory:
- `v_monthly_revenue.duckdb`
- `v_store_performance.duckdb`
- `v_category_sales.duckdb`
- `v_top_products.duckdb`
- `v_sales_summary.duckdb`

### Scenario 2: Verify each file is independently queryable

```bash
python -c "
import duckdb

views = [
    'v_monthly_revenue', 'v_store_performance', 'v_category_sales',
    'v_top_products', 'v_sales_summary'
]
for v in views:
    con = duckdb.connect(f'output/{v}.duckdb', read_only=True)
    result = con.execute(f'SELECT COUNT(*) FROM {v}').fetchone()
    print(f'{v}: {result[0]} rows')
    con.close()
"
```

**Expected outcome**: Each view returns rows without errors.

### Scenario 3: Verify data consistency across files

```bash
python -c "
import duckdb

views = [
    'v_monthly_revenue', 'v_store_performance', 'v_category_sales',
    'v_top_products', 'v_sales_summary'
]
counts = {}
for v in views:
    con = duckdb.connect(f'output/{v}.duckdb', read_only=True)
    counts[v] = con.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
    con.close()

assert len(set(counts.values())) == 1, f'Inconsistent counts: {counts}'
print(f'All files have {list(counts.values())[0]} rows')
"
```

**Expected outcome**: All 5 files contain the same row count.

### Scenario 4: Run existing tests

```bash
pytest tests/test_store.py -v
```

**Expected outcome**: All tests pass (tests will be updated for per-file behavior).

### Scenario 5: Tableau connectivity (manual)

Open Tableau Desktop → Connect → DuckDB → select any `output/v_*.duckdb` file → verify the view data loads without errors.

**Expected outcome**: Tableau reads the view data successfully.
