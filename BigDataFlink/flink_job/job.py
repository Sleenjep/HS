from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # kafka Source
    t_env.execute_sql(
        """
        CREATE TABLE source_kafka (
            id STRING,
            customer_first_name STRING,
            customer_last_name STRING,
            customer_age STRING,
            customer_email STRING,
            customer_country STRING,
            customer_postal_code STRING,
            customer_pet_type STRING,
            customer_pet_name STRING,
            customer_pet_breed STRING,
            seller_first_name STRING,
            seller_last_name STRING,
            seller_email STRING,
            seller_country STRING,
            seller_postal_code STRING,
            product_name STRING,
            product_category STRING,
            product_price STRING,
            product_quantity STRING,
            sale_date STRING,
            sale_customer_id STRING,
            sale_seller_id STRING,
            sale_product_id STRING,
            sale_quantity STRING,
            sale_total_price STRING,
            store_name STRING,
            store_location STRING,
            store_city STRING,
            store_state STRING,
            store_country STRING,
            store_phone STRING,
            store_email STRING,
            pet_category STRING,
            product_weight STRING,
            product_color STRING,
            product_size STRING,
            product_brand STRING,
            product_material STRING,
            product_description STRING,
            product_rating STRING,
            product_reviews STRING,
            product_release_date STRING,
            product_expiry_date STRING,
            supplier_name STRING,
            supplier_contact STRING,
            supplier_email STRING,
            supplier_phone STRING,
            supplier_address STRING,
            supplier_city STRING,
            supplier_country STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sales_topic',
            'properties.bootstrap.servers' = 'kafka:9092',
            'properties.group.id' = 'flink_group',
            'format' = 'json',
            'scan.startup.mode' = 'earliest-offset'
        )
    """
    )

    # dim customer
    t_env.execute_sql(
        """
        CREATE TABLE dim_customer (
            customer_id INT,
            first_name STRING,
            last_name STRING,
            email STRING,
            country STRING,
            PRIMARY KEY (customer_id) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/spark_db',
            'table-name' = 'dim_customer',
            'username' = 'spark_user_name',
            'password' = 'spark_my_secret_password'
        )
    """
    )

    # dim product
    t_env.execute_sql(
        """
        CREATE TABLE dim_product (
            product_id INT,
            product_name STRING,
            category STRING,
            price DECIMAL(10, 2),
            PRIMARY KEY (product_id) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/spark_db',
            'table-name' = 'dim_product',
            'username' = 'spark_user_name',
            'password' = 'spark_my_secret_password'
        )
    """
    )

    # dim seller
    t_env.execute_sql(
        """
        CREATE TABLE dim_seller (
            seller_id INT,
            first_name STRING,
            last_name STRING,
            email STRING,
            country STRING,
            PRIMARY KEY (seller_id) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/spark_db',
            'table-name' = 'dim_seller',
            'username' = 'spark_user_name',
            'password' = 'spark_my_secret_password'
        )
    """
    )

    # dim store
    t_env.execute_sql(
        """
        CREATE TABLE dim_store (
            store_name STRING,
            city STRING,
            country STRING,
            PRIMARY KEY (store_name, city) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/spark_db',
            'table-name' = 'dim_store',
            'username' = 'spark_user_name',
            'password' = 'spark_my_secret_password'
        )
    """
    )

    # fact sales
    t_env.execute_sql(
        """
        CREATE TABLE fact_sales (
            customer_id INT,
            seller_id INT,
            product_id INT,
            store_name STRING,
            city STRING,
            quantity INT,
            total_amount DECIMAL(10, 2),
            sale_date DATE
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/spark_db',
            'table-name' = 'fact_sales',
            'username' = 'spark_user_name',
            'password' = 'spark_my_secret_password'
        )
    """
    )

    statement_set = t_env.create_statement_set()

    statement_set.add_insert_sql(
        """
        INSERT INTO dim_customer
        SELECT DISTINCT
            CAST(sale_customer_id AS INT),
            customer_first_name,
            customer_last_name,
            customer_email,
            customer_country
        FROM source_kafka
        WHERE sale_customer_id IS NOT NULL
    """
    )

    statement_set.add_insert_sql(
        """
        INSERT INTO dim_product
        SELECT DISTINCT
            CAST(sale_product_id AS INT),
            product_name,
            product_category,
            CAST(product_price AS DECIMAL(10, 2))
        FROM source_kafka
        WHERE sale_product_id IS NOT NULL
    """
    )

    statement_set.add_insert_sql(
        """
        INSERT INTO dim_seller
        SELECT DISTINCT
            CAST(sale_seller_id AS INT),
            seller_first_name,
            seller_last_name,
            seller_email,
            seller_country
        FROM source_kafka
        WHERE sale_seller_id IS NOT NULL
    """
    )

    statement_set.add_insert_sql(
        """
        INSERT INTO dim_store
        SELECT DISTINCT
            store_name,
            store_city,
            store_country
        FROM source_kafka
        WHERE store_name IS NOT NULL
    """
    )

    statement_set.add_insert_sql(
        """
        INSERT INTO fact_sales
        SELECT
            CAST(sale_customer_id AS INT),
            CAST(sale_seller_id AS INT),
            CAST(sale_product_id AS INT),
            store_name,
            store_city,
            CAST(sale_quantity AS INT),
            CAST(sale_total_price AS DECIMAL(10, 2)),
            CAST(TO_TIMESTAMP(sale_date, 'M/d/yyyy') AS DATE)
        FROM source_kafka
    """
    )

    statement_set.execute()


if __name__ == "__main__":
    main()
