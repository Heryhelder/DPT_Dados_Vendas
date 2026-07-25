"""Módulo de persistência analítica (Stage 5 do pipeline ETL).

Recebe DataFrame analítico de analyze_sales() e persiste em DuckDB
via SQL — tabela sales e views de consulta.
"""

import logging
import re
import time
from pathlib import Path

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

_SQL_DIR = Path(__file__).parent / "sql"


def _extract_view_names(sql_content: str) -> list[str]:
    """Extrai nomes das views de definições SQL CREATE VIEW.

    Args:
        sql_content: Conteúdo SQL com definições de views.

    Returns:
        Lista de nomes de views encontrados.
    """
    return re.findall(
        r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS",
        sql_content,
        re.IGNORECASE,
    )


def _parse_view_statements(sql_content: str) -> list[tuple[str, str]]:
    """Divide conteúdo SQL em declarações individuais de view.

    Args:
        sql_content: Conteúdo SQL com múltiplas definições de views.

    Returns:
        Lista de tuplas (nome_da_view, sql_da_view).
    """
    statements = [s.strip() for s in re.split(r";\s*\n", sql_content) if s.strip()]
    results = []
    for stmt in statements:
        match = re.search(
            r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS",
            stmt,
            re.IGNORECASE,
        )
        if match:
            results.append((match.group(1), stmt))
    return results


def store_analytics(df: pd.DataFrame, db_path: str | Path) -> None:
    """Persiste DataFrame analítico em arquivos DuckDB individuais por view.

    Cria um arquivo .duckdb para cada view definida em create_views.sql.
    Cada arquivo contém a tabela sales e exatamente uma view.
    Processo idempotente — reexecuções sobrescrevem dados existentes.

    Args:
        df: DataFrame com 34 colunas analíticas (saída de analyze_sales).
        db_path: Diretório de saída onde os arquivos .duckdb serão criados.

    Raises:
        ValueError: Se o DataFrame de entrada estiver vazio.
        ValueError: Se contagem de registros ou soma de receita divergir.
    """
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio")

    output_dir = Path(db_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    _start = time.perf_counter()

    views_sql = (_SQL_DIR / "create_views.sql").read_text(encoding="utf-8")
    view_statements = _parse_view_statements(views_sql)

    expected_count = len(df)
    expected_rev = float(df["net_revenue"].sum())

    for view_name, view_sql in view_statements:
        file_path = output_dir / f"{view_name}.duckdb"
        con = duckdb.connect(str(file_path))
        try:
            con.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM df")
            con.execute(view_sql)

            row_count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
            db_rev = con.execute(
                "SELECT SUM(net_revenue) FROM sales"
            ).fetchone()[0]
        finally:
            con.close()

        if row_count != expected_count:
            raise ValueError(
                f"Contagem de registros divergente em {view_name}: "
                f"DuckDB={row_count}, DataFrame={expected_count}"
            )

        if abs(db_rev - expected_rev) > 0.01:
            raise ValueError(
                f"Soma de net_revenue divergente em {view_name}: "
                f"DuckDB={db_rev}, DataFrame={expected_rev}"
            )

    elapsed = time.perf_counter() - _start
    logger.info(
        "Persistência concluída | dir=%s files=%d rows=%d revenue=%.2f duration=%.2fs",
        str(output_dir),
        len(view_statements),
        expected_count,
        expected_rev,
        elapsed,
    )
