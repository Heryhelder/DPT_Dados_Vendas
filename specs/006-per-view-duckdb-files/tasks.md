# Tasks: Per-View DuckDB Files

**Input**: Design documents from `/specs/006-per-view-duckdb-files/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per constitution (TDD — Principle III). Written FIRST, must FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Update configuration for directory-based output

- [x] T001 Update `DUCKDB_PATH` in `src/config.py` from `"output/data.duckdb"` to `"output"` (directory path)

---

## Phase 2: Foundational (SQL Parsing Helpers)

**Purpose**: Extract helper functions needed by all user stories to parse `create_views.sql`

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Add `import re` and implement `_parse_view_statements(sql_content: str) -> list[tuple[str, str]]` helper in `src/store.py` that splits `create_views.sql` into individual `(view_name, view_sql)` tuples using regex per research.md R1
- [x] T003 Implement `_extract_view_names(sql_content: str) -> list[str]` helper in `src/store.py` that extracts view names from SQL using `re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS', ...)`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Generate Individual DuckDB Files Per View (Priority: P1) 🎯 MVP

**Goal**: Each analytical view is saved as a separate `.duckdb` file in the output directory

**Independent Test**: Run `store_analytics(df, "output")` and verify 5 `.duckdb` files exist, each queryable

### Tests for User Story 1 (TDD — Write FIRST, must FAIL)

> **NOTE: Write these tests FIRST, run them, confirm they FAIL, THEN implement**

- [x] T004 [P] [US1] Write test `test_store_creates_five_duckdb_files` in `tests/test_store.py` — calls `store_analytics(df, tmp_path)`, asserts exactly 5 `.duckdb` files exist in the output directory
- [x] T005 [P] [US1] Write test `test_store_creates_correct_filenames` in `tests/test_store.py` — asserts the 5 files are named `v_monthly_revenue.duckdb`, `v_store_performance.duckdb`, `v_category_sales.duckdb`, `v_top_products.duckdb`, `v_sales_summary.duckdb`
- [x] T006 [P] [US1] Write test `test_each_file_contains_sales_table_and_one_view` in `tests/test_store.py` — for each `.duckdb` file, asserts it has exactly 1 table (`sales`) and exactly 1 view
- [x] T007 [P] [US1] Write test `test_each_file_is_independently_queryable` in `tests/test_store.py` — for each `.duckdb` file, queries the view and asserts results are returned without error

### Implementation for User Story 1

- [x] T008 [US1] Rewrite `store_analytics()` in `src/store.py` to: (1) read `create_views.sql`, (2) parse into individual view statements using `_parse_view_statements()`, (3) for each view: create `{db_path}/{view_name}.duckdb`, create `sales` table from DataFrame, execute single view DDL
- [x] T009 [US1] Run tests T004–T007 and confirm they PASS

**Checkpoint**: User Story 1 fully functional — 5 per-view `.duckdb` files generated

---

## Phase 4: User Story 2 — Backward-Compatible Storage Interface (Priority: P2)

**Goal**: `store_analytics(df, db_path)` function signature unchanged; `db_path` now means output directory

**Independent Test**: Call `store_analytics()` with same arguments as today; verify new per-file output structure

### Tests for User Story 2 (TDD — Write FIRST, must FAIL)

- [x] T010 [P] [US2] Write test `test_store_function_signature_unchanged` in `tests/test_store.py` — calls `store_analytics(df, str(tmp_path))` with positional args, asserts no error raised
- [x] T011 [P] [US2] Write test `test_db_path_as_directory_creates_files_inside` in `tests/test_store.py` — asserts `.duckdb` files are created inside the specified directory (not as a single file at that path)
- [x] T012 [P] [US2] Write test `test_store_auto_creates_output_directory` in `tests/test_store.py` — uses a nested non-existent path, asserts directory and files are created

### Implementation for User Story 2

- [x] T013 [US2] Ensure `db_path` in `store_analytics()` is treated as directory — `Path(db_path).mkdir(parents=True, exist_ok=True)`, no file extension logic on `db_path` itself
- [x] T014 [US2] Run tests T010–T012 and confirm they PASS

**Checkpoint**: Function interface backward-compatible; `db_path` = output directory

---

## Phase 5: User Story 3 — Data Integrity Across All View Files (Priority: P3)

**Goal**: All 5 `.duckdb` files contain identical `sales` table data

**Independent Test**: Query `sales` in each file; verify matching row count and `SUM(net_revenue)`

### Tests for User Story 3 (TDD — Write FIRST, must FAIL)

- [x] T015 [P] [US3] Write test `test_all_files_have_identical_row_count` in `tests/test_store.py` — generates files, queries `COUNT(*) FROM sales` in each, asserts all equal
- [x] T016 [P] [US3] Write test `test_all_files_have_identical_revenue_sum` in `tests/test_store.py` — queries `SUM(net_revenue)` in each, asserts all within 0.01 tolerance
- [x] T017 [P] [US3] Write test `test_per_file_validation_raises_on_mismatch` in `tests/test_store.py` — (if feasible) corrupts a file and re-runs, asserts `ValueError` raised
- [x] T018 [P] [US3] Write test `test_store_is_idempotent` in `tests/test_store.py` — runs `store_analytics()` twice with same data, asserts identical output

### Implementation for User Story 3

- [x] T019 [US3] Add per-file validation loop in `store_analytics()` — after creating each `.duckdb` file, open it read-only, query `COUNT(*)` and `SUM(net_revenue)`, compare against DataFrame, raise `ValueError` on mismatch
- [x] T020 [US3] Run tests T015–T018 and confirm they PASS

**Checkpoint**: All 3 user stories independently functional and tested

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, linting, cleanup

- [x] T021 Run `ruff check src/store.py src/config.py tests/test_store.py` and fix any lint errors
- [x] T022 Run full test suite `pytest tests/ -v` and confirm all tests pass (including pre-existing tests in other modules)
- [x] T023 Run quickstart.md validation scenarios manually (Scenario 1–4) and confirm expected outcomes
- [x] T024 Remove unused `create_tables.sql` reference if applicable (it's not used by any code — verify)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Stories (Phase 3–5)**: All depend on Phase 2 completion
  - US1 (P1) → US2 (P2) → US3 (P3) sequential (US2/US3 build on US1 implementation)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P2)**: Can start after Phase 2 — tests verify interface compatibility with US1 output
- **US3 (P3)**: Can start after Phase 2 — validation logic depends on US1 file structure

### Within Each User Story

- Tests FIRST (Red) → Implementation (Green) → Refactor
- All [P] tests within a story can run in parallel
- Implementation tasks are sequential within a story

### Parallel Opportunities

- T004, T005, T006, T007 (all US1 tests) can run in parallel
- T010, T011, T012 (all US2 tests) can run in parallel
- T015, T016, T017, T018 (all US3 tests) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (TDD Red phase):
Task: "test_store_creates_five_duckdb_files in tests/test_store.py"
Task: "test_store_creates_correct_filenames in tests/test_store.py"
Task: "test_each_file_contains_sales_table_and_one_view in tests/test_store.py"
Task: "test_each_file_is_independently_queryable in tests/test_store.py"

# Then implement (TDD Green phase):
Task: "Rewrite store_analytics() in src/store.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (config update)
2. Complete Phase 2: Foundational (SQL parsing helpers)
3. Complete Phase 3: User Story 1 (per-file generation)
4. **STOP and VALIDATE**: 5 `.duckdb` files exist and are queryable
5. Run quickstart Scenario 1–2

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → 5 per-view files working (MVP!)
3. Add US2 → Test independently → Interface backward-compatible
4. Add US3 → Test independently → Data integrity verified
5. Polish → Lint, full test suite, quickstart validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD is MANDATORY per constitution (Principle III) — tests written FIRST
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
