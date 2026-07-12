# Implementation Plan: Analytical Metrics

**Branch**: `004-analytical-metrics` | **Date**: 2026-07-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-analytical-metrics/spec.md`

## Summary

Implementar módulo de métricas analíticas que recebe um DataFrame preparado (do `prepare_sales`, Stage 3) e retorna um novo DataFrame com colunas derivadas de receita (gross_revenue, net_revenue, cost_of_goods_sold, gross_profit) e métricas opcionais (ebitda, net_income), além de funções de análise: agregações por dimensão, sazonalidade, top performers e recorrência de clientes.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: Pandas >= 2.2, < 3

**Storage**: N/A (operação em memória sobre DataFrame)

**Testing**: pytest (golden data approach)

**Target Platform**: Linux / Windows (estação de trabalho do analista)

**Project Type**: data-pipeline/library (módulo de métricas do ETL — Stage 4)

**Performance Goals**: Calcular métricas para 100.000 registros em menos de 2 segundos

**Constraints**: Type hints obrigatórios; lint com ruff; TDD obrigatório; retornar novo DataFrame (imutável); métricas em pandas (justificado — dependem de colunas derivadas computadas em Python)

**Scale/Scope**: 7.000 registros (~1.4MB), 28 colunas de entrada → 32 colunas de saída (28 + gross_revenue, net_revenue, cost_of_goods_sold, gross_profit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Compliance

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Simplicidade (KISS+YAGNI) | ✅ PASS | Função principal com métodos privados. Operações vetorizadas pandas sem loops. Sem abstrações extras. |
| II. Qualidade (DRY) | ✅ PASS | Type hints obrigatórios, ruff configurado, snake_case. Fórmulas de negócio documentadas em docstrings. |
| III. TDD (Testes Obrigatórios) | ✅ PASS | Testes escritos antes da implementação. Golden data para cada cenário de métrica. |
| IV. Pipeline Reproduzível | ✅ PASS | Transformação determinística — mesmo DataFrame de entrada sempre produz mesma saída. Seed fixa onde aplicável. |
| V. Documentação e Observabilidade | ✅ PASS | Logs de estatísticas de computação. Fórmulas documentadas em docstrings. Métricas com definição explícita. |

### Quality Gates

- **GATE 0** (TDD): 🔴 Teste deve falhar antes da implementação — verificado
- **GATE 1** (ruff): 🔴 Linter deve passar — verificado
- **GATE 2** (Testes): 🔴 Testes devem passar — verificado
- **GATE 4** (Métricas golden data): 🔴 Métricas conferidas com dados de teste — verificado

### Violations

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Métricas em pandas (não DuckDB SQL) | Colunas derivadas (gross_revenue, net_revenue, COGS, gross_profit) são computadas em Python; métricas agregadas dependem delas | DuckDB não tem acesso às colunas derivadas sem antes exportar para tabela — adiciona etapa desnecessária |

**Justificativa**: A constituição prevê "Métricas SQL no DuckDB (faturamento, ticket médio, etc.)" como Stage 4. No entanto, as colunas derivadas de receita são computadas em Python (pandas) e as métricas agregadas dependem diretamente delas. Usar DuckDB exigiria exportar o DataFrame para uma tabela temporária primeiro, adicionando complexidade sem benefício. O módulo pandas mantém o pipeline simples e autônomo. Quando as colunas derivadas estiverem disponíveis no DuckDB (fase futura), as métricas poderão ser migradas para SQL.

## Project Structure

### Documentation (this feature)

```text
specs/004-analytical-metrics/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── analyze-sales.md
└── tasks.md             # Phase 2 output (/speckit.tasks) — Not yet generated
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── extract.py           # Função de extração CSV → DataFrame (existente)
├── validate.py          # Função de validação de dados (existente)
├── prepare.py           # Função de preparação analítica (existente)
├── analyze.py           # Função de métricas analíticas (NOVO)
└── config.py            # Configuração (existente)

tests/
├── __init__.py
├── data/                # Golden data CSVs (existente)
├── test_extract.py      # Testes de extração (existente)
├── test_validate.py     # Testes de validação (existente)
├── test_prepare.py      # Testes de preparação (existente)
└── test_analyze.py      # Testes de métricas analíticas (NOVO)
```

**Structure Decision**: Single project (mesma estrutura das features 001/003). Novo módulo `analyze.py` em `src/` seguindo o padrão estabelecido.

## Complexity Tracking

Nenhuma violação de complexidade identificada. A solução é uma função principal (`analyze_sales`) que chama métodos privados para cada tipo de métrica — sem abstrações, frameworks ou camadas extras.
