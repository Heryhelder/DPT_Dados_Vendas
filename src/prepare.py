import logging

import pandas as pd

logger = logging.getLogger(__name__)

DIMENSION_COLUMNS = [
    "region",
    "sales_rep",
    "category",
    "sales_channel",
    "customer_type",
]


def prepare_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara DataFrame validado para análise analítica.

    Cria colunas temporais (mês, ano, trimestre) a partir de order_date
    e padroniza dimensões de negócio para título (title case).

    Args:
        df: DataFrame validado com 25 colunas de validate_sales().

    Returns:
        pd.DataFrame: Novo DataFrame com 28 colunas (25 originais + 3 temporais).

    Raises:
        ValueError: Se o DataFrame de entrada estiver vazio.
    """
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio")

    result = df.copy()
    initial_cols = len(result.columns)

    result = _create_time_columns(result)
    result = _standardize_dimensions(result)

    null_dates = int(result["month"].isna().sum())
    dims_standardized = sum(
        int(result[col].notna().sum()) for col in DIMENSION_COLUMNS
    )

    logger.info(
        "Preparação concluída | rows_processed=%d columns_added=%d "
        "dimensions_standardized=%d null_dates=%d",
        len(result),
        len(result.columns) - initial_cols,
        dims_standardized,
        null_dates,
    )

    return result


def _create_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas month, year, quarter a partir de order_date."""
    dates = pd.to_datetime(df["order_date"], errors="coerce")
    df["month"] = dates.dt.month.astype("float64")
    df["year"] = dates.dt.year.astype("float64")
    df["quarter"] = dates.dt.quarter.astype("float64")
    return df


def _standardize_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica title case + strip nas colunas de dimensão."""
    for col in DIMENSION_COLUMNS:
        if col in df.columns:
            mask = df[col].isna()
            df[col] = df[col].astype(str).str.strip().str.title()
            df.loc[mask, col] = pd.NA
    return df
