from pyspark.sql import SparkSession, Window
import pyspark.sql.functions as F

APP_NAME = "DWHtoMongoDBReports"
POSTGRES_JDBC_JAR_PATH = "/opt/spark/jars/postgresql-42.6.0.jar"

PG_DB_URL = "jdbc:postgresql://postgres_db:5432/spark_db"
PG_DB_PROPERTIES = {
    "user": "spark_user_name",
    "password": "spark_my_secret_password",
    "driver": "org.postgresql.Driver",
}

MONGO_CONNECTION_URI = "mongodb://mongodb_db:27017"
MONGO_DATABASE = "reports"


def initialize_spark_session(app_name, pg_jar):
    """Initializes and returns a SparkSession."""
    jars_path = f"{pg_jar}"
    session = (
        SparkSession.builder.appName(app_name)
        .config("spark.jars", jars_path)
        .getOrCreate()
    )
    return session


def load_dwh_table(spark, table_name):
    """Loads a table from PostgreSQL DWH."""
    df = (
        spark.read.format("jdbc")
        .option("url", PG_DB_URL)
        .option("dbtable", table_name)
        .options(**PG_DB_PROPERTIES)
        .load()
    )
    return df


def save_report_to_mongodb(report_df, collection_name):
    """Saves a report DataFrame to a MongoDB collection using pymongo."""

    data = [row.asDict() for row in report_df.collect()]
    from decimal import Decimal
    import datetime

    def _normalize_value(v):
        if isinstance(v, Decimal):
            try:
                return float(v)
            except Exception:
                return float(str(v))
        if isinstance(v, datetime.date) or isinstance(v, datetime.datetime):
            return v.isoformat()
        if isinstance(v, list):
            return [_normalize_value(x) for x in v]
        if isinstance(v, dict):
            return {kk: _normalize_value(vv) for kk, vv in v.items()}
        return v

    normalized_data = []
    for row in data:
        normalized_row = {k: _normalize_value(v) for k, v in row.items()}
        normalized_data.append(normalized_row)

    if not normalized_data:
        return

    import pymongo

    try:
        client = pymongo.MongoClient(MONGO_CONNECTION_URI)
        db = client[MONGO_DATABASE]
        collection = db[collection_name]

        # Drop collection to overwrite
        collection.drop()

        # Insert data
        collection.insert_many(normalized_data)

        client.close()
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        raise


def generate_reports(spark):
    """Generates and saves all required reports to MongoDB."""

    print("Loading base DWH tables...")
    fact_sales_df = load_dwh_table(spark, "fact_sales").cache()
    dim_product_df = load_dwh_table(spark, "dim_product").cache()
    dim_customer_df = load_dwh_table(spark, "dim_customer").cache()
    dim_date_df = load_dwh_table(spark, "dim_date").cache()
    dim_store_df = load_dwh_table(spark, "dim_store").cache()
    dim_supplier_df = load_dwh_table(spark, "dim_supplier").cache()
    print("Base DWH tables loaded and cached.")

    # --- Витрина продаж по продуктам ---

    # 1.1. Топ-10 самых продаваемых продуктов (по количеству)
    report_top_10_products = (
        fact_sales_df.groupBy("product_sk")
        .agg(
            F.sum("sale_quantity").alias("total_quantity_sold"),
            F.sum("sale_total_price").alias("total_revenue_generated"),
        )
        .join(dim_product_df, "product_sk")
        .select(
            dim_product_df.product_id.alias("business_product_id"),
            dim_product_df.name.alias("product_name"),
            dim_product_df.category.alias("product_category"),
            "total_quantity_sold",
            "total_revenue_generated",
        )
        .orderBy(F.desc("total_quantity_sold"))
        .limit(10)
    )
    save_report_to_mongodb(report_top_10_products, "mart_top_10_selling_products")

    # 1.2 Общая выручка по категориям продуктов
    report_revenue_by_category = (
        fact_sales_df.join(dim_product_df, "product_sk")
        .groupBy(dim_product_df.category.alias("product_category"))
        .agg(F.sum("sale_total_price").alias("category_total_revenue"))
        .orderBy(F.desc("category_total_revenue"))
    )
    save_report_to_mongodb(
        report_revenue_by_category, "mart_revenue_by_product_category"
    )

    # 1.3 Средний рейтинг и количество отзывов для каждого продукта
    report_product_feedback_summary = dim_product_df.select(
        dim_product_df.product_id.alias("business_product_id"),
        dim_product_df.name.alias("product_name"),
        dim_product_df.category.alias("product_category"),
        dim_product_df.rating.alias("average_rating"),
        dim_product_df.reviews.alias("number_of_reviews"),
    ).orderBy(F.desc("number_of_reviews"))
    save_report_to_mongodb(
        report_product_feedback_summary, "mart_product_feedback_summary"
    )

    # --- Витрина продаж по клиентам ---

    # 2.1 Топ-10 клиентов с наибольшей общей суммой покупок
    report_top_10_customers_by_purchase = (
        fact_sales_df.groupBy("customer_sk")
        .agg(F.sum("sale_total_price").alias("customer_total_purchases"))
        .join(dim_customer_df, "customer_sk")
        .select(
            dim_customer_df.customer_id.alias("business_customer_id"),
            dim_customer_df.first_name,
            dim_customer_df.last_name,
            dim_customer_df.country.alias("customer_country"),
            "customer_total_purchases",
        )
        .orderBy(F.desc("customer_total_purchases"))
        .limit(10)
    )
    save_report_to_mongodb(
        report_top_10_customers_by_purchase, "mart_top_10_customers_by_purchase"
    )

    # 2.2 Распределение клиентов по странам
    report_customer_distribution_by_country = (
        dim_customer_df.groupBy(dim_customer_df.country.alias("customer_country"))
        .agg(
            F.countDistinct(dim_customer_df.customer_id).alias(
                "distinct_customer_count"
            )
        )
        .orderBy(F.desc("distinct_customer_count"))
    )
    save_report_to_mongodb(
        report_customer_distribution_by_country, "mart_customer_distribution_by_country"
    )

    # 2.3 Средний чек для каждого клиента
    report_avg_customer_order_value = (
        fact_sales_df.groupBy("customer_sk")
        .agg(
            (F.sum("sale_total_price") / F.countDistinct("sale_sk")).alias(
                "avg_transaction_value_per_customer"
            )
        )
        .join(dim_customer_df, "customer_sk")
        .select(
            dim_customer_df.customer_id.alias("business_customer_id"),
            dim_customer_df.first_name,
            dim_customer_df.last_name,
            "avg_transaction_value_per_customer",
        )
        .orderBy(F.desc("avg_transaction_value_per_customer"))
    )
    save_report_to_mongodb(
        report_avg_customer_order_value, "mart_avg_customer_order_value"
    )

    # --- Витрина продаж по времени ---

    # 3.1 Месячные и годовые тренды продаж
    sales_with_date_details_df = fact_sales_df.join(dim_date_df, "date_sk")

    report_monthly_sales_trends = (
        sales_with_date_details_df.groupBy(
            dim_date_df.year, dim_date_df.month, dim_date_df.month_name
        )
        .agg(
            F.sum("sale_total_price").alias("monthly_total_revenue"),
            F.sum("sale_quantity").alias("monthly_total_quantity_sold"),
        )
        .orderBy(dim_date_df.year, dim_date_df.month)
    )
    save_report_to_mongodb(report_monthly_sales_trends, "mart_monthly_sales_trends")

    report_yearly_sales_trends = (
        sales_with_date_details_df.groupBy(dim_date_df.year)
        .agg(
            F.sum("sale_total_price").alias("yearly_total_revenue"),
            F.sum("sale_quantity").alias("yearly_total_quantity_sold"),
        )
        .orderBy(dim_date_df.year)
    )
    save_report_to_mongodb(report_yearly_sales_trends, "mart_yearly_sales_trends")

    # 3.2 Сравнение выручки за разные периоды (MoM - Month over Month)
    window_spec_mom = Window.orderBy("year", "month")
    report_mom_revenue_comparison = (
        report_monthly_sales_trends.withColumn(
            "previous_month_revenue",
            F.lag("monthly_total_revenue", 1, 0).over(window_spec_mom),
        )
        .withColumn(
            "mom_revenue_change",
            (F.col("monthly_total_revenue") - F.col("previous_month_revenue")),
        )
        .withColumn(
            "mom_revenue_change_percent",
            F.when(
                F.col("previous_month_revenue") != 0,
                F.round(
                    (F.col("mom_revenue_change") / F.col("previous_month_revenue"))
                    * 100,
                    2,
                ),
            ).otherwise(None),
        )
        .select(
            "year",
            "month",
            "month_name",
            "monthly_total_revenue",
            "previous_month_revenue",
            "mom_revenue_change",
            "mom_revenue_change_percent",
        )
    )
    report_mom_revenue_comparison = report_mom_revenue_comparison.fillna(
        {
            "previous_month_revenue": 0.0,
            "mom_revenue_change": 0.0,
            "mom_revenue_change_percent": 0.0,
        }
    )
    save_report_to_mongodb(report_mom_revenue_comparison, "mart_mom_revenue_comparison")

    # 3.3 Средний размер заказа по месяцам
    report_avg_order_size_by_month = (
        sales_with_date_details_df.groupBy(
            dim_date_df.year, dim_date_df.month, dim_date_df.month_name
        )
        .agg(
            (F.sum("sale_total_price") / F.countDistinct("sale_sk")).alias(
                "avg_monthly_order_size"
            )
        )
        .orderBy(dim_date_df.year, dim_date_df.month)
    )
    save_report_to_mongodb(
        report_avg_order_size_by_month, "mart_avg_order_size_by_month"
    )

    # --- Витрина продаж по магазинам ---

    sales_with_store_details_df = fact_sales_df.join(dim_store_df, "store_sk")

    # 4.1 Топ-5 магазинов с наибольшей выручкой
    report_top_5_stores_by_revenue = (
        sales_with_store_details_df.groupBy(
            dim_store_df.name.alias("store_name"),
            dim_store_df.city,
            dim_store_df.country,
        )
        .agg(F.sum("sale_total_price").alias("store_total_revenue"))
        .orderBy(F.desc("store_total_revenue"))
        .limit(5)
    )
    save_report_to_mongodb(
        report_top_5_stores_by_revenue, "mart_top_5_stores_by_revenue"
    )

    # 4.2 Распределение продаж по городам и странам (магазинов)
    report_sales_by_store_location = (
        sales_with_store_details_df.groupBy(
            dim_store_df.city.alias("store_city"),
            dim_store_df.country.alias("store_country"),
        )
        .agg(
            F.sum("sale_total_price").alias("location_total_revenue"),
            F.sum("sale_quantity").alias("location_total_quantity_sold"),
        )
        .orderBy(F.desc("location_total_revenue"))
    )
    save_report_to_mongodb(
        report_sales_by_store_location, "mart_sales_by_store_location"
    )

    # 4.3 Средний чек для каждого магазина
    report_avg_store_order_value = (
        sales_with_store_details_df.groupBy(dim_store_df.name.alias("store_name"))
        .agg(
            (F.sum("sale_total_price") / F.countDistinct("sale_sk")).alias(
                "avg_transaction_value_per_store"
            )
        )
        .orderBy(F.desc("avg_transaction_value_per_store"))
    )
    save_report_to_mongodb(report_avg_store_order_value, "mart_avg_store_order_value")

    sales_with_supplier_details_df = fact_sales_df.join(dim_supplier_df, "supplier_sk")

    # 5.1 Топ-5 поставщиков с наибольшей выручкой (от продаж товаров этих поставщиков)
    report_top_5_suppliers_by_revenue = (
        sales_with_supplier_details_df.groupBy(
            dim_supplier_df.name.alias("supplier_name"),
            dim_supplier_df.country.alias("supplier_country"),
        )
        .agg(F.sum("sale_total_price").alias("supplier_generated_revenue"))
        .orderBy(F.desc("supplier_generated_revenue"))
        .limit(5)
    )
    save_report_to_mongodb(
        report_top_5_suppliers_by_revenue, "mart_top_5_suppliers_by_revenue"
    )

    # 5.2 Средняя цена товаров (transaction_unit_price из fact_sales) от каждого поставщика
    report_avg_product_price_by_supplier = (
        fact_sales_df.join(dim_product_df, "product_sk")
        .join(dim_supplier_df, "supplier_sk")
        .groupBy(dim_supplier_df.name.alias("supplier_name"))
        .agg(F.avg("transaction_unit_price").alias("avg_sold_unit_price_from_supplier"))
        .orderBy(F.desc("avg_sold_unit_price_from_supplier"))
    )
    save_report_to_mongodb(
        report_avg_product_price_by_supplier, "mart_avg_product_price_by_supplier"
    )

    # 5.3 Распределение продаж по странам поставщиков
    report_sales_by_supplier_country = (
        sales_with_supplier_details_df.groupBy(
            dim_supplier_df.country.alias("supplier_country")
        )
        .agg(
            F.sum("sale_total_price").alias("country_total_revenue"),
            F.sum("sale_quantity").alias("country_total_quantity_sold"),
        )
        .orderBy(F.desc("country_total_revenue"))
    )
    save_report_to_mongodb(
        report_sales_by_supplier_country, "mart_sales_by_supplier_country"
    )

    # --- Витрина качества продукции ---

    # 6.1 Продукты с наивысшим и наименьшим рейтингом (Топ-10 для каждого)
    report_highest_rated_products = (
        dim_product_df.select(
            dim_product_df.product_id.alias("business_product_id"),
            dim_product_df.name.alias("product_name"),
            dim_product_df.rating,
        )
        .orderBy(F.desc_nulls_last("rating"))
        .limit(10)
    )
    save_report_to_mongodb(report_highest_rated_products, "mart_highest_rated_products")

    report_lowest_rated_products = (
        dim_product_df.select(
            dim_product_df.product_id.alias("business_product_id"),
            dim_product_df.name.alias("product_name"),
            dim_product_df.rating,
        )
        .filter(F.col("rating").isNotNull())
        .orderBy(F.asc_nulls_first("rating"))
        .limit(10)
    )
    save_report_to_mongodb(report_lowest_rated_products, "mart_lowest_rated_products")

    # 6.2 Корреляция между рейтингом и объемом продаж
    product_sales_and_rating_df = (
        fact_sales_df.join(dim_product_df, "product_sk")
        .groupBy(
            dim_product_df.product_id.alias("business_product_id"),
            dim_product_df.name.alias("product_name"),
        )
        .agg(
            F.avg(dim_product_df.rating).alias("avg_product_rating"),
            F.sum(fact_sales_df.sale_quantity).alias("total_product_quantity_sold"),
        )
        .filter(
            F.col("avg_product_rating").isNotNull()
            & (F.col("total_product_quantity_sold").isNotNull())
        )
    )

    if product_sales_and_rating_df.count() > 1:
        correlation_value = product_sales_and_rating_df.stat.corr(
            "avg_product_rating", "total_product_quantity_sold"
        )
    else:
        correlation_value = None

    correlation_df = spark.createDataFrame(
        [(correlation_value if correlation_value is not None else float("nan"),)],
        ["rating_sales_volume_correlation_coeff"],
    )
    save_report_to_mongodb(correlation_df, "mart_rating_sales_correlation")

    # 6.3 Продукты с наибольшим количеством отзывов (Топ-10)
    report_top_reviewed_products = (
        dim_product_df.select(
            dim_product_df.product_id.alias("business_product_id"),
            dim_product_df.name.alias("product_name"),
            dim_product_df.reviews.alias("number_of_reviews"),
        )
        .orderBy(F.desc_nulls_last("number_of_reviews"))
        .limit(10)
    )
    save_report_to_mongodb(report_top_reviewed_products, "mart_top_reviewed_products")

    fact_sales_df.unpersist()
    dim_product_df.unpersist()
    dim_customer_df.unpersist()
    dim_date_df.unpersist()
    dim_store_df.unpersist()
    dim_supplier_df.unpersist()


if __name__ == "__main__":
    spark_session = initialize_spark_session(APP_NAME, POSTGRES_JDBC_JAR_PATH)
    try:
        generate_reports(spark_session)
    finally:
        spark_session.stop()
