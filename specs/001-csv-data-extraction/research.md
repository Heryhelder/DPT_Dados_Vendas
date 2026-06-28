# Research: Extração de Dados CSV

## Technology Decisions

### Language & Runtime

- **Decision**: Python 3.14
- **Rationale**: Versão definida no escopo do projeto e na constituição.
- **Alternatives considered**: N/A — fixado pelo projeto.

### CSV Parsing

- **Decision**: Pandas `read_csv()`
- **Rationale**: Biblioteca padrão do projeto (Pandas >= 2.2, < 3).
  `read_csv` é madura, performática e oferece suporte nativo a
  encoding, delimitadores, inferência de tipos e tratamento de erros.
- **Alternatives considered**:
  - `csv` padrão do Python: muito verboso, sem inferência de tipos
  - DuckDB `read_csv_auto`: excelente para SQL, mas foge do fluxo
    Pandas → DataFrame definido na especificação
  - Polars: não consta no stack do projeto

### Test Framework

- **Decision**: pytest
- **Rationale**: Padrão da indústria Python para testes. Suporte a
  fixtures, parametrização e golden data via `pytest`.
- **Alternatives considered**:
  - unittest: muito verboso, sem vantagens sobre pytest
  - hypothesis: bom para propriedades, mas golden data é mais direto

### Logging

- **Decision**: Módulo `logging` padrão do Python + estrutura JSON
- **Rationale**: Obrigatório pela constituição (Princípio V). O módulo
  `logging` é suficiente para logs estruturados sem dependência extra.
- **Alternatives considered**:
  - structlog: dependência extra não justificada (YAGNI)
  - loguru: mesma justificativa

### File Size Limit

- **Decision**: Rejeitar arquivos > 100MB com mensagem clara
- **Rationale**: Clarificação do usuário (opção A). Simplifica
  implementação ao evitar streaming/chunking. 100MB é suficiente para
  datasets analíticos típicos.
- **Alternatives considered**:
  - Streaming/chunked loading: complexidade injustificada (KISS)
  - DuckDB lazy loading: desnecessário para o escopo
