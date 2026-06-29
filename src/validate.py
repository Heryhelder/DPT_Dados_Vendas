import logging

import pandas as pd

logger = logging.getLogger(__name__)

DATE_COLUMNS = ["first_purchase_date", "last_purchase_date", "order_date"]
MONETARY_COLUMNS = [
    "unit_price",
    "operating_expenses",
    "cash_balance",
    "debt_balance",
    "monthly_burn",
]
TEXT_COLUMNS = [
    "customer_name",
    "product_name",
    "category",
    "sub_category",
    "brand",
    "customer_segment",
    "customer_type",
    "sales_channel",
    "payment_method",
    "sales_rep",
    "region",
]
NAME_COLUMNS = ["customer_name", "product_name", "brand", "sales_rep"]
CATEGORICAL_COLUMNS = [
    "customer_segment",
    "customer_type",
    "category",
    "sub_category",
    "sales_channel",
    "payment_method",
    "region",
]
_OTHER_REQUIRED = [
    "order_id", "customer_id", "product_id",
    "quantity", "discount_pct", "churn_flag",
]
REQUIRED_COLUMNS = set(DATE_COLUMNS + MONETARY_COLUMNS + TEXT_COLUMNS + _OTHER_REQUIRED)


def validate_sales(df: pd.DataFrame) -> pd.DataFrame:
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
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Coluna obrigatória ausente: {missing.pop()}")

    total = len(df)

    df = _standardize_dates(df)
    df = _standardize_monetary(df)
    df = _clean_text(df)

    mask_quantity = _validate_quantity(df)
    mask_unit_price = _validate_unit_price(df)
    mask_discount = _validate_discount(df)
    mask_sale_value = _validate_sale_value(df)
    mask_dates_consistency = _validate_dates_consistency(df)

    combined_mask = (
        mask_quantity
        & mask_unit_price
        & mask_discount
        & mask_sale_value
        & mask_dates_consistency
    )

    df = df[combined_mask]
    df = _remove_duplicates(df)

    valid = len(df)
    rejected = total - valid
    logger.info(
        "Validação concluída | total=%d válidos=%d rejeitados=%d",
        total,
        valid,
        rejected,
    )

    return df


def _standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas de data para datetime. Rejeita registros com NaT."""
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    df = df.dropna(subset=DATE_COLUMNS)
    return df


def _standardize_monetary(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que colunas monetárias sejam float64 com 2 casas decimais."""
    for col in MONETARY_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
    return df


def _clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços extras e padroniza capitalização."""
    for col in TEXT_COLUMNS:
        df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    for col in NAME_COLUMNS:
        df[col] = df[col].str.title()
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].str.capitalize()
    return df


def _validate_quantity(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para quantity >= 1."""
    return df["quantity"] >= 1


def _validate_unit_price(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para unit_price > 0."""
    return df["unit_price"] > 0


def _validate_discount(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para discount_pct in [0, 1]."""
    return (df["discount_pct"] >= 0.0) & (df["discount_pct"] <= 1.0)


def _validate_sale_value(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para sale_value calculado >= 0."""
    sale_value = df["quantity"] * df["unit_price"] * (1.0 - df["discount_pct"])
    return sale_value >= 0


def _validate_dates_consistency(df: pd.DataFrame) -> pd.Series:
    """Retorna máscara booleana: True para order_date >= first_purchase_date."""
    return df["order_date"] >= df["first_purchase_date"]


def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas duplicadas exatas."""
    return df.drop_duplicates()
