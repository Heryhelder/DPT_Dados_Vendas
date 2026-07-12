# Feature Specification: Analytical Metrics

**Feature Branch**: `004-analytical-metrics`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "adicione uma feature que irá gerar dados analíticos sobre comportamentos e padrões nos dados, com as seguintes especificidades: 1. Analisar sazonalidade, observando picos e quedas ao longo do tempo. Calcular faturamento total, ticket médio, quantidade vendida e desconto médio. Identificar produtos e categorias de melhor desempenho. Calcular gross_revenue = quantity * unit_price. Calcular net_revenue = gross_revenue * (1 - discount_pct). Criar cost_of_goods_sold com base em regra por subcategoria e depois calcular gross_profit = net_revenue - cost_of_goods_sold. 2. Métricas opcionais: ebitda, net_income, avg_ticket, comparações de desempenho. Utilizar customer_id para verificação de recorrência."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compute Core Revenue Metrics (Priority: P1)

As a data analyst, I want the system to automatically calculate gross_revenue, net_revenue, cost_of_goods_sold, and gross_profit for each transaction, so that I can analyze profitability at the transaction level without manual formula application.

**Why this priority**: These four metrics are the foundation for all downstream analytical aggregations. Without them, no revenue or profit analysis is possible.

**Independent Test**: Can be fully tested by providing a DataFrame with quantity, unit_price, discount_pct, and sub_category columns, then verifying that each derived column is correctly calculated row-by-row.

**Acceptance Scenarios**:

1. **Given** a DataFrame with quantity=10, unit_price=50.0, **When** gross_revenue is computed, **Then** gross_revenue = 500.0 (quantity * unit_price)
2. **Given** gross_revenue=500.0 and discount_pct=0.1, **When** net_revenue is computed, **Then** net_revenue = 450.0 (gross_revenue * (1 - discount_pct))
3. **Given** sub_category="Smartphone" and a COGS rule defining its cost percentage, **When** cost_of_goods_sold is computed, **Then** cost_of_goods_sold = net_revenue * cost_percentage for that sub_category
4. **Given** net_revenue=450.0 and cost_of_goods_sold=270.0, **When** gross_profit is computed, **Then** gross_profit = 180.0 (net_revenue - cost_of_goods_sold)
5. **Given** a DataFrame with all required columns, **When** the transformation is applied, **Then** the original columns (quantity, unit_price, discount_pct, sub_category) remain unchanged

---

### User Story 2 - Generate Aggregated Analytical Metrics (Priority: P2)

As a business analyst, I want the system to produce aggregated metrics (total revenue, average ticket, quantity sold, average discount) across different dimensions, so that I can understand overall business performance and compare segments.

**Why this priority**: Aggregated metrics are essential for KPI reporting and executive dashboards. They depend on the core metrics from US1.

**Independent Test**: Can be tested by providing a DataFrame with the four core revenue columns and verifying that aggregated totals and averages match expected values when grouped by any dimension.

**Acceptance Scenarios**:

1. **Given** a DataFrame with net_revenue values, **When** total revenue is computed, **Then** total_revenue = sum(net_revenue) for the given scope
2. **Given** a DataFrame with net_revenue and order_id, **When** average ticket is computed, **Then** avg_ticket = mean(net_revenue per order)
3. **Given** a DataFrame with quantity values, **When** total quantity sold is computed, **Then** total_quantity = sum(quantity)
4. **Given** a DataFrame with discount_pct values, **When** average discount is computed, **Then** avg_discount = mean(discount_pct)
5. **Given** a grouping dimension (e.g., region), **When** aggregated metrics are computed per group, **Then** each group has its own set of aggregated metrics

---

### User Story 3 - Analyze Seasonality and Top Performers (Priority: P3)

As a data analyst, I want the system to identify seasonality patterns (monthly/quarterly trends) and highlight top-performing products and categories, so that I can discover behavioral patterns and prioritize business focus areas.

**Why this priority**: These analytical outputs build on US1 and US2, providing actionable insights for strategic decisions.

**Independent Test**: Can be tested by verifying that seasonal summaries show correct totals per time period and that top performer lists rank items correctly by revenue/quantity.

**Acceptance Scenarios**:

1. **Given** a DataFrame with month and net_revenue columns, **When** seasonality analysis is performed, **Then** monthly totals are correctly computed for each month present in the data
2. **Given** a DataFrame with quarter and net_revenue columns, **When** seasonality analysis is performed, **Then** quarterly totals are correctly computed for each quarter
3. **Given** a DataFrame with product_name and net_revenue, **When** top performers are identified, **Then** products are ranked by total revenue in descending order
4. **Given** a DataFrame with category and net_revenue, **When** top performers are identified, **Then** categories are ranked by total revenue in descending order
5. **Given** a DataFrame with customer_id, **When** customer recurrence is analyzed, **Then** the system identifies repeat customers (more than one order) and reports recurrence rate

---

### User Story 4 - Compute Optional Business Metrics (Priority: P4)

As a business analyst, I want the system to optionally calculate EBITDA, net income, and support cross-dimensional performance comparisons, so that I can perform deeper financial analysis beyond basic profitability.

**Why this priority**: These are advanced metrics that extend the core analysis. They are optional and build on US1-US3.

**Independent Test**: Can be tested by providing required inputs for optional metrics and verifying correctness. Feature degrades gracefully if optional inputs are missing.

**Acceptance Scenarios**:

1. **Given** a DataFrame with gross_profit and operating_expenses, **When** EBITDA is computed, **Then** EBITDA = gross_profit - operating_expenses
2. **Given** a DataFrame with EBITDA and applicable tax rate, **When** net_income is computed, **Then** net_income = EBITDA * (1 - tax_rate)
3. **Given** aggregated metrics across two dimensions (e.g., region × channel), **When** cross-dimensional comparison is performed, **Then** the result shows metrics for each dimension combination
4. **Given** optional metric inputs are missing or incomplete, **When** the system processes the data, **Then** optional metrics are set to NaN for affected rows (no errors thrown)

---

### Edge Cases

- What happens when quantity or unit_price is NULL or zero? → gross_revenue = 0 or NaN; downstream metrics propagate NaN
- What happens when sub_category has no COGS rule defined? → cost_of_goods_sold = NaN, gross_profit = NaN for that row
- What happens when discount_pct is NULL? → net_revenue = gross_revenue (no discount applied)
- What happens when the DataFrame has zero rows after filtering? → Aggregated metrics return empty results; no errors thrown
- What happens when all transactions belong to a single customer? → customer recurrence rate = 0% (no repeat customers)
- What happens when COGS rule dictionary is empty? → All cost_of_goods_sold values = NaN

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute `gross_revenue` = `quantity * unit_price` for each transaction row
- **FR-002**: System MUST compute `net_revenue` = `gross_revenue * (1 - discount_pct)` for each transaction row
- **FR-003**: System MUST compute `cost_of_goods_sold` based on a configurable rule dictionary mapping sub_category to cost percentage. Default rules: Smartphones=0.65, Laptops=0.70, Audio=0.55, Peripherals=0.50, Tablets=0.60
- **FR-004**: System MUST compute `gross_profit` = `net_revenue` - `cost_of_goods_sold` for each transaction row
- **FR-005**: System MUST preserve all input columns when adding derived metric columns (return new DataFrame)
- **FR-006**: System MUST support aggregated metric computation: total_revenue, avg_ticket, total_quantity, avg_discount
- **FR-007**: System MUST support aggregation by any combination of dimensions (region, sales_rep, category, sales_channel, customer_type, month, year, quarter)
- **FR-008**: System MUST analyze seasonality by computing revenue totals per month and per quarter
- **FR-009**: System MUST identify top-performing products and categories ranked by revenue and quantity
- **FR-010**: System MUST analyze customer recurrence using customer_id (identify repeat customers, compute recurrence rate)
- **FR-011**: System MUST optionally compute `ebitda` = `gross_profit` - `operating_expenses` when gross_profit is available
- **FR-012**: System MUST optionally compute `net_income` from EBITDA and tax rate (default tax_rate=0.0)
- **FR-013**: System MUST support cross-dimensional performance comparisons (e.g., region × channel)
- **FR-014**: When input values are NULL or zero, System MUST propagate NaN through derived calculations (no silent defaults)
- **FR-015**: System MUST log computation statistics: rows processed, columns added, NaN counts per derived column
- **FR-016**: System MUST accept a configurable COGS rules dictionary (sub_category → cost percentage) as input parameter
- **FR-017**: System MUST return a new DataFrame; input DataFrame MUST remain unchanged (immutability)

### Key Entities

- **Transaction Metrics**: Per-row derived columns: gross_revenue, net_revenue, cost_of_goods_sold, gross_profit
- **COGS Rules**: Configuration dictionary mapping sub_category names to cost percentage (0-1). Default: Smartphones=0.65, Laptops=0.70, Audio=0.55, Peripherals=0.50, Tablets=0.60
- **Aggregated Metrics**: Summary statistics computed across dimensions: total_revenue, avg_ticket, total_quantity, avg_discount
- **Seasonality Summary**: Revenue totals grouped by month and quarter
- **Top Performers**: Products and categories ranked by revenue/quantity
- **Customer Recurrence**: Analysis of repeat purchase behavior using customer_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Core metric computation (gross_revenue, net_revenue, COGS, gross_profit) completes for 100,000 rows in under 2 seconds
- **SC-002**: Aggregated metrics match manual calculation results within floating-point tolerance (1e-6)
- **SC-003**: Seasonality analysis produces correct monthly and quarterly totals matching source data
- **SC-004**: Top performer rankings are deterministic and correctly sorted by revenue/quantity
- **SC-005**: Customer recurrence calculation correctly identifies all repeat customers and computes accurate recurrence rate
- **SC-006**: Optional metrics (EBITDA, net_income) degrade gracefully — NaN for rows with missing inputs, no errors thrown
- **SC-007**: All derived columns are correctly populated with no silent data loss (NULL propagation rule verified)
- **SC-008**: Transformation is deterministic (same input produces same output)

## Assumptions

- Input data has already been validated and prepared (Stage 3 complete, 28 columns from `prepare_sales`)
- COGS rules are provided as a dictionary; default rules: Smartphones=0.65, Laptops=0.70, Audio=0.55, Peripherals=0.50, Tablets=0.60
- cost_percentage in COGS rules is expressed as a decimal (0-1), not a percentage
- Optional metrics (EBITDA, net_income) require operating_expenses column which is already present in the input data
- tax_rate for net_income computation is a constant parameter (default 0.0 — no tax applied unless overridden)
- customer_id is present in input data for recurrence analysis
- Raw CSV file is never modified (constitution principle)
- Transformations follow TDD approach with golden data tests
- Python 3.14 with pandas >= 2.2 is used for implementation
- Analyses (seasonality, top performers, recurrence) are performed in-memory with pandas (not DuckDB SQL) since they depend on derived columns computed in Python

## Clarifications

### Session 2026-07-12

- Q: What are the specific COGS rules per sub_category? → A: Smartphones=0.65, Laptops=0.70, Audio=0.55, Peripherals=0.50, Tablets=0.60
- Q: What is the default tax_rate for net_income computation? → A: 0.0 (no tax applied by default; user provides rate via parameter)
- Q: Should seasonality analysis include year-over-year comparison or just within-year monthly/quarterly totals? → A: Include both — monthly totals per year and quarterly totals per year, enabling YoY comparison.
