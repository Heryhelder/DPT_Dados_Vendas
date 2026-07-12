"""Módulo de persistência analítica (Stage 5 do pipeline ETL).

Recebe DataFrame analítico de analyze_sales() e persiste em DuckDB
via SQL — tabela sales e views de consulta.
"""

import logging
import time
from pathlib import Path

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

_SQL_DIR = Path(__file__).parent / "sql"


def store_analytics(df: pd.DataFrame, db_path: str | Path) -> None:
    """Persiste DataFrame analítico em banco DuckDB via SQL.

    Cria tabela sales e views analíticas. Processo idempotente —
    reexecuções sobrescrevem dados existentes sem duplicação.

    Args:
        df: DataFrame com 34 colunas analíticas (saída de analyze_sales).
        db_path: Caminho do arquivo DuckDB de destino.

    Raises:
        ValueError: Se o DataFrame de entrada estiver vazio.
    """
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio")

    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    _start = time.perf_counter()

    con = duckdb.connect(str(path))
    try:
        con.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM df")

        views_sql = (_SQL_DIR / "create_views.sql").read_text(encoding="utf-8")
        con.execute(views_sql)

        row_count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        db_rev = con.execute(
            "SELECT SUM(net_revenue) FROM sales"
        ).fetchone()[0]
    finally:
        con.close()

    expected_count = len(df)
    expected_rev = float(df["net_revenue"].sum())

    if row_count != expected_count:
        raise ValueError(
            f"Contagem de registros divergente: "
            f"DuckDB={row_count}, DataFrame={expected_count}"
        )

    if abs(db_rev - expected_rev) > 0.01:
        raise ValueError(
            f"Soma de net_revenue divergente: "
            f"DuckDB={db_rev}, DataFrame={expected_rev}"
        )

    elapsed = time.perf_counter() - _start
    logger.info(
        "Persistência concluída | path=%s rows=%d revenue=%.2f duration=%.2fs",
        str(path),
        row_count,
        db_rev,
        elapsed,
    )
