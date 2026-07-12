# Research: Analytical Metrics

**Date**: 2026-07-12

## Decisions

### 1. Revenue Metric Computation Method

**Decision**: Use pandas vectorized operations for all per-row metric computations (gross_revenue, net_revenue, COGS, gross_profit).

**Rationale**: All four core metrics are row-level calculations that map directly to pandas Series operations. Vectorized computation is the fastest approach and aligns with the constitution's simplicity principle. No loops or apply() needed.

**Alternatives considered**:
- DuckDB SQL: Rejected — derived columns are computed in Python; exporting to DuckDB for row-level math adds unnecessary complexity
- NumPy directly: Rejected — pandas Series operations are sufficient and more readable
- `df.apply()` with lambda: Rejected — slower than vectorized operations, no benefit

### 2. COGS Rule Application

**Decision**: Map sub_category to cost percentage using a dictionary, then use `map()` to create a cost_percentage column, and compute COGS as `net_revenue * cost_percentage`.

**Rationale**: `Series.map()` with a dictionary is the most pandas-idiomatic approach. Missing sub_categories naturally produce NaN. The dictionary is configurable via function parameter with sensible defaults.

**Alternatives considered**:
- `np.select()` with conditions: Rejected — more verbose, no benefit over simple dictionary mapping
- Hardcoded if/elif: Rejected — violates DRY, not configurable
- External config file: Rejected — adds I/O dependency; dictionary parameter is simpler

### 3. Aggregation Function Design

**Decision**: Single `aggregate_metrics()` function that accepts a list of grouping columns and returns a DataFrame with aggregated metrics.

**Rationale**: Flexible — supports any combination of dimensions via `groupby()`. Single function avoids code duplication. Returns a DataFrame (not dict) for consistency with the pipeline's data flow.

**Alternatives considered**:
- Separate functions per dimension (e.g., `aggregate_by_region()`): Rejected — violates DRY
- Return dict of DataFrames: Rejected — harder to chain operations, inconsistent with pipeline
- DuckDB SQL aggregation: Rejected — depends on derived columns computed in Python

### 4. Seasonality Analysis Design

**Decision**: Two separate aggregations: monthly totals (grouped by year+month) and quarterly totals (grouped by year+quarter).

**Rationale**: Enables year-over-year comparison. Grouping by both year and period ensures each time bucket is unique across years. Returns two DataFrames for independent consumption.

**Alternatives considered**:
- Single combined table with period_type column: Rejected — adds complexity for filtering
- Only within-year totals (no YoY): Rejected — was clarified as needed in spec

### 5. Top Performers Design

**Decision**: Two functions: `top_products()` and `top_categories()`, each returning a DataFrame ranked by revenue and quantity.

**Rationale**: Products and categories have different cardinalities and use different grouping columns. Separate functions keep the interface clean. Each returns a single DataFrame with both revenue and quantity rankings.

**Alternatives considered**:
- Single `top_performers(entity_type)` function: Rejected — adds unnecessary branching logic
- Return only top N: Rejected — let the caller filter; return full ranked list

### 6. Customer Recurrence Analysis

**Decision**: Compute recurrence by counting orders per customer_id, identifying customers with >1 order, and calculating recurrence rate.

**Rationale**: Simple groupby + count approach. Recurrence rate = customers_with_repeat_orders / total_customers. Returns a summary dict with key metrics.

**Alternatives considered**:
- RFM analysis (recency, frequency, monetary): Rejected — YAGNI; only recurrence was requested
- Cohort analysis: Rejected — out of scope for this feature

### 7. Optional Metrics (EBITDA, Net Income)

**Decision**: Compute only when `operating_expenses` column is present and non-null. Default tax_rate=0.0.

**Rationale**: Graceful degradation per spec requirement. If operating_expenses is missing, EBITDA and net_income are set to NaN. The tax_rate parameter defaults to 0.0 (net_income = EBITDA when no tax).

**Alternatives considered**:
- Require operating_expenses: Rejected — violates graceful degradation requirement
- Compute EBITDA as gross_profit (ignore operating_expenses): Rejected — misleading

### 8. Cross-Dimensional Comparison

**Decision**: Reuse `aggregate_metrics()` with multiple grouping columns (e.g., `groupby(["region", "sales_channel"])`).

**Rationale**: The aggregation function already supports arbitrary grouping columns. Cross-dimensional comparison is just aggregation with 2+ dimensions. No separate function needed.

**Alternatives considered**:
- Separate cross-tabulation function: Rejected — duplicates aggregation logic
- Pivot table: Rejected — harder to generalize, less flexible

## Technology Choices

| Technology | Version | Justification |
|-----------|---------|---------------|
| Python | 3.14 | Constitution requirement |
| pandas | >= 2.2, < 3 | Constitution requirement |
| pytest | >= 8.0 | Existing test framework |
| ruff | >= 0.9 | Constitution linter |

## Integration Points

- **Input**: Output of `prepare_sales()` — DataFrame with 28 columns (25 original + month, year, quarter)
- **Output**: DataFrame with 32 columns (28 input + gross_revenue, net_revenue, cost_of_goods_sold, gross_profit) + optional ebitda, net_income
- **Next stage**: Aggregation functions produce summary DataFrames for analysis
- **Downstream**: Tableau export (Stage 5)
