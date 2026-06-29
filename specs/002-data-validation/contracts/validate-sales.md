# Contract: Validar Dados de Vendas

## Function Signature

```python
def validate_sales(df: "pd.DataFrame") -> "pd.DataFrame":
    """Valida e padroniza um DataFrame de vendas eletrônicas.

    Aplica regras de validação sequenciais:
    1. Padronização de tipos (datas → datetime, monetários → float)
    2. Limpeza de texto (trim, capitalização)
    3. Validação de consistência numérica
    4. Remoção de duplicatas
    5. Filtragem de registros rejeitados

    Args:
        df: DataFrame bruto com as 25 colunas do CSV de vendas.

    Returns:
        pd.DataFrame: DataFrame contendo apenas registros válidos,
                      com tipos padronizados e textos limpos.

    Raises:
        ValueError: Se o DataFrame de entrada estiver vazio ou
                    se colunas obrigatórias estiverem ausentes.
    """
```

## Input Contract

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `df` | `pd.DataFrame` | Sim | DataFrame com colunas do CSV de vendas |

### Expected Input Columns

As 25 colunas abaixo DEVEM estar presentes no DataFrame de entrada:

| Column | Expected Raw Type |
|--------|-------------------|
| `order_id` | `int64` |
| `customer_id` | `object` |
| `customer_name` | `object` |
| `customer_segment` | `object` |
| `customer_type` | `object` |
| `first_purchase_date` | `object` |
| `last_purchase_date` | `object` |
| `product_id` | `object` |
| `product_name` | `object` |
| `category` | `object` |
| `sub_category` | `object` |
| `brand` | `object` |
| `order_date` | `object` |
| `quantity` | `int64` |
| `unit_price` | `float64` |
| `discount_pct` | `float64` |
| `sales_channel` | `object` |
| `payment_method` | `object` |
| `sales_rep` | `object` |
| `region` | `object` |
| `operating_expenses` | `float64` |
| `cash_balance` | `float64` |
| `debt_balance` | `float64` |
| `monthly_burn` | `float64` |
| `churn_flag` | `int64` |

## Output Contract

### Success

| Field | Type | Description |
|-------|------|-------------|
| return | `pd.DataFrame` | Apenas registros válidos, tipos padronizados |

### Error

| Condition | Exception | Message |
|-----------|-----------|---------|
| DataFrame vazio | `ValueError` | "DataFrame de entrada está vazio" |
| Coluna obrigatória ausente | `ValueError` | "Coluna obrigatória ausente: {column}" |
| Todas as linhas rejeitadas | N/A | Retorna DataFrame vazio (com as colunas intactas) |

## Internal Methods (Private)

```python
def _standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas de data para datetime. Rejeita registros com NaT."""

def _standardize_monetary(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que colunas monetárias sejam float64 com 2 casas decimais."""

def _clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços extras e padroniza capitalização."""

def _validate_quantity(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para quantity >= 1."""

def _validate_unit_price(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para unit_price > 0."""

def _validate_discount(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para discount_pct in [0, 1]."""

def _validate_sale_value(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para sale_value calculado >= 0."""

def _validate_dates_consistency(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para order_date >= first_purchase_date."""

def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas duplicadas exatas."""
```

## Dependencies

- `pandas` >= 2.2, < 3
- `logging` (stdlib)

## Version

1.0.0 — Initial contract for data-validation feature.
