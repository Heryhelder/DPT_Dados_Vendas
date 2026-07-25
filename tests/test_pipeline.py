import logging
import os
from pathlib import Path

import duckdb

from src.config import DEFAULT_INPUT_PATH
from src.pipeline import run_pipeline

EXPECTED_VIEWS = [
    "v_monthly_revenue",
    "v_store_performance",
    "v_category_sales",
    "v_top_products",
    "v_sales_summary",
]


# ---------------------------------------------------------------------------
# US1: Run Full Pipeline End-to-End (P1)
# ---------------------------------------------------------------------------


class TestUS1CreatesFiveDuckdbFiles:
    """T002: run_pipeline() cria 5 arquivos .duckdb."""

    def test_run_pipeline_creates_five_duckdb_files(self, tmp_path):
        output_dir = str(tmp_path / "output")
        run_pipeline(output_dir=output_dir)
        duckdb_files = [f for f in os.listdir(output_dir) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5


class TestUS1ReturnsOutputPath:
    """T003: run_pipeline() retorna caminho do diretório de saída."""

    def test_run_pipeline_returns_output_path(self, tmp_path):
        output_dir = str(tmp_path / "output")
        result = run_pipeline(output_dir=output_dir)
        assert isinstance(result, Path)
        assert result.exists()


class TestUS1FilesAreQueryable:
    """T004: Cada arquivo gerado pode ser consultado."""

    def test_run_pipeline_files_are_queryable(self, tmp_path):
        output_dir = str(tmp_path / "output")
        run_pipeline(output_dir=output_dir)
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            result = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
            con.close()
            assert result[0] > 0, f"{view_name}: returned 0 rows"


class TestUS1SalesTableHasData:
    """T005: Tabela sales contém dados."""

    def test_run_pipeline_sales_table_has_data(self, tmp_path):
        output_dir = str(tmp_path / "output")
        run_pipeline(output_dir=output_dir)
        path = os.path.join(output_dir, "v_monthly_revenue.duckdb")
        con = duckdb.connect(path, read_only=True)
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        con.close()
        assert count > 0


# ---------------------------------------------------------------------------
# US2: Configurable Input and Output Paths (P2)
# ---------------------------------------------------------------------------


class TestUS2CustomOutputDir:
    """T008: Saída vai para diretório personalizado."""

    def test_run_pipeline_custom_output_dir(self, tmp_path):
        custom_dir = str(tmp_path / "custom_output")
        run_pipeline(output_dir=custom_dir)
        duckdb_files = [f for f in os.listdir(custom_dir) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5


class TestUS2CustomInputPath:
    """T009: Aceita caminho de entrada personalizado."""

    def test_run_pipeline_custom_input_path(self, tmp_path):
        output_dir = str(tmp_path / "output")
        result = run_pipeline(
            input_path=DEFAULT_INPUT_PATH,
            output_dir=output_dir,
        )
        assert result.exists()


class TestUS2DefaultParams:
    """T010: Parâmetros padrão funcionam."""

    def test_run_pipeline_default_params(self, tmp_path):
        output_dir = str(tmp_path / "output")
        result = run_pipeline(output_dir=output_dir)
        assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# US3: Pipeline Reports Processing Summary (P3)
# ---------------------------------------------------------------------------


class TestUS3LogsSummary:
    """T013: Pipeline loga resumo do processamento."""

    def test_run_pipeline_logs_summary(self, tmp_path, caplog):
        output_dir = str(tmp_path / "output")
        with caplog.at_level(logging.INFO, logger="src.pipeline"):
            run_pipeline(output_dir=output_dir)
        assert "linhas" in caplog.text or "rows" in caplog.text.lower()


class TestUS3LogsDuration:
    """T014: Pipeline loga duração do processamento."""

    def test_run_pipeline_logs_duration(self, tmp_path, caplog):
        output_dir = str(tmp_path / "output")
        with caplog.at_level(logging.INFO, logger="src.pipeline"):
            run_pipeline(output_dir=output_dir)
        assert "duração" in caplog.text or "duration" in caplog.text.lower()
