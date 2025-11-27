CREATE TABLE IF NOT EXISTS clickhouse.mock_data.dim_customers (
    customer_id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    age INT,
    email VARCHAR,
    country VARCHAR,
    postal_code VARCHAR,
    pet_type VARCHAR,
    pet_name VARCHAR,
    pet_breed VARCHAR
);

CREATE TABLE IF NOT EXISTS clickhouse.mock_data.dim_products (
    product_id INT,
    name VARCHAR,
    category VARCHAR,
    price DECIMAL(10, 2),
    pet_category VARCHAR,
    weight DECIMAL(10, 2),
    color VARCHAR,
    size VARCHAR,
    brand VARCHAR,
    material VARCHAR,
    description VARCHAR,
    rating DECIMAL(3, 1),
    reviews INT,
    release_date DATE,
    expiry_date DATE
);

CREATE TABLE IF NOT EXISTS clickhouse.mock_data.dim_sellers (
    seller_id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    country VARCHAR,
    postal_code VARCHAR
);

CREATE TABLE IF NOT EXISTS clickhouse.mock_data.dim_stores (
    store_name VARCHAR,
    location VARCHAR,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    phone VARCHAR,
    email VARCHAR
);

CREATE TABLE IF NOT EXISTS clickhouse.mock_data.dim_suppliers (
    supplier_name VARCHAR,
    contact VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    address VARCHAR,
    city VARCHAR,
    country VARCHAR
);

CREATE TABLE IF NOT EXISTS clickhouse.mock_data.fact_sales (
    sale_id INT,
    customer_id INT,
    seller_id INT,
    product_id INT,
    store_name VARCHAR,
    supplier_name VARCHAR,
    sale_date DATE,
    quantity INT,
    total_price DECIMAL(10, 2)
);
