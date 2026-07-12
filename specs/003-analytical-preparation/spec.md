# Feature Specification: Analytical Data Preparation

**Feature Branch**: `003-analytical-preparation`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "adicione uma nova feature que vai padronizar os dados da seguinte maneira: Padronizações típicas: Criar colunas para ajudar na análise como mês, ano, trimestre. Estruturar a base por dimensões de negócio: região, vendedor, categoria, canal e tipo de cliente. Organizar a tabela para facilitar filtros e comparações."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Time-Based Analytical Columns (Priority: P1)

As a data analyst, I want the system to automatically create month, year, and quarter columns from the order date, so that I can perform time-based analysis and comparisons without manual date extraction.

**Why this priority**: Time-based dimensions are fundamental for sales analysis (monthly trends, quarterly performance, year-over-year comparisons). This is the core transformation that enables all subsequent analytical queries.

**Independent Test**: Can be fully tested by providing a DataFrame with order_date column and verifying that month, year, quarter columns are correctly populated with proper values.

**Acceptance Scenarios**:

1. **Given** a DataFrame with order_date column, **When** the transformation is applied, **Then** a "month" column is created containing the month number (1-12) extracted from order_date
2. **Given** a DataFrame with order_date column, **When** the transformation is applied, **Then** a "year" column is created containing the 4-digit year extracted from order_date
3. **Given** a DataFrame with order_date column, **When** the transformation is applied, **Then** a "quarter" column is created containing the calendar quarter number (1=Jan-Mar through 4=Oct-Dec) extracted from order_date
4. **Given** a DataFrame with order_date in various formats, **When** the transformation is applied, **Then** all three time columns are correctly populated regardless of original date format
5. **Given** a DataFrame with order_date column, **When** the transformation is applied, **Then** the original order_date column remains unchanged

---

### User Story 2 - Structure Data by Business Dimensions (Priority: P2)

As a business analyst, I want the data to be organized by key business dimensions (region, seller, category, channel, customer type), so that I can easily filter, group, and compare performance across these dimensions.

**Why this priority**: Business dimensions enable segmentation analysis (regional performance, seller effectiveness, category trends, channel comparison, customer type insights). This structure is essential for dimensional analysis and reporting.

**Independent Test**: Can be fully tested by verifying that dimension columns are properly formatted and consistent, enabling accurate grouping and filtering operations.

**Acceptance Scenarios**:

1. **Given** a DataFrame with region column, **When** the transformation is applied, **Then** all region values are converted to title case with trimmed whitespace
2. **Given** a DataFrame with sales_rep column, **When** the transformation is applied, **Then** all seller names are converted to title case with trimmed whitespace
3. **Given** a DataFrame with category column, **When** the transformation is applied, **Then** all category values are converted to title case
4. **Given** a DataFrame with sales_channel column, **When** the transformation is applied, **Then** all channel values are converted to title case
5. **Given** a DataFrame with customer_type column, **When** the transformation is applied, **Then** all customer type values are converted to title case

---

### User Story 3 - Optimize Table for Filters and Comparisons (Priority: P3)

As a data consumer, I want the final table to be optimized for filtering and comparison operations, so that I can quickly analyze data across multiple dimensions without complex transformations.

**Why this priority**: This ensures the prepared data is immediately usable for ad-hoc analysis, dashboards, and reporting tools like Tableau.

**Independent Test**: Can be tested by performing common filter and comparison operations on the prepared data to verify usability.

**Acceptance Scenarios**:

1. **Given** a prepared DataFrame, **When** filtering by any dimension column, **Then** the filter returns accurate results with consistent values
2. **Given** a prepared DataFrame, **When** grouping by time columns (month, year, quarter), **Then** aggregations produce correct totals
3. **Given** a prepared DataFrame, **When** grouping by business dimensions, **Then** aggregations produce correct segment-level totals
4. **Given** a prepared DataFrame, **When** comparing across dimensions (e.g., region vs. channel), **Then** cross-tabulations are accurate and meaningful

---

### Edge Cases

- When order_date is NULL or invalid, month/year/quarter columns are set to NULL (row is preserved)
- When dimension columns contain NULL values, they are preserved as-is
- When dimension columns contain unexpected values (e.g., typos), they are preserved (no fuzzy matching)
- Dimension values with special characters or accents are preserved as-is (no normalization beyond casing/whitespace)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create a "month" column extracting month number (1-12) from order_date
- **FR-002**: System MUST create a "year" column extracting 4-digit year from order_date
- **FR-003**: System MUST create a "quarter" column extracting calendar quarter (Q1=Jan-Mar through Q4=Oct-Dec) from order_date
- **FR-004**: System MUST preserve the original order_date column unchanged
- **FR-005**: System MUST standardize region values to title case (trim whitespace, normalize casing)
- **FR-006**: System MUST standardize sales_rep values to title case
- **FR-007**: System MUST standardize category values to title case
- **FR-008**: System MUST standardize sales_channel values to title case
- **FR-009**: System MUST standardize customer_type values to title case
- **FR-010**: When order_date is NULL or invalid, System MUST set month, year, and quarter columns to NULL (row preserved)
- **FR-011**: System MUST handle NULL/missing values in dimension columns gracefully (preserve NULLs)
- **FR-012**: System MUST return a new DataFrame with all existing columns preserved (input DataFrame unchanged)
- **FR-013**: System MUST log transformation statistics: rows processed, columns added, dimensions standardized count, and NULL dates count

### Key Entities

- **Analytical DataFrame**: The output dataset with enriched time-based and dimension columns
- **Time Dimensions**: month, year, quarter columns derived from order_date
- **Business Dimensions**: region, sales_rep, category, sales_channel, customer_type columns
- **Transformation Log**: Statistics about the preparation process

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Time column creation adds month, year, quarter columns in under 1 second for datasets up to 100,000 rows
- **SC-002**: Dimension standardization produces consistent values enabling accurate grouping (100% identical values for identical underlying data)
- **SC-003**: Prepared data supports filtering by any single dimension with correct results
- **SC-004**: Prepared data supports cross-dimensional analysis (e.g., region × channel) with accurate aggregations
- **SC-005**: All existing columns are preserved without data loss during transformation
- **SC-006**: Transformation is deterministic (same input produces same output)

## Clarifications

### Session 2026-07-12

- Q: When order_date is NULL or invalid, should time columns be NULL, rows removed, or default values? → A: Set month/year/quarter to NULL when order_date is invalid (keep row)
- Q: What casing format should dimension values use? → A: Title case (e.g., "South", "Electronics", "Online")
- Q: Should quarter use calendar year or fiscal year? → A: Calendar year: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
- Q: Should the function return a new DataFrame or modify input in place? → A: Return a new DataFrame (input unchanged)
- Q: Which statistics should be logged? → A: Rows processed, columns added, dimensions standardized, NULL dates count

## Assumptions

- Input data has already been validated and standardized (Stage 2 complete)
- Order dates are in a parseable format after validation
- Dimension columns contain valid values (no data cleaning required beyond formatting)
- Raw CSV file is never modified (constitution principle)
- Transformations follow TDD approach with golden data tests
- Python 3.14 with pandas >= 2.2 is used for implementation
