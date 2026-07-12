# Quickstart: Analytical Metrics

**Date**: 2026-07-12

## Prerequisites

- Python 3.14 with pandas >= 2.2
- Project dependencies installed: `pip install -e ".[dev]"`
- Prepared DataFrame from Stage 3 (`prepare_sales`)

## Validation Scenarios

### Scenario 1: Core Revenue Metrics

```python
import pandas as pd
from src.analyze import analyze_sales

# Create minimal prepared DataFrame with required columns
df = pd.DataFrame([{
    "order_id": 1,
    "customer_id": "C001",
    "product_name": "iPhone 15",
    "sub_category": "Smartphones",
    "quantity": 10,
    "unit_price": 50.0,
    "discount_pct": 0.1,
    "operating_expenses": 100.0,
    "month": 6.0,
    "year": 2024.0,
    "quarter": 2.0,
    # ... other 19 columns
}])

result = analyze_sales(df)

# Verify core metrics
assert result["gross_revenue"].iloc[0] == 500.0   # 10 * 50
assert result["net_revenue"].iloc[0] == 450.0     # 500 * 0.9
assert result["cost_of_goods_sold"].iloc[0] == 292.5  # 450 * 0.65
assert result["gross_profit"].iloc[0] == 157.5    # 450 - 292.5
```

### Scenario 2: Aggregated Metrics

```python
from src.analyze import aggregate_metrics

result = analyze_sales(df_prepared)
agg = aggregate_metrics(result, group_by=["region"])

assert "total_revenue" in agg.columns
assert "avg_ticket" in agg.columns
assert "total_quantity" in agg.columns
assert "avg_discount" in agg.columns
```

### Scenario 3: Seasonality Analysis

```python
from src.analyze import analyze_seasonality

result = analyze_sales(df_prepared)
season = analyze_seasonality(result)

assert "monthly" in season
assert "quarterly" in season
assert "year" in season["monthly"].columns
assert "month" in season["monthly"].columns
assert "total_revenue" in season["monthly"].columns
```

### Scenario 4: Top Performers

```python
from src.analyze import top_products, top_categories

result = analyze_sales(df_prepared)
products = top_products(result, n=5)
categories = top_categories(result)

assert len(products) <= 5
assert products["total_revenue"].is_monotonic_decreasing
```

### Scenario 5: Customer Recurrence

```python
from src.analyze import analyze_recurrence

result = analyze_sales(df_prepared)
recurrence = analyze_recurrence(result)

assert "total_customers" in recurrence
assert "repeat_customers" in recurrence
assert "recurrence_rate" in recurrence
assert 0 <= recurrence["recurrence_rate"] <= 1
```

### Scenario 6: Optional Metrics (EBITDA/Net Income)

```python
result = analyze_sales(df_prepared, tax_rate=0.25)

assert "ebitda" in result.columns
assert "net_income" in result.columns
assert result["ebitda"].iloc[0] == 57.5   # 157.5 - 100
assert result["net_income"].iloc[0] == 43.125  # 57.5 * 0.75
```

### Scenario 7: Immutability Check

```python
df = df_prepared.copy()
original_cols = list(df.columns)

result = analyze_sales(df)

assert result is not df  # New DataFrame
assert list(df.columns) == original_cols  # Input unchanged
```

## Running Tests

```bash
# Run only analyze tests
pytest tests/test_analyze.py -v

# Run with coverage
pytest tests/test_analyze.py --cov=src/analyze

# Run full test suite
pytest tests/ -v
```

## Expected Outcomes

| Metric | Expected |
|--------|----------|
| Test pass rate | 100% |
| Lint pass rate | 100% (ruff) |
| Input columns preserved | 28 |
| Output columns (core) | 32 |
| Output columns (optional) | 34 |
| Performance (100K rows) | < 2 seconds |

## Integration Test

```bash
# Full pipeline: extract → validate → prepare → analyze
python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales

df = extract_csv('data/electronics_sales_raw.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
print(f'Output: {len(df)} rows, {len(df.columns)} columns')
print(f'Columns: {list(df.columns)}')
print(f'gross_revenue range: {df[\"gross_revenue\"].min():.2f} - {df[\"gross_revenue\"].max():.2f}')
print(f'net_revenue range: {df[\"net_revenue\"].min():.2f} - {df[\"net_revenue\"].max():.2f}')
"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `KeyError: 'sub_category'` | Missing column | Ensure prepare_sales ran first |
| `NaN in cost_of_goods_sold` | sub_category not in COGS rules | Check COGS dictionary keys match data |
| `NaN in ebitda` | operating_expenses not in DataFrame | Optional metric — expected if column missing |
| `ZeroDivisionError` | All quantities are zero | Check upstream data quality |
