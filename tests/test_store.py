import os

import duckdb
import pandas as pd
import pytest

from src.store import store_analytics


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
def db_path(tmp_path) -> str:
    """Caminho temporário para arquivo DuckDB."""
    return str(tmp_path / "test.duckdb")


class TestUS1StoreCreatesFile:
    def test_store_creates_duckdb_file(self, sample_df, db_path):
        """T006: store_analytics() cria arquivo .duckdb no caminho informado."""
        assert not os.path.exists(db_path)
        store_analytics(sample_df, db_path)
        assert os.path.exists(db_path)
        assert db_path.endswith(".duckdb")


class TestUS1StoreCreatesSalesTable:
    def test_store_creates_sales_table(self, sample_df, db_path):
        """T007: Tabela 'sales' existe com 34 colunas."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        columns = con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'sales' ORDER BY ordinal_position"
        ).fetchall()
        con.close()
        assert len(columns) == 34


class TestUS1StorePreservesRecordCount:
    def test_store_preserves_record_count(self, sample_df, db_path):
        """T008: Contagem de registros no DuckDB confere com DataFrame."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        con.close()
        assert count == len(sample_df)


class TestUS1StorePreservesColumnTypes:
    def test_store_preserves_column_types(self, sample_df, db_path):
        """T009: Tipos de coluna do DuckDB conferem com data-model.md."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        col_types = dict(
            con.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'sales'"
            ).fetchall()
        )
        con.close()

        assert col_types["order_id"] == "VARCHAR"
        assert "TIMESTAMP" in col_types["order_date"]
        assert "INT" in col_types["quantity"]
        assert col_types["unit_price"] == "DOUBLE"
        assert col_types["net_revenue"] == "DOUBLE"
        assert "INT" in col_types["churn_flag"]


class TestUS1StoreAutoCreatesDirectory:
    def test_store_auto_creates_directory(self, sample_df, tmp_path):
        """T010: Diretório aninhado inexistente é criado automaticamente."""
        nested_path = str(tmp_path / "subdir" / "nested" / "test.duckdb")
        assert not os.path.exists(tmp_path / "subdir")
        store_analytics(sample_df, nested_path)
        assert os.path.exists(nested_path)


EXPECTED_VIEWS = [
    "v_monthly_revenue",
    "v_store_performance",
    "v_category_sales",
    "v_top_products",
    "v_sales_summary",
]


class TestUS2StoreCreatesViews:
    def test_store_creates_views(self, sample_df, db_path):
        """T014: Todas as 5 views são criadas no DuckDB."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        views = con.execute(
            "SELECT table_name FROM information_schema.views "
            "WHERE table_schema = 'main'"
        ).fetchall()
        view_names = {v[0] for v in views}
        con.close()
        for name in EXPECTED_VIEWS:
            assert name in view_names, f"View '{name}' not found"


class TestUS2ViewMonthlyRevenue:
    def test_view_monthly_revenue_returns_data(self, sample_df, db_path):
        """T015: v_monthly_revenue retorna linhas com colunas esperadas."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        result = con.execute("SELECT * FROM v_monthly_revenue").fetchdf()
        con.close()
        assert len(result) > 0
        assert "year" in result.columns
        assert "month" in result.columns
        assert "total_orders" in result.columns
        assert "total_revenue" in result.columns
        assert "avg_order_value" in result.columns


class TestUS2ViewSalesSummary:
    def test_view_sales_summary_kpis(self, sample_df, db_path):
        """T016: v_sales_summary retorna KPIs corretos."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        result = con.execute("SELECT * FROM v_sales_summary").fetchdf()
        con.close()
        assert len(result) == 1
        assert "total_orders" in result.columns
        assert "total_customers" in result.columns
        assert "total_revenue" in result.columns
        assert "total_profit" in result.columns
        assert "avg_order_value" in result.columns
        assert "total_units_sold" in result.columns
        assert result["total_orders"].iloc[0] == 2
        assert result["total_customers"].iloc[0] == 2
        assert result["total_units_sold"].iloc[0] == 15


class TestUS2ViewsReflectChanges:
    def test_views_reflect_table_changes(self, sample_df, db_path):
        """T017: Views refletem mudanças na tabela sales automaticamente."""
        store_analytics(sample_df, db_path)

        con = duckdb.connect(db_path, read_only=True)
        first_count = con.execute(
            "SELECT total_orders FROM v_sales_summary"
        ).fetchone()[0]
        con.close()

        updated_df = pd.concat(
            [sample_df, sample_df.iloc[[0]].assign(order_id="ORD003")],
            ignore_index=True,
        )
        store_analytics(updated_df, db_path)

        con = duckdb.connect(db_path, read_only=True)
        second_count = con.execute(
            "SELECT total_orders FROM v_sales_summary"
        ).fetchone()[0]
        con.close()

        assert first_count == 2
        assert second_count == 3


class TestUS3StoreIsIdempotent:
    def test_store_is_idempotent(self, sample_df, db_path):
        """T020: Duas execuções produzem resultados idênticos."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        r1_count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        r1_rev = con.execute(
            "SELECT SUM(net_revenue) FROM sales"
        ).fetchone()[0]
        con.close()

        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        r2_count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        r2_rev = con.execute(
            "SELECT SUM(net_revenue) FROM sales"
        ).fetchone()[0]
        con.close()

        assert r1_count == r2_count
        assert abs(r1_rev - r2_rev) < 0.01


class TestUS3StoreValidatesRecordCount:
    def test_store_validates_record_count(self, sample_df, db_path):
        """T021: Validação de contagem confere com DataFrame de entrada."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        con.close()
        assert count == len(sample_df)


class TestUS3StoreValidatesRevenueSum:
    def test_store_validates_revenue_sum(self, sample_df, db_path):
        """T022: Soma de net_revenue no DuckDB confere com DataFrame."""
        store_analytics(sample_df, db_path)
        con = duckdb.connect(db_path, read_only=True)
        db_rev = con.execute(
            "SELECT SUM(net_revenue) FROM sales"
        ).fetchone()[0]
        con.close()
        expected_rev = sample_df["net_revenue"].sum()
        assert abs(db_rev - expected_rev) < 0.01


class TestUS3StoreHandlesEmptyDataFrame:
    def test_store_handles_empty_dataframe(self, db_path):
        """T023: DataFrame vazio levanta ValueError."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="vazio"):
            store_analytics(empty_df, db_path)
