# Data Model: Analytical Metrics

**Date**: 2026-07-12

## Entities

### AnalyticalMetricsDataFrame

The output dataset with computed revenue metrics and optional financial metrics.

**Input** (28 columns from `prepare_sales`):

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
| month | float64 | Month number (1-12) |
| year | float64 | 4-digit year |
| quarter | float64 | Calendar quarter (1-4) |

**Output** (32 columns — 28 input + 4 core metrics):

| Column | Type | Source | Formula | Description |
|--------|------|--------|---------|-------------|
| gross_revenue | float64 | Derived | quantity * unit_price | Total revenue before discounts |
| net_revenue | float64 | Derived | gross_revenue * (1 - discount_pct) | Revenue after discounts |
| cost_of_goods_sold | float64 | Derived | net_revenue * cost_percentage | Cost of goods sold by sub_category |
| gross_profit | float64 | Derived | net_revenue - cost_of_goods_sold | Profit before operating expenses |

**Optional columns** (34 total when enabled):

| Column | Type | Source | Formula | Description |
|--------|------|--------|---------|-------------|
| ebitda | float64 | Derived | gross_profit - operating_expenses | Earnings before interest, taxes, depreciation, amortization |
| net_income | float64 | Derived | ebitda * (1 - tax_rate) | Net income after tax |

**Note**: All derived columns are float64 to support NaN propagation for missing/invalid input values.

## COGS Rules

Default cost-of-goods-sold percentages by sub_category:

| sub_category | cost_percentage | Rationale |
|-------------|----------------|-----------|
| Smartphones | 0.65 | Higher margins typical for smartphones |
| Laptops | 0.70 | Higher COGS for laptops |
| Audio | 0.55 | Lower COGS for audio accessories |
| Peripherals | 0.50 | Lowest COGS for peripherals |
| Tablets | 0.60 | Moderate COGS for tablets |

**Missing sub_category**: If a sub_category is not in the rules dictionary, `cost_of_goods_sold` = NaN, `gross_profit` = NaN for that row.

## Aggregated Metrics

Summary statistics computed by `aggregate_metrics()`:

| Metric | Formula | Grouping |
|--------|---------|----------|
| total_revenue | sum(net_revenue) | Any dimension combination |
| avg_ticket | mean(net_revenue per order_id) — average revenue per order | Any dimension combination |
| total_quantity | sum(quantity) | Any dimension combination |
| avg_discount | mean(discount_pct) | Any dimension combination |

## Seasonality Summary

Revenue totals grouped by time period:

| Metric | Grouping | Description |
|--------|----------|-------------|
| monthly_revenue | year + month | Total net_revenue per month per year |
| quarterly_revenue | year + quarter | Total net_revenue per quarter per year |

## Top Performers

Ranked lists of products and categories:

| Metric | Grouping | Ranking |
|--------|----------|---------|
| product_revenue | product_name | Descending by sum(net_revenue) |
| product_quantity | product_name | Descending by sum(quantity) |
| category_revenue | category | Descending by sum(net_revenue) |
| category_quantity | category | Descending by sum(quantity) |

## Customer Recurrence

Repeat purchase analysis using customer_id:

| Metric | Formula | Description |
|--------|---------|-------------|
| total_customers | nunique(customer_id) | Total distinct customers |
| repeat_customers | count(customers with >1 order) | Customers with multiple orders |
| recurrence_rate | repeat_customers / total_customers | Percentage of repeat customers |

## Validation Rules

| Rule | Applied To | Condition | Action |
|------|-----------|-----------|--------|
| NULL propagation | All derived columns | Any input NULL/NaN | Derived column = NaN |
| COGS fallback | cost_of_goods_sold | sub_category not in rules | Set to NaN |
| Immutability | Input DataFrame | All operations | Return new DataFrame, input unchanged |
| Graceful degradation | Optional metrics | Missing operating_expenses | EBITDA/net_income = NaN |

## State Transitions

```
Input DataFrame (28 cols, prepared)
        │
        ▼
_compute_revenue_metrics()
        │
        ▼
DataFrame (28 cols + gross_revenue, net_revenue, cost_of_goods_sold, gross_profit)
        │
        ▼
_compute_optional_metrics() [if enabled]
        │
        ▼
DataFrame (32 cols + optional ebitda, net_income)
        │
        ▼
Output: Enriched DataFrame + aggregated analysis DataFrames
```

## Relationships

- **Input** ← `prepare_sales()` output
- **Output** → Aggregation functions (aggregate_metrics, seasonality, top performers)
- **Output** → Tableau export (Stage 5)
