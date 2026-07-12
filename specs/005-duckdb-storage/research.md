# Research: DuckDB Analytical Storage

**Feature**: 005-duckdb-storage
**Date**: 2026-07-12

## R1: DuckDB Python API — Persistência de DataFrames

**Decision**: Usar `duckdb.connect(database=path)` com `CREATE OR REPLACE TABLE ... AS SELECT * FROM df` para persistência idempotente.

**Rationale**: DuckDB permite registrar DataFrames Pandas diretamente em consultas SQL — sem necessidade de exportação intermediária. O padrão `CREATE OR REPLACE TABLE` garante idempotência nativa. DataFrames registrados em memória são acessíveis via SQL na mesma conexão.

**Alternatives considered**:
- `INSERT OR REPLACE`: Requer chave primária/única — complexidade desnecessária para overwrite completo
- Exportar CSV e importar via DuckDB CLI: Pipeline extra sem benefício
- Usar SQLAlchemy como abstração: Viola Princípio I (Simplicidade) — SQL direto é mais simples

**Key findings**:
- `duckdb.connect("path/to/file.duckdb")` cria o arquivo se não existir, mas **NÃO cria o diretório pai** — `Path.parent.mkdir(parents=True, exist_ok=True)` é obrigatório antes de conectar
- DataFrames são automaticamente acessíveis em SQL via `SELECT * FROM df` (nomes das variáveis Python)
- `con.execute(sql_text)` executa múltiplas statements SQL (separadas por `;`)
- `con.execute(...).fetchdf()` retorna DataFrame Pandas para validação
- `con.execute(...).fetchone()` retorna tupla para métricas simples (COUNT, SUM)
- Conexão deve ser fechada explicitamente (`con.close()`) para garantir persistência no arquivo

## R2: Scripts SQL como Fonte Única de Verdade

**Decision**: DDL de tabelas e views vive em arquivos `.sql` separados (`src/sql/create_tables.sql` e `src/sql/create_views.sql`), lidos e executados via Python.

**Rationale**: A constituição (Princípio IV) estabelece "Scripts SQL no DuckDB SÃO a fonte única de verdade para regras de negócio". Manter SQL em arquivos dedicados permite versionamento, auditoria e reuso independente do Python.

**Alternatives considered**:
- SQL inline no Python: Viola a constituição — SQL deve viver em arquivos
- Migration tools (Alembic, etc.): Complexidade desnecessária para pipeline local
- SQL em templates Jinja2: Over-engineering para DDL estático

## R3: Padrão de Validação Pós-Persistência

**Decision**: Validar contagem de registros e valores agregados-chave (soma de net_revenue) após cada persistência, usando consultas SQL diretas.

**Rationale**: Validação simples e eficaz que confirma integridade sem complexidade. Dois pontos de verificação (contagem + soma) são suficientes para detectar perda ou duplicação de dados.

**Alternatives considered**:
- Checksum completo de dados: Computacionalmente custoso, sem benefício adicional
- Comparação byte-a-byte com CSV: Fragiliza-se com diferenças de formatação
- Validação de todas as colunas individualmente: Over-engineering

## R4: Estrutura do Banco de Dados

**Decision**: Tabela única `sales` com todas as 32+ colunas analíticas, plus views para consultas agregadas.

**Rationale**: Os dados vêm de um único DataFrame (saída de `analyze_sales`). Normalizar em múltiplas tabelas exigiria JOINs constantes e adiciona complexidade. Views providenciam a camada de consulta sem duplicação de dados.

**Tables**:
- `sales`: Todos os dados analíticos (32+ colunas)

**Views** (consultas pré-definidas):
- `v_monthly_revenue`: Receita total por mês/ano
- `v_store_performance`: Métricas por loja (receita, pedidos, ticket médio)
- `v_category_sales`: Vendas por categoria e sub_categoria
- `v_top_products`: Ranking de produtos por receita
- `v_sales_summary`: Resumo geral com KPIs

## R5: Integração com Pipeline Existente

**Decision**: Novo módulo `store.py` com função `store_analytics()` que recebe DataFrame analítico e caminho do banco. Integrado como Stage 5 do pipeline.

**Rationale**: Segue o padrão estabelecido (um módulo por stage: extract → validate → prepare → analyze → store). Função pura com side effect controlado (escrita em disco).

**Pipeline flow**:
```
CSV → extract.py → validate.py → prepare.py → analyze.py → store.py → DuckDB
```
