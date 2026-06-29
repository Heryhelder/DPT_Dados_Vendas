# Research: Validação de Dados de Vendas

## Technology Decisions

### Language & Runtime

- **Decision**: Python 3.14
- **Rationale**: Versão fixada pelo projeto e pela constituição.
- **Alternatives considered**: N/A — fixado pelo projeto.

### Data Validation Approach

- **Decision**: Pandas com validação imperativa (métodos privados por regra)
- **Rationale**: O stack do projeto já inclui Pandas. Métodos privados isolam cada regra de validação (FR-001 a FR-012), facilitando teste unitário e manutenção. A validação é aplicada via transformações vetorizadas do Pandas, sem necessidade de loop explícito.
- **Alternatives considered**:
  - DuckDB SQL: validação em SQL seria possível, mas foge do fluxo Pandas → DataFrame definido no pipeline.
  - Pydantic: dependência extra não justificada (YAGNI) — Pandas já oferece conversão de tipos e validação.
  - Great Expectations: overkill para o escopo — framework completo de expectativas que adiciona complexidade sem necessidade imediata.

### Test Framework

- **Decision**: pytest + golden data
- **Rationale**: Mesmo framework usado na extração. Golden data (CSV de entrada conhecido → DataFrame esperado conhecido) é a abordagem mais direta para validar transformações de dados.
- **Alternatives considered**: N/A — fixado pelo projeto.

### Logging

- **Decision**: Módulo `logging` padrão do Python
- **Rationale**: Obrigatório pela constituição (Princípio V). Suficiente para registrar contagem de registros processados, válidos e rejeitados.
- **Alternatives considered**: N/A — fixado pelo projeto.

### Output Format

- **Decision**: DataFrame Pandas (sem persistência em disco)
- **Rationale**: Clarificado na spec (Q1). A função retorna apenas registros válidos; rejeitados são descartados em memória.
- **Alternatives considered**: CSV em disco — rejeitado pelo usuário.

### Date Parsing

- **Decision**: `pd.to_datetime()` com `format="mixed"` e `errors="coerce"`
- **Rationale**: O CSV usa formato ISO (YYYY-MM-DD), mas `format="mixed"` permite detectar automaticamente outros formatos sem falhar em variações. `errors="coerce"` converte datas inválidas para NaT, que são então filtradas como registros rejeitados.
- **Alternatives considered**:
  - `errors="raise"`: Quebraria o pipeline no primeiro registro com data inválida — comportamento inadequado para batch validation.
  - Formato fixo (`format="%Y-%m-%d"`): Muito restritivo para dados reais que podem ter variações.

### Text Normalization

- **Decision**: `str.strip()` para remoção de espaços; `str.title()` para nomes próprios; `str.capitalize()` ou mapeamento fixo para campos categóricos.
- **Rationale**: `str.strip()` remove espaços extras. `str.title()` é adequado para nomes (ex: "thiago alves" → "Thiago Alves"). Campos categóricos como `customer_segment` ("Consumer", "Corporate", "SMB") usam capitalização padronizada por dicionário ou `str.capitalize()`.
- **Alternatives considered**: Regex — desnecessário para operações que o Pandas já resolve vetorizadamente.
