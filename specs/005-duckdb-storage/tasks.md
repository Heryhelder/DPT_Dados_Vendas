# Tasks: DuckDB Analytical Storage

**Input**: Design documents from `specs/005-duckdb-storage/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD obrigatório (Constituição Princípio III). Testes escritos ANTES da implementação.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — add DuckDB dependency and configuration

- [x] T001 Add `duckdb` dependency to `pyproject.toml` under `[project.dependencies]`
- [x] T002 Add `DUCKDB_PATH` constant to `src/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: SQL scripts and directory structure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create `src/sql/` directory and `src/sql/__init__.py`
- [x] T004 Create `src/sql/create_tables.sql` with `CREATE OR REPLACE TABLE sales` DDL per data-model.md (34 columns)
- [x] T005 [P] Create `src/sql/create_views.sql` with all 5 views per data-model.md

**Checkpoint**: Foundation ready — SQL scripts exist and can be tested independently

---

## Phase 3: User Story 1 — Persistência dos dados em tabelas (Priority: P1) MVP

**Goal**: DataFrame analítico é persistido como tabela `sales` no DuckDB, com tipos preservados e criação automática de diretório

**Independent Test**: Executar pipeline completo e verificar que arquivo DuckDB é criado com tabela `sales` contendo todos os registros e tipos corretos

### Tests for User Story 1 (TDD —写 these FIRST, ensure they FAIL)

- [x] T006 [P] [US1] Write test `test_store_creates_duckdb_file` in `tests/test_store.py` — verify `store_analytics()` creates `.duckdb` file at given path
- [x] T007 [P] [US1] Write test `test_store_creates_sales_table` in `tests/test_store.py` — verify `sales` table exists with correct column count (34)
- [x] T008 [P] [US1] Write test `test_store_preserves_record_count` in `tests/test_store.py` — verify row count in DuckDB matches input DataFrame length
- [x] T009 [P] [US1] Write test `test_store_preserves_column_types` in `tests/test_store.py` — verify TIMESTAMP, DOUBLE, VARCHAR, INTEGER types match data-model.md
- [x] T010 [P] [US1] Write test `test_store_auto_creates_directory` in `tests/test_store.py` — verify nested nonexistent directory is created automatically

### Implementation for User Story 1

- [x] T011 [US1] Implement `store_analytics()` function in `src/store.py` — connect to DuckDB, read `create_tables.sql`, execute DDL, persist DataFrame via `CREATE OR REPLACE TABLE sales AS SELECT * FROM df`, close connection
- [x] T012 [US1] Add `Path(db_path).parent.mkdir(parents=True, exist_ok=True)` in `src/store.py` for directory auto-creation (FR-006)
- [x] T013 [US1] Add structured logging to `store_analytics()` — log path, row count, duration (Princípio V)

**Checkpoint**: User Story 1 fully functional — pipeline persists data to DuckDB with correct types

---

## Phase 4: User Story 2 — Views de consulta analítica (Priority: P2)

**Goal**: 5 views SQL são criadas no DuckDB, retornando resultados corretos e refletindo mudanças na tabela subjacente

**Independent Test**: Consultar cada view e verificar que resultados são consistentes com os dados brutos da tabela `sales`

### Tests for User Story 2 (TDD — write these FIRST, ensure they FAIL)

- [x] T014 [P] [US2] Write test `test_store_creates_views` in `tests/test_store.py` — verify all 5 views exist: v_monthly_revenue, v_store_performance, v_category_sales, v_top_products, v_sales_summary
- [x] T015 [P] [US2] Write test `test_view_monthly_revenue_returns_data` in `tests/test_store.py` — verify v_monthly_revenue returns rows with year, month, total_orders, total_revenue, avg_order_value
- [x] T016 [P] [US2] Write test `test_view_sales_summary_kpis` in `tests/test_store.py` — verify v_sales_summary returns total_orders, total_customers, total_revenue, total_profit, avg_order_value, total_units_sold
- [x] T017 [P] [US2] Write test `test_views_reflect_table_changes` in `tests/test_store.py` — verify views auto-update when underlying `sales` table data changes (re-persist with different data, query view again)

### Implementation for User Story 2

- [x] T018 [US2] Execute `create_views.sql` in `src/store.py` after table persistence — read SQL file, execute via `con.execute(sql_text)`
- [x] T019 [US2] Add view creation logging in `src/store.py` — log each view name after creation

**Checkpoint**: User Stories 1 AND 2 both work — data persisted with analytical views ready for consumption

---

## Phase 5: User Story 3 — Integridade e idempotência (Priority: P2)

**Goal**: Persistência é idempotente (reexecução = mesmo resultado) e validação pós-escrita confere contagem e soma de receita

**Independent Test**: Executar pipeline duas vezes e verificar resultados idênticos; validar contagem e soma de `net_revenue` entre DataFrame e DuckDB

### Tests for User Story 3 (TDD — write these FIRST, ensure they FAIL)

- [x] T020 [P] [US3] Write test `test_store_is_idempotent` in `tests/test_store.py` — run `store_analytics()` twice with same data, verify row count and `SUM(net_revenue)` are identical after second run
- [x] T021 [P] [US3] Write test `test_store_validates_record_count` in `tests/test_store.py` — verify `store_analytics()` raises or logs error when persisted count != input count
- [x] T022 [P] [US3] Write test `test_store_validates_revenue_sum` in `tests/test_store.py` — verify `store_analytics()` raises or logs error when `SUM(net_revenue)` in DuckDB != `df['net_revenue'].sum()`
- [x] T023 [P] [US3] Write test `test_store_handles_empty_dataframe` in `tests/test_store.py` — verify `store_analytics()` raises `ValueError` when input DataFrame is empty (edge case from spec)

### Implementation for User Story 3

- [x] T024 [US3] Add post-persistence validation in `src/store.py` — query `COUNT(*)` and `SUM(net_revenue)` from DuckDB, compare with input DataFrame, raise `ValueError` on mismatch
- [x] T025 [US3] Add empty DataFrame guard at top of `store_analytics()` — raise `ValueError` if `df.empty` (consistent with other pipeline stages)

**Checkpoint**: All user stories complete — pipeline persists data idempotently with integrity validation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, linting, and documentation alignment

- [x] T026 Run `ruff check src/store.py tests/test_store.py` and fix any lint errors (GATE 1)
- [x] T027 Run full test suite `pytest tests/test_store.py -v` and verify all tests pass (GATE 2)
- [x] T028 Run quickstart.md validation scenarios end-to-end (GATE 4)
- [x] T029 Run `ruff check src/ tests/` for full project lint (GATE 1 global)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (duckdb dependency installed)
- **US1 (Phase 3)**: Depends on T004 (create_tables.sql exists)
- **US2 (Phase 4)**: Depends on T011 (store.py exists with table persistence)
- **US3 (Phase 5)**: Depends on T011 (store.py exists with table persistence)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependencies on other stories
- **US2 (P2)**: Can start after US1 implementation (T011) — needs table to exist for views
- **US3 (P2)**: Can start after US1 implementation (T011) — validates persistence behavior
- US2 and US3 can run in parallel after US1 is complete

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Implementation follows tests
- Each story independently testable at its checkpoint

### Parallel Opportunities

- T006-T010 (US1 tests): All [P], can run in parallel
- T014-T017 (US2 tests): All [P], can run in parallel
- T020-T023 (US3 tests): All [P], can run in parallel
- T004 and T005 (SQL scripts): [P], can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
Task: "Write test test_store_creates_duckdb_file in tests/test_store.py"
Task: "Write test test_store_creates_sales_table in tests/test_store.py"
Task: "Write test test_store_preserves_record_count in tests/test_store.py"
Task: "Write test test_store_preserves_column_types in tests/test_store.py"
Task: "Write test test_store_auto_creates_directory in tests/test_store.py"

# Then implement (sequential — same file):
Task: "Implement store_analytics() in src/store.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (duckdb dependency)
2. Complete Phase 2: Foundational (SQL scripts)
3. Complete Phase 3: User Story 1 (table persistence)
4. **STOP and VALIDATE**: Run `pytest tests/test_store.py -v -k "not view and not idempotent and not valid"` — US1 tests pass
5. Pipeline now persists data to DuckDB

### Incremental Delivery

1. Setup + Foundational → SQL scripts ready
2. US1 → Table persistence works → MVP!
3. US2 → Views created → Analytical queries ready
4. US3 → Integrity validation → Production-ready
5. Polish → Lint + full validation → Ship

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once US1 (T011) is complete:
   - Developer A: US2 (views)
   - Developer B: US3 (validation)
3. Stories integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD is mandatory per Constitution Princípio III — tests FIRST, then implementation
- Golden data approach: use `data/input.csv` as source, verify outputs match expected values
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
