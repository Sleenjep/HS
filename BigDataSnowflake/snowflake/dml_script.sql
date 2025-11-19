-- загрузка уникальных покупателей
INSERT INTO dim_customer (
    customer_first_name, customer_last_name, customer_age, customer_email,
    customer_country, customer_postal_code, customer_pet_type, customer_pet_name, 
    customer_pet_breed, pet_category
)
SELECT DISTINCT
    customer_first_name, customer_last_name, customer_age, customer_email,
    customer_country, customer_postal_code, customer_pet_type, customer_pet_name,
    customer_pet_breed, pet_category
FROM pet_sales
WHERE customer_email IS NOT NULL;

-- загрузка уникальных продавцов
INSERT INTO dim_seller (
    seller_first_name, seller_last_name, seller_email, 
    seller_country, seller_postal_code
)
SELECT DISTINCT
    seller_first_name, seller_last_name, seller_email,
    seller_country, seller_postal_code
FROM pet_sales
WHERE seller_email IS NOT NULL;

-- загрузка уникальных магазинов
INSERT INTO dim_store (
    store_name, store_location, store_city, store_state,
    store_country, store_phone, store_email
)
SELECT DISTINCT
    store_name, store_location, store_city, store_state,
    store_country, store_phone, store_email
FROM pet_sales
WHERE store_email IS NOT NULL;

-- загрузка уникальных продуктов
INSERT INTO dim_product (
    product_name, product_category, product_weight, product_color,
    product_size, product_brand, product_material, product_description,
    product_rating, product_reviews, product_release_date,
    product_expiry_date, product_price
)
SELECT DISTINCT
    product_name, product_category, product_weight, product_color,
    product_size, product_brand, product_material, product_description,
    product_rating, product_reviews, product_release_date,
    product_expiry_date, product_price
FROM pet_sales
WHERE product_name IS NOT NULL;

-- загрузка уникальных поставщиков
INSERT INTO dim_supplier (
    supplier_name, supplier_contact, supplier_email,
    supplier_phone, supplier_address, supplier_city, supplier_country
)
SELECT DISTINCT
    supplier_name, supplier_contact, supplier_email,
    supplier_phone, supplier_address, supplier_city, supplier_country
FROM pet_sales
WHERE supplier_email IS NOT NULL;

-- загрузка фактов продаж
INSERT INTO fact_sales (
    customer_id,
    seller_id,
    store_id,
    product_id,
    supplier_id,
    sale_date,
    sale_quantity,
    sale_total_price,
    product_quantity,
    product_price
)
SELECT
    dc.customer_id,
    ds.seller_id,
    dst.store_id,
    dp.product_id,
    dsu.supplier_id,
    ps.sale_date,
    ps.sale_quantity,
    ps.sale_total_price,
    ps.product_quantity,
    ps.product_price
FROM pet_sales ps
JOIN dim_customer dc ON
    TRIM(ps.customer_first_name) = TRIM(dc.customer_first_name) AND
    TRIM(ps.customer_last_name) = TRIM(dc.customer_last_name) AND
    TRIM(ps.customer_email) = TRIM(dc.customer_email)
JOIN dim_seller ds ON
    TRIM(ps.seller_first_name) = TRIM(ds.seller_first_name) AND
    TRIM(ps.seller_last_name) = TRIM(ds.seller_last_name) AND
    TRIM(ps.seller_email) = TRIM(ds.seller_email)
JOIN dim_store dst ON
    TRIM(ps.store_name) = TRIM(dst.store_name) AND
    TRIM(ps.store_email) = TRIM(dst.store_email)
JOIN dim_product dp ON
    TRIM(ps.product_name) = TRIM(dp.product_name) AND
    ROUND(ps.product_price::NUMERIC, 2) = ROUND(dp.product_price::NUMERIC, 2)
JOIN dim_supplier dsu ON
    TRIM(ps.supplier_name) = TRIM(dsu.supplier_name) AND
    TRIM(ps.supplier_email) = TRIM(dsu.supplier_email);
