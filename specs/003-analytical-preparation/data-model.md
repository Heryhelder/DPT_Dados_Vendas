# Data Model: Analytical Data Preparation

**Date**: 2026-07-12

## Entities

### AnalyticalDataFrame

The output dataset with enriched time-based and dimension columns.

**Input** (25 columns from `validate_sales`):

| Column | Type | Description |
|--------|------|-------------|
| order_id | int64 | Unique order identifier |
| customer_id | object | Customer code |
| customer_name | object | Customer full name (title case) |
| customer_segment | object | Segment: Consumer, Corporate, etc. |
| customer_type | object | Type: New, Existing |
| first_purchase_date | datetime64 | First purchase date |
| last_purchase_date | datetime64 | Last purchase date |
| product_id | object | Product code |
| product_name | object | Product name |
| category | object | Product category |
| sub_category | object | Product sub-category |
| brand | object | Brand name |
| order_date | datetime64 | Order date |
| quantity | int64 | Units purchased |
| unit_price | float64 | Price per unit |
| discount_pct | float64 | Discount as decimal (0-1) |
| sales_channel | object | Online, Retail |
| payment_method | object | Payment method |
| sales_rep | object | Sales representative |
| region | object | Geographic region |
| operating_expenses | float64 | Operating cost |
| cash_balance | float64 | Cash balance |
| debt_balance | float64 | Debt balance |
| monthly_burn | float64 | Monthly burn rate |
| churn_flag | int64 | Churn indicator (0/1) |

**Output** (28 columns — 25 original + 3 new):

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| month | float64 | Derived | Month number (1-12), NaN if invalid date |
| year | float64 | Derived | 4-digit year, NaN if invalid date |
| quarter | float64 | Derived | Calendar quarter (1-4), NaN if invalid date |

**Note**: month, year, quarter are float64 (not int64) to support NaN values for invalid dates.

## Business Dimensions

Columns used for dimensional analysis:

| Dimension | Column | Standardization | Example |
|-----------|--------|-----------------|---------|
| Region | region | Title case | "south" → "South" |
| Seller | sales_rep | Title case | "maria santos" → "Maria Santos" |
| Category | category | Title case | "electronics" → "Electronics" |
| Channel | sales_channel | Title case | "retail" → "Retail" |
| Customer Type | customer_type | Title case | "new" → "New" |

## Validation Rules

| Rule | Applied To | Condition | Action |
|------|-----------|-----------|--------|
| Date coercion | order_date | Invalid/NULL | Set month, year, quarter to NaN |
| Title case | All dimension columns | All values | Apply `.str.strip().str.title()` |
| NULL preservation | All columns | NULL values | Preserve as-is (no removal) |
| Immutability | Input DataFrame | All operations | Return new DataFrame, input unchanged |

## State Transitions

```
Input DataFrame (25 cols, validated)
        │
        ▼
_create_time_columns()
        │
        ▼
DataFrame (25 cols + month, year, quarter)
        │
        ▼
_standardize_dimensions()
        │
        ▼
Output DataFrame (28 cols, analytics-ready)
```

## Relationships

- **Input** ← `validate_sales()` output
- **Output** → DuckDB SQL queries (Stage 4 metrics)
- **Output** → Tableau export (Stage 5)
