# Data Model: DuckDB Analytical Storage

**Feature**: 005-duckdb-storage
**Date**: 2026-07-12

## Entity: `sales` (Tabela Principal)

Tabela única que armazena todos os dados analíticos do pipeline ETL. Equivalente à saída de `analyze_sales()` (Stage 4) persistida em DuckDB.

### Colunas

| # | Column | DuckDB Type | Source | Description |
|---|--------|-------------|--------|-------------|
| 1 | `order_id` | VARCHAR | CSV | Identificador do pedido |
| 2 | `customer_id` | VARCHAR | CSV | Identificador do cliente |
| 3 | `product_id` | VARCHAR | CSV | Identificador do produto |
| 4 | `customer_name` | VARCHAR | CSV/validate | Nome do cliente (title case) |
| 5 | `product_name` | VARCHAR | CSV/validate | Nome do produto (title case) |
| 6 | `category` | VARCHAR | CSV/validate/prepare | Categoria do produto (capitalized) |
| 7 | `sub_category` | VARCHAR | CSV/validate | Sub-categoria do produto |
| 8 | `brand` | VARCHAR | CSV/validate | Marca do produto (title case) |
| 9 | `customer_segment` | VARCHAR | CSV/validate | Segmento do cliente |
| 10 | `customer_type` | VARCHAR | CSV/validate/prepare | Tipo de cliente |
| 11 | `sales_channel` | VARCHAR | CSV/validate/prepare | Canal de venda |
| 12 | `payment_method` | VARCHAR | CSV/validate | Método de pagamento |
| 13 | `sales_rep` | VARCHAR | CSV/validate/prepare | Representante de vendas (title case) |
| 14 | `region` | VARCHAR | CSV/validate/prepare | Região |
| 15 | `order_date` | TIMESTAMP | CSV/validate | Data do pedido |
| 16 | `first_purchase_date` | TIMESTAMP | CSV/validate | Data da primeira compra |
| 17 | `last_purchase_date` | TIMESTAMP | CSV/validate | Data da última compra |
| 18 | `quantity` | INTEGER | CSV/validate | Quantidade vendida |
| 19 | `unit_price` | DOUBLE | CSV/validate | Preço unitário |
| 20 | `discount_pct` | DOUBLE | CSV/validate | Percentual de desconto (0-1) |
| 21 | `operating_expenses` | DOUBLE | CSV/validate | Despesas operacionais |
| 22 | `cash_balance` | DOUBLE | CSV/validate | Saldo de caixa |
| 23 | `debt_balance` | DOUBLE | CSV/validate | Saldo de dívida |
| 24 | `monthly_burn` | DOUBLE | CSV/validate | Burn rate mensal |
| 25 | `churn_flag` | INTEGER | CSV | Flag de churn (0/1) |
| 26 | `month` | DOUBLE | prepare | Mês da order_date (1-12) |
| 27 | `year` | DOUBLE | prepare | Ano da order_date |
| 28 | `quarter` | DOUBLE | prepare | Trimestre da order_date (1-4) |
| 29 | `gross_revenue` | DOUBLE | analyze | Receita bruta (qty * unit_price) |
| 30 | `net_revenue` | DOUBLE | analyze | Receita líquida (gross * (1-discount)) |
| 31 | `cost_of_goods_sold` | DOUBLE | analyze | Custo dos produtos vendidos |
| 32 | `gross_profit` | DOUBLE | analyze | Lucro bruto (net_revenue - COGS) |
| 33 | `ebitda` | DOUBLE | analyze | EBITDA (gross_profit - opex) |
| 34 | `net_income` | DOUBLE | analyze | Lucro líquido (ebitda * (1-tax)) |

### Validation Rules

- `quantity` >= 1
- `unit_price` > 0
- `discount_pct` BETWEEN 0 AND 1
- `order_date` >= `first_purchase_date`
- Sem registros duplicados (order_id + product_id)
- Sem valores nulos em colunas obrigatórias

## Views Analíticas

### `v_monthly_revenue`

Receita total por mês/ano. Para análise de tendência temporal.

```sql
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT
    year,
    month,
    COUNT(*) AS total_orders,
    SUM(net_revenue) AS total_revenue,
    AVG(net_revenue) AS avg_order_value
FROM sales
GROUP BY year, month
ORDER BY year, month;
```

### `v_store_performance`

Métricas de desempenho por representante de vendas.

```sql
CREATE OR REPLACE VIEW v_store_performance AS
SELECT
    sales_rep,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(net_revenue) AS total_revenue,
    AVG(net_revenue) AS avg_ticket
FROM sales
GROUP BY sales_rep, region
ORDER BY total_revenue DESC;
```

### `v_category_sales`

Vendas por categoria e sub-categoria.

```sql
CREATE OR REPLACE VIEW v_category_sales AS
SELECT
    category,
    sub_category,
    COUNT(*) AS total_items,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit,
    AVG(discount_pct) AS avg_discount
FROM sales
GROUP BY category, sub_category
ORDER BY total_revenue DESC;
```

### `v_top_products`

Ranking de produtos por receita.

```sql
CREATE OR REPLACE VIEW v_top_products AS
SELECT
    product_name,
    category,
    brand,
    SUM(quantity) AS total_quantity,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit
FROM sales
GROUP BY product_name, category, brand
ORDER BY total_revenue DESC;
```

### `v_sales_summary`

Resumo geral de KPIs.

```sql
CREATE OR REPLACE VIEW v_sales_summary AS
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit,
    AVG(net_revenue) AS avg_order_value,
    SUM(quantity) AS total_units_sold
FROM sales;
```

## Relationships

- `sales` é a tabela única de fatos — não há tabelas de dimensões separadas (decisão de simplicidade, Princípio I)
- Views referenciam apenas a tabela `sales` (sem JOINs entre tabelas)
- Dados de origem nunca são alterados (CSV permanece intocado)

## State Transitions

```
[DataFrame em memória] → CREATE OR REPLACE TABLE sales → [Tabela populada no DuckDB]
                                                                  ↓
                                                     CREATE OR REPLACE VIEW v_* → [Views atualizadas]
```

Reexecução substitui completamente (`CREATE OR REPLACE`), garantindo idempotência.
