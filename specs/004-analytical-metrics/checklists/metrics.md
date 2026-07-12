# Metrics Quality Checklist: Analytical Metrics

**Purpose**: Validate metric definitions for clarity, consistency, completeness, and measurability
**Created**: 2026-07-12
**Feature**: [spec.md](../spec.md)

## Metric Definition Completeness

- [ ] CHK001 - Are all four core metric formulas (gross_revenue, net_revenue, cost_of_goods_sold, gross_profit) explicitly defined with exact mathematical expressions? [Completeness, Spec §FR-001–FR-004]
- [ ] CHK002 - Are aggregated metric formulas (total_revenue, avg_ticket, total_quantity, avg_discount) explicitly defined? [Completeness, Spec §FR-006]
- [ ] CHK003 - Are optional metric formulas (ebitda, net_income) explicitly defined? [Completeness, Spec §FR-011–FR-012]
- [ ] CHK004 - Is the recurrence rate formula explicitly defined (repeat_customers / total_customers)? [Completeness, Spec §FR-010]
- [ ] CHK005 - Are seasonality metric formulas (monthly_revenue, quarterly_revenue) explicitly defined? [Completeness, Spec §FR-008]
- [ ] CHK006 - Are top performer ranking criteria explicitly defined (sort key, direction)? [Completeness, Spec §FR-009]

## Metric Definition Clarity

- [ ] CHK007 - Is "avg_ticket" clearly defined as mean(net_revenue per order_id) or mean(net_revenue per customer)? The term "ticket" is ambiguous. [Clarity, Spec §FR-006, US2]
- [ ] CHK008 - Is "avg_discount" defined as mean(all discount_pct values) or mean(non-zero discount_pct values)? [Clarity, Spec §FR-006]
- [ ] CHK009 - Is "repeat customer" defined as customer_id with >1 order, or >=1 order? [Clarity, Spec §FR-010, US3]
- [ ] CHK010 - Is the COGS rule lookup case-sensitive or case-insensitive (e.g., "Smartphones" vs "smartphones")? [Clarity, Spec §FR-003]

## Metric Consistency

- [ ] CHK011 - Does the edge case "gross_revenue = 0 or NaN" for NULL quantity/unit_price conflict with FR-014 (NaN propagation)? [Conflict, Spec §Edge Cases vs §FR-014]
- [ ] CHK012 - Are NULL handling rules consistent across all four core metrics? (e.g., if quantity is NULL → gross_revenue=NaN → net_revenue=NaN → COGS=NaN → gross_profit=NaN) [Consistency, Spec §FR-014]
- [ ] CHK013 - Are NULL handling rules consistent between core metrics and optional metrics? (e.g., if gross_profit is NaN → ebitda=NaN → net_income=NaN) [Consistency, Spec §FR-014, §FR-011–FR-012]
- [ ] CHK014 - Is the discount_pct NULL behavior consistent? Edge case says "net_revenue = gross_revenue" (no discount), but FR-014 says NaN propagation. [Conflict, Spec §Edge Cases vs §FR-014]

## Acceptance Criteria Quality

- [ ] CHK015 - Can SC-002 (aggregated metrics match manual calculation within 1e-6) be objectively verified for all four aggregated metrics? [Measurability, Spec §SC-002]
- [ ] CHK016 - Is SC-001 (100K rows in <2 seconds) measurable with a specific benchmark setup? [Measurability, Spec §SC-001]
- [ ] CHK017 - Is SC-004 (deterministic top performer rankings) testable when tied values exist? [Measurability, Spec §SC-004]
- [ ] CHK018 - Is SC-005 (customer recurrence accuracy) verifiable with known golden data? [Measurability, Spec §SC-005]

## Scenario Coverage

- [ ] CHK019 - Are NULL input scenarios defined for all input columns used in metric formulas (quantity, unit_price, discount_pct, sub_category, operating_expenses)? [Coverage, Gap]
- [ ] CHK020 - Are zero-value input scenarios defined for quantity=0 and unit_price=0? [Coverage, Gap]
- [ ] CHK021 - Are negative value scenarios defined for quantity, unit_price, or discount_pct? [Coverage, Gap]
- [ ] CHK022 - Is the scenario where all rows have NULL sub_category addressed (all COGS = NaN)? [Coverage, Edge Case]
- [ ] CHK023 - Is the scenario where discount_pct > 1.0 or < 0.0 addressed (invalid discount)? [Coverage, Gap]

## Edge Case Coverage

- [ ] CHK024 - Is division by zero addressed for recurrence_rate when total_customers = 0? [Edge Case, Spec §FR-010]
- [ ] CHK025 - Is the scenario where COGS rule dictionary is empty explicitly covered in requirements? [Edge Case, Spec §Edge Cases]
- [ ] CHK026 - Are tie-breaking rules defined for top performers when multiple products/categories have identical revenue? [Edge Case, Gap]
- [ ] CHK027 - Is the behavior defined when operating_expenses column exists but contains all NULL values? [Edge Case, Gap]

## Non-Functional Requirements

- [ ] CHK028 - Are performance requirements (SC-001) specified for each metric computation independently or only for the combined pipeline? [Clarity, Spec §SC-001]
- [ ] CHK029 - Is logging granularity (FR-015) specified — what exactly is logged per metric? [Clarity, Spec §FR-015]
- [ ] CHK030 - Are determinism requirements (SC-008) specified for floating-point operations (e.g., sum order sensitivity)? [Clarity, Spec §SC-008]

## Dependencies & Assumptions

- [ ] CHK031 - Is the assumption that "operating_expenses is always present in input data" validated or just assumed? [Assumption, Spec §Assumptions]
- [ ] CHK032 - Is the dependency on prepare_sales output (28 columns) explicitly documented as a prerequisite? [Dependency, Spec §Assumptions]
- [ ] CHK033 - Is the assumption that "discount_pct is always 0-1" validated or just assumed? [Assumption, Spec §Assumptions]

## Ambiguities & Conflicts

- [ ] CHK034 - Is the term "faturamento total" (total revenue) clearly mapped to total_revenue = sum(net_revenue) or sum(gross_revenue)? [Ambiguity, Spec §US2]
- [ ] CHK035 - Is "ticket médio" (average ticket) clearly defined — per order or per customer? [Ambiguity, Spec §US2]
- [ ] CHK036 - Are the COGS percentage values (0.65, 0.70, etc.) validated against actual data distribution? [Assumption, Spec §FR-003]
