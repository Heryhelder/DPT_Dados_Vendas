# Implementation Plan: Analytical Data Preparation

**Branch**: `003-analytical-preparation` | **Date**: 2026-07-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-analytical-preparation/spec.md`

## Summary

Implementar função de preparação analítica que recebe um DataFrame validado (do `validate_sales`) e retorna um novo DataFrame com colunas temporais (mês, ano, trimestre) extraídas de `order_date`, dimensões de negócio padronizadas (título) para região, vendedor, categoria, canal e tipo de cliente, e logging de estatísticas de transformação.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: Pandas >= 2.2, < 3

**Storage**: N/A (operação em memória sobre DataFrame)

**Testing**: pytest (golden data approach)

**Target Platform**: Linux / Windows (estação de trabalho do analista)

**Project Type**: data-pipeline/library (módulo de preparação do ETL)

**Performance Goals**: Preparar 100.000 registros em menos de 1 segundo

**Constraints**: Type hints obrigatórios; lint com ruff; TDD obrigatório; retornar novo DataFrame (imutável)

**Scale/Scope**: 7.000 registros (~1.4MB), 25 colunas de entrada → 28 colunas de saída

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Compliance

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Simplicidade (KISS+YAGNI) | ✅ PASS | Função única com métodos privados. Operações vetorizadas pandas sem loops. |
| II. Qualidade (DRY) | ✅ PASS | Type hints obrigatórios, ruff configurado, snake_case. Lógica centralizada em módulo único. |
| III. TDD (Testes Obrigatórios) | ✅ PASS | Testes escritos antes da implementação. Golden data para cada cenário. |
| IV. Pipeline Reproduzível | ✅ PASS | Transformação determinística — mesmo DataFrame de entrada sempre produz mesma saída. |
| V. Documentação e Observabilidade | ✅ PASS | Logs de estatísticas de transformação. Docstrings em todas as funções. |

### Quality Gates

- **GATE 0** (TDD): 🔴 Teste deve falhar antes da implementação — verificado
- **GATE 1** (ruff): 🔴 Linter deve passar — verificado
- **GATE 2** (Testes): 🔴 Testes devem passar — verificado

### Violations

Nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/003-analytical-preparation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── prepare-sales.md
└── tasks.md             # Phase 2 output (/speckit.tasks) — Generated 2026-07-12
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── extract.py           # Função de extração CSV → DataFrame (existente)
├── validate.py          # Função de validação de dados (existente)
├── prepare.py           # Função de preparação analítica (NOVO)
└── config.py            # Configuração (existente)

tests/
├── __init__.py
├── data/                # Golden data CSVs (existente)
├── test_extract.py      # Testes de extração (existente)
├── test_validate.py     # Testes de validação (existente)
└── test_prepare.py      # Testes de preparação (NOVO)
```

**Structure Decision**: Single project (mesma estrutura das features 001/002). Organização simples com `src/` para código fonte e `tests/` para testes.

## Complexity Tracking

Nenhuma violação de complexidade identificada. A solução é uma função principal que chama métodos privados — sem abstrações, frameworks ou camadas extras.
