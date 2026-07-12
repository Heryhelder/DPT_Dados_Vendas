# Implementation Plan: DuckDB Analytical Storage

**Branch**: `005-duckdb-storage` | **Date**: 2026-07-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-duckdb-storage/spec.md`

## Summary

Implementar módulo de persistência analítica que recebe o DataFrame analítico (saída do `analyze_sales`, Stage 4) e o armazena em um banco de dados DuckDB via SQL. Criar tabela `sales` com todos os dados analíticos e views pré-definidas para consultas agregadas (métricas por período, loja, categoria, ranking de produtos, ticket médio). Persistência idempotente com validação de integridade.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: Pandas >= 2.2, < 3; DuckDB (novo — adicionar ao pyproject.toml)

**Storage**: DuckDB (arquivo `.duckdb` local)

**Testing**: pytest (golden data approach, TDD obrigatório)

**Target Platform**: Linux / Windows (estação de trabalho do analista)

**Project Type**: data-pipeline/library (módulo de persistência do ETL — Stage 5)

**Performance Goals**: Persistir 10.000 registros em menos de 3 segundos; views consultáveis em < 5 segundos

**Constraints**: Type hints obrigatórios; lint com ruff; TDD obrigatório; SQL para criação de tabelas/views (não pandas); persistência idempotente; raw data CSV nunca alterado

**Scale/Scope**: ~7.000 registros (~1.4MB), 32 colunas analíticas → 1 tabela + 5 views no DuckDB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Compliance

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Simplicidade (KISS+YAGNI) | ✅ PASS | Um módulo (`store.py`) com uma função principal. SQL direto no DuckDB sem abstrações extras. Tabela única com views para consultas. |
| II. Qualidade (DRY) | ✅ PASS | Type hints obrigatórios, ruff configurado, snake_case. Scripts SQL centralizados. Lógica de validação reutilizável. |
| III. TDD (Testes Obrigatórios) | ✅ PASS | Testes escritos antes da implementação. Golden data para cada cenário de persistência e consulta. |
| IV. Pipeline Reproduzível | ✅ PASS | Persistência idempotente (`CREATE OR REPLACE`). Mesma entrada sempre produz mesmo resultado. Seed fixa nos dados de teste. |
| V. Documentação e Observabilidade | ✅ PASS | Views documentam regras de negócio via SQL. Logs de persistência. Validação de integridade. |

### Quality Gates

- **GATE 0** (TDD): 🔴 Teste deve falhar antes da implementação — verificado
- **GATE 1** (ruff): 🔴 Linter deve passar — verificado
- **GATE 2** (Testes): 🔴 Testes devem passar — verificado
- **GATE 4** (Métricas golden data): 🔴 Dados conferidos com validação SQL — verificado

### Violations

Nenhuma violação. A solução é alinhada com todos os princípios.

## Project Structure

### Documentation (this feature)

```text
specs/005-duckdb-storage/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/          # Spec quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks) — Not yet generated
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── extract.py           # Função de extração CSV → DataFrame (existente)
├── validate.py          # Função de validação de dados (existente)
├── prepare.py           # Função de preparação analítica (existente)
├── analyze.py           # Função de métricas analíticas (existente)
├── store.py             # Função de persistência DuckDB (NOVO)
├── config.py            # Configuração (existente — adicionar DUCKDB_PATH)
└── sql/
    ├── create_tables.sql  # Scripts SQL de criação de tabelas (NOVO)
    └── create_views.sql   # Scripts SQL de criação de views (NOVO)

tests/
├── __init__.py
├── data/                # Golden data CSVs (existente)
├── test_extract.py      # Testes de extração (existente)
├── test_validate.py     # Testes de validação (existente)
├── test_prepare.py      # Testes de preparação (existente)
├── test_analyze.py      # Testes de métricas analíticas (existente)
└── test_store.py        # Testes de persistência DuckDB (NOVO)
```

**Structure Decision**: Single project (mesma estrutura das features anteriores). Novo módulo `store.py` em `src/` e diretório `sql/` para scripts SQL, seguindo o padrão estabelecido. A constituição exige "Scripts SQL no DuckDB SÃO a fonte única de verdade para regras de negócio" — portanto, DDL de tabelas e views vive em arquivos `.sql`, não em Python.

## Complexity Tracking

Nenhuma violação de complexidade identificada. A solução é uma função principal (`store_analytics`) que lê scripts SQL, cria tabelas/views e persiste o DataFrame — sem abstrações, frameworks ou camadas extras.
