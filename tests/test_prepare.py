import numpy as np
import pandas as pd
import pytest

from src.prepare import prepare_sales


@pytest.fixture
def valid_row() -> dict:
    return {
        "order_id": 1,
        "customer_id": "C001",
        "customer_name": "Thiago Alves",
        "customer_segment": "Consumer",
        "customer_type": "Existing",
        "first_purchase_date": "2023-01-15",
        "last_purchase_date": "2024-06-20",
        "product_id": "P001",
        "product_name": "Office Chair",
        "category": "Furniture",
        "sub_category": "Chairs",
        "brand": "ErgoComfort",
        "order_date": "2024-06-15",
        "quantity": 2,
        "unit_price": 150.0,
        "discount_pct": 0.1,
        "sales_channel": "Online",
        "payment_method": "Credit Card",
        "sales_rep": "Carlos Silva",
        "region": "Southeast",
        "operating_expenses": 5000.0,
        "cash_balance": 15000.0,
        "debt_balance": 3000.0,
        "monthly_burn": 2000.0,
        "churn_flag": 0,
    }


@pytest.fixture
def valid_df(valid_row) -> pd.DataFrame:
    return pd.DataFrame([valid_row])


class TestUS1TimeColumns:
    def test_create_month_column(self, valid_df):
        result = prepare_sales(valid_df)
        assert "month" in result.columns
        assert result["month"].iloc[0] == 6.0
        assert result["month"].dtype == np.float64

    def test_create_year_column(self, valid_df):
        result = prepare_sales(valid_df)
        assert "year" in result.columns
        assert result["year"].iloc[0] == 2024.0
        assert result["year"].dtype == np.float64

    def test_create_quarter_column(self, valid_df):
        result = prepare_sales(valid_df)
        assert "quarter" in result.columns
        assert result["quarter"].iloc[0] == 2.0
        assert result["quarter"].dtype == np.float64

    def test_order_date_preserved(self, valid_row):
        df = pd.DataFrame([{**valid_row, "order_date": pd.Timestamp("2024-06-15")}])
        result = prepare_sales(df)
        assert "order_date" in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result["order_date"])

    def test_null_date_sets_time_null(self, valid_row):
        df = pd.DataFrame([{**valid_row, "order_date": None}])
        result = prepare_sales(df)
        assert len(result) == 1
        assert pd.isna(result["month"].iloc[0])
        assert pd.isna(result["year"].iloc[0])
        assert pd.isna(result["quarter"].iloc[0])

    def test_returns_new_dataframe(self, valid_df):
        original_cols = list(valid_df.columns)
        result = prepare_sales(valid_df)
        assert result is not valid_df
        assert list(valid_df.columns) == original_cols


class TestUS2Dimensions:
    def test_standardize_region(self, valid_row):
        df = pd.DataFrame([{**valid_row, "region": "  south  "}])
        result = prepare_sales(df)
        assert result["region"].iloc[0] == "South"

    def test_standardize_sales_rep(self, valid_row):
        df = pd.DataFrame([{**valid_row, "sales_rep": "maria santos"}])
        result = prepare_sales(df)
        assert result["sales_rep"].iloc[0] == "Maria Santos"

    def test_standardize_category(self, valid_row):
        df = pd.DataFrame([{**valid_row, "category": "electronics"}])
        result = prepare_sales(df)
        assert result["category"].iloc[0] == "Electronics"

    def test_standardize_sales_channel(self, valid_row):
        df = pd.DataFrame([{**valid_row, "sales_channel": "retail"}])
        result = prepare_sales(df)
        assert result["sales_channel"].iloc[0] == "Retail"

    def test_standardize_customer_type(self, valid_row):
        df = pd.DataFrame([{**valid_row, "customer_type": "new"}])
        result = prepare_sales(df)
        assert result["customer_type"].iloc[0] == "New"

    def test_null_dimensions_preserved(self, valid_row):
        df = pd.DataFrame([{**valid_row, "region": None, "sales_rep": None}])
        result = prepare_sales(df)
        assert pd.isna(result["region"].iloc[0])
        assert pd.isna(result["sales_rep"].iloc[0])

    def test_input_not_modified(self, valid_row):
        df = pd.DataFrame([{**valid_row, "region": "  south  "}])
        original_region = df["region"].iloc[0]
        prepare_sales(df)
        assert df["region"].iloc[0] == original_region


class TestUS3AnalysisReady:
    def test_filter_by_dimension(self, valid_row):
        rows = [
            valid_row,
            {**valid_row, "order_id": 2, "region": "North"},
        ]
        df = pd.DataFrame(rows)
        result = prepare_sales(df)
        south = result[result["region"] == "Southeast"]
        assert len(south) == 1
        assert south["order_id"].iloc[0] == 1

    def test_groupby_time(self, valid_row):
        rows = [
            valid_row,
            {**valid_row, "order_id": 2, "order_date": "2024-03-10"},
        ]
        df = pd.DataFrame(rows)
        result = prepare_sales(df)
        q2 = result[result["quarter"] == 2.0]
        assert len(q2) == 1
        q1 = result[result["quarter"] == 1.0]
        assert len(q1) == 1

    def test_cross_dimension_analysis(self, valid_row):
        rows = [
            valid_row,
            {**valid_row, "order_id": 2, "region": "North", "sales_channel": "Retail"},
            {**valid_row, "order_id": 3, "region": "North", "sales_channel": "Online"},
        ]
        df = pd.DataFrame(rows)
        result = prepare_sales(df)
        north_online = result[
            (result["region"] == "North") & (result["sales_channel"] == "Online")
        ]
        assert len(north_online) == 1
        north_retail = result[
            (result["region"] == "North") & (result["sales_channel"] == "Retail")
        ]
        assert len(north_retail) == 1


class TestUS3Logging:
    def test_logging_stats(self, caplog, valid_row):
        caplog.set_level("INFO")
        df = pd.DataFrame([valid_row])
        prepare_sales(df)
        log_msg = caplog.records[-1].getMessage()
        assert "rows_processed=1" in log_msg
        assert "columns_added=3" in log_msg
        assert "dimensions_standardized=5" in log_msg
        assert "null_dates=0" in log_msg
