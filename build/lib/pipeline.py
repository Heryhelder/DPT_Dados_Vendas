"""Orquestrador do pipeline ETL (Stage 5 — integração completa).

Executa todas as etapas do pipeline sequencialmente:
extract → validate → prepare → analyze → store.
"""

import logging
import time
from pathlib import Path

import config
from analyze import analyze_sales
from extract import extract_csv
from prepare import prepare_sales
from store import store_analytics
from validate import validate_sales

logger = logging.getLogger(__name__)


def run_pipeline(
    input_path: str | Path = config.DEFAULT_INPUT_PATH,
    output_dir: str | Path = config.DUCKDB_PATH,
) -> Path:
    """Executa o pipeline ETL completo de ponta a ponta.

    Carrega CSV, valida, prepara, calcula métricas e persiste em
    arquivos DuckDB individuais por view.

    Args:
        input_path: Caminho do arquivo CSV de entrada.
        output_dir: Diretório de saída para os arquivos .duckdb.

    Returns:
        Caminho do diretório de saída.

    Raises:
        FileNotFoundError: Se o arquivo de entrada não existir.
        ValueError: Se o DataFrame estiver vazio após validação.
    """
    _start = time.perf_counter()

    df_raw = extract_csv(str(input_path))
    df_clean = validate_sales(df_raw)
    df_prepared = prepare_sales(df_clean)
    df_analyzed = analyze_sales(df_prepared)
    store_analytics(df_analyzed, str(output_dir))

    elapsed = time.perf_counter() - _start
    revenue = float(df_analyzed["net_revenue"].sum())
    n_files = len(
        [f for f in Path(output_dir).iterdir() if f.suffix == ".duckdb"]
    )

    logger.info(
        "Pipeline concluído | arquivo=%s linhas=%d receita=%.2f "
        "arquivos=%d duração=%.2fs",
        str(input_path),
        len(df_analyzed),
        revenue,
        n_files,
        elapsed,
    )

    return Path(output_dir)
