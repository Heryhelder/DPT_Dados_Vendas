# Tasks: Analytical Metrics

**Input**: Design documents from `/specs/004-analytical-metrics/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/analyze-sales.md

**Tests**: TDD mandatory per constitution (GATE 0). Tests written BEFORE implementation for each user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Module initialization and shared constants

- [ ] T001 [P] Create src/analyze.py with module docstring, imports, and logger setup in src/analyze.py
- [ ] T002 [P] Define DEFAULT_COGS_RULES constant dict in src/analyze.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Create tests/test_analyze.py with test class structure and shared fixtures (minimal DataFrame with all 28 required columns) in tests/test_analyze.py

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Compute Core Revenue Metrics (Priority: P1) 🎯 MVP

**Goal**: Compute gross_revenue, net_revenue, cost_of_goods_sold, gross_profit for each transaction row

**Independent Test**: Provide DataFrame with quantity, unit_price, discount_pct, sub_category; verify each derived column row-by-row

### Tests for User Story 1 (TDD — write FIRST, ensure FAIL)

- [ ] T004 [P] [US1] Write test_gross_revenue_computation in tests/test_analyze.py — verify gross_revenue = quantity * unit_price
- [ ] T005 [P] [US1] Write test_net_revenue_computation in tests/test_analyze.py — verify net_revenue = gross_revenue * (1 - discount_pct)
- [ ] T006 [P] [US1] Write test_cogs_computation in tests/test_analyze.py — verify COGS = net_revenue * cost_percentage per sub_category
- [ ] T007 [P] [US1] Write test_gross_profit_computation in tests/test_analyze.py — verify gross_profit = net_revenue - COGS
- [ ] T008 [P] [US1] Write test_input_columns_preserved in tests/test_analyze.py — verify all 28 input columns unchanged
- [ ] T009 [P] [US1] Write test_null_propagation in tests/test_analyze.py — verify NULL inputs propagate NaN through all derived columns
- [ ] T010 [P] [US1] Write test_empty_dataframe_raises in tests/test_analyze.py — verify ValueError on empty input
- [ ] T011 [P] [US1] Write test_custom_cogs_rules in tests/test_analyze.py — verify custom COGS dictionary is applied
- [ ] T012 [P] [US1] Write test_unknown_sub_category_nan in tests/test_analyze.py — verify NaN when sub_category not in rules

### Implementation for User Story 1

- [ ] T013 [US1] Implement _compute_revenue_metrics(df) in src/analyze.py — vectorized computation of gross_revenue, net_revenue, cost_of_goods_sold, gross_profit
- [ ] T014 [US1] Implement analyze_sales(df, cogs_rules, tax_rate) main function in src/analyze.py — calls _compute_revenue_metrics, returns new DataFrame

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Generate Aggregated Analytical Metrics (Priority: P2)

**Goal**: Produce aggregated metrics (total_revenue, avg_ticket, total_quantity, avg_discount) across dimensions

**Independent Test**: Provide DataFrame with core revenue columns; verify aggregated totals match manual calculation

### Tests for User Story 2 (TDD — write FIRST, ensure FAIL)

- [ ] T015 [P] [US2] Write test_aggregate_total_revenue in tests/test_analyze.py — verify total_revenue = sum(net_revenue)
- [ ] T016 [P] [US2] Write test_aggregate_avg_ticket in tests/test_analyze.py — verify avg_ticket = mean(net_revenue per order)
- [ ] T017 [P] [US2] Write test_aggregate_total_quantity in tests/test_analyze.py — verify total_quantity = sum(quantity)
- [ ] T018 [P] [US2] Write test_aggregate_avg_discount in tests/test_analyze.py — verify avg_discount = mean(discount_pct)
- [ ] T019 [P] [US2] Write test_aggregate_by_dimension in tests/test_analyze.py — verify grouping by region produces per-group metrics
- [ ] T020 [P] [US2] Write test_aggregate_empty_input in tests/test_analyze.py — verify empty DataFrame returns empty result

### Implementation for User Story 2

- [ ] T021 [US2] Implement aggregate_metrics(df, group_by) in src/analyze.py — groupby + aggregation with total_revenue, avg_ticket, total_quantity, avg_discount

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Analyze Seasonality and Top Performers (Priority: P3)

**Goal**: Identify seasonality patterns (monthly/quarterly trends), top-performing products/categories, and customer recurrence

**Independent Test**: Verify seasonal summaries show correct totals per time period; verify top performers ranked correctly; verify recurrence rate accurate

### Tests for User Story 3 (TDD — write FIRST, ensure FAIL)

- [ ] T022 [P] [US3] Write test_seasonality_monthly_totals in tests/test_analyze.py — verify monthly revenue totals per year
- [ ] T023 [P] [US3] Write test_seasonality_quarterly_totals in tests/test_analyze.py — verify quarterly revenue totals per year
- [ ] T024 [P] [US3] Write test_top_products_ranking in tests/test_analyze.py — verify products ranked by revenue descending
- [ ] T025 [P] [US3] Write test_top_categories_ranking in tests/test_analyze.py — verify categories ranked by revenue descending
- [ ] T026 [P] [US3] Write test_top_products_limit_n in tests/test_analyze.py — verify top_n parameter limits results
- [ ] T027 [P] [US3] Write test_recurrence_rate in tests/test_analyze.py — verify recurrence = repeat_customers / total_customers
- [ ] T028 [P] [US3] Write test_recurrence_single_customer in tests/test_analyze.py — verify 0% recurrence when all orders from one customer
- [ ] T029 [P] [US3] Write test_recurrence_no_customers in tests/test_analyze.py — verify graceful handling when total_customers = 0

### Implementation for User Story 3

- [ ] T030 [US3] Implement analyze_seasonality(df) in src/analyze.py — returns dict with "monthly" and "quarterly" DataFrames
- [ ] T031 [US3] Implement top_products(df, n) in src/analyze.py — products ranked by revenue and quantity
- [ ] T032 [US3] Implement top_categories(df, n) in src/analyze.py — categories ranked by revenue and quantity
- [ ] T033 [US3] Implement analyze_recurrence(df) in src/analyze.py — returns dict with total_customers, repeat_customers, recurrence_rate

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Compute Optional Business Metrics (Priority: P4)

**Goal**: Optionally compute EBITDA, net_income; support cross-dimensional comparisons

**Independent Test**: Provide required inputs; verify optional metrics correct; verify graceful degradation when inputs missing

### Tests for User Story 4 (TDD — write FIRST, ensure FAIL)

- [ ] T034 [P] [US4] Write test_ebitda_computation in tests/test_analyze.py — verify ebitda = gross_profit - operating_expenses
- [ ] T035 [P] [US4] Write test_net_income_computation in tests/test_analyze.py — verify net_income = ebitda * (1 - tax_rate)
- [ ] T036 [P] [US4] Write test_optional_metrics_graceful_degradation in tests/test_analyze.py — verify NaN when operating_expenses missing
- [ ] T037 [P] [US4] Write test_cross_dimensional_comparison in tests/test_analyze.py — verify aggregate_metrics with multiple group_by columns produces correct per-combination metrics (satisfies FR-013)

### Implementation for User Story 4

- [ ] T038 [US4] Implement _compute_optional_metrics(df, tax_rate) in src/analyze.py — compute ebitda and net_income when operating_expenses present
- [ ] T039 [US4] Update analyze_sales to call _compute_optional_metrics in src/analyze.py — integrate optional metrics into main function

**Checkpoint**: All user stories complete with optional metrics

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Logging, validation, documentation, and final quality checks

- [ ] T040 Implement logging in analyze_sales in src/analyze.py — log rows_processed, columns_added, nan_counts per derived column (FR-015)
- [ ] T041 [P] Run quickstart.md validation scenarios in specs/004-analytical-metrics/quickstart.md — verify all 7 scenarios pass
- [ ] T042 [P] Run ruff lint on src/analyze.py and tests/test_analyze.py — ensure zero errors
- [ ] T043 [P] Run full test suite pytest tests/ -v — verify all tests pass (existing + new)
- [ ] T044 [P] Write performance benchmark test in tests/test_analyze.py — verify analyze_sales processes 100,000 rows in under 2 seconds (SC-001)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion
  - US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4) — sequential priority order
  - US2, US3, US4 depend on US1 (core revenue metrics must exist first)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 — uses gross_revenue, net_revenue columns
- **User Story 3 (P3)**: Depends on US1 — uses net_revenue, product_name, category, customer_id
- **User Story 4 (P4)**: Depends on US1 — uses gross_profit, operating_expenses

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD — GATE 0)
- Implementation follows Red → Green → Refactor cycle
- Story complete before moving to next priority

### Parallel Opportunities

- T001 + T002 (Setup tasks) can run in parallel
- T004–T012 (US1 tests) can all run in parallel
- T015–T020 (US2 tests) can all run in parallel
- T022–T029 (US3 tests) can all run in parallel
- T034–T037 (US4 tests) can all run in parallel
- T041 + T042 + T043 (Polish tasks) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (TDD — must FAIL first):
Task: "Write test_gross_revenue_computation in tests/test_analyze.py"
Task: "Write test_net_revenue_computation in tests/test_analyze.py"
Task: "Write test_cogs_computation in tests/test_analyze.py"
Task: "Write test_gross_profit_computation in tests/test_analyze.py"
Task: "Write test_input_columns_preserved in tests/test_analyze.py"
Task: "Write test_null_propagation in tests/test_analyze.py"
Task: "Write test_empty_dataframe_raises in tests/test_analyze.py"
Task: "Write test_custom_cogs_rules in tests/test_analyze.py"
Task: "Write test_unknown_sub_category_nan in tests/test_analyze.py"

# Then implement (all tests should PASS):
Task: "Implement _compute_revenue_metrics(df) in src/analyze.py"
Task: "Implement analyze_sales(df, cogs_rules, tax_rate) in src/analyze.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core metrics)
   - Developer B: User Story 2 (aggregations) — after US1 core is done
   - Developer C: User Story 3 (seasonality/top performers) — after US1 core is done
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD mandatory per constitution — tests MUST fail before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 44 (T001–T044)
