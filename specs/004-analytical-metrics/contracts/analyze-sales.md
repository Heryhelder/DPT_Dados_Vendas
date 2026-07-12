# Contract: analyze_sales

**Date**: 2026-07-12

## Function Signature

```python
def analyze_sales(
    df: pd.DataFrame,
    cogs_rules: dict[str, float] | None = None,
    tax_rate: float = 0.0,
) -> pd.DataFrame:
```

## Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| df | pd.DataFrame | Yes | — | Prepared DataFrame with 28 columns from `prepare_sales()` |
| cogs_rules | dict[str, float] \| None | No | None (uses defaults) | Dictionary mapping sub_category → cost percentage (0-1) |
| tax_rate | float | No | 0.0 | Tax rate for net_income computation (0-1) |

### Input Requirements

- Must contain all 28 columns from `prepare_sales()` output
- Must contain: quantity (int64), unit_price (float64), discount_pct (float64), sub_category (object)
- Optional: operating_expenses (float64) for EBITDA computation
- Must contain: month, year, quarter (float64) for seasonality analysis

### Input Validation

| Condition | Error | Message |
|-----------|-------|---------|
| DataFrame is empty | ValueError | "DataFrame de entrada está vazio" |

### Default COGS Rules

When `cogs_rules` is None, the following defaults are used:

```python
DEFAULT_COGS_RULES = {
    "Smartphones": 0.65,
    "Laptops": 0.70,
    "Audio": 0.55,
    "Peripherals": 0.50,
    "Tablets": 0.60,
}
```

## Output

| Type | Description |
|------|-------------|
| pd.DataFrame | New DataFrame with 32 columns (28 input + 4 core metrics) |

### Output Columns (Core — always present)

All 28 input columns preserved, plus:

| Column | Type | Formula | Null Handling |
|--------|------|---------|---------------|
| gross_revenue | float64 | quantity * unit_price | NaN if quantity or unit_price is NULL |
| net_revenue | float64 | gross_revenue * (1 - discount_pct) | NaN if gross_revenue is NULL; gross_revenue if discount_pct is NULL |
| cost_of_goods_sold | float64 | net_revenue * cost_percentage | NaN if sub_category not in rules or net_revenue is NULL |
| gross_profit | float64 | net_revenue - cost_of_goods_sold | NaN if cost_of_goods_sold is NULL |

### Output Columns (Optional — when operating_expenses is present)

| Column | Type | Formula | Null Handling |
|--------|------|---------|---------------|
| ebitda | float64 | gross_profit - operating_expenses | NaN if gross_profit or operating_expenses is NULL |
| net_income | float64 | ebitda * (1 - tax_rate) | NaN if ebitda is NULL |

### Output Guarantees

- Input DataFrame is never modified (immutability)
- All original columns preserved in original order
- Derived columns appended after original columns
- NULL values propagate through calculations (no silent defaults)
- Deterministic: same input always produces same output

## Side Effects

| Effect | Scope | Description |
|--------|-------|-------------|
| Logging | `src.analyze` logger | INFO level: rows_processed, columns_added, nan_counts |

## Usage Example

```python
from src.prepare import prepare_sales
from src.analyze import analyze_sales

# Stage 3: Prepare
df_prepared = prepare_sales(df_validated)

# Stage 4: Analyze (this contract)
df_analytics = analyze_sales(df_prepared)

# df_analytics has 32 columns with revenue metrics
# Optional: custom COGS rules and tax rate
df_analytics = analyze_sales(
    df_prepared,
    cogs_rules={"Smartphones": 0.70, "Laptops": 0.75},
    tax_rate=0.25,
)
```

## Analysis Functions (Companion)

### aggregate_metrics

```python
def aggregate_metrics(
    df: pd.DataFrame,
    group_by: list[str] | None = None,
) -> pd.DataFrame:
```

Groups by specified columns and returns: total_revenue, avg_ticket, total_quantity, avg_discount.

### analyze_seasonality

```python
def analyze_seasonality(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
```

Returns dict with "monthly" and "quarterly" DataFrames containing revenue totals per time period.

### top_products

```python
def top_products(
    df: pd.DataFrame,
    n: int | None = None,
) -> pd.DataFrame:
```

Returns products ranked by revenue and quantity. If n is specified, returns top N.

### top_categories

```python
def top_categories(
    df: pd.DataFrame,
    n: int | None = None,
) -> pd.DataFrame:
```

Returns categories ranked by revenue and quantity. If n is specified, returns top N.

### analyze_recurrence

```python
def analyze_recurrence(df: pd.DataFrame) -> dict[str, float]:
```

Returns dict with: total_customers, repeat_customers, recurrence_rate.

## Error Conditions

| Error Type | Condition | Recovery |
|------------|-----------|----------|
| ValueError | Empty DataFrame | Check upstream pipeline |
| KeyError | Missing required column | Ensure prepare_sales ran first |
| TypeError | Non-numeric quantity/unit_price | Validate input types |
