# Implementation Plan: Extração de Dados CSV

**Branch**: `001-csv-data-extraction` | **Date**: 2026-06-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-csv-data-extraction/spec.md`

## Summary

Implementar uma função de extração que carrega dados de um arquivo CSV
em um diretório e retorna uma estrutura de dados tabular (DataFrame).
A função deve aceitar parâmetros customizáveis (delimitador, encoding,
tipos de coluna), rejeitar arquivos >100MB, registrar logs estruturados
e tratar erros de forma clara (arquivo ausente, vazio, malformado).

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: Pandas >= 2.2, < 3; ipykernel >= 7.2.0

**Storage**: DuckDB (dados analíticos persistidos para Tableau); CSV
bruto mantido inalterado no sistema de arquivos

**Testing**: pytest (golden data approach)

**Target Platform**: Linux / Windows (estação de trabalho do analista)

**Project Type**: data-pipeline/library (módulo de extração do ETL)

**Performance Goals**: Carregar CSV de até 100MB em < 2 segundos

**Constraints**: < 200MB de memória para o processo de extração; TDD
obrigatório; lint com ruff; type hints obrigatórios

**Scale/Scope**: Arquivos CSV únicos de até 100MB; encoding UTF-8
(padrão) e Latin-1 (custom); delimitadores vírgula, ponto-e-vírgula,
tab

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Compliance

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Simplicidade (KISS+YAGNI) | ✅ PASS | Função única de extração, sem abstrações desnecessárias. Pandas `read_csv` é a abordagem mais simples. |
| II. Qualidade (DRY) | ✅ PASS | Type hints obrigatórios, ruff configurado, snake_case. Lógica de leitura centralizada em um módulo. |
| III. TDD (Testes Obrigatórios) | ✅ PASS | Testes escritos antes da implementação. Golden data para cada cenário. |
| IV. Pipeline Reproduzível | ✅ PASS | Leitura de CSV é determinística. Seed fixa não aplicável (não há aleatoriedade). |
| V. Documentação e Observabilidade | ✅ PASS | FR-011: logs estruturados obrigatórios. Documentação inline da função. |

### Quality Gates

- **GATE 0** (TDD): 🔴 Teste deve falhar antes da implementação — verificado
- **GATE 1** (ruff): 🔴 Linter deve passar — verificado
- **GATE 2** (Testes): 🔴 Testes devem passar — verificado

### Violations

Nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/001-csv-data-extraction/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── extract.py           # Função de extração CSV → DataFrame
└── config.py            # Configuração (constantes, defaults)

tests/
├── __init__.py
├── test_extract.py      # Testes de extração (golden data)
└── data/                # CSVs de teste (golden files)
    ├── sample_10rows.csv
    ├── sample_empty.csv
    └── sample_malformed.csv

data/                    # Dados brutos (input) — NUNCA alterar
└── input.csv
```

**Structure Decision**: Single project (Option 1 — DEFAULT). Organização
simples com `src/` para código fonte e `tests/` para testes, conforme
projeto de dados unificado (sem frontend/backend).

## Complexity Tracking

Nenhuma violação de complexidade identificada. A solução é uma função
única com parâmetros opcionais — sem abstrações, frameworks ou camadas
extras.
