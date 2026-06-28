<!--
  Sync Impact Report
  Version change: 1.0.0 → 1.1.0
  Modified principles:
    III. Testes de Dados Obrigatórios → III. TDD — Testes de Dados Obrigatórios
  Added sections:
    - Processo de Emendas (governance, reinstated)
    - Política de Versionamento (governance, reinstated)
    - Etapa TDD no Fluxo de Desenvolvimento
    - GATE 0: TDD Compliance
  Removed sections: none
  Templates requiring updates:
    ✅ .specify/templates/plan-template.md
    ✅ .specify/templates/spec-template.md
    ⚠ .specify/templates/tasks-template.md (test tasks now mandatory per constitution)
  Follow-up TODOs: none
-->

# DPT - Dados_Vendas Constitution

## Core Principles

### I. Simplicidade como Padrão (KISS + YAGNI)

Toda solução DEVE começar pela abordagem mais simples que atenda aos
requisitos. Nenhuma abstração, framework ou camada extra DEVE ser
introduzida sem necessidade imediata comprovada. Código, estrutura de
dados e pipeline DEVEM ser eliminados quando não mais agregam valor.

**Rationale**: Projetos de dados acumulam complexidade acidental
rapidamente. Manter simplicidade reduz custos de manutenção, facilita
auditoria e permite que qualquer membro da equipe entenda o fluxo
completo sem documentação extensa.

### II. Qualidade e Consistência de Código (DRY)

Lógica de transformação NÃO DEVE ser duplicada em múltiplos pontos do
pipeline. Type hints SÃO OBRIGATÓRIOS em todo código Python. O linter
(ruff) DEVE ser executado antes de cada commit. Nomes de colunas,
funções e variáveis DEVEM seguir um padrão consistente (snake_case).

**Rationale**: Duplicação é a principal fonte de divergência entre
dados reportados. Tipagem explícita previne erros silenciosos em
transformações de dados. Linting automatizado garante que o código
permaneça legível e consistente ao longo do tempo.

### III. TDD — Testes de Dados Obrigatórios

Toda transformação no pipeline ETL DEVE seguir o ciclo TDD (Test-Driven
Development):
1. **Red**: Escrever o teste antes da implementação — o teste DEVE
   falhar inicialmente
2. **Green**: Implementar a transformação mínima para passar o teste
3. **Refactor**: Melhorar o código sem quebrar o teste

Testes DEVEM seguir a abordagem de "golden data": entrada conhecida →
saída esperada conhecida. Cada estágio do pipeline (extração,
validação, preparação, métricas) DEVE ser testável de forma
independente. Testes SÃO EXIGIDOS em toda feature — não são opcionais.

**Rationale**: O ciclo TDD garante que todo código de transformação
seja escrito exclusivamente para atender a um comportamento
verificável. Isso elimina código não testado, revela suposições
incorretas sobre os dados antes da implementação e documenta o
comportamento esperado de cada transformação.

### IV. Pipeline Reproduzível e Determinístico

O ETL DEVE produzir os mesmos resultados quando executado com os mesmos
dados de entrada. TODAS as operações com componente aleatório DEVEM
usar seed fixa. Scripts SQL no DuckDB SÃO a fonte única de verdade
para regras de negócio. O pipeline DEVE ser executável de ponta a
ponta com um único comando.

**Rationale**: Reproducibilidade é fundamental para auditoria,
depuração e confiança nos dados. Se duas execuções produzem resultados
diferentes, o pipeline não pode ser verificado nem auditado.

### V. Documentação e Observabilidade

Toda métrica de negócio DEVE ter definição explícita (fórmula, escopo,
exclusões). Transformações relevantes DEVEM ser comentadas no código
ou em documentação adjacente. A linhagem dos dados (origem →
transformação → dashboard) DEVE ser rastreável. Logs estruturados DEVEM
ser usados para diagnóstico de falhas.

**Rationale**: Sem documentação, métricas perdem significado quando a
pessoa que as criou não está mais no projeto. Rastreabilidade permite
identificar rapidamente a causa de discrepâncias em relatórios.

## Technology Stack & Constraints

### Stack Obrigatória

- **Linguagem**: Python 3.14
- **Manipulação de Dados**: Pandas >= 2.2, < 3
- **Banco Analítico**: DuckDB (SQL)
- **Visualização**: Tableau
- **Linter**: ruff

### Constraints

- Versões de dependências DEVEM ser fixadas (sem ranges abertos além
  dos especificados)
- Nenhuma dependência externa além das listadas DEVE ser adicionada sem
  justificativa por escrito
- O dado bruto (`input.csv`) NUNCA DEVE ser alterado — transformações
  sempre produzem novas tabelas/arquivos
- Tabelas e views analíticas DEVEM ser criadas via SQL no DuckDB, não
  em memória com pandas

## Development Workflow & Quality Gates

### Fluxo de Desenvolvimento

0. **TDD** — Para cada etapa abaixo, escrever o teste antes da
   implementação (Red → Green → Refactor)
1. **Extrair** dados brutos do CSV para DataFrame
2. **Validar** tipos, consistência e integridade
3. **Preparar** colunas analíticas (mês, ano, trimestre, dimensões)
4. **Métricas** SQL no DuckDB (faturamento, ticket médio, etc.)
5. **Exportar** para Tableau

### Quality Gates

- **GATE 0**: Teste escrito e falhando antes de qualquer código de
  implementação (TDD compliance)
- **GATE 1**: Linter (ruff) passa sem erros
- **GATE 2**: Testes de transformação passam
- **GATE 3**: Validação de dados concluída sem registros rejeitados
  além do tolerável
- **GATE 4**: Métricas conferidas com golden data
- **GATE 5**: Dados exportados para Tableau batem com consulta SQL
  direta

## Governance

A constituição substitui todas as práticas anteriores não documentadas.
Todo PR ou alteração DEVE verificar conformidade com os princípios
aqui definidos.

### Processo de Emendas

1. Propor alteração via PR com justificativa
2. Documentar impacto nos princípios existentes
3. Obter aprovação de ao menos um revisor
4. Atualizar `LAST_AMENDED_DATE`
5. Incrementar versão conforme política abaixo

### Política de Versionamento

- **MAJOR**: Remoção ou redefinição de princípio existente
- **MINOR**: Adição de novo princípio ou seção, ou expansão material
  de orientação existente
- **PATCH**: Esclarecimentos, correções de redação, ajustes não
  semânticos

### Revisão de Conformidade

Toda feature spec DEVE incluir uma seção "Constitution Check"
verificando aderência. O plan template já inclui este gate.

**Version**: 1.1.0 | **Ratified**: 2026-06-28 | **Last Amended**: 2026-06-28
