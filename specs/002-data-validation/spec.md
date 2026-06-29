# Feature Specification: Validação de Dados de Vendas

**Feature Branch**: `002-data-validation`

**Created**: 2026-06-29

**Status**: Draft

**Input**: "Adicionar uma nova feature que deve validar os dados do arquivo data/electronics_sales_raw.csv. Conferir consistência entre colunas numéricas (quantidade, valor unitário, desconto e valor de venda). Padronizar tipos de dados (datas para datetime, valores monetários para float). Remover espaços extras, corrigir capitalizações e manter apenas registros válidos após o tratamento inicial."

## Clarifications

### Session 2026-06-29

- Q: Os conjuntos válido e rejeitado devem ser arquivos CSV ou DataFrames em memória?
  → A: A função deve remover dados rejeitados e retornar um DataFrame com os dados válidos (registros rejeitados são descartados, sem persistência em arquivo).
- Q: Como validar o "valor de venda" se não existe coluna correspondente no CSV?
  → A: Validar que `quantity * unit_price * (1 - discount_pct) >= 0` (valor de venda calculado não pode ser negativo).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Padronização de Tipos e Limpeza de Texto (Priority: P1)

Como analista de dados, quero que todas as colunas do CSV tenham tipos de dados corretos (datas como datetime, valores monetários como float) e que textos estejam limpos (sem espaços extras, capitalização consistente), para que as etapas seguintes de análise não quebrem por inconsistências de formato.

**Why this priority**: É a base de toda a validação — sem tipos padronizados e textos limpos, as verificações de consistência numérica não podem ser executadas de forma confiável.

**Independent Test**: Pode ser testado fornecendo um CSV com datas em formato textual, valores monetários como strings e textos com capitalização irregular, e verificando que a saída retorna datas como datetime, valores como float e textos normalizados.

**Acceptance Scenarios**:

1. **Given** um CSV com colunas de data em formato texto,
   **When** a validação é executada,
   **Then** as colunas `first_purchase_date`, `last_purchase_date` e `order_date` são convertidas para datetime.
2. **Given** um CSV com valores monetários (`unit_price`, `operating_expenses`, `cash_balance`, `debt_balance`, `monthly_burn`) como float64,
   **When** a validação é executada,
   **Then** todos os valores monetários permanecem como float64 e são arredondados para 2 casas decimais.
3. **Given** um CSV com textos contendo espaços extras ou capitalização inconsistente,
   **When** a validação é executada,
   **Then** colunas de texto (`customer_name`, `product_name`, `category`, `sub_category`, `brand`, `customer_segment`, `customer_type`, `sales_channel`, `payment_method`, `sales_rep`, `region`) têm espaços removidos e capitalização padronizada (title case para nomes próprios, maiúsculo para siglas).

### User Story 2 - Consistência entre Colunas Numéricas (Priority: P1)

Como analista, quero verificar que as colunas numéricas relacionadas são consistentes entre si (quantidade, valor unitário, percentual de desconto e valor total calculado), para garantir que não há registros com dados corrompidos ou inconsistentes.

**Why this priority**: Inconsistências numéricas indicam dados corrompidos que, se não detectados, geram métricas erradas nos dashboards.

**Independent Test**: Pode ser testado fornecendo um CSV onde alguns registros têm valores inconsistentes (ex: quantidade × preço unitário não corresponde ao esperado) e verificando que esses registros são sinalizados.

**Acceptance Scenarios**:

1. **Given** um registro onde `quantity * unit_price * (1 - discount_pct)` é negativo,
   **When** a validação é executada,
   **Then** o registro é rejeitado por inconsistência entre quantidade, preço e desconto.
2. **Given** um registro onde `discount_pct` está fora do intervalo [0, 1],
   **When** a validação é executada,
   **Then** o registro é marcado como inválido.
3. **Given** um registro onde `quantity` é zero ou negativo,
   **When** a validação é executada,
   **Then** o registro é marcado como inválido.
4. **Given** um registro onde `unit_price` é negativo,
   **When** a validação é executada,
   **Then** o registro é marcado como inválido.

### User Story 3 - Filtragem de Registros Válidos (Priority: P2)

Como analista, quero que o pipeline retorne apenas registros válidos após a validação, descartando os registros que falharam em qualquer regra, para que eu possa prosseguir com a análise confiando na integridade dos dados.

**Why this priority**: A filtragem de registros inválidos é essencial para garantir que análises e dashboards usem apenas dados consistentes.

**Independent Test**: Pode ser testado fornecendo uma mistura de registros válidos e inválidos e verificando que apenas os válidos estão no DataFrame retornado.

**Acceptance Scenarios**:

1. **Given** um CSV com 100 registros, sendo 10 inválidos por diferentes razões,
   **When** a validação e filtragem são executadas,
   **Then** o DataFrame retornado contém 90 registros.
2. **Given** um CSV onde todos os registros são válidos,
   **When** a validação e filtragem são executadas,
   **Then** o DataFrame retornado contém todos os registros originais.
3. **Given** um CSV onde todos os registros são inválidos,
   **When** a validação e filtragem são executadas,
   **Then** o DataFrame retornado está vazio.

### Edge Cases

- **Valor de venda negativo**: O CSV não possui coluna explícita de "valor de venda". A validação deve calcular `quantity * unit_price * (1 - discount_pct)` e rejeitar registros onde o resultado for negativo, pois isso indica inconsistência entre quantidade, preço e desconto.
- **Percentual de desconto como decimal vs. percentual**: O desconto pode vir como 0.05 (5%) ou 5.0 (5%). A validação deve interpretar corretamente considerando o intervalo [0, 1] como decimal.
- **Datas inválidas (ex: 2024-02-30, 31/06/2024)**: Registros com datas impossíveis devem ser rejeitados.
- **Valores monetários com símbolos (ex: R$ 1.234,56)**: O pipeline deve lidar ou rejeitar formatos não padronizados.
- **Linhas totalmente vazias ou com apenas separadores**: Devem ser rejeitadas silenciosamente.
- **Duplicatas exatas de linhas**: Devem ser detectadas e removidas com registro no log de rejeição.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST convert date columns (`first_purchase_date`, `last_purchase_date`, `order_date`) to datetime type, rejecting records with unparseable dates.
- **FR-002**: System MUST ensure monetary columns (`unit_price`, `operating_expenses`, `cash_balance`, `debt_balance`, `monthly_burn`) are float64 with 2-decimal precision.
- **FR-003**: System MUST trim leading/trailing whitespace from all text columns.
- **FR-004**: System MUST normalize text columns to title case for names (`customer_name`, `product_name`, `brand`, `sales_rep`) and consistent case for categorical fields (`customer_segment`, `customer_type`, `category`, `sub_category`, `sales_channel`, `payment_method`, `region`).
- **FR-005**: System MUST validate that `quantity` is a positive integer (≥ 1).
- **FR-006**: System MUST validate that `unit_price` is a positive number (> 0).
- **FR-007**: System MUST validate that `discount_pct` is in the range [0.0, 1.0] (interpreted as decimal).
- **FR-008**: System MUST compute `quantity * unit_price * (1 - discount_pct)` and reject records where the result is negative (indicating data inconsistency).
- **FR-009**: System MUST validate that `order_date` is not earlier than `first_purchase_date`.
- **FR-010**: System MUST detect and remove exact duplicate rows, logging them as rejected.
- **FR-011**: System MUST return a single DataFrame containing only records that passed all validation checks; rejected records are discarded.
- **FR-012**: System MUST log the count of total, valid, and rejected records after each run.

### Key Entities

- **Registro de Venda**: Linha individual do CSV contendo dados de um pedido (order_id, produto, cliente, quantidade, preço, etc.). É a unidade básica de validação.
- **Conjunto Válido**: Subconjunto dos registros que passaram em todas as regras de validação. Pronto para consumo nas etapas seguintes do pipeline.
- **Regra de Validação**: Condição individual testada contra cada registro (ex: tipo de dado correto, intervalo numérico, consistência entre colunas). Pode ser reutilizada entre diferentes features.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das colunas de data são convertidas para datetime sem perda de informação.
- **SC-002**: 100% dos valores monetários estão formatados como float com 2 casas decimais.
- **SC-003**: 0 registros com espaços extras ou capitalização inconsistente no conjunto de saída válido.
- **SC-004**: 100% dos registros com inconsistências numéricas (quantidade ≤ 0, preço ≤ 0, desconto fora de [0,1]) são detectados e rejeitados.
- **SC-005**: A validação de 7.000 registros é concluída em menos de 10 segundos.
- **SC-006**: O sistema registra em log o total de registros processados, válidos e rejeitados após cada execução.

## Assumptions

- O arquivo de entrada mantém o formato CSV com cabeçalho na primeira linha.
- A coluna de "valor de venda" não existe atualmente no CSV; a validação calcula `quantity * unit_price * (1 - discount_pct)` e rejeita registros com resultado negativo.
- Percentuais de desconto estão representados como decimal (0.05 = 5%), não como percentual (5.0).
- O pipeline existente de extração (`extract_csv`) já carrega o CSV bruto. Esta feature opera sobre o DataFrame resultante.
- Registros duplicados são definidos como linhas onde todas as colunas são idênticas. Duplicatas parciais (mesmo `order_id` com dados diferentes) serão tratadas como registros distintos.
- O limite de tolerância para arredondamento monetário é de R$ 0,01.
- Registros rejeitados são descartados em memória — não há persistência em disco do conjunto de rejeitados.
