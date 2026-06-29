import pandas as pd
import pytest

from src.validate import validate_sales

REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "customer_name",
    "customer_segment",
    "customer_type",
    "first_purchase_date",
    "last_purchase_date",
    "product_id",
    "product_name",
    "category",
    "sub_category",
    "brand",
    "order_date",
    "quantity",
    "unit_price",
    "discount_pct",
    "sales_channel",
    "payment_method",
    "sales_rep",
    "region",
    "operating_expenses",
    "cash_balance",
    "debt_balance",
    "monthly_burn",
    "churn_flag",
]


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
        "order_date": "2024-06-20",
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


@pytest.fixture
def sample_df(valid_row) -> pd.DataFrame:
    rows = [
        valid_row,
        {**valid_row, "order_id": 2, "quantity": 0},
        {**valid_row, "order_id": 3, "unit_price": -10.0},
        {**valid_row, "order_id": 4, "discount_pct": 1.5},
        {
            **valid_row,
            "order_id": 5,
            "order_date": "2022-01-01",
            "first_purchase_date": "2023-01-15",
        },
        {
            **valid_row,
            "order_id": 6,
            "quantity": 3,
            "unit_price": 50.0,
            "discount_pct": 0.2,
        },
        {**valid_row, "order_id": 7, "first_purchase_date": "invalid-date"},
        {**valid_row, "order_id": 8, "customer_name": "  maria  santos  "},
        {**valid_row, "order_id": 9, "unit_price": "100.50"},
        {**valid_row, "order_id": 10, "discount_pct": -0.1},
    ]
    return pd.DataFrame(rows)


def test_empty_dataframe():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="DataFrame de entrada está vazio"):
        validate_sales(df)


def test_missing_required_column(valid_row):
    df = pd.DataFrame([valid_row]).drop(columns=["order_id"])
    with pytest.raises(ValueError, match="Coluna obrigatória ausente"):
        validate_sales(df)


class TestUS1DateStandardization:
    def test_date_columns_are_datetime(self, valid_df):
        result = validate_sales(valid_df)
        date_cols = ["first_purchase_date", "last_purchase_date", "order_date"]
        for col in date_cols:
            assert pd.api.types.is_datetime64_any_dtype(result[col]), (
                f"{col} não é datetime"
            )

    def test_invalid_date_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "first_purchase_date": "not-a-date"}])
        result = validate_sales(df)
        assert len(result) == 0

    def test_mixed_date_formats(self, valid_row):
        df = pd.DataFrame([
            valid_row,
            {**valid_row, "order_id": 2, "first_purchase_date": "2023/01/15"},
        ])
        result = validate_sales(df)
        assert len(result) == 2


class TestUS1MonetaryStandardization:
    def test_monetary_columns_are_float64(self, valid_df):
        result = validate_sales(valid_df)
        monetary = [
            "unit_price", "operating_expenses",
            "cash_balance", "debt_balance", "monthly_burn",
        ]
        for col in monetary:
            assert pd.api.types.is_float_dtype(result[col]), f"{col} não é float"

    def test_monetary_values_rounded_to_two_decimals(self, valid_row):
        df = pd.DataFrame([{**valid_row, "unit_price": 150.456}])
        result = validate_sales(df)
        assert result["unit_price"].iloc[0] == 150.46

    def test_string_monetary_is_converted(self, valid_row):
        df = pd.DataFrame([{**valid_row, "unit_price": "99.99"}])
        result = validate_sales(df)
        assert result["unit_price"].iloc[0] == 99.99


class TestUS1TextCleaning:
    def test_whitespace_trimmed(self, valid_row):
        df = pd.DataFrame([{**valid_row, "customer_name": "  João  Silva  "}])
        result = validate_sales(df)
        assert result["customer_name"].iloc[0] == "João Silva"

    def test_name_title_case(self, valid_row):
        df = pd.DataFrame([{**valid_row, "customer_name": "joão silva"}])
        result = validate_sales(df)
        assert result["customer_name"].iloc[0] == "João Silva"

    def test_categorical_capitalized(self, valid_row):
        df = pd.DataFrame([{**valid_row, "customer_segment": "consumer"}])
        result = validate_sales(df)
        assert result["customer_segment"].iloc[0] == "Consumer"


class TestUS2QuantityValidation:
    def test_quantity_one_is_valid(self, valid_row):
        df = pd.DataFrame([{**valid_row, "quantity": 1}])
        result = validate_sales(df)
        assert len(result) == 1

    def test_quantity_zero_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "quantity": 0}])
        result = validate_sales(df)
        assert len(result) == 0

    def test_quantity_negative_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "quantity": -5}])
        result = validate_sales(df)
        assert len(result) == 0


class TestUS2UnitPriceValidation:
    def test_unit_price_positive_is_valid(self, valid_row):
        df = pd.DataFrame([{**valid_row, "unit_price": 0.01}])
        result = validate_sales(df)
        assert len(result) == 1

    def test_unit_price_zero_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "unit_price": 0.0}])
        result = validate_sales(df)
        assert len(result) == 0

    def test_unit_price_negative_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "unit_price": -1.0}])
        result = validate_sales(df)
        assert len(result) == 0


class TestUS2DiscountValidation:
    def test_discount_zero_is_valid(self, valid_row):
        df = pd.DataFrame([{**valid_row, "discount_pct": 0.0}])
        result = validate_sales(df)
        assert len(result) == 1

    def test_discount_one_is_valid(self, valid_row):
        df = pd.DataFrame([{**valid_row, "discount_pct": 1.0}])
        result = validate_sales(df)
        assert len(result) == 1

    def test_discount_above_one_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "discount_pct": 1.01}])
        result = validate_sales(df)
        assert len(result) == 0

    def test_discount_negative_is_rejected(self, valid_row):
        df = pd.DataFrame([{**valid_row, "discount_pct": -0.01}])
        result = validate_sales(df)
        assert len(result) == 0


class TestUS2SaleValueValidation:
    def test_sale_value_zero_is_valid(self, valid_row):
        df = pd.DataFrame([
            {**valid_row, "quantity": 5, "unit_price": 100.0, "discount_pct": 1.0},
        ])
        result = validate_sales(df)
        assert len(result) == 1

    def test_sale_value_positive_is_valid(self, valid_row):
        df = pd.DataFrame([valid_row])
        result = validate_sales(df)
        assert len(result) == 1

    def test_sale_value_negative_is_rejected(self, valid_row):
        df = pd.DataFrame([
            {**valid_row, "quantity": 1, "unit_price": 100.0, "discount_pct": 2.0},
        ])
        result = validate_sales(df)
        assert len(result) == 0


class TestUS2DateConsistency:
    def test_order_date_equals_first_purchase_date(self, valid_row):
        row = {
            **valid_row,
            "order_date": "2023-01-15",
            "first_purchase_date": "2023-01-15",
        }
        df = pd.DataFrame([row])
        result = validate_sales(df)
        assert len(result) == 1

    def test_order_date_after_first_purchase_date(self, valid_row):
        df = pd.DataFrame([valid_row])
        result = validate_sales(df)
        assert len(result) == 1

    def test_order_date_before_first_purchase_is_rejected(self, valid_row):
        row = {
            **valid_row,
            "order_date": "2022-01-01",
            "first_purchase_date": "2023-01-15",
        }
        df = pd.DataFrame([row])
        result = validate_sales(df)
        assert len(result) == 0


class TestUS3DuplicateRemoval:
    def test_exact_duplicate_removed(self, valid_row):
        df = pd.DataFrame([valid_row, valid_row])
        result = validate_sales(df)
        assert len(result) == 1

    def test_no_duplicates_preserves_all(self, valid_row):
        df = pd.DataFrame([valid_row, {**valid_row, "order_id": 2}])
        result = validate_sales(df)
        assert len(result) == 2


class TestUS3EndToEnd:
    def test_all_valid_records_returned(self, valid_df):
        result = validate_sales(valid_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_mixed_valid_and_invalid(self, valid_row):
        rows = [
            valid_row,
            {**valid_row, "order_id": 2, "quantity": 0},
            {**valid_row, "order_id": 3, "unit_price": -5.0},
            {**valid_row, "order_id": 4, "discount_pct": 1.5},
            {
                **valid_row,
                "order_id": 5,
                "quantity": 3,
                "unit_price": 50.0,
                "discount_pct": 0.1,
            },
        ]
        df = pd.DataFrame(rows)
        result = validate_sales(df)
        assert len(result) == 2

    def test_all_invalid_returns_empty(self, valid_row):
        rows = [
            {**valid_row, "order_id": 1, "quantity": 0},
            {**valid_row, "order_id": 2, "quantity": -1},
        ]
        df = pd.DataFrame(rows)
        result = validate_sales(df)
        assert len(result) == 0

    def test_all_valid_returns_all(self, valid_row):
        rows = [
            valid_row,
            {**valid_row, "order_id": 2},
        ]
        df = pd.DataFrame(rows)
        result = validate_sales(df)
        assert len(result) == 2


class TestUS3Logging:
    def test_logging_records_counts(self, caplog, valid_row):
        caplog.set_level("INFO")
        rows = [
            valid_row,
            {**valid_row, "order_id": 2, "quantity": 0},
            {**valid_row, "order_id": 3},
        ]
        df = pd.DataFrame(rows)
        validate_sales(df)
        log_msg = caplog.records[-1].getMessage()
        assert "total=3" in log_msg
        assert "válidos=2" in log_msg or "valid=2" in log_msg
        assert "rejeitados=1" in log_msg or "rejected=1" in log_msg


class TestUS3IntegrationWithExtract:
    def test_integration_with_extract_csv(self, valid_row):
        import os
        import tempfile

        from src.extract import extract_csv

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        columns = list(valid_row.keys())
        tmp.write(",".join(columns) + "\n")
        tmp.write(",".join(str(valid_row[c]) for c in columns) + "\n")
        tmp.close()

        try:
            df = extract_csv(tmp.name)
            result = validate_sales(df)
            assert len(result) == 1
        finally:
            os.unlink(tmp.name)
