-- product sales showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_product_sales;
CREATE TABLE clickhouse.mock_data.report_product_sales AS
SELECT
    p.name AS product_name,
    p.category AS product_category,
    SUM(f.total_price) AS total_revenue,
    SUM(f.quantity) AS total_quantity_sold,
    AVG(p.rating) AS avg_rating,
    MAX(p.reviews) AS review_count
FROM clickhouse.mock_data.fact_sales f
JOIN clickhouse.mock_data.dim_products p ON f.product_id = p.product_id
GROUP BY p.name, p.category;

-- customer sales showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_customer_sales;
CREATE TABLE clickhouse.mock_data.report_customer_sales AS
SELECT
    c.first_name as first_name,
    c.last_name as last_name,
    c.country as country,
    SUM(f.total_price) AS total_spent,
    AVG(f.total_price) AS avg_check
FROM clickhouse.mock_data.fact_sales f
JOIN clickhouse.mock_data.dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.first_name, c.last_name, c.country;

-- time sales showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_time_sales;
CREATE TABLE clickhouse.mock_data.report_time_sales AS
SELECT
    YEAR(f.sale_date) AS sale_year,
    MONTH(f.sale_date) AS sale_month,
    SUM(f.total_price) AS total_revenue,
    AVG(f.total_price) AS avg_order_size
FROM clickhouse.mock_data.fact_sales f
GROUP BY YEAR(f.sale_date), MONTH(f.sale_date);

-- store sales showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_store_sales;
CREATE TABLE clickhouse.mock_data.report_store_sales AS
SELECT
    s.store_name as store_name,
    s.city as city,
    s.country as country,
    SUM(f.total_price) AS total_revenue,
    AVG(f.total_price) AS avg_check
FROM clickhouse.mock_data.fact_sales f
JOIN clickhouse.mock_data.dim_stores s ON f.store_name = s.store_name
GROUP BY s.store_name, s.city, s.country;

-- supplier sales showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_supplier_sales;
CREATE TABLE clickhouse.mock_data.report_supplier_sales AS
SELECT
    sup.supplier_name as supplier_name,
    sup.country as country,
    SUM(f.total_price) AS total_revenue,
    AVG(p.price) AS avg_product_price
FROM clickhouse.mock_data.fact_sales f
JOIN clickhouse.mock_data.dim_suppliers sup ON f.supplier_name = sup.supplier_name
JOIN clickhouse.mock_data.dim_products p ON f.product_id = p.product_id
GROUP BY sup.supplier_name, sup.country;

-- quality showcase
DROP TABLE IF EXISTS clickhouse.mock_data.report_quality;
CREATE TABLE clickhouse.mock_data.report_quality AS
SELECT
    p.name AS product_name,
    p.rating,
    p.reviews,
    SUM(f.quantity) AS total_sales_volume
FROM clickhouse.mock_data.fact_sales f
JOIN clickhouse.mock_data.dim_products p ON f.product_id = p.product_id
GROUP BY p.name, p.rating, p.reviews;
