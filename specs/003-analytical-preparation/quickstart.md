# Quickstart: Analytical Data Preparation

**Date**: 2026-07-12

## Prerequisites

- Python 3.14 with pandas >= 2.2
- Project dependencies installed: `pip install -e ".[dev]"`
- Validated DataFrame from Stage 2 (`validate_sales`)

## Validation Scenarios

### Scenario 1: Basic Time Column Extraction

```python
import pandas as pd
from src.prepare import prepare_sales

# Create minimal valid DataFrame
df = pd.DataFrame([{
    "order_id": 1,
    "order_date": "2024-06-15",
    "region": "south",
    # ... other 23 columns
}])

result = prepare_sales(df)

# Verify
assert "month" in result.columns  # 6
assert "year" in result.columns   # 2024
assert "quarter" in result.columns  # 2
```

### Scenario 2: Dimension Standardization

```python
df = pd.DataFrame([{
    "order_date": "2024-06-15",
    "region": "  SOUTH  ",
    "sales_rep": "maria santos",
    # ...
}])

result = prepare_sales(df)

assert result["region"].iloc[0] == "South"      # title case, trimmed
assert result["sales_rep"].iloc[0] == "Maria Santos"
```

### Scenario 3: NULL Date Handling

```python
df = pd.DataFrame([
    {"order_date": "2024-06-15", ...},
    {"order_date": None, ...},  # NULL date
])

result = prepare_sales(df)

assert len(result) == 2  # Row preserved
assert pd.isna(result["month"].iloc[1])  # Time columns are NaN
```

### Scenario 4: Immutability Check

```python
df = pd.DataFrame([...])
original_id = df["order_id"].iloc[0]

result = prepare_sales(df)

assert result is not df  # New DataFrame
assert df["order_id"].iloc[0] == original_id  # Input unchanged
```

## Running Tests

```bash
# Run only prepare tests
pytest tests/test_prepare.py -v

# Run with coverage
pytest tests/test_prepare.py --cov=src/prepare

# Run full test suite
pytest tests/ -v
```

## Expected Outcomes

| Metric | Expected |
|--------|----------|
| Test pass rate | 100% (25 tests) |
| Lint pass rate | 100% (ruff) |
| Input columns preserved | 25 |
| Output columns | 28 |
| Performance (100K rows) | < 1 second |

## Integration Test

```bash
# Full pipeline: extract → validate → prepare
python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales

df = extract_csv('data/electronics_sales_raw.csv')
df = validate_sales(df)
df = prepare_sales(df)
print(f'Output: {len(df)} rows, {len(df.columns)} columns')
print(f'Columns: {list(df.columns)}')
"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `AttributeError: Can only use .dt accessor` | order_date not datetime | Ensure validate_sales ran first |
| `NaN in time columns` | Invalid/NULL order_date | Expected behavior, check upstream data |
| `Dimension not title case` | Missing column in DIMENSION_COLUMNS | Check prepare.py constants |
