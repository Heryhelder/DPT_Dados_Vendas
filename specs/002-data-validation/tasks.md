---

description: "Task list for sales data validation feature"

---

# Tasks: Validação de Dados de Vendas

**Input**: Design documents from `specs/002-data-validation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Obrigatórios por constituição (Princípio III: TDD). Testes DEVEM ser escritos antes da implementação e DEVEM falhar inicialmente (Red → Green → Refactor).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Project is already initialized (src/, tests/, pyproject.toml exist from feature 001)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Config constants exist in src/config.py (DEFAULT_DELIMITER, MAX_FILE_SIZE, etc. from feature 001)
- [X] T003 [P] Create src/validate.py with validate_sales() function signature, docstring, and private method stubs (one per validation rule) per contract in contracts/validate-sales.md
- [X] T004 [P] Create tests/test_validate.py with imports and helper fixtures for golden data

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Padronização de Tipos e Limpeza de Texto (Priority: P1) 🎯 MVP

**Goal**: Padronizar tipos (datas → datetime, monetários → float) e limpar textos (trim, capitalização)

**Independent Test**: Fornecer DataFrame com datas em formato texto, valores monetários como strings e textos com capitalização irregular, e verificar que a saída retorna tipos corretos e textos normalizados

### Tests for User Story 1 (TDD obrigatório) ⚠️

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [X] T005 [P] [US1] Write failing test for date standardization (FR-001: first_purchase_date, last_purchase_date, order_date → datetime) in tests/test_validate.py
- [X] T006 [P] [US1] Write failing test for monetary standardization (FR-002: unit_price, operating_expenses, cash_balance, debt_balance, monthly_burn → float64 2-dec) in tests/test_validate.py
- [X] T007 [P] [US1] Write failing test for text cleaning (FR-003/004: trim whitespace, title case for names, capitalized case for categoricals) in tests/test_validate.py

### Implementation for User Story 1

- [X] T008 [US1] Implement _standardize_dates() private method in src/validate.py (FR-001)
- [X] T009 [US1] Implement _standardize_monetary() private method in src/validate.py (FR-002)
- [X] T010 [US1] Implement _clean_text() private method in src/validate.py (FR-003, FR-004)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Consistência entre Colunas Numéricas (Priority: P1)

**Goal**: Validar consistência de colunas numéricas (quantidade, preço, desconto, valor de venda, datas)

**Independent Test**: Fornecer DataFrame com registros inconsistentes (quantity ≤ 0, unit_price ≤ 0, discount fora de [0,1], sale_value negativo, order_date < first_purchase_date) e verificar que são rejeitados

### Tests for User Story 2 (TDD obrigatório) ⚠️

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [X] T011 [P] [US2] Write failing test for quantity validation (FR-005: ≥ 1) in tests/test_validate.py
- [X] T012 [P] [US2] Write failing test for unit price validation (FR-006: > 0) in tests/test_validate.py
- [X] T013 [P] [US2] Write failing test for discount validation (FR-007: [0.0, 1.0]) in tests/test_validate.py
- [X] T014 [P] [US2] Write failing test for sale value validation (FR-008: calculado ≥ 0) in tests/test_validate.py
- [X] T015 [P] [US2] Write failing test for date consistency (FR-009: order_date ≥ first_purchase_date) in tests/test_validate.py

### Implementation for User Story 2

- [X] T016 [US2] Implement _validate_quantity() private method in src/validate.py (FR-005)
- [X] T017 [US2] Implement _validate_unit_price() private method in src/validate.py (FR-006)
- [X] T018 [US2] Implement _validate_discount() private method in src/validate.py (FR-007)
- [X] T019 [US2] Implement _validate_sale_value() private method in src/validate.py (FR-008)
- [X] T020 [US2] Implement _validate_dates_consistency() private method in src/validate.py (FR-009)

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Filtragem de Registros Válidos (Priority: P2)

**Goal**: Integrar todas as validações no método principal, remover duplicatas, filtrar rejeitados e retornar DataFrame válido

**Independent Test**: Fornecer mistura de registros válidos e inválidos e verificar que apenas válidos estão no DataFrame retornado

### Tests for User Story 3 (TDD obrigatório) ⚠️

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [X] T021 [P] [US3] Write failing test for duplicate removal (FR-010) in tests/test_validate.py
- [X] T022 [P] [US3] Write failing test for end-to-end validation (FR-011: retorna apenas registros válidos) in tests/test_validate.py
- [X] T023 [P] [US3] Write failing test for empty input rejection (ValueError se DataFrame vazio) in tests/test_validate.py
- [X] T024 [P] [US3] Write failing test for logging (FR-012: logs total, valid, rejected counts) in tests/test_validate.py
- [X] T025 [P] [US3] Write failing test for integration with extract_csv (validate_sales(extract_csv(...))) in tests/test_validate.py

### Implementation for User Story 3

- [X] T026 [US3] Implement _remove_duplicates() private method in src/validate.py (FR-010)
- [X] T027 [US3] Implement main validate_sales() orchestrator in src/validate.py (FR-011): chain all private methods, combine masks, filter and return
- [X] T028 [US3] Add structured logging (FR-012) to validate_sales() in src/validate.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T029 [P] Run ruff linter and fix all issues
- [X] T030 [P] Run full test suite and confirm all tests pass (green)
- [X] T031 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent from US1 (different private methods)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 methods being implemented (orchestrator calls all private methods)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Implementation after tests
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks marked [P] can run in parallel
- Once Foundational phase completes, US1 and US2 can start in parallel
- All tests for a user story marked [P] can run in parallel
- All implementation tasks within a user story run sequentially (same file)
- US3 depends on US1 + US2 implementations (precisa dos métodos privados)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write tests first):
Task: "Write failing test for date standardization in tests/test_validate.py"
Task: "Write failing test for monetary standardization in tests/test_validate.py"
Task: "Write failing test for text cleaning in tests/test_validate.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational
2. Complete Phase 3: User Story 1 (Padronização)
3. **STOP and VALIDATE**: Test User Story 1 independently
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP!
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2 (independent)
3. After US1+US2 implementation is complete:
   - Developer C: User Story 3 (depends on US1 + US2)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD obrigatório: verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Ruff linter must pass (Constitution GATE 1)
- All tests must pass (Constitution GATE 2)
- Implementation follows Python + Pandas; validations as private methods per plan

---

## Phase 7: Convergence

- [X] T032 Reject rows with NaN in monetary columns after standardization per FR-002 (partial)
- [X] T033 Include customer_id and product_id in text cleaning scope per FR-003 (partial)
