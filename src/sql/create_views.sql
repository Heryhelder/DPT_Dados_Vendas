CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT
    year,
    month,
    COUNT(*) AS total_orders,
    SUM(net_revenue) AS total_revenue,
    AVG(net_revenue) AS avg_order_value
FROM sales
GROUP BY year, month
ORDER BY year, month;

CREATE OR REPLACE VIEW v_store_performance AS
SELECT
    sales_rep,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(net_revenue) AS total_revenue,
    AVG(net_revenue) AS avg_ticket
FROM sales
GROUP BY sales_rep, region
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW v_category_sales AS
SELECT
    category,
    sub_category,
    COUNT(*) AS total_items,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit,
    AVG(discount_pct) AS avg_discount
FROM sales
GROUP BY category, sub_category
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW v_top_products AS
SELECT
    product_name,
    category,
    brand,
    SUM(quantity) AS total_quantity,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit
FROM sales
GROUP BY product_name, category, brand
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW v_sales_summary AS
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(net_revenue) AS total_revenue,
    SUM(gross_profit) AS total_profit,
    AVG(net_revenue) AS avg_order_value,
    SUM(quantity) AS total_units_sold
FROM sales;
