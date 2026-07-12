# Tasks: Analytical Data Preparation

**Input**: Design documents from `specs/003-analytical-preparation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/prepare-sales.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3

---

## Phase 1: Foundational (TDD Baseline)

**Purpose**: Ensure existing tests pass and src/prepare.py starts clean (TDD baseline)

**GATE 0**: Must verify red-green baseline before any implementation

- [ ] T001 [US1] Verify existing tests pass in `tests/test_validate.py` (`pytest tests/test_validate.py`)
- [ ] T002 [US1] [P] Verify `src/prepare.py` does not exist or remove if present (`rm src/prepare.py 2>/dev/null`)
- [ ] T003 [US1] [P] Create empty test file `tests/test_prepare.py` with initial imports (`import pandas as pd`)

**Checkpoint**: Existing pipeline green, src/prepare.py absent, test file empty (red baseline)

---

## Phase 2: User Story 1 — Create Time Columns (P1) 🎯 MVP

**Goal**: Create month, year, quarter columns from order_date (float64, NaN for invalid)

**Independent Test**: Provide DataFrame with order_date, verify month/year/quarter columns correct

### Tests ⚠️ (MUST write FIRST, verify FAIL before implementation)

- [ ] T004 [P] [US1] Write test: `test_create_month_column` — valid order_date → month (1-12) as float64 in `tests/test_prepare.py`
- [ ] T005 [P] [US1] Write test: `test_create_year_column` — valid order_date → year (4-digit) as float64 in `tests/test_prepare.py`
- [ ] T006 [P] [US1] Write test: `test_create_quarter_column` — valid order_date → quarter (1-4) as float64 in `tests/test_prepare.py`
- [ ] T007 [US1] Write test: `test_order_date_preserved` — order_date column unchanged after prepare in `tests/test_prepare.py`
- [ ] T008 [US1] Write test: `test_null_date_sets_time_null` — NULL order_date → month/year/quarter = NaN, row preserved in `tests/test_prepare.py`
- [ ] T009 [US1] Write test: `test_returns_new_dataframe` — input DataFrame not modified in `tests/test_prepare.py`

### Implementation

- [ ] T010 [US1] Create `prepare_sales()` skeleton in `src/prepare.py` with type hints and docstring
- [ ] T011 [US1] Implement `_create_time_columns(df)` — extract month/year/quarter as float64 using pandas datetime accessors
- [ ] T012 [US1] Run `pytest tests/test_prepare.py -k time` — all time column tests pass
- [ ] T013 [US1] Run `ruff check src/prepare.py tests/test_prepare.py` — lint clean

**Checkpoint**: Time columns created correctly, 6 tests passing, lint clean

---

## Phase 3: User Story 2 — Standardize Dimensions (P2)

**Goal**: Standardize region, sales_rep, category, sales_channel, customer_type to title case with trim

**Independent Test**: Verify all dimension columns have title-cased values after prepare

### Tests ⚠️ (MUST write FIRST, verify FAIL before implementation)

- [ ] T014 [P] [US2] Write test: `test_standardize_region` — region values → title case, whitespace trimmed in `tests/test_prepare.py`
- [ ] T015 [P] [US2] Write test: `test_standardize_sales_rep` — sales_rep values → title case in `tests/test_prepare.py`
- [ ] T016 [P] [US2] Write test: `test_standardize_category` — category values → title case in `tests/test_prepare.py`
- [ ] T017 [P] [US2] Write test: `test_standardize_sales_channel` — sales_channel values → title case in `tests/test_prepare.py`
- [ ] T018 [P] [US2] Write test: `test_standardize_customer_type` — customer_type values → title case in `tests/test_prepare.py`
- [ ] T019 [US2] Write test: `test_null_dimensions_preserved` — NULL values in dimension columns stay NULL in `tests/test_prepare.py`
- [ ] T020 [US2] Write test: `test_input_not_modified` — input DataFrame dimension columns unchanged in `tests/test_prepare.py`

### Implementation

- [ ] T021 [US2] Implement `_standardize_dimensions(df)` — title case + strip for all 5 dimension columns in `src/prepare.py`
- [ ] T022 [US2] Wire `_standardize_dimensions()` into `prepare_sales()` main function
- [ ] T023 [US2] Run `pytest tests/test_prepare.py -k dimension` — all dimension tests pass
- [ ] T024 [US2] Run `ruff check src/prepare.py tests/test_prepare.py` — lint clean

**Checkpoint**: Dimensions standardized, 13 tests total passing, lint clean

---

## Phase 4: User Story 3 — Table Ready for Analysis (P3)

**Goal**: Verify prepared data supports filtering, grouping, and cross-dimensional analysis

**Independent Test**: Filter/group/cross-tab on prepared data, verify correctness

### Tests ⚠️ (MUST write FIRST, verify FAIL before implementation)

- [ ] T025 [P] [US3] Write test: `test_filter_by_dimension` — filter by region returns correct subset in `tests/test_prepare.py`
- [ ] T026 [P] [US3] Write test: `test_groupby_time` — group by month/year/quarter → correct aggregates in `tests/test_prepare.py`
- [ ] T027 [US3] Write test: `test_cross_dimension_analysis` — region × channel cross-tab produces accurate totals in `tests/test_prepare.py`

### Implementation

- [ ] T028 [US3] Implement `_compute_quarter()` helper if not already complete — ensure calendar quarter logic correct in `src/prepare.py`
- [ ] T029 [US3] Run `pytest tests/test_prepare.py` — all 20+ tests pass
- [ ] T030 [US3] Run `ruff check src/prepare.py tests/test_prepare.py` — lint clean

**Checkpoint**: All user stories independently testable, 20+ tests passing

---

## Phase 5: Logging & Polish (Cross-Cutting)

**Goal**: Add transformation statistics logging and final validation

### Implementation

- [ ] T031 [US3] Add logging in `prepare_sales()` — rows processed, columns added, dimensions standardized, NULL dates count using `logging` module with key=value format in `src/prepare.py`
- [ ] T032 [US3] Write test: `test_logging_stats` — verify log output contains expected stats in `tests/test_prepare.py`
- [ ] T033 [US3] Run `pytest tests/test_prepare.py -v` — full test suite passing
- [ ] T034 [US3] Run `ruff check src/prepare.py tests/test_prepare.py tests/test_validate.py` — all lint clean

**Checkpoint**: Production-ready, fully tested, lint clean

---

## Phase 6: Final Validation

**Goal**: Verify against quickstart.md scenarios

- [ ] T035 [US3] Run quickstart.md validation scenario 1: time columns correct for sample dates
- [ ] T036 [US3] Run quickstart.md validation scenario 2: NULL dates handled correctly
- [ ] T037 [US3] Run quickstart.md validation scenario 3: dimensions title-cased
- [ ] T038 [US3] Run `pytest tests/` — full test suite passes (no regressions in extract/validate)
- [ ] T039 [US3] Run `ruff check src/` — all lint clean

**Checkpoint**: Feature complete, all tests green, ready for review

---

## Dependency Map

```
Phase 1: T001 → T002 → T003
                  ↓
Phase 2: T004-T006 (parallel) → T007-T009 (sequential) → T010-T013
                  ↓
Phase 3: T014-T018 (parallel) → T019-T020 → T021-T024
                  ↓
Phase 4: T025-T026 (parallel) → T027 → T028-T030
                  ↓
Phase 5: T031-T034 (sequential)
                  ↓
Phase 6: T035-T039 (sequential final validation)
```

## Parallel Execution Guide

```
# Phase 1: Sequential (clean slate)
T001 → T002 → T003

# Phase 2 tests: 3 parallel
Task: T004 test_create_month_column
Task: T005 test_create_year_column
Task: T006 test_create_quarter_column

# Phase 3 tests: 5 parallel
Task: T014 test_standardize_region
Task: T015 test_standardize_sales_rep
Task: T016 test_standardize_category
Task: T017 test_standardize_sales_channel
Task: T018 test_standardize_customer_type

# Phase 4 tests: 2 parallel
Task: T025 test_filter_by_dimension
Task: T026 test_groupby_time
```
