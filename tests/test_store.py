import os

import duckdb
import pandas as pd
import pytest

from src.store import store_analytics

EXPECTED_VIEWS = [
    "v_monthly_revenue",
    "v_store_performance",
    "v_category_sales",
    "v_top_products",
    "v_sales_summary",
]


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """DataFrame mínimo com 34 colunas (saída de analyze_sales)."""
    return pd.DataFrame(
        [
            {
                "order_id": "ORD001",
                "customer_id": "C001",
                "product_id": "P001",
                "customer_name": "Thiago Alves",
                "product_name": "iPhone 15",
                "category": "Electronics",
                "sub_category": "Smartphones",
                "brand": "Apple",
                "customer_segment": "Consumer",
                "customer_type": "Existing",
                "sales_channel": "Online",
                "payment_method": "Credit Card",
                "sales_rep": "Carlos Silva",
                "region": "Southeast",
                "order_date": pd.Timestamp("2024-06-15"),
                "first_purchase_date": pd.Timestamp("2023-01-15"),
                "last_purchase_date": pd.Timestamp("2024-06-20"),
                "quantity": 10,
                "unit_price": 50.0,
                "discount_pct": 0.1,
                "operating_expenses": 100.0,
                "cash_balance": 15000.0,
                "debt_balance": 3000.0,
                "monthly_burn": 2000.0,
                "churn_flag": 0,
                "month": 6.0,
                "year": 2024.0,
                "quarter": 2.0,
                "gross_revenue": 500.0,
                "net_revenue": 450.0,
                "cost_of_goods_sold": 292.5,
                "gross_profit": 157.5,
                "ebitda": 57.5,
                "net_income": 57.5,
            },
            {
                "order_id": "ORD002",
                "customer_id": "C002",
                "product_id": "P002",
                "customer_name": "Ana Costa",
                "product_name": "Galaxy S24",
                "category": "Electronics",
                "sub_category": "Smartphones",
                "brand": "Samsung",
                "customer_segment": "Consumer",
                "customer_type": "New",
                "sales_channel": "Retail",
                "payment_method": "Debit Card",
                "sales_rep": "Maria Santos",
                "region": "North",
                "order_date": pd.Timestamp("2024-07-10"),
                "first_purchase_date": pd.Timestamp("2024-07-10"),
                "last_purchase_date": pd.Timestamp("2024-07-10"),
                "quantity": 5,
                "unit_price": 80.0,
                "discount_pct": 0.05,
                "operating_expenses": 50.0,
                "cash_balance": 8000.0,
                "debt_balance": 1000.0,
                "monthly_burn": 500.0,
                "churn_flag": 0,
                "month": 7.0,
                "year": 2024.0,
                "quarter": 3.0,
                "gross_revenue": 400.0,
                "net_revenue": 380.0,
                "cost_of_goods_sold": 247.0,
                "gross_profit": 133.0,
                "ebitda": 83.0,
                "net_income": 83.0,
            },
        ]
    )


@pytest.fixture
def output_dir(tmp_path) -> str:
    """Caminho temporário para diretório de saída."""
    return str(tmp_path / "output")


# ---------------------------------------------------------------------------
# US1: Generate Individual DuckDB Files Per View (P1)
# ---------------------------------------------------------------------------


class TestUS1CreatesFiveDuckdbFiles:
    """T004: store_analytics() cria exatamente 5 arquivos .duckdb."""

    def test_store_creates_five_duckdb_files(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        duckdb_files = [f for f in os.listdir(output_dir) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5


class TestUS1CreatesCorrectFilenames:
    """T005: Arquivos têm nomes corretos baseados nas views."""

    def test_store_creates_correct_filenames(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        duckdb_files = sorted(os.listdir(output_dir))
        expected = sorted(f"{v}.duckdb" for v in EXPECTED_VIEWS)
        assert duckdb_files == expected


class TestUS1EachFileContainsTableAndView:
    """T006: Cada arquivo contém tabela sales e exatamente uma view."""

    def test_each_file_contains_sales_table_and_one_view(
        self, sample_df, output_dir
    ):
        store_analytics(sample_df, output_dir)
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            tables = con.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'main' AND table_type = 'BASE TABLE'"
            ).fetchall()
            views = con.execute(
                "SELECT table_name FROM information_schema.views "
                "WHERE table_schema = 'main' "
                "AND table_name NOT LIKE 'duckdb_%' "
                "AND table_name NOT LIKE 'sqlite_%' "
                "AND table_name NOT LIKE 'pragma_%'"
            ).fetchall()
            con.close()
            table_names = [t[0] for t in tables]
            view_names = [v[0] for v in views]
            assert "sales" in table_names, f"{view_name}: missing sales table"
            assert len(view_names) == 1, (
                f"{view_name}: expected 1 view, got {len(view_names)}: {view_names}"
            )
            assert view_names[0] == view_name


class TestUS1EachFileIsQueryable:
    """T007: Cada arquivo pode ser consultado independentemente."""

    def test_each_file_is_independently_queryable(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            result = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
            con.close()
            assert result[0] > 0, f"{view_name}: returned 0 rows"


# ---------------------------------------------------------------------------
# US2: Backward-Compatible Storage Interface (P2)
# ---------------------------------------------------------------------------


class TestUS2FunctionSignatureUnchanged:
    """T010: Assinatura da função permanece compatível."""

    def test_store_function_signature_unchanged(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        duckdb_files = [f for f in os.listdir(output_dir) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5


class TestUS2DbPathAsDirectory:
    """T011: db_path tratado como diretório, não arquivo."""

    def test_db_path_as_directory_creates_files_inside(
        self, sample_df, output_dir
    ):
        store_analytics(sample_df, output_dir)
        assert os.path.isdir(output_dir)
        duckdb_files = [f for f in os.listdir(output_dir) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5
        assert not os.path.isfile(output_dir)


class TestUS2AutoCreatesDirectory:
    """T012: Diretório de saída é criado automaticamente."""

    def test_store_auto_creates_output_directory(self, sample_df, tmp_path):
        nested = str(tmp_path / "a" / "b" / "c")
        assert not os.path.exists(nested)
        store_analytics(sample_df, nested)
        assert os.path.isdir(nested)
        duckdb_files = [f for f in os.listdir(nested) if f.endswith(".duckdb")]
        assert len(duckdb_files) == 5


class TestUS2ViewsExistInFiles:
    """T014: Views são criadas nos arquivos individuais."""

    def test_store_creates_views(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            views = con.execute(
                "SELECT table_name FROM information_schema.views "
                "WHERE table_schema = 'main' "
                "AND table_name NOT LIKE 'duckdb_%'"
            ).fetchall()
            view_names = {v[0] for v in views}
            con.close()
            assert view_name in view_names, f"View '{view_name}' not found"


class TestUS2ViewMonthlyRevenue:
    """T015: v_monthly_revenue retorna dados corretos."""

    def test_view_monthly_revenue_returns_data(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        path = os.path.join(output_dir, "v_monthly_revenue.duckdb")
        con = duckdb.connect(path, read_only=True)
        result = con.execute("SELECT * FROM v_monthly_revenue").fetchdf()
        con.close()
        assert len(result) > 0
        assert "year" in result.columns
        assert "month" in result.columns
        assert "total_orders" in result.columns
        assert "total_revenue" in result.columns
        assert "avg_order_value" in result.columns


class TestUS2ViewSalesSummary:
    """T016: v_sales_summary retorna KPIs corretos."""

    def test_view_sales_summary_kpis(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        path = os.path.join(output_dir, "v_sales_summary.duckdb")
        con = duckdb.connect(path, read_only=True)
        result = con.execute("SELECT * FROM v_sales_summary").fetchdf()
        con.close()
        assert len(result) == 1
        assert result["total_orders"].iloc[0] == 2
        assert result["total_customers"].iloc[0] == 2
        assert result["total_units_sold"].iloc[0] == 15


class TestUS2ViewsReflectChanges:
    """T017: Views refletem mudanças na tabela sales."""

    def test_views_reflect_table_changes(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        path = os.path.join(output_dir, "v_sales_summary.duckdb")
        con = duckdb.connect(path, read_only=True)
        first_count = con.execute(
            "SELECT total_orders FROM v_sales_summary"
        ).fetchone()[0]
        con.close()

        updated_df = pd.concat(
            [sample_df, sample_df.iloc[[0]].assign(order_id="ORD003")],
            ignore_index=True,
        )
        store_analytics(updated_df, output_dir)

        con = duckdb.connect(path, read_only=True)
        second_count = con.execute(
            "SELECT total_orders FROM v_sales_summary"
        ).fetchone()[0]
        con.close()

        assert first_count == 2
        assert second_count == 3


# ---------------------------------------------------------------------------
# US3: Data Integrity Across All View Files (P3)
# ---------------------------------------------------------------------------


class TestUS3IdenticalRowCount:
    """T015: Todos os arquivos têm mesma contagem de registros."""

    def test_all_files_have_identical_row_count(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        counts = {}
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            counts[view_name] = con.execute(
                "SELECT COUNT(*) FROM sales"
            ).fetchone()[0]
            con.close()
        assert len(set(counts.values())) == 1, f"Inconsistent counts: {counts}"


class TestUS3IdenticalRevenueSum:
    """T016: Todos os arquivos têm mesma soma de receita."""

    def test_all_files_have_identical_revenue_sum(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        revenues = {}
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            revenues[view_name] = con.execute(
                "SELECT SUM(net_revenue) FROM sales"
            ).fetchone()[0]
            con.close()
        values = list(revenues.values())
        assert all(abs(v - values[0]) < 0.01 for v in values), (
            f"Inconsistent revenues: {revenues}"
        )


class TestUS3Idempotent:
    """T018: Duas execuções produzem resultados idênticos."""

    def test_store_is_idempotent(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        first_counts = {}
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            first_counts[view_name] = con.execute(
                "SELECT COUNT(*) FROM sales"
            ).fetchone()[0]
            con.close()

        store_analytics(sample_df, output_dir)
        second_counts = {}
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            second_counts[view_name] = con.execute(
                "SELECT COUNT(*) FROM sales"
            ).fetchone()[0]
            con.close()

        assert first_counts == second_counts


class TestUS3SalesTableHas34Columns:
    """Tabela sales tem 34 colunas em cada arquivo."""

    def test_sales_table_has_34_columns(self, sample_df, output_dir):
        store_analytics(sample_df, output_dir)
        for view_name in EXPECTED_VIEWS:
            path = os.path.join(output_dir, f"{view_name}.duckdb")
            con = duckdb.connect(path, read_only=True)
            columns = con.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'sales' ORDER BY ordinal_position"
            ).fetchall()
            con.close()
            assert len(columns) == 34, (
                f"{view_name}: expected 34 columns, got {len(columns)}"
            )


class TestUS3StoreHandlesEmptyDataFrame:
    """DataFrame vazio levanta ValueError."""

    def test_store_handles_empty_dataframe(self, output_dir):
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="vazio"):
            store_analytics(empty_df, output_dir)
