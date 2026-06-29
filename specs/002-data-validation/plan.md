# Implementation Plan: Validação de Dados de Vendas

**Branch**: `002-data-validation` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-data-validation/spec.md`

## Summary

Implementar função de validação de dados de vendas que recebe um DataFrame bruto (do `extract_csv`) e retorna um DataFrame limpo contendo apenas registros válidos. A validação inclui: padronização de tipos (datas → datetime, monetários → float), limpeza de texto (trim, capitalização), verificação de consistência numérica (quantidade, preço, desconto, valor de venda), validação de datas, remoção de duplicatas e log de registros rejeitados. Cada regra de validação é implementada como método privado e orquestrada por um método principal.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: Pandas >= 2.2, < 3

**Storage**: N/A (operação em memória sobre DataFrame)

**Testing**: pytest (golden data approach)

**Target Platform**: Linux / Windows (estação de trabalho do analista)

**Project Type**: data-pipeline/library (módulo de validação do ETL)

**Performance Goals**: Validar 7.000 registros em menos de 10 segundos

**Constraints**: Type hints obrigatórios; lint com ruff; TDD obrigatório; cada regra de validação em método privado separado

**Scale/Scope**: 7.000 registros (~1.4MB), 25 colunas; arquivo de entrada limitado a 100MB pelo extract_csv

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Compliance

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Simplicidade (KISS+YAGNI) | ✅ PASS | Função única com métodos privados por regra. Sem abstrações desnecessárias. Pandas operations vetorizadas sem loops. |
| II. Qualidade (DRY) | ✅ PASS | Type hints obrigatórios, ruff configurado, snake_case. Lógica de validação centralizada em módulo único. |
| III. TDD (Testes Obrigatórios) | ✅ PASS | Testes escritos antes da implementação. Golden data para cada cenário. |
| IV. Pipeline Reproduzível | ✅ PASS | Validação determinística — mesmo DataFrame de entrada sempre produz mesma saída. |
| V. Documentação e Observabilidade | ✅ PASS | Logs de contagem de registros processados/válidos/rejeitados. Documentação inline da função. |

### Quality Gates

- **GATE 0** (TDD): 🔴 Teste deve falhar antes da implementação — verificado
- **GATE 1** (ruff): 🔴 Linter deve passar — verificado
- **GATE 2** (Testes): 🔴 Testes devem passar — verificado

### Violations

Nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/002-data-validation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── validate-sales.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── extract.py           # Função de extração CSV → DataFrame (existente)
├── config.py            # Configuração (existente)
└── validate.py          # Função de validação de dados de vendas (NOVO)

tests/
├── __init__.py
├── data/                # Golden data CSVs (existente)
└── test_validate.py     # Testes de validação (NOVO)
```

**Structure Decision**: Single project (mesma estrutura da feature 001). Organização simples com `src/` para código fonte e `tests/` para testes.

## Complexity Tracking

Nenhuma violação de complexidade identificada. A solução é uma função principal que chama métodos privados — sem abstrações, frameworks ou camadas extras.
