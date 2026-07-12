import pandas as pd
import pytest

from src.analyze import (
    aggregate_metrics,
    analyze_recurrence,
    analyze_sales,
    analyze_seasonality,
    top_categories,
    top_products,
)


@pytest.fixture
def minimal_row() -> dict:
    """Linha mínima com todas as 28 colunas de prepare_sales()."""
    return {
        "order_id": 1,
        "customer_id": "C001",
        "customer_name": "Thiago Alves",
        "customer_segment": "Consumer",
        "customer_type": "Existing",
        "first_purchase_date": pd.Timestamp("2023-01-15"),
        "last_purchase_date": pd.Timestamp("2024-06-20"),
        "product_id": "P001",
        "product_name": "iPhone 15",
        "category": "Electronics",
        "sub_category": "Smartphones",
        "brand": "Apple",
        "order_date": pd.Timestamp("2024-06-15"),
        "quantity": 10,
        "unit_price": 50.0,
        "discount_pct": 0.1,
        "sales_channel": "Online",
        "payment_method": "Credit Card",
        "sales_rep": "Carlos Silva",
        "region": "Southeast",
        "operating_expenses": 100.0,
        "cash_balance": 15000.0,
        "debt_balance": 3000.0,
        "monthly_burn": 2000.0,
        "churn_flag": 0,
        "month": 6.0,
        "year": 2024.0,
        "quarter": 2.0,
    }


@pytest.fixture
def minimal_df(minimal_row) -> pd.DataFrame:
    """DataFrame mínimo com uma linha e 28 colunas."""
    return pd.DataFrame([minimal_row])


class TestUS1CoreMetrics:
    def test_gross_revenue_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        assert result["gross_revenue"].iloc[0] == 500.0

    def test_net_revenue_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        assert result["net_revenue"].iloc[0] == 450.0

    def test_cogs_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        expected = pytest.approx(292.5)
        assert result["cost_of_goods_sold"].iloc[0] == expected

    def test_gross_profit_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        expected = pytest.approx(157.5)
        assert result["gross_profit"].iloc[0] == expected

    def test_input_columns_preserved(self, minimal_df):
        original_cols = set(minimal_df.columns)
        result = analyze_sales(minimal_df)
        for col in original_cols:
            assert col in result.columns

    def test_null_propagation(self, minimal_row):
        row = {**minimal_row, "quantity": None}
        df = pd.DataFrame([row])
        result = analyze_sales(df)
        assert pd.isna(result["gross_revenue"].iloc[0])
        assert pd.isna(result["net_revenue"].iloc[0])
        assert pd.isna(result["cost_of_goods_sold"].iloc[0])
        assert pd.isna(result["gross_profit"].iloc[0])

    def test_empty_dataframe_raises(self):
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="vazio"):
            analyze_sales(df)

    def test_custom_cogs_rules(self, minimal_row):
        custom = {"Smartphones": 0.50}
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df, cogs_rules=custom)
        expected = pytest.approx(225.0)
        assert result["cost_of_goods_sold"].iloc[0] == expected

    def test_unknown_sub_category_nan(self, minimal_row):
        row = {**minimal_row, "sub_category": "Unknown"}
        df = pd.DataFrame([row])
        result = analyze_sales(df)
        assert pd.isna(result["cost_of_goods_sold"].iloc[0])
        assert pd.isna(result["gross_profit"].iloc[0])


class TestUS2AggregatedMetrics:
    def test_returns_new_dataframe(self, minimal_df):
        original_cols = list(minimal_df.columns)
        result = analyze_sales(minimal_df)
        assert result is not minimal_df
        assert list(minimal_df.columns) == original_cols

    def test_aggregate_total_revenue(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        agg = aggregate_metrics(result)
        assert agg["total_revenue"].iloc[0] == pytest.approx(450.0)

    def test_aggregate_avg_ticket(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "quantity": 10, "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "quantity": 5, "discount_pct": 0.2, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        agg = aggregate_metrics(df)
        assert agg["avg_ticket"].iloc[0] == pytest.approx(375.0)

    def test_aggregate_total_quantity(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "quantity": 10, "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "quantity": 5, "discount_pct": 0.2, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        agg = aggregate_metrics(df)
        assert agg["total_quantity"].iloc[0] == 15

    def test_aggregate_avg_discount(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "quantity": 10, "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "quantity": 5, "discount_pct": 0.2, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        agg = aggregate_metrics(df)
        assert agg["avg_discount"].iloc[0] == pytest.approx(0.15)

    def test_aggregate_by_dimension(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "quantity": 10, "discount_pct": 0.1, "region": "North",
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "quantity": 5, "discount_pct": 0.2, "region": "South",
            },
            {
                "order_id": 3, "net_revenue": 200.0,
                "quantity": 3, "discount_pct": 0.0, "region": "North",
            },
        ]
        df = pd.DataFrame(rows)
        agg = aggregate_metrics(df, group_by=["region"])
        north = agg[agg["region"] == "North"]
        south = agg[agg["region"] == "South"]
        assert len(north) == 1
        assert len(south) == 1
        assert north["total_revenue"].iloc[0] == pytest.approx(650.0)
        assert south["total_revenue"].iloc[0] == pytest.approx(300.0)

    def test_aggregate_empty_input(self):
        cols = ["order_id", "net_revenue", "quantity", "discount_pct", "region"]
        df = pd.DataFrame(columns=cols)
        agg = aggregate_metrics(df)
        assert len(agg) == 0


class TestUS3Seasonality:
    def test_seasonality_monthly_totals(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "year": 2024.0, "month": 1.0, "quarter": 1.0,
                "quantity": 10, "discount_pct": 0.1,
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "year": 2024.0, "month": 1.0, "quarter": 1.0,
                "quantity": 5, "discount_pct": 0.2,
            },
            {
                "order_id": 3, "net_revenue": 200.0,
                "year": 2024.0, "month": 3.0, "quarter": 1.0,
                "quantity": 3, "discount_pct": 0.0,
            },
        ]
        df = pd.DataFrame(rows)
        season = analyze_seasonality(df)
        assert "monthly" in season
        monthly = season["monthly"]
        jan = monthly[
            (monthly["year"] == 2024.0) & (monthly["month"] == 1.0)
        ]
        assert len(jan) == 1
        assert jan["total_revenue"].iloc[0] == pytest.approx(750.0)

    def test_seasonality_quarterly_totals(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0,
                "year": 2024.0, "month": 1.0, "quarter": 1.0,
                "quantity": 10, "discount_pct": 0.1,
            },
            {
                "order_id": 2, "net_revenue": 300.0,
                "year": 2024.0, "month": 4.0, "quarter": 2.0,
                "quantity": 5, "discount_pct": 0.2,
            },
        ]
        df = pd.DataFrame(rows)
        season = analyze_seasonality(df)
        assert "quarterly" in season
        quarterly = season["quarterly"]
        q1 = quarterly[
            (quarterly["year"] == 2024.0) & (quarterly["quarter"] == 1.0)
        ]
        q2 = quarterly[
            (quarterly["year"] == 2024.0) & (quarterly["quarter"] == 2.0)
        ]
        assert len(q1) == 1
        assert len(q2) == 1
        assert q1["total_revenue"].iloc[0] == pytest.approx(450.0)
        assert q2["total_revenue"].iloc[0] == pytest.approx(300.0)


class TestUS3TopPerformers:
    def test_top_products_ranking(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 200.0, "quantity": 3,
                "product_name": "B", "category": "C1",
                "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "net_revenue": 500.0, "quantity": 10,
                "product_name": "A", "category": "C1",
                "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 3, "net_revenue": 100.0, "quantity": 2,
                "product_name": "C", "category": "C2",
                "discount_pct": 0.1, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        products = top_products(df)
        assert products.iloc[0]["product_name"] == "A"
        assert products.iloc[1]["product_name"] == "B"
        assert products.iloc[2]["product_name"] == "C"

    def test_top_categories_ranking(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 200.0, "quantity": 3,
                "product_name": "X", "category": "CatB",
                "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "net_revenue": 500.0, "quantity": 10,
                "product_name": "Y", "category": "CatA",
                "discount_pct": 0.1, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        cats = top_categories(df)
        assert cats.iloc[0]["category"] == "CatA"

    def test_top_products_limit_n(self):
        rows = [
            {
                "order_id": i, "net_revenue": float(100 * i),
                "quantity": i, "product_name": f"P{i}",
                "category": "C1", "discount_pct": 0.1, "region": "A",
            }
            for i in range(1, 6)
        ]
        df = pd.DataFrame(rows)
        products = top_products(df, n=2)
        assert len(products) == 2

    def test_recurrence_rate(self):
        rows = [
            {
                "order_id": 1, "customer_id": "C001",
                "net_revenue": 450.0, "quantity": 10,
                "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "customer_id": "C001",
                "net_revenue": 300.0, "quantity": 5,
                "discount_pct": 0.2, "region": "A",
            },
            {
                "order_id": 3, "customer_id": "C002",
                "net_revenue": 200.0, "quantity": 3,
                "discount_pct": 0.0, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        rec = analyze_recurrence(df)
        assert rec["total_customers"] == 2
        assert rec["repeat_customers"] == 1
        assert rec["recurrence_rate"] == pytest.approx(0.5)

    def test_recurrence_single_customer(self):
        rows = [
            {
                "order_id": 1, "customer_id": "C001",
                "net_revenue": 450.0, "quantity": 10,
                "discount_pct": 0.1, "region": "A",
            },
            {
                "order_id": 2, "customer_id": "C001",
                "net_revenue": 300.0, "quantity": 5,
                "discount_pct": 0.2, "region": "A",
            },
        ]
        df = pd.DataFrame(rows)
        rec = analyze_recurrence(df)
        assert rec["total_customers"] == 1
        assert rec["repeat_customers"] == 1
        assert rec["recurrence_rate"] == pytest.approx(1.0)

    def test_recurrence_no_customers(self):
        cols = [
            "order_id", "customer_id", "net_revenue",
            "quantity", "discount_pct", "region",
        ]
        df = pd.DataFrame(columns=cols)
        rec = analyze_recurrence(df)
        assert rec["total_customers"] == 0
        assert rec["repeat_customers"] == 0
        assert rec["recurrence_rate"] == 0.0


class TestUS4OptionalMetrics:
    def test_ebitda_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df)
        assert "ebitda" in result.columns
        assert result["ebitda"].iloc[0] == pytest.approx(57.5)

    def test_net_income_computation(self, minimal_row):
        df = pd.DataFrame([minimal_row])
        result = analyze_sales(df, tax_rate=0.25)
        assert "net_income" in result.columns
        assert result["net_income"].iloc[0] == pytest.approx(43.125)

    def test_optional_metrics_graceful_degradation(self, minimal_row):
        row = {
            k: v for k, v in minimal_row.items()
            if k != "operating_expenses"
        }
        df = pd.DataFrame([row])
        result = analyze_sales(df)
        assert "ebitda" not in result.columns
        assert "net_income" not in result.columns

    def test_cross_dimensional_comparison(self):
        rows = [
            {
                "order_id": 1, "net_revenue": 450.0, "quantity": 10,
                "discount_pct": 0.1, "region": "North",
                "sales_channel": "Online",
            },
            {
                "order_id": 2, "net_revenue": 300.0, "quantity": 5,
                "discount_pct": 0.2, "region": "North",
                "sales_channel": "Retail",
            },
            {
                "order_id": 3, "net_revenue": 200.0, "quantity": 3,
                "discount_pct": 0.0, "region": "South",
                "sales_channel": "Online",
            },
        ]
        df = pd.DataFrame(rows)
        agg = aggregate_metrics(
            df, group_by=["region", "sales_channel"]
        )
        assert len(agg) == 3
        no = agg[
            (agg["region"] == "North")
            & (agg["sales_channel"] == "Online")
        ]
        assert len(no) == 1
        assert no["total_revenue"].iloc[0] == pytest.approx(450.0)


class TestPerformance:
    def test_analyze_sales_100k_rows(self, minimal_row):
        import time

        rows = []
        for i in range(100_000):
            row = {
                **minimal_row,
                "order_id": i + 1,
                "quantity": (i % 10) + 1,
            }
            rows.append(row)
        df = pd.DataFrame(rows)

        start = time.perf_counter()
        analyze_sales(df)
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, (
            f"analyze_sales took {elapsed:.2f}s, expected < 2.0s"
        )


class TestLogging:
    def test_logging_stats(self, caplog, minimal_row):
        caplog.set_level("INFO")
        df = pd.DataFrame([minimal_row])
        analyze_sales(df)
        log_msg = caplog.records[-1].getMessage()
        assert "rows_processed=1" in log_msg
        assert "columns_added=6" in log_msg
