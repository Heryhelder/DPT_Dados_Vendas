"""Módulo de métricas analíticas (Stage 4 do pipeline ETL).

Recebe DataFrame preparado por prepare_sales() e retorna novo DataFrame
com colunas derivadas de receita e métricas agregadas de negócio.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_COGS_RULES: dict[str, float] = {
    "Smartphones": 0.65,
    "Laptops": 0.70,
    "Audio": 0.55,
    "Peripherals": 0.50,
    "Tablets": 0.60,
}


def analyze_sales(
    df: pd.DataFrame,
    cogs_rules: dict[str, float] | None = None,
    tax_rate: float = 0.0,
) -> pd.DataFrame:
    """Computa métricas de receita e retorno financeiro por transação.

    Args:
        df: DataFrame preparado com 28 colunas de prepare_sales().
        cogs_rules: Dicionário sub_category -> cost_percentage (0-1).
            Se None, usa DEFAULT_COGS_RULES.
        tax_rate: Alíquota para cálculo do net_income (0-1). Default: 0.0.

    Returns:
        Novo DataFrame com 32+ colunas (28 input + 4 core + 2 optional).

    Raises:
        ValueError: Se o DataFrame de entrada estiver vazio.
    """
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio")

    result = df.copy()
    result = _compute_revenue_metrics(result, cogs_rules)
    result = _compute_optional_metrics(result, tax_rate)

    derived_cols = [c for c in result.columns if c not in df.columns]
    nan_counts = {col: int(result[col].isna().sum()) for col in derived_cols}
    nan_summary = " ".join(f"{k}={v}" for k, v in nan_counts.items())

    logger.info(
        "Análise concluída | rows_processed=%d columns_added=%d %s",
        len(result),
        len(derived_cols),
        nan_summary,
    )

    return result


def _compute_revenue_metrics(
    df: pd.DataFrame,
    cogs_rules: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Computa gross_revenue, net_revenue, cost_of_goods_sold, gross_profit.

    Formulas:
        gross_revenue = quantity * unit_price
        net_revenue = gross_revenue * (1 - discount_pct)
        cost_of_goods_sold = net_revenue * cost_percentage
        gross_profit = net_revenue - cost_of_goods_sold
    """
    rules = DEFAULT_COGS_RULES if cogs_rules is None else cogs_rules

    df["gross_revenue"] = df["quantity"].astype("float64") * df["unit_price"]
    df["net_revenue"] = df["gross_revenue"] * (1 - df["discount_pct"])

    cost_pct = df["sub_category"].map(rules)
    df["cost_of_goods_sold"] = df["net_revenue"] * cost_pct

    df["gross_profit"] = df["net_revenue"] - df["cost_of_goods_sold"]

    return df


def aggregate_metrics(
    df: pd.DataFrame,
    group_by: list[str] | None = None,
) -> pd.DataFrame:
    """Agrega métricas de receita por dimensões especificadas.

    Args:
        df: DataFrame com colunas net_revenue, quantity, discount_pct.
        group_by: Lista de colunas para agrupamento. Se None, retorna totais gerais.

    Returns:
        DataFrame com total_revenue, avg_ticket, total_quantity, avg_discount.
    """
    if df.empty:
        return pd.DataFrame()

    agg_dict = {
        "net_revenue": "sum",
        "order_id": "nunique",
        "quantity": "sum",
        "discount_pct": "mean",
    }

    available = {k: v for k, v in agg_dict.items() if k in df.columns}

    if group_by:
        grouped = df.groupby(group_by, as_index=False).agg(available)
    else:
        grouped = df.agg(available)
        grouped = grouped.to_frame().T

    rename_map = {"net_revenue": "total_revenue", "order_id": "total_orders"}
    grouped.rename(columns=rename_map, inplace=True)

    if "total_revenue" in grouped.columns and "total_orders" in grouped.columns:
        grouped["avg_ticket"] = (
            grouped["total_revenue"] / grouped["total_orders"]
        )

    rename_map2 = {"quantity": "total_quantity", "discount_pct": "avg_discount"}
    grouped.rename(columns=rename_map2, inplace=True)

    return grouped


def analyze_seasonality(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Analisa sazonalidade com totais mensais e trimestrais de receita.

    Args:
        df: DataFrame com year, month, quarter, net_revenue.

    Returns:
        Dict com DataFrames "monthly" e "quarterly".
    """
    monthly = (
        df.groupby(["year", "month"], as_index=False)
        .agg(total_revenue=("net_revenue", "sum"))
        .sort_values(["year", "month"])
        .reset_index(drop=True)
    )

    quarterly = (
        df.groupby(["year", "quarter"], as_index=False)
        .agg(total_revenue=("net_revenue", "sum"))
        .sort_values(["year", "quarter"])
        .reset_index(drop=True)
    )

    return {"monthly": monthly, "quarterly": quarterly}


def top_products(
    df: pd.DataFrame,
    n: int | None = None,
) -> pd.DataFrame:
    """Ranking de produtos por receita e quantidade.

    Args:
        df: DataFrame com product_name, net_revenue, quantity.
        n: Número de top produtos a retornar. Se None, retorna todos.

    Returns:
        DataFrame ordenado por receita decrescente.
    """
    agg = (
        df.groupby("product_name", as_index=False)
        .agg(total_revenue=("net_revenue", "sum"), total_quantity=("quantity", "sum"))
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    if n is not None:
        agg = agg.head(n)

    return agg


def top_categories(
    df: pd.DataFrame,
    n: int | None = None,
) -> pd.DataFrame:
    """Ranking de categorias por receita e quantidade.

    Args:
        df: DataFrame com category, net_revenue, quantity.
        n: Número de top categorias a retornar. Se None, retorna todas.

    Returns:
        DataFrame ordenado por receita decrescente.
    """
    agg = (
        df.groupby("category", as_index=False)
        .agg(total_revenue=("net_revenue", "sum"), total_quantity=("quantity", "sum"))
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    if n is not None:
        agg = agg.head(n)

    return agg


def analyze_recurrence(df: pd.DataFrame) -> dict[str, float]:
    """Analisa taxa de recorrência de clientes.

    Args:
        df: DataFrame com customer_id e order_id.

    Returns:
        Dict com total_customers, repeat_customers, recurrence_rate.
    """
    if df.empty or "customer_id" not in df.columns:
        return {
            "total_customers": 0,
            "repeat_customers": 0,
            "recurrence_rate": 0.0,
        }

    orders_per_customer = df.groupby("customer_id")["order_id"].nunique()
    total = int(len(orders_per_customer))
    repeat = int((orders_per_customer > 1).sum())
    rate = repeat / total if total > 0 else 0.0

    return {
        "total_customers": total,
        "repeat_customers": repeat,
        "recurrence_rate": rate,
    }


def _compute_optional_metrics(
    df: pd.DataFrame,
    tax_rate: float = 0.0,
) -> pd.DataFrame:
    """Computa ebitda e net_income quando operating_expenses está presente.

    Formulas:
        ebitda = gross_profit - operating_expenses
        net_income = ebitda * (1 - tax_rate)

    Se operating_expenses não existe no DataFrame, retorna sem alterações.
    """
    if "operating_expenses" not in df.columns:
        return df

    df["ebitda"] = df["gross_profit"] - df["operating_expenses"]
    df["net_income"] = df["ebitda"] * (1 - tax_rate)

    return df
