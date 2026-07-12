# Feature Specification: DuckDB Analytical Storage

**Feature Branch**: `005-duckdb-storage`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "Pegar os dados analíticos, já limpos e processados, e armazená-los no banco de dados DuckDB. Criar tabelas para armazenar os dados analíticos tratados e modelados. Criar views para facilitar a consulta aos dados. Utilizar a linguagem SQL para criar tabelas e views. Salvar os dados no DuckDB."

## User Scenarios & Testing

### User Story 1 - Persistência dos dados analíticos em tabelas (Priority: P1)

O pipeline ETL deve gravar os dados analíticos já limpos e processados em tabelas dentro de um banco de dados DuckDB. Cada tabela deve representar uma entidade analítica distinta (faturamento, vendas, etc.) e ser criada via SQL, com esquema consistente e tipos de dados adequados.

**Why this priority**: Sem persistir os dados em um banco, não é possível consultá-los, auditá-los ou integrá-los a ferramentas de visualização. Esta é a fundação de toda a camada de armazenamento analítico.

**Independent Test**: Pode ser testado executando o pipeline e verificando que o arquivo DuckDB é criado com todas as tabelas esperadas, contendo os dados corretos e tipos apropriados.

**Acceptance Scenarios**:

1. **Given** dados analíticos já limpos e processados disponíveis em memória, **When** a etapa de persistência é executada, **Then** o banco de dados DuckDB é criado/atualizado com todas as tabelas definidas no esquema
2. **Given** tabelas já existentes no DuckDB, **When** a persistência é reexecutada, **Then** as tabelas são substituídas com os dados atualizados (overwrite), sem duplicação
3. **Given** dados com diferentes tipos (datas, decimais, texto), **When** gravados no DuckDB, **Then** os tipos de coluna do DuckDB refletem corretamente os tipos dos dados de origem

---

### User Story 2 - Views de consulta analítica (Priority: P2)

Devem ser criadas views SQL no DuckDB que facilitem consultas analíticas comuns: métricas agregadas por período, por loja, por categoria, etc. As views devem ser criadas via SQL puro e representar agregações e cruzamentos já resolvidos.

**Why this priority**: As views eliminam a necessidade de escrever consultas complexas toda vez que alguém precisa de uma métrica. São o principal ponto de consumo dos dados armazenados.

**Independent Test**: Pode ser testado executando consultas SQL nas views e verificando que os resultados retornados são consistentes com os dados brutos gravados nas tabelas subjacentes.

**Acceptance Scenarios**:

1. **Given** tabelas de dados analíticos populadas no DuckDB, **When** as views são criadas, **Then** cada view retorna resultados corretos ao ser consultada
2. **Given** uma view de métricas agregadas, **When** consultada com filtros de período ou loja, **Then** os valores retornados batem com o cálculo manual sobre os dados brutos
3. **Given** views dependentes de múltiplas tabelas, **When** os dados de uma tabela subjacente mudam, **Then** a view reflete automaticamente as mudanças na próxima consulta

---

### User Story 3 - Verificação de integridade e idempotência (Priority: P2)

A execução do processo de persistência deve ser idempotente: rodar duas vezes deve produzir o mesmo resultado que rodar uma vez. Deve haver validação de que os dados gravados conferem com os dados de entrada (quantidade de registros, valores agregados-chave).

**Why this priority**: Garante que o pipeline pode ser reexecutado sem corromper dados ou gerar duplicatas, e dá confiança de que os dados armazenados são fiéis aos processados.

**Independent Test**: Pode ser testado executando o pipeline duas vezes consecutivamente e verificando que os dados finais são idênticos e que uma validação de contagem/valores passa.

**Acceptance Scenarios**:

1. **Given** pipeline executado uma vez com sucesso, **When** reexecutado, **Then** o banco de dados contém exatamente os mesmos registros e valores
2. **Given** dados processados com 1000 registros, **When** persistidos no DuckDB, **Then** a contagem de registros na tabela correspondente é exatamente 1000
3. **Given** uma métrica de faturamento calculada nos dados processados, **When** consultada via SQL no DuckDB, **Then** o valor retornado é idêntico ao calculado em memória

---

### Edge Cases

- O que acontece se o diretório de destino do arquivo DuckDB não existir?
- O que acontece se os dados de entrada estiverem vazios (0 registros)?
- O que acontece se uma coluna contiver valores nulos — os tipos do DuckDB são preservados?
- O que acontece se o esquema dos dados mudar entre execuções (coluna adicionada/removida)?

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE criar tabelas no DuckDB via SQL para cada entidade analítica (faturamento, vendas, dimensões)
- **FR-002**: O sistema DEVE criar views no DuckDB que agreguem e cruze dados de múltiplas tabelas para consultas analíticas comuns
- **FR-003**: O sistema DEVE persistir os dados usando SQL, não apenas operações em memória com pandas
- **FR-004**: O processo de persistência DEVE ser idempotente — reexecuções não devem gerar duplicatas
- **FR-005**: O sistema DEVE validar a integridade dos dados gravados (contagem de registros, valores-chave) após cada persistência
- **FR-006**: O sistema DEVE tratar automaticamente a criação do diretório de destino caso não exista
- **FR-007**: O sistema DEVE preservar tipos de dados corretos (datas, decimais, inteiros, texto) nas tabelas DuckDB

### Key Entities

- **Tabela de Faturamento**: Dados agregados de faturamento por loja, período e categorias de produto
- **Tabela de Vendas**: Dados detalhados de vendas com informações de produto, loja, data e valores
- **Tabelas de Dimensões**: Tabelas de referência (lojas, produtos, períodos) para enriquecimento de consultas
- **Views Analíticas**: Consultas SQL pré-definidas que agregam dados para consumo direto (métricas por período, ranking de lojas, ticket médio, etc.)
- **Banco DuckDB**: Arquivo de banco de dados que armazena todas as tabelas e views

## Success Criteria

### Measurable Outcomes

- **SC-001**: Todas as tabelas analíticas são criadas e populadas com sucesso em uma única execução do pipeline
- **SC-002**: As views retornam resultados consistentes com os dados brutos em 100% das consultas de validação
- **SC-003**: O processo é idempotente — duas execuções consecutivas produzem resultados idênticos
- **SC-004**: Validação de integridade confirma que contagem de registros e valores agregados conferem entre dados processados e dados armazenados
- **SC-005**: Consultas nas views completam em tempo hábil para consumo interativo (< 5 segundos para volumes esperados)

## Constitution Check

- **Princípio I (Simplicidade)**: A solução usa SQL direto no DuckDB, sem abstrações desnecessárias
- **Princípio II (DRY)**: Lógica de criação de tabelas/views é centralizada, não duplicada
- **Princípio III (TDD)**: Testes serão escritos antes da implementação, seguindo ciclo Red-Green-Refactor com golden data
- **Princípio IV (Reprodutibilidade)**: Persistência idempotente garante resultados determinísticos
- **Princípio V (Documentação)**: Views documentam implicitamente as regras de negócio via SQL

## Assumptions

- Os dados analíticos já estão limpos e processados pelas etapas anteriores do pipeline (extração, validação, preparação)
- O esquema das tabelas analíticas é definido pela feature 004-analytical-metrics ou anterior
- O arquivo DuckDB será armazenado em um diretório de saída padronizado no projeto
- O volume de dados é compatível com as capacidades do DuckDB (milhões de registros)
- Apenas uma instância do pipeline executa por vez (sem concorrência de escrita)
