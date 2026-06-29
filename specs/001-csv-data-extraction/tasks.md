---

description: "Task list for CSV data extraction feature"
---

# Tasks: Extração de Dados CSV

**Input**: Design documents from `specs/001-csv-data-extraction/`

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

- [X] T001 Create project directory structure (src/, tests/, tests/data/, data/)
- [X] T002 [P] Create src/__init__.py and tests/__init__.py
- [X] T003 [P] Create pyproject.toml with dependencies (pandas>=2.2,<3, pytest, ruff, ipykernel>=7.2.0)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create configuration constants in src/config.py (DEFAULT_DELIMITER, DEFAULT_ENCODING, MAX_FILE_SIZE, SUPPORTED_ENCODINGS, SUPPORTED_DELIMITERS)
- [X] T005 [P] Create golden data CSV files in tests/data/ (sample_10rows.csv with 10 rows, 5 columns including valores extremos: negativo, decimal, notação científica, booleano, data, texto)
- [X] T006 [P] Create malformed CSV golden data in tests/data/sample_malformed.csv
- [X] T006a [P] Create empty CSV golden data in tests/data/sample_empty.csv

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Carregamento Padrão de CSV (Priority: P1) 🎯 MVP

**Goal**: Carregar CSV com cabeçalho e delimitador padrão (vírgula, UTF-8) e retornar DataFrame com tipos inferidos

**Independent Test**: Fornecer CSV de 10 linhas, 5 colunas e verificar que a tabela retornada tem o mesmo número de linhas, colunas e valores

### Tests for User Story 1 (TDD obrigatório) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Write failing test for basic CSV loading (10 rows, column names preserved) in tests/test_extract.py
- [X] T008 [P] [US1] Write failing test for type inference (numeric columns as numbers, text as text) in tests/test_extract.py
- [X] T008b [P] [US1] Write failing test for structured logging FR-011 (verificar path, linhas, duração no registro de log) in tests/test_extract.py

### Implementation for User Story 1

- [X] T009 [US1] Implement extract_csv() function (FR-001, FR-002, FR-003) with basic path param, pd.read_csv() and automatic type inference in src/extract.py
- [X] T010 [US1] Add structured logging (FR-011) to extract operation in src/extract.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Parâmetros Customizados (Priority: P2)

**Goal**: Especificar delimitador, encoding e tipos de coluna para carregar CSVs não padronizados

**Independent Test**: Fornecer CSV separado por ponto-e-vírgula com encoding Latin-1 e verificar que a tabela é carregada corretamente

### Tests for User Story 2 (TDD obrigatório) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US2] Write failing test for custom delimiter (semicolon) in tests/test_extract.py
- [X] T012 [P] [US2] Write failing test for custom encoding (Latin-1 with accented chars) in tests/test_extract.py
- [X] T013 [P] [US2] Write failing test for explicit dtypes (date column) in tests/test_extract.py

### Implementation for User Story 2

- [X] T014 [US2] Implement custom delimiter parameter (FR-004) in src/extract.py
- [X] T015 [US2] Implement custom encoding parameter (FR-005) in src/extract.py
- [X] T016 [US2] Implement explicit dtypes parameter (FR-006) in src/extract.py

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Tratamento de Erros (Priority: P3)

**Goal**: Mensagens de erro claras para arquivo ausente, vazio, malformado ou >100MB

**Independent Test**: Chamar a função com caminho inexistente e verificar que uma exceção descritiva é lançada

### Tests for User Story 3 (TDD obrigatório) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US3] Write failing test for FileNotFoundError FR-007 (verificar mensagem em português) in tests/test_extract.py
- [X] T018 [P] [US3] Write failing test for empty CSV detection FR-008 (verificar "CSV vazio" em português) in tests/test_extract.py
- [X] T019 [P] [US3] Write failing test for malformed CSV detection FR-009 (verificar mensagem descritiva em português) in tests/test_extract.py
- [X] T020 [P] [US3] Write failing test for file size > 100MB rejection FR-010 (verificar mensagem de rejeição em português) in tests/test_extract.py

### Implementation for User Story 3

- [X] T021 [US3] Implement FileNotFoundError handling (FR-007) in src/extract.py
- [X] T022 [US3] Implement empty CSV validation (FR-008) in src/extract.py
- [X] T023 [US3] Implement malformed CSV detection (FR-009) in src/extract.py
- [X] T024 [US3] Implement file size limit check (FR-010) in src/extract.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T025 [P] Run ruff linter and fix all issues
- [X] T026 [P] Run full test suite and confirm all tests pass (green)
- [X] T027 Run quickstart.md validation

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent from US1 (different parameters)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on extract function from US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Implementation after tests
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Once Foundational phase completes, US1 and US2 can start in parallel; US3 depende da implementação do US1 (precisa da função extract_csv)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write tests first):
Task: "Write failing test for basic CSV loading in tests/test_extract.py"
Task: "Write failing test for type inference in tests/test_extract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Carregamento Padrão)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

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
3. After US1 implementation is complete:
   - Developer C: User Story 3 (depends on US1)
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
