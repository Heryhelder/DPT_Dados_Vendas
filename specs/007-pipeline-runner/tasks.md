# Tasks: Pipeline Runner

**Input**: Design documents from `/specs/007-pipeline-runner/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per constitution (TDD — Principle III). Written FIRST, must FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Add default input path constant to config

- [x] T001 Add `DEFAULT_INPUT_PATH = "data/electronics_sales_raw.csv"` to `src/config.py`

---

## Phase 2: User Story 1 — Run Full Pipeline End-to-End (Priority: P1) 🎯 MVP

**Goal**: Single function that runs all 5 ETL stages and produces 5 `.duckdb` files

**Independent Test**: Call `run_pipeline()` and verify 5 `.duckdb` files exist with valid data

### Tests for User Story 1 (TDD — Write FIRST, must FAIL)

> **NOTE: Write these tests FIRST, run them, confirm they FAIL, THEN implement**

- [x] T002 [P] [US1] Write test `test_run_pipeline_creates_five_duckdb_files` in `tests/test_pipeline.py` — calls `run_pipeline()`, asserts 5 `.duckdb` files exist in `output/`
- [x] T003 [P] [US1] Write test `test_run_pipeline_returns_output_path` in `tests/test_pipeline.py` — asserts return value is a `Path` pointing to the output directory
- [x] T004 [P] [US1] Write test `test_run_pipeline_files_are_queryable` in `tests/test_pipeline.py` — for each output file, queries the view and asserts rows > 0
- [x] T005 [P] [US1] Write test `test_run_pipeline_sales_table_has_data` in `tests/test_pipeline.py` — queries `COUNT(*) FROM sales` in any output file, asserts > 0

### Implementation for User Story 1

- [x] T006 [US1] Create `src/pipeline.py` with `run_pipeline()` function that calls `extract_csv()` → `validate_sales()` → `prepare_sales()` → `analyze_sales()` → `store_analytics()` sequentially
- [x] T007 [US1] Run tests T002–T005 and confirm they PASS

**Checkpoint**: Pipeline runs end-to-end, produces 5 per-view `.duckdb` files

---

## Phase 3: User Story 2 — Configurable Input and Output Paths (Priority: P2)

**Goal**: `run_pipeline()` accepts optional `input_path` and `output_dir` parameters

**Independent Test**: Call `run_pipeline(input_path=..., output_dir=...)` and verify output in custom location

### Tests for User Story 2 (TDD — Write FIRST, must FAIL)

- [x] T008 [P] [US2] Write test `test_run_pipeline_custom_output_dir` in `tests/test_pipeline.py` — calls `run_pipeline(output_dir="custom_output")`, asserts 5 files in `custom_output/`
- [x] T009 [P] [US2] Write test `test_run_pipeline_custom_input_path` in `tests/test_pipeline.py` — calls `run_pipeline(input_path="data/electronics_sales_raw.csv")`, asserts pipeline completes without error
- [x] T010 [P] [US2] Write test `test_run_pipeline_default_params` in `tests/test_pipeline.py` — calls `run_pipeline()` with no args, asserts uses defaults from config

### Implementation for User Story 2

- [x] T011 [US2] Add `input_path` and `output_dir` parameters with defaults to `run_pipeline()` in `src/pipeline.py`
- [x] T012 [US2] Run tests T008–T010 and confirm they PASS

**Checkpoint**: Function accepts custom paths; defaults work

---

## Phase 4: User Story 3 — Pipeline Reports Processing Summary (Priority: P3)

**Goal**: Pipeline logs a summary with rows processed, revenue, files created, duration

**Independent Test**: Run pipeline and check log output includes expected summary fields

### Tests for User Story 3 (TDD — Write FIRST, must FAIL)

- [x] T013 [P] [US3] Write test `test_run_pipeline_logs_summary` in `tests/test_pipeline.py` — runs pipeline with `caplog`, asserts log contains row count and revenue info
- [x] T014 [P] [US3] Write test `test_run_pipeline_logs_duration` in `tests/test_pipeline.py` — runs pipeline with `caplog`, asserts log contains duration info

### Implementation for User Story 3

- [x] T015 [US3] Add `logger.info()` call at end of `run_pipeline()` with processing summary (rows, revenue, files, duration) in `src/pipeline.py`
- [x] T016 [US3] Run tests T013–T014 and confirm they PASS

**Checkpoint**: All 3 user stories functional and tested

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, linting, cleanup

- [x] T017 Run `ruff check src/pipeline.py src/config.py tests/test_pipeline.py` and fix any lint errors
- [x] T018 Run full test suite `pytest tests/ -v` and confirm all tests pass (no regressions)
- [x] T019 Run quickstart.md validation scenarios manually (Scenario 1–4) and confirm expected outcomes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on Phase 1 — core pipeline function
- **US2 (Phase 3)**: Depends on Phase 2 — adds parameters to existing function
- **US3 (Phase 4)**: Depends on Phase 2 — adds logging to existing function
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 1 — no dependencies on other stories
- **US2 (P2)**: Can start after Phase 2 — adds parameters to US1 function
- **US3 (P3)**: Can start after Phase 2 — adds logging to US1 function

### Within Each User Story

- Tests FIRST (Red) → Implementation (Green) → Refactor
- All [P] tests within a story can run in parallel
- Implementation tasks are sequential within a story

### Parallel Opportunities

- T002, T003, T004, T005 (all US1 tests) can run in parallel
- T008, T009, T010 (all US2 tests) can run in parallel
- T013, T014 (all US3 tests) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (TDD Red phase):
Task: "test_run_pipeline_creates_five_duckdb_files in tests/test_pipeline.py"
Task: "test_run_pipeline_returns_output_path in tests/test_pipeline.py"
Task: "test_run_pipeline_files_are_queryable in tests/test_pipeline.py"
Task: "test_run_pipeline_sales_table_has_data in tests/test_pipeline.py"

# Then implement (TDD Green phase):
Task: "Create src/pipeline.py with run_pipeline()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (config constant)
2. Complete Phase 2: User Story 1 (core pipeline function)
3. **STOP and VALIDATE**: Pipeline runs, 5 `.duckdb` files produced
4. Run quickstart Scenario 1–2

### Incremental Delivery

1. Setup → Config ready
2. Add US1 → Test independently → Pipeline works (MVP!)
3. Add US2 → Test independently → Custom paths supported
4. Add US3 → Test independently → Logging summary available
5. Polish → Lint, full test suite, quickstart validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD is MANDATORY per constitution (Principle III) — tests written FIRST
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
