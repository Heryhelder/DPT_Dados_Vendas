# Quickstart: Pipeline Runner

**Date**: 2026-07-25

## Prerequisites

- Python environment with `pandas`, `duckdb` installed
- Raw CSV file at `data/electronics_sales_raw.csv`

## Validation Scenarios

### Scenario 1: Run pipeline with defaults

```bash
cd "/c/Users/Carlo/Documents/Projetos/DPT - Dados_Vendas"
python3 -c "
from src.pipeline import run_pipeline
output = run_pipeline()
print(f'Output: {output}')
"
```

**Expected outcome**: 5 `.duckdb` files created in `output/` directory. Log output shows rows processed, revenue, and duration.

### Scenario 2: Verify output files

```bash
python3 -c "
import os
files = sorted(f for f in os.listdir('output') if f.endswith('.duckdb'))
print(f'Files: {len(files)}')
for f in files:
    print(f'  {f}')
"
```

**Expected outcome**: 5 files listed: `v_category_sales.duckdb`, `v_monthly_revenue.duckdb`, `v_sales_summary.duckdb`, `v_store_performance.duckdb`, `v_top_products.duckdb`.

### Scenario 3: Run with custom paths

```bash
python3 -c "
from src.pipeline import run_pipeline
output = run_pipeline(
    input_path='data/electronics_sales_raw.csv',
    output_dir='custom_output',
)
print(f'Output: {output}')
"
```

**Expected outcome**: 5 `.duckdb` files created in `custom_output/` directory.

### Scenario 4: Run tests

```bash
pytest tests/test_pipeline.py -v
```

**Expected outcome**: All tests pass.

### Scenario 5: Run full test suite

```bash
pytest tests/ -v
```

**Expected outcome**: All tests pass (no regressions).
