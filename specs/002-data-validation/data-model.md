# Data Model: Validação de Dados de Vendas

## Entities

### Registro de Venda (SaleRecord)

Linha individual do CSV representando um pedido de venda. É a unidade básica de validação.

| Attribute | Type | Source Column | Validation |
|-----------|------|---------------|------------|
| order_id | `int64` | `order_id` | — |
| customer_id | `object` | `customer_id` | Trim, uppercase |
| customer_name | `object` | `customer_name` | Trim, title case |
| customer_segment | `object` | `customer_segment` | Trim, capitalized |
| customer_type | `object` | `customer_type` | Trim, capitalized |
| first_purchase_date | `datetime64[ns]` | `first_purchase_date` | Must be parseable |
| last_purchase_date | `datetime64[ns]` | `last_purchase_date` | Must be parseable |
| product_id | `object` | `product_id` | Trim |
| product_name | `object` | `product_name` | Trim, title case |
| category | `object` | `category` | Trim, capitalized |
| sub_category | `object` | `sub_category` | Trim, capitalized |
| brand | `object` | `brand` | Trim, title case |
| order_date | `datetime64[ns]` | `order_date` | Must be parseable; ≥ first_purchase_date |
| quantity | `int64` | `quantity` | ≥ 1 |
| unit_price | `float64` | `unit_price` | > 0 |
| discount_pct | `float64` | `discount_pct` | [0.0, 1.0] |
| sales_channel | `object` | `sales_channel` | Trim, capitalized |
| payment_method | `object` | `payment_method` | Trim, capitalized |
| sales_rep | `object` | `sales_rep` | Trim, title case |
| region | `object` | `region` | Trim, capitalized |
| operating_expenses | `float64` | `operating_expenses` | — |
| cash_balance | `float64` | `cash_balance` | — |
| debt_balance | `float64` | `debt_balance` | — |
| monthly_burn | `float64` | `monthly_burn` | — |
| churn_flag | `int64` | `churn_flag` | — |

**Calculated attributes** (used during validation):
- `sale_value = quantity * unit_price * (1 - discount_pct)` — validado como ≥ 0

### Conjunto Válido (ValidDataset)

DataFrame contendo apenas registros que passaram em todas as regras de validação.

- **Type**: `pd.DataFrame`
- **Rows**: ≤ total de registros de entrada
- **Columns**: Mesmas 25 colunas do CSV de entrada, com tipos padronizados

## Validation Rules

### Regras por Requisito

| FR | Rule | Rejection Condition |
|----|------|---------------------|
| FR-001 | Date parsing | `pd.to_datetime()` retorna NaT para `first_purchase_date`, `last_purchase_date` ou `order_date` |
| FR-002 | Monetary precision | Colunas monetárias com dtype não-float |
| FR-003 | Whitespace trim | N/A (aplicado a todos, sem rejeição) |
| FR-004 | Case normalization | N/A (aplicado a todos, sem rejeição) |
| FR-005 | Quantity ≥ 1 | `quantity < 1` |
| FR-006 | Unit price > 0 | `unit_price <= 0` |
| FR-007 | Discount in [0, 1] | `discount_pct < 0` ou `discount_pct > 1` |
| FR-008 | Sale value ≥ 0 | `quantity * unit_price * (1 - discount_pct) < 0` |
| FR-009 | Order date ≥ first purchase | `order_date < first_purchase_date` |
| FR-010 | Duplicate removal | Linha duplicata exata (todas as colunas) |
| FR-011 | Return valid only | N/A (mecanismo de saída) |
| FR-012 | Log counts | N/A (observabilidade) |

### Regras por User Story

**US1 (P1)** — Padronização:
- Datas convertidas para datetime
- Valores monetários como float64 com 2 casas decimais
- Textos sem espaços extras e com capitalização padronizada

**US2 (P1)** — Consistência numérica:
- quantity ≥ 1
- unit_price > 0
- discount_pct em [0, 1]
- sale_value calculado ≥ 0
- order_date ≥ first_purchase_date

**US3 (P2)** — Filtragem:
- Retorna apenas registros que passaram todas as regras
- Descarta registros rejeitados (sem persistência)

## State Transitions

```
DataFrame bruto (do extract_csv) → [validate_sales()] → DataFrame validado
                                                          ↻ Log: total, válidos, rejeitados
```

A validação é operação puramente funcional: mesmo DataFrame de entrada sempre produz o mesmo DataFrame de saída (determinístico, Princípio IV).
