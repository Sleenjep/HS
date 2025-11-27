-- dim_customers
INSERT INTO clickhouse.mock_data.dim_customers
SELECT DISTINCT
    sale_customer_id,
    customer_first_name,
    customer_last_name,
    customer_age,
    customer_email,
    customer_country,
    customer_postal_code,
    customer_pet_type,
    customer_pet_name,
    customer_pet_breed
FROM (
    SELECT 
        sale_customer_id, 
        customer_first_name, 
        customer_last_name, 
        customer_age, 
        customer_email, 
        customer_country, 
        customer_postal_code, 
        customer_pet_type, 
        customer_pet_name, 
        customer_pet_breed
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        sale_customer_id, 
        customer_first_name, 
        customer_last_name, 
        customer_age, 
        customer_email, 
        customer_country, 
        customer_postal_code, 
        customer_pet_type, 
        customer_pet_name, 
        customer_pet_breed
    FROM clickhouse.mock_data.mock_data
);

-- dim_products
INSERT INTO clickhouse.mock_data.dim_products
SELECT DISTINCT
    sale_product_id,
    product_name,
    product_category,
    product_price,
    pet_category,
    product_weight,
    product_color,
    product_size,
    product_brand,
    product_material,
    product_description,
    product_rating,
    product_reviews,
    product_release_date,
    product_expiry_date
FROM (
    SELECT 
        sale_product_id, 
        product_name, 
        product_category, 
        product_price, 
        pet_category, 
        product_weight, 
        product_color, 
        product_size, 
        product_brand, 
        product_material, 
        product_description, 
        product_rating, 
        product_reviews, 
        product_release_date, 
        product_expiry_date
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        sale_product_id, 
        product_name, 
        product_category, 
        CAST(product_price AS DECIMAL(10, 2)) as product_price, 
        pet_category, 
        CAST(product_weight AS DECIMAL(10, 2)) as product_weight, 
        product_color, 
        product_size, 
        product_brand, 
        product_material, 
        product_description, 
        CAST(product_rating AS DECIMAL(3, 1)) as product_rating, 
        product_reviews, 
        date_parse(product_release_date, '%m/%d/%Y') as product_release_date, 
        date_parse(product_expiry_date, '%m/%d/%Y') as product_expiry_date
    FROM clickhouse.mock_data.mock_data
);

-- dim_sellers
INSERT INTO clickhouse.mock_data.dim_sellers
SELECT DISTINCT
    sale_seller_id,
    seller_first_name,
    seller_last_name,
    seller_email,
    seller_country,
    seller_postal_code
FROM (
    SELECT 
        sale_seller_id, 
        seller_first_name, 
        seller_last_name, 
        seller_email, 
        seller_country, 
        seller_postal_code
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        sale_seller_id, 
        seller_first_name, 
        seller_last_name, 
        seller_email, 
        seller_country, 
        seller_postal_code
    FROM clickhouse.mock_data.mock_data
);

-- dim_stores
INSERT INTO clickhouse.mock_data.dim_stores
SELECT DISTINCT
    store_name,
    store_location,
    store_city,
    store_state,
    store_country,
    store_phone,
    store_email
FROM (
    SELECT 
        store_name, 
        store_location, 
        store_city, 
        store_state, 
        store_country, 
        store_phone, 
        store_email
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        store_name, 
        store_location, 
        store_city, 
        store_state, 
        store_country, 
        store_phone, 
        store_email
    FROM clickhouse.mock_data.mock_data
);

-- dim_suppliers
INSERT INTO clickhouse.mock_data.dim_suppliers
SELECT DISTINCT
    supplier_name,
    supplier_contact,
    supplier_email,
    supplier_phone,
    supplier_address,
    supplier_city,
    supplier_country
FROM (
    SELECT 
        supplier_name, 
        supplier_contact, 
        supplier_email, 
        supplier_phone, 
        supplier_address, 
        supplier_city, 
        supplier_country
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        supplier_name, 
        supplier_contact, 
        supplier_email, 
        supplier_phone, 
        supplier_address, 
        supplier_city, 
        supplier_country
    FROM clickhouse.mock_data.mock_data
);

-- fact_sales
INSERT INTO clickhouse.mock_data.fact_sales
SELECT
    id,
    sale_customer_id,
    sale_seller_id,
    sale_product_id,
    store_name,
    supplier_name,
    sale_date,
    sale_quantity,
    sale_total_price
FROM (
    SELECT 
        id, sale_customer_id, sale_seller_id, sale_product_id, 
        store_name, 
        supplier_name, 
        sale_date, 
        sale_quantity, 
        sale_total_price
    FROM postgresql.public.mock_data
    UNION ALL
    SELECT 
        id, sale_customer_id, sale_seller_id, sale_product_id, 
        store_name, 
        supplier_name, 
        date_parse(sale_date, '%m/%d/%Y') as sale_date, 
        sale_quantity, 
        CAST(sale_total_price AS DECIMAL(10, 2)) as sale_total_price
    FROM clickhouse.mock_data.mock_data
);
