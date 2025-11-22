# Высоконагруженные системы

## Лабораторная работа №2: BigDataSpark

```markdown
Выполнил:
- студент уч. группы М8О-209СВ
- Дрёмов Александр
```

# Отчёт к л.р. №2: BigDataSpark

## Инструкция по запуску:

```bash
docker compose up -d
```

## Загрузка данных из CSV:

```bash
# загрузка основного файла
docker exec -i postgres_db psql -U spark_user_name -d spark_db -c "\
COPY mock_data FROM '/input_data_mount/MOCK_DATA.csv' CSV HEADER;"

# загрузка mock-файлов
for i in {1..9}; do
  docker exec -i postgres_db psql -U spark_user_name -d spark_db -c "\
  COPY mock_data FROM '/input_data_mount/MOCK_DATA ($i).csv' CSV HEADER;"
done
```

**Проверка количества загруженных строк:**
```bash
# docker exec -i postgres_db psql -U spark_user_name -d spark_db -c "SELECT count(*) FROM mock_data;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -i postgres_db psql -U spark_user_name -d spark_db -c "SELECT count(*) FROM mock_data;"
 count 
-------
 10000
(1 row)
```

## ETL-spark процессы

### Staging -> Star Schema (PostgreSQL)

Скрипт: `spark_apps/postgres_to_star_schema.py`

Действие: Читает `mock_data`, нормализует данные, заполняет измерения (`dim_`) и факты (`fact_sales`).

```bash
docker exec -u root spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --jars /opt/spark/jars/postgresql-42.6.0.jar \
  /opt/spark-apps/postgres_to_star_schema.py
```

### Star Schema -> ClickHouse Reports

Скрипт: `spark_apps/star_to_clickhouse_reports.py`

Действие: Агрегирует данные из Star Schema и сохраняет витрины в ClickHouse.

```bash
docker exec -u root spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --jars /opt/spark/jars/postgresql-42.6.0.jar,/opt/spark/jars/clickhouse-0.4.6.jar \
  /opt/spark-apps/star_to_clickhouse_reports.py
```

### Star Schema -> MongoDB Reports

Скрипт: `spark_apps/star_to_mongodb_reports.py`

Действие: Агрегирует данные и сохраняет витрины в MongoDB.

Предварительно, сдедует установить pymongo в контейнере Spark (необходимо для работы скрипта):

```bash
docker exec -u root spark-master pip install pymongo
```

**Запуск Job:**

```bash
docker exec -u root spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --jars /opt/spark/jars/postgresql-42.6.0.jar,/opt/spark/jars/mongo-10.2.1.jar \
  /opt/spark-apps/star_to_mongodb_reports.py
```

## Проверка корректности загрузки mock-данных

### ClickHouse

**Проверка наличия таблиц и данных:**
```bash
# SHOW TABLES LIKE 'mart%';

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SHOW TABLES LIKE 'mart%';"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SHOW TABLES LIKE 'mart%';"
┌─name──────────────────────────────────┐
│ mart_avg_customer_order_value         │
│ mart_avg_order_size_by_month          │
│ mart_avg_product_price_by_supplier    │
│ mart_avg_store_order_value            │
│ mart_customer_distribution_by_country │
│ mart_highest_rated_products           │
│ mart_lowest_rated_products            │
│ mart_mom_revenue_comparison           │
│ mart_monthly_sales_trends             │
│ mart_product_feedback_summary         │
│ mart_rating_sales_correlation         │
│ mart_revenue_by_product_category      │
│ mart_sales_by_store_location          │
│ mart_sales_by_supplier_country        │
│ mart_top_10_customers_by_purchase     │
│ mart_top_10_selling_products          │
│ mart_top_5_stores_by_revenue          │
│ mart_top_5_suppliers_by_revenue       │
│ mart_top_reviewed_products            │
│ mart_yearly_sales_trends              │
└───────────────────────────────────────┘
```

**Пример выборки из витрины топ продуктов**
```bash
# SELECT * FROM mart_top_10_selling_products LIMIT 5;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_10_selling_products LIMIT 5;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_top_10_selling_products LIMIT 5;"
┌─business_product_id─┬─product_name─┬─product_category─┬─total_quantity_sold─┬─total_revenue_generated─┐
│                 881 │ Bird Cage    │ Food             │                  76 │                 1618.15 │
│                 790 │ Cat Toy      │ Cage             │                  77 │                 2325.62 │
│                 622 │ Bird Cage    │ Food             │                  77 │                 2185.49 │
│                 624 │ Bird Cage    │ Food             │                  77 │                 2621.96 │
│                 699 │ Bird Cage    │ Cage             │                  77 │                 2691.13 │
└─────────────────────┴──────────────┴──────────────────┴─────────────────────┴─────────────────────────┘
```

### MongoDB

**Список коллекций**
```bash
# docker exec -it mongodb_db mongosh reports --eval "db.getCollectionNames()"

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports --eval "db.getCollectionNames()"
[
  'mart_top_5_stores_by_revenue',
  'mart_yearly_sales_trends',
  'mart_product_feedback_summary',
  'mart_top_10_selling_products',
  'mart_sales_by_store_location',
  'mart_avg_customer_order_value',
  'mart_top_5_suppliers_by_revenue',
  'mart_customer_distribution_by_country',
  'mart_avg_order_size_by_month',
  'mart_monthly_sales_trends',
  'mart_rating_sales_correlation',
  'mart_lowest_rated_products',
  'mart_avg_store_order_value',
  'mart_top_reviewed_products',
  'mart_avg_product_price_by_supplier',
  'mart_revenue_by_product_category',
  'mart_top_10_customers_by_purchase',
  'mart_highest_rated_products',
  'mart_sales_by_supplier_country',
  'mart_mom_revenue_comparison'
]
```

**Пример документа из витрины топ продуктов**

```bash
# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_10_selling_products.find().limit(3).pretty()"

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports --eval "db.mart_top_10_selling_products.find().limit(3).pretty()"
[
  {
    _id: ObjectId('69201bdb972cebc1b5cca7ff'),
    business_product_id: 963,
    product_name: 'Dog Food',
    product_category: 'Food',
    total_quantity_sold: 84,
    total_revenue_generated: 2116.63
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca800'),
    business_product_id: 562,
    product_name: 'Bird Cage',
    product_category: 'Toy',
    total_quantity_sold: 84,
    total_revenue_generated: 2791.52
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca801'),
    business_product_id: 673,
    product_name: 'Dog Food',
    product_category: 'Cage',
    total_quantity_sold: 80,
    total_revenue_generated: 2113.29
  }
]
```

## Аналитические запросы к витринам данных (листинг)

### ClickHouse

#### ClickHouse: 1. Витрина продаж по продуктам

```bash
# -- Топ-10 самых продаваемых продуктов

# SELECT * FROM mart_top_10_selling_products;
# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_10_selling_products;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_10_selling_products;"
┌─business_product_id─┬─product_name─┬─product_category─┬─total_quantity_sold─┬─total_revenue_generated─┐
│                 881 │ Bird Cage    │ Food             │                  76 │                 1618.15 │
│                 790 │ Cat Toy      │ Cage             │                  77 │                 2325.62 │
│                 622 │ Bird Cage    │ Food             │                  77 │                 2185.49 │
│                 624 │ Bird Cage    │ Food             │                  77 │                 2621.96 │
│                 699 │ Bird Cage    │ Cage             │                  77 │                 2691.13 │
│                 392 │ Bird Cage    │ Cage             │                  78 │                 2809.37 │
│                 673 │ Dog Food     │ Cage             │                  80 │                 2113.29 │
│                 692 │ Cat Toy      │ Toy              │                  80 │                 2964.14 │
│                 963 │ Dog Food     │ Food             │                  84 │                 2116.63 │
│                 562 │ Bird Cage    │ Toy              │                  84 │                 2791.52 │
└─────────────────────┴──────────────┴──────────────────┴─────────────────────┴─────────────────────────┘
```

```bash
# -- Общая выручка по категориям продуктов

# SELECT * FROM mart_revenue_by_product_category;
# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_revenue_by_product_category;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_revenue_by_product_category;"
┌─product_category─┬─category_total_revenue─┐
│ Cage             │               835992.6 │
│ Food             │              838494.48 │
│ Toy              │              855365.04 │
└──────────────────┴────────────────────────┘
```

```bash
# -- Средний рейтинг и количество отзывов (пример первых 10)

# SELECT * FROM mart_product_feedback_summary LIMIT 10;
# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_product_feedback_summary LIMIT 10;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_product_feedback_summary LIMIT 10;"
┌─business_product_id─┬─product_name─┬─product_category─┬─average_rating─┬─number_of_reviews─┐
│                   1 │ Dog Food     │ Cage             │            3.3 │               903 │
│                   2 │ Bird Cage    │ Food             │            1.4 │                57 │
│                   3 │ Dog Food     │ Food             │            3.2 │               287 │
│                   4 │ Dog Food     │ Food             │            2.3 │               182 │
│                   5 │ Bird Cage    │ Toy              │            2.8 │               535 │
│                   6 │ Bird Cage    │ Food             │            4.1 │               924 │
│                   7 │ Cat Toy      │ Toy              │            2.6 │               881 │
│                   8 │ Bird Cage    │ Toy              │            2.2 │               600 │
│                   9 │ Bird Cage    │ Cage             │            1.6 │               194 │
│                  10 │ Dog Food     │ Cage             │            2.6 │               151 │
└─────────────────────┴──────────────┴──────────────────┴────────────────┴───────────────────┘
```

#### ClickHouse: 2. Витрина продаж по клиентам

**Топ-10 клиентов с наибольшей суммой покупок**

```bash
# SELECT * FROM mart_top_10_customers_by_purchase;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_10_customers_by_purchase;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_top_10_customers_by_purchase;"
┌─business_customer_id─┬─first_name─┬─last_name──┬─customer_country─┬─customer_total_purchases─┐
│                  997 │ Meyer      │ Blinder    │ Brazil           │                  3537.04 │
│                  406 │ Boony      │ Bitcheno   │ China            │                  3546.42 │
│                  767 │ Audrie     │ Samson     │ Pakistan         │                  3548.86 │
│                   74 │ Daphne     │ Bake       │ South Korea      │                   3571.1 │
│                   84 │ Dov        │ Stanton    │ Czech Republic   │                  3616.93 │
│                  795 │ Sarajane   │ Trulocke   │ Thailand         │                  3645.94 │
│                  269 │ Donnie     │ Kollaschek │ Costa Rica       │                  3682.52 │
│                  434 │ Amalle     │ Picknett   │ Indonesia        │                  3751.09 │
│                  779 │ Mercy      │ Antonomoli │ Laos             │                  3784.44 │
│                  611 │ Randolf    │ Rillatt    │ Brazil           │                  4005.98 │
└──────────────────────┴────────────┴────────────┴──────────────────┴──────────────────────────┘
```

**Распределение клиентов по странам**
```bash
# SELECT * FROM mart_customer_distribution_by_country;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_customer_distribution_by_country;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_customer_distribution_by_country;"
┌─customer_country─────────────────────────────┬─distinct_customer_count─┐
│ Afghanistan                                  │                       1 │
│ Aland Islands                                │                       1 │
│ Albania                                      │                       3 │
│ Angola                                       │                       1 │
│ Antigua and Barbuda                          │                       1 │
│ Argentina                                    │                       7 │
│ Armenia                                      │                       8 │
│ Bahamas                                      │                       1 │
│ Bangladesh                                   │                       4 │
│ Belarus                                      │                       4 │
# ---
# ...
# ---
│ Ukraine                                      │                      11 │
│ United Kingdom                               │                       2 │
│ United States                                │                      27 │
│ Uzbekistan                                   │                       2 │
│ Venezuela                                    │                       3 │
│ Vietnam                                      │                       8 │
│ Yemen                                        │                       3 │
│ Zambia                                       │                       1 │
└──────────────────────────────────────────────┴─────────────────────────┘
```

**Средний чек для каждого клиента (пример первых 10)**
```bash
# SELECT * FROM mart_avg_customer_order_value LIMIT 10;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_avg_customer_order_value LIMIT 10;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_avg_customer_order_value LIMIT 10;"
┌─business_customer_id─┬─first_name─┬─last_name──┬─avg_transaction_value_per_customer─┐
│                    1 │ Rourke     │ Rackley    │                            219.732 │
│                    2 │ Ainsley    │ Visick     │                            321.326 │
│                    3 │ Quill      │ Ellin      │                            168.372 │
│                    4 │ Mortimer   │ Fitzsimon  │                            248.531 │
│                    5 │ Darb       │ Scimonelli │                            190.319 │
│                    6 │ Frankie    │ Waycott    │                            312.767 │
│                    7 │ Karine     │ Radbourn   │                            322.346 │
│                    8 │ Maryrose   │ Comizzoli  │                            195.121 │
│                    9 │ Jeanine    │ Hume       │                            278.415 │
│                   10 │ Kaspar     │ Mort       │                            271.333 │
└──────────────────────┴────────────┴────────────┴────────────────────────────────────┘
```

#### ClickHouse: 3. Витрина продаж по времени

**Месячные тренды продаж**

```bash
# SELECT * FROM mart_monthly_sales_trends;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_monthly_sales_trends;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_monthly_sales_trends;"
┌─year─┬─month─┬─month_name─┬─monthly_total_revenue─┬─monthly_total_quantity_sold─┐
│ 2021 │     1 │ January    │             224158.54 │                        4856 │
│ 2021 │     2 │ February   │             192348.31 │                        4070 │
│ 2021 │     3 │ March      │              207282.2 │                        4561 │
│ 2021 │     4 │ April      │             206592.82 │                        4564 │
│ 2021 │     5 │ May        │             211764.86 │                        4451 │
│ 2021 │     6 │ June       │              215042.8 │                        4438 │
│ 2021 │     7 │ July       │             220496.51 │                        4750 │
│ 2021 │     8 │ August     │             221275.78 │                        4818 │
│ 2021 │     9 │ September  │             210623.43 │                        4507 │
│ 2021 │    10 │ October    │             228743.32 │                        4976 │
│ 2021 │    11 │ November   │             200154.69 │                        4297 │
│ 2021 │    12 │ December   │             191368.86 │                        4335 │
└──────┴───────┴────────────┴───────────────────────┴─────────────────────────────┘
```

**Годовые тренды продаж**
```bash
# SELECT * FROM mart_yearly_sales_trends;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_yearly_sales_trends;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_yearly_sales_trends;"
┌─year─┬─yearly_total_revenue─┬─yearly_total_quantity_sold─┐
│ 2021 │           2529852.12 │                      54623 │
└──────┴──────────────────────┴────────────────────────────┘
```

**Сравнение выручки (Month over Month)**
```bash
# SELECT * FROM mart_mom_revenue_comparison;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_mom_revenue_comparison;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_mom_revenue_comparison;"
┌─year─┬─month─┬─month_name─┬─monthly_total_revenue─┬─previous_month_revenue─┬─mom_revenue_change─┬─mom_revenue_change_percent─┐
│ 2021 │     1 │ January    │             224158.54 │                      0 │          224158.54 │                          0 │
│ 2021 │     2 │ February   │             192348.31 │              224158.54 │          -31810.23 │                     -14.19 │
│ 2021 │     3 │ March      │              207282.2 │              192348.31 │           14933.89 │                       7.76 │
│ 2021 │     4 │ April      │             206592.82 │               207282.2 │            -689.38 │                      -0.33 │
│ 2021 │     5 │ May        │             211764.86 │              206592.82 │            5172.04 │                        2.5 │
│ 2021 │     6 │ June       │              215042.8 │              211764.86 │            3277.94 │                       1.55 │
│ 2021 │     7 │ July       │             220496.51 │               215042.8 │            5453.71 │                       2.54 │
│ 2021 │     8 │ August     │             221275.78 │              220496.51 │             779.27 │                       0.35 │
│ 2021 │     9 │ September  │             210623.43 │              221275.78 │          -10652.35 │                      -4.81 │
│ 2021 │    10 │ October    │             228743.32 │              210623.43 │           18119.89 │                        8.6 │
│ 2021 │    11 │ November   │             200154.69 │              228743.32 │          -28588.63 │                      -12.5 │
│ 2021 │    12 │ December   │             191368.86 │              200154.69 │           -8785.83 │                      -4.39 │
└──────┴───────┴────────────┴───────────────────────┴────────────────────────┴────────────────────┴────────────────────────────┘
```

**Средний размер заказа по месяцам**
```bash
# SELECT * FROM mart_avg_order_size_by_month;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_avg_order_size_by_month;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_avg_order_size_by_month;"
┌─year─┬─month─┬─month_name─┬─avg_monthly_order_size─┐
│ 2021 │     1 │ January    │ 256.474302059496567506 │
│ 2021 │     2 │ February   │ 260.281880920162381597 │
│ 2021 │     3 │ March      │ 245.886358244365361803 │
│ 2021 │     4 │ April      │ 246.825352449223416965 │
│ 2021 │     5 │ May        │ 255.754661835748792271 │
│ 2021 │     6 │ June       │ 261.609245742092457421 │
│ 2021 │     7 │ July       │ 256.988939393939393939 │
│ 2021 │     8 │ August     │ 246.684258639910813824 │
│ 2021 │     9 │ September  │ 251.041036948748510131 │
│ 2021 │    10 │ October    │ 256.438699551569506726 │
│ 2021 │    11 │ November   │  249.88101123595505618 │
│ 2021 │    12 │ December   │ 248.530987012987012987 │
└──────┴───────┴────────────┴────────────────────────┘
```

#### ClickHouse: 4. Витрина продаж по магазинам

**Топ-5 магазинов с наибольшей выручкой**
```bash
# SELECT * FROM mart_top_5_stores_by_revenue;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_5_stores_by_revenue;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_top_5_stores_by_revenue;"
┌─store_name─┬─city───────┬─country─────┬─store_total_revenue─┐
│ Realcube   │ Sumenep    │ China       │            13700.77 │
│ Quinu      │ Zhiqu      │ New Zealand │            13952.88 │
│ Jayo       │ Wang Yang  │ China       │            13976.01 │
│ Quatz      │ Itumbiara  │ China       │            15176.64 │
│ Mynte      │ Slyudyanka │ Nigeria     │            15751.71 │
└────────────┴────────────┴─────────────┴─────────────────────┘
```

**Распределение продаж по локациям**
```bash
# SELECT * FROM mart_sales_by_store_location;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_sales_by_store_location;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_sales_by_store_location;"
┌─store_city────────────────┬─store_country────────────────────┬─location_total_revenue─┬─location_total_quantity_sold─┐
│ Huimin                    │ Afghanistan                      │               11235.31 │                          256 │
│ La Colorada               │ Albania                          │                6872.83 │                          135 │
│ Banjar Lalangpasek        │ Argentina                        │                6189.44 │                           88 │
│ Chavusy                   │ Argentina                        │                7120.04 │                          133 │
│ Kashar                    │ Argentina                        │                7274.61 │                          160 │
│ Kvartsitnyy               │ Argentina                        │                 4685.2 │                          111 │
│ Longsheng                 │ Argentina                        │                6556.65 │                          136 │
│ Si Satchanalai            │ Argentina                        │                6737.91 │                          206 │
# ---
# ...
# ---
│ Unquillo                  │ United States                    │                5548.35 │                          130 │
│ Reims                     │ Uzbekistan                       │                6824.76 │                          157 │
│ Šabac                     │ Venezuela                        │                4161.21 │                          126 │
│ Bogoria                   │ Vietnam                          │                7724.42 │                          161 │
│ Niujiang                  │ Vietnam                          │                4527.53 │                           79 │
│ Palaiomonástiron          │ Vietnam                          │                5032.07 │                          104 │
│ Guintubhan                │ Yemen                            │                 7055.5 │                          154 │
│ Parintins                 │ Yemen                            │                6162.18 │                          190 │
└───────────────────────────┴──────────────────────────────────┴────────────────────────┴──────────────────────────────┘
```

**Средний чек для каждого магазина**
```bash
# SELECT * FROM mart_avg_store_order_value;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_avg_store_order_value;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_avg_store_order_value;"
┌─store_name────┬─avg_transaction_value_per_store─┐
│ Abata         │          262.563928571428571429 │
│ Abatz         │          240.512592592592592593 │
│ Agimba        │                         233.372 │
│ Agivu         │          284.857058823529411765 │
│ Aibox         │          252.351904761904761905 │
│ Ailane        │                          282.15 │
│ Aimbo         │          264.427857142857142857 │
│ Aimbu         │          204.871153846153846154 │
│ Ainyx         │          313.378888888888888889 │
│ Aivee         │          233.807241379310344828 │
│ Avamba        │          231.592068965517241379 │
│ Avamm         │          262.628709677419354839 │
│ Avavee        │          258.337142857142857143 │
│ Avaveo        │          239.315925925925925926 │
│ Babbleblab    │                        243.4605 │
│ Babbleopia    │          243.198709677419354839 │
│ Babbleset     │          223.695357142857142857 │
# ---
# ...
# ---
│ Zoombeat      │          287.332142857142857143 │
│ Zoombox       │          286.645789473684210526 │
│ Zoomcast      │          224.547241379310344828 │
│ Zoomdog       │                         291.932 │
│ Zoomlounge    │          278.841153846153846154 │
│ Zoomzone      │          222.969523809523809524 │
│ Zoonder       │          185.971764705882352941 │
│ Zoonoodle     │          263.043636363636363636 │
│ Zooveo        │          285.126071428571428571 │
│ Zoovu         │          272.156111111111111111 │
│ Zooxo         │                         278.545 │
│ Zoozzy        │          243.838333333333333333 │
└───────────────┴─────────────────────────────────┘
```

#### ClickHouse: 5. Витрина продаж по поставщикам

```sql
-- Топ-5 поставщиков с наибольшей выручкой
SELECT * FROM mart_top_5_suppliers_by_revenue;
```

**Топ-5 поставщиков с наибольшей выручкой**
```bash
# SELECT * FROM mart_top_5_suppliers_by_revenue;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_5_suppliers_by_revenue;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_top_5_suppliers_by_revenue;"
┌─supplier_name─┬─supplier_country─┬─supplier_generated_revenue─┐
│ Jayo          │ Indonesia        │                   14409.04 │
│ Mynte         │ Brazil           │                   14784.34 │
│ Katz          │ Indonesia        │                   16372.18 │
│ Livetube      │ Indonesia        │                   17422.08 │
│ Wikizz        │ Portugal         │                   17729.73 │
└───────────────┴──────────────────┴────────────────────────────┘
```

**Средняя цена товаров от каждого поставщика**
```bash
# SELECT * FROM mart_avg_product_price_by_supplier;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_avg_product_price_by_supplier;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_avg_product_price_by_supplier;"
┌─supplier_name─┬─avg_sold_unit_price_from_supplier─┐
│ Abata         │         47.2507692307692307692308 │
│ Abatz         │                            51.185 │
│ Agimba        │         50.8603448275862068965517 │
│ Agivu         │         44.5668571428571428571429 │
│ Aibox         │         46.5046153846153846153846 │
│ Ailane        │         54.7317241379310344827586 │
│ Aimbo         │                             50.25 │
# ---
# ...
# ---
│ Zoonoodle     │         52.2129166666666666666667 │
│ Zooveo        │                        56.4509375 │
│ Zoovu         │         51.5382142857142857142857 │
│ Zooxo         │         47.5691428571428571428571 │
│ Zoozzy        │         58.0125806451612903225806 │
└───────────────┴───────────────────────────────────┘
```

```sql
-- Распределение продаж по странам поставщиков
SELECT * FROM mart_sales_by_supplier_country;
```

**Распределение продаж по странам поставщиков**
```bash
# SELECT * FROM mart_sales_by_supplier_country;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_sales_by_supplier_country;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_sales_by_supplier_country;"
┌─supplier_country─────────────────┬─country_total_revenue─┬─country_total_quantity_sold─┐
│ Afghanistan                      │               6424.53 │                         108 │
│ Argentina                        │              25840.59 │                         530 │
│ Armenia                          │                 18382 │                         409 │
│ Azerbaijan                       │               5382.18 │                         119 │
│ Bangladesh                       │              11654.52 │                         308 │
│ Belarus                          │              29866.63 │                         528 │
│ Botswana                         │               5251.49 │                         104 │
│ Brazil                           │             153864.48 │                        3383 │
# ---
# ...
# ---
│ Venezuela                        │              12022.94 │                         259 │
│ Vietnam                          │              25793.17 │                         571 │
│ Yemen                            │               16356.4 │                         368 │
└──────────────────────────────────┴───────────────────────┴─────────────────────────────┘
```

#### ClickHouse: 6. Витрина качества продукции

**Продукты с наивысшим рейтингом**
```bash
# SELECT * FROM mart_highest_rated_products;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_highest_rated_products;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_highest_rated_products;"
┌─business_product_id─┬─product_name─┬─rating─┐
│                 505 │ Dog Food     │      5 │
│                 914 │ Cat Toy      │      5 │
│                 524 │ Cat Toy      │      5 │
│                 408 │ Dog Food     │      5 │
│                 548 │ Dog Food     │      5 │
│                 711 │ Dog Food     │      5 │
│                 727 │ Cat Toy      │      5 │
│                 177 │ Dog Food     │      5 │
│                 773 │ Cat Toy      │      5 │
│                 684 │ Bird Cage    │      5 │
└─────────────────────┴──────────────┴────────┘
```

**Продукты с наименьшим рейтингом**
```bash
# SELECT * FROM mart_lowest_rated_products;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_lowest_rated_products;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_lowest_rated_products;"
┌─business_product_id─┬─product_name─┬─rating─┐
│                 137 │ Cat Toy      │      1 │
│                 240 │ Cat Toy      │      1 │
│                  62 │ Dog Food     │      1 │
│                 183 │ Dog Food     │      1 │
│                 227 │ Dog Food     │      1 │
│                 471 │ Cat Toy      │      1 │
│                 622 │ Bird Cage    │      1 │
│                 894 │ Cat Toy      │      1 │
│                 902 │ Bird Cage    │      1 │
│                 904 │ Cat Toy      │      1 │
└─────────────────────┴──────────────┴────────┘
```

**Корреляция между рейтингом и объемом продаж**
```bash
# SELECT * FROM mart_rating_sales_correlation;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_rating_sales_correlation;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_rating_sales_correlation;"
┌─rating_sales_volume_correlation_coeff─┐
│                  0.015170265597630222 │
└───────────────────────────────────────┘
```

**Продукты с наибольшим количеством отзывов**
```bash
# SELECT * FROM mart_top_reviewed_products;

# docker exec -it clickhouse_db clickhouse-client --format PrettyCompactMonoBlock --query "SELECT * FROM mart_top_reviewed_products;"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it clickhouse_db clickhouse-client \
  --format PrettyCompactMonoBlock \
  --query "SELECT * FROM mart_top_reviewed_products;"
┌─business_product_id─┬─product_name─┬─number_of_reviews─┐
│                  93 │ Dog Food     │               995 │
│                 489 │ Bird Cage    │               996 │
│                 246 │ Cat Toy      │               997 │
│                 573 │ Bird Cage    │               997 │
│                 438 │ Bird Cage    │               999 │
│                 568 │ Dog Food     │               999 │
│                 596 │ Cat Toy      │               999 │
│                 658 │ Cat Toy      │               999 │
│                  30 │ Cat Toy      │              1000 │
│                 696 │ Cat Toy      │              1000 │
└─────────────────────┴──────────────┴───────────────────┘
```

### 6.2 MongoDB (MQL)

Для выполнения запросов используйте `mongosh` внутри контейнера:
`docker exec -it mongodb_db mongosh reports`

#### MongoDB: 1. Витрина продаж по продуктам

**Топ-10 самых продаваемых продуктов**
```bash
# db.mart_top_10_selling_products.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_10_selling_products.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_top_10_selling_products.find().pretty();"
[
  {
    _id: ObjectId('69201bdb972cebc1b5cca7ff'),
    business_product_id: 963,
    product_name: 'Dog Food',
    product_category: 'Food',
    total_quantity_sold: 84,
    total_revenue_generated: 2116.63
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca800'),
    business_product_id: 562,
    product_name: 'Bird Cage',
    product_category: 'Toy',
    total_quantity_sold: 84,
    total_revenue_generated: 2791.52
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca801'),
    business_product_id: 673,
    product_name: 'Dog Food',
    product_category: 'Cage',
    total_quantity_sold: 80,
    total_revenue_generated: 2113.29
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca802'),
    business_product_id: 692,
    product_name: 'Cat Toy',
    product_category: 'Toy',
    total_quantity_sold: 80,
    total_revenue_generated: 2964.14
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca803'),
    business_product_id: 392,
    product_name: 'Bird Cage',
    product_category: 'Cage',
    total_quantity_sold: 78,
    total_revenue_generated: 2809.37
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca804'),
    business_product_id: 790,
    product_name: 'Cat Toy',
    product_category: 'Cage',
    total_quantity_sold: 77,
    total_revenue_generated: 2325.62
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca805'),
    business_product_id: 622,
    product_name: 'Bird Cage',
    product_category: 'Food',
    total_quantity_sold: 77,
    total_revenue_generated: 2185.49
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca806'),
    business_product_id: 624,
    product_name: 'Bird Cage',
    product_category: 'Food',
    total_quantity_sold: 77,
    total_revenue_generated: 2621.96
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca807'),
    business_product_id: 699,
    product_name: 'Bird Cage',
    product_category: 'Cage',
    total_quantity_sold: 77,
    total_revenue_generated: 2691.13
  },
  {
    _id: ObjectId('69201bdb972cebc1b5cca808'),
    business_product_id: 881,
    product_name: 'Bird Cage',
    product_category: 'Food',
    total_quantity_sold: 76,
    total_revenue_generated: 1618.15
  }
]
```

**Общая выручка по категориям продуктов**
```bash
# db.mart_revenue_by_product_category.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_revenue_by_product_category.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_revenue_by_product_category.find().pretty();"
[
  {
    _id: ObjectId('69201bdc972cebc1b5cca80a'),
    product_category: 'Toy',
    category_total_revenue: 855365.04
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca80b'),
    product_category: 'Food',
    category_total_revenue: 838494.48
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca80c'),
    product_category: 'Cage',
    category_total_revenue: 835992.6
  }
]
```

**Средний рейтинг и количество отзывов**
```bash
# db.mart_product_feedback_summary.find().limit(5).pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_product_feedback_summary.find().limit(5).pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_product_feedback_summary.find().limit(5).pretty();"
[
  {
    _id: ObjectId('69201bdc972cebc1b5cca80e'),
    business_product_id: 30,
    product_name: 'Cat Toy',
    product_category: 'Cage',
    average_rating: 4.6,
    number_of_reviews: 1000
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca80f'),
    business_product_id: 696,
    product_name: 'Cat Toy',
    product_category: 'Toy',
    average_rating: 4.7,
    number_of_reviews: 1000
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca810'),
    business_product_id: 438,
    product_name: 'Bird Cage',
    product_category: 'Cage',
    average_rating: 2.6,
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca811'),
    business_product_id: 568,
    product_name: 'Dog Food',
    product_category: 'Cage',
    average_rating: 3.9,
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201bdc972cebc1b5cca812'),
    business_product_id: 596,
    product_name: 'Cat Toy',
    product_category: 'Food',
    average_rating: 3.9,
    number_of_reviews: 999
  }
]
```

#### MongoDB: 2. Витрина продаж по клиентам

**Топ-10 клиентов с наибольшей суммой покупок**
```bash
# db.mart_top_10_customers_by_purchase.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_10_customers_by_purchase.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_top_10_customers_by_purchase.find().pretty();"
[
  {
    _id: ObjectId('69201bdd972cebc1b5ccabf7'),
    business_customer_id: 611,
    first_name: 'Randolf',
    last_name: 'Rillatt',
    customer_country: 'Brazil',
    customer_total_purchases: 4005.98
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabf8'),
    business_customer_id: 779,
    first_name: 'Mercy',
    last_name: 'Antonomoli',
    customer_country: 'Laos',
    customer_total_purchases: 3784.44
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabf9'),
    business_customer_id: 434,
    first_name: 'Amalle',
    last_name: 'Picknett',
    customer_country: 'Indonesia',
    customer_total_purchases: 3751.09
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabfa'),
    business_customer_id: 269,
    first_name: 'Donnie',
    last_name: 'Kollaschek',
    customer_country: 'Costa Rica',
    customer_total_purchases: 3682.52
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabfb'),
    business_customer_id: 795,
    first_name: 'Sarajane',
    last_name: 'Trulocke',
    customer_country: 'Thailand',
    customer_total_purchases: 3645.94
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabfc'),
    business_customer_id: 84,
    first_name: 'Dov',
    last_name: 'Stanton',
    customer_country: 'Czech Republic',
    customer_total_purchases: 3616.93
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabfd'),
    business_customer_id: 74,
    first_name: 'Daphne',
    last_name: 'Bake',
    customer_country: 'South Korea',
    customer_total_purchases: 3571.1
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabfe'),
    business_customer_id: 767,
    first_name: 'Audrie',
    last_name: 'Samson',
    customer_country: 'Pakistan',
    customer_total_purchases: 3548.86
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccabff'),
    business_customer_id: 406,
    first_name: 'Boony',
    last_name: 'Bitcheno',
    customer_country: 'China',
    customer_total_purchases: 3546.42
  },
  {
    _id: ObjectId('69201bdd972cebc1b5ccac00'),
    business_customer_id: 997,
    first_name: 'Meyer',
    last_name: 'Blinder',
    customer_country: 'Brazil',
    customer_total_purchases: 3537.04
  }
]
```

**Распределение клиентов по странам**
```bash
# db.mart_customer_distribution_by_country.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_customer_distribution_by_country.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_customer_distribution_by_country.find().pretty();"
[
  {
    _id: ObjectId('69201bde972cebc1b5ccac02'),
    customer_country: 'China',
    distinct_customer_count: 178
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac03'),
    customer_country: 'Indonesia',
    distinct_customer_count: 107
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac04'),
    customer_country: 'Russia',
    distinct_customer_count: 73
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac05'),
    customer_country: 'Brazil',
    distinct_customer_count: 53
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac06'),
    customer_country: 'Philippines',
    distinct_customer_count: 50
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac07'),
    customer_country: 'Poland',
    distinct_customer_count: 33
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac08'),
    customer_country: 'France',
    distinct_customer_count: 27
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac09'),
    customer_country: 'United States',
    distinct_customer_count: 27
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0a'),
    customer_country: 'Japan',
    distinct_customer_count: 26
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0b'),
    customer_country: 'Portugal',
    distinct_customer_count: 26
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0c'),
    customer_country: 'Sweden',
    distinct_customer_count: 17
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0d'),
    customer_country: 'Czech Republic',
    distinct_customer_count: 17
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0e'),
    customer_country: 'Colombia',
    distinct_customer_count: 14
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac0f'),
    customer_country: 'Thailand',
    distinct_customer_count: 13
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac10'),
    customer_country: 'Canada',
    distinct_customer_count: 12
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac11'),
    customer_country: 'Greece',
    distinct_customer_count: 11
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac12'),
    customer_country: 'Nigeria',
    distinct_customer_count: 11
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac13'),
    customer_country: 'Ukraine',
    distinct_customer_count: 11
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac14'),
    customer_country: 'Peru',
    distinct_customer_count: 10
  },
  {
    _id: ObjectId('69201bde972cebc1b5ccac15'),
    customer_country: 'Croatia',
    distinct_customer_count: 9
  }
]
Type "it" for more
```

**Средний чек для каждого клиента**
```bash
# db.mart_avg_customer_order_value.find().limit(5).pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_avg_customer_order_value.find().limit(5).pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_avg_customer_order_value.find().limit(5).pretty();"
[
  {
    _id: ObjectId('69201bdf972cebc1b5ccac7f'),
    business_customer_id: 611,
    first_name: 'Randolf',
    last_name: 'Rillatt',
    avg_transaction_value_per_customer: 400.598
  },
  {
    _id: ObjectId('69201bdf972cebc1b5ccac80'),
    business_customer_id: 779,
    first_name: 'Mercy',
    last_name: 'Antonomoli',
    avg_transaction_value_per_customer: 378.444
  },
  {
    _id: ObjectId('69201bdf972cebc1b5ccac81'),
    business_customer_id: 434,
    first_name: 'Amalle',
    last_name: 'Picknett',
    avg_transaction_value_per_customer: 375.109
  },
  {
    _id: ObjectId('69201bdf972cebc1b5ccac82'),
    business_customer_id: 269,
    first_name: 'Donnie',
    last_name: 'Kollaschek',
    avg_transaction_value_per_customer: 368.252
  },
  {
    _id: ObjectId('69201bdf972cebc1b5ccac83'),
    business_customer_id: 795,
    first_name: 'Sarajane',
    last_name: 'Trulocke',
    avg_transaction_value_per_customer: 364.594
  }
]
```

#### MongoDB: 3. Витрина продаж по времени

**Месячные тренды продаж**
```bash
# db.mart_monthly_sales_trends.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_monthly_sales_trends.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_monthly_sales_trends.find().pretty();"
[
  {
    _id: ObjectId('69201be0972cebc1b5ccb068'),
    year: 2021,
    month: 1,
    month_name: 'January',
    monthly_total_revenue: 224158.54,
    monthly_total_quantity_sold: 4856
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb069'),
    year: 2021,
    month: 2,
    month_name: 'February',
    monthly_total_revenue: 192348.31,
    monthly_total_quantity_sold: 4070
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06a'),
    year: 2021,
    month: 3,
    month_name: 'March',
    monthly_total_revenue: 207282.2,
    monthly_total_quantity_sold: 4561
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06b'),
    year: 2021,
    month: 4,
    month_name: 'April',
    monthly_total_revenue: 206592.82,
    monthly_total_quantity_sold: 4564
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06c'),
    year: 2021,
    month: 5,
    month_name: 'May',
    monthly_total_revenue: 211764.86,
    monthly_total_quantity_sold: 4451
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06d'),
    year: 2021,
    month: 6,
    month_name: 'June',
    monthly_total_revenue: 215042.8,
    monthly_total_quantity_sold: 4438
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06e'),
    year: 2021,
    month: 7,
    month_name: 'July',
    monthly_total_revenue: 220496.51,
    monthly_total_quantity_sold: 4750
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb06f'),
    year: 2021,
    month: 8,
    month_name: 'August',
    monthly_total_revenue: 221275.78,
    monthly_total_quantity_sold: 4818
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb070'),
    year: 2021,
    month: 9,
    month_name: 'September',
    monthly_total_revenue: 210623.43,
    monthly_total_quantity_sold: 4507
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb071'),
    year: 2021,
    month: 10,
    month_name: 'October',
    monthly_total_revenue: 228743.32,
    monthly_total_quantity_sold: 4976
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb072'),
    year: 2021,
    month: 11,
    month_name: 'November',
    monthly_total_revenue: 200154.69,
    monthly_total_quantity_sold: 4297
  },
  {
    _id: ObjectId('69201be0972cebc1b5ccb073'),
    year: 2021,
    month: 12,
    month_name: 'December',
    monthly_total_revenue: 191368.86,
    monthly_total_quantity_sold: 4335
  }
]
```

**Годовые тренды продаж**
```bash
# db.mart_yearly_sales_trends.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_yearly_sales_trends.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_yearly_sales_trends.find().pretty();"
[
  {
    _id: ObjectId('69201be0972cebc1b5ccb075'),
    year: 2021,
    yearly_total_revenue: 2529852.12,
    yearly_total_quantity_sold: 54623
  }
]
```

**Сравнение выручки (Month over Month)**
```bash
# db.mart_mom_revenue_comparison.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_mom_revenue_comparison.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_mom_revenue_comparison.find().pretty();"
[
  {
    _id: ObjectId('69201be1972cebc1b5ccb077'),
    year: 2021,
    month: 1,
    month_name: 'January',
    monthly_total_revenue: 224158.54,
    previous_month_revenue: 0,
    mom_revenue_change: 224158.54,
    mom_revenue_change_percent: 0
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb078'),
    year: 2021,
    month: 2,
    month_name: 'February',
    monthly_total_revenue: 192348.31,
    previous_month_revenue: 224158.54,
    mom_revenue_change: -31810.23,
    mom_revenue_change_percent: -14.19
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb079'),
    year: 2021,
    month: 3,
    month_name: 'March',
    monthly_total_revenue: 207282.2,
    previous_month_revenue: 192348.31,
    mom_revenue_change: 14933.89,
    mom_revenue_change_percent: 7.76
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07a'),
    year: 2021,
    month: 4,
    month_name: 'April',
    monthly_total_revenue: 206592.82,
    previous_month_revenue: 207282.2,
    mom_revenue_change: -689.38,
    mom_revenue_change_percent: -0.33
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07b'),
    year: 2021,
    month: 5,
    month_name: 'May',
    monthly_total_revenue: 211764.86,
    previous_month_revenue: 206592.82,
    mom_revenue_change: 5172.04,
    mom_revenue_change_percent: 2.5
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07c'),
    year: 2021,
    month: 6,
    month_name: 'June',
    monthly_total_revenue: 215042.8,
    previous_month_revenue: 211764.86,
    mom_revenue_change: 3277.94,
    mom_revenue_change_percent: 1.55
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07d'),
    year: 2021,
    month: 7,
    month_name: 'July',
    monthly_total_revenue: 220496.51,
    previous_month_revenue: 215042.8,
    mom_revenue_change: 5453.71,
    mom_revenue_change_percent: 2.54
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07e'),
    year: 2021,
    month: 8,
    month_name: 'August',
    monthly_total_revenue: 221275.78,
    previous_month_revenue: 220496.51,
    mom_revenue_change: 779.27,
    mom_revenue_change_percent: 0.35
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb07f'),
    year: 2021,
    month: 9,
    month_name: 'September',
    monthly_total_revenue: 210623.43,
    previous_month_revenue: 221275.78,
    mom_revenue_change: -10652.35,
    mom_revenue_change_percent: -4.81
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb080'),
    year: 2021,
    month: 10,
    month_name: 'October',
    monthly_total_revenue: 228743.32,
    previous_month_revenue: 210623.43,
    mom_revenue_change: 18119.89,
    mom_revenue_change_percent: 8.6
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb081'),
    year: 2021,
    month: 11,
    month_name: 'November',
    monthly_total_revenue: 200154.69,
    previous_month_revenue: 228743.32,
    mom_revenue_change: -28588.63,
    mom_revenue_change_percent: -12.5
  },
  {
    _id: ObjectId('69201be1972cebc1b5ccb082'),
    year: 2021,
    month: 12,
    month_name: 'December',
    monthly_total_revenue: 191368.86,
    previous_month_revenue: 200154.69,
    mom_revenue_change: -8785.83,
    mom_revenue_change_percent: -4.39
  }
]
```

**Средний размер заказа по месяцам**
```bash
# db.mart_avg_order_size_by_month.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_avg_order_size_by_month.
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_avg_order_size_by_month.find().pretty();"
[
  {
    _id: ObjectId('69201be2972cebc1b5ccb084'),
    year: 2021,
    month: 1,
    month_name: 'January',
    avg_monthly_order_size: 256.47430205949655
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb085'),
    year: 2021,
    month: 2,
    month_name: 'February',
    avg_monthly_order_size: 260.2818809201624
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb086'),
    year: 2021,
    month: 3,
    month_name: 'March',
    avg_monthly_order_size: 245.88635824436537
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb087'),
    year: 2021,
    month: 4,
    month_name: 'April',
    avg_monthly_order_size: 246.82535244922343
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb088'),
    year: 2021,
    month: 5,
    month_name: 'May',
    avg_monthly_order_size: 255.7546618357488
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb089'),
    year: 2021,
    month: 6,
    month_name: 'June',
    avg_monthly_order_size: 261.60924574209247
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08a'),
    year: 2021,
    month: 7,
    month_name: 'July',
    avg_monthly_order_size: 256.9889393939394
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08b'),
    year: 2021,
    month: 8,
    month_name: 'August',
    avg_monthly_order_size: 246.6842586399108
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08c'),
    year: 2021,
    month: 9,
    month_name: 'September',
    avg_monthly_order_size: 251.0410369487485
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08d'),
    year: 2021,
    month: 10,
    month_name: 'October',
    avg_monthly_order_size: 256.4386995515695
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08e'),
    year: 2021,
    month: 11,
    month_name: 'November',
    avg_monthly_order_size: 249.88101123595504
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb08f'),
    year: 2021,
    month: 12,
    month_name: 'December',
    avg_monthly_order_size: 248.53098701298703
  }
]
```

#### MongoDB: 4. Витрина продаж по магазинам

**Топ-5 магазинов с наибольшей выручкой**
```bash
# db.mart_top_5_stores_by_revenue.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_5_stores_by_revenue.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_top_5_stores_by_revenue.find().pretty();"
[
  {
    _id: ObjectId('69201be2972cebc1b5ccb091'),
    store_name: 'Mynte',
    city: 'Slyudyanka',
    country: 'Nigeria',
    store_total_revenue: 15751.71
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb092'),
    store_name: 'Quatz',
    city: 'Itumbiara',
    country: 'China',
    store_total_revenue: 15176.64
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb093'),
    store_name: 'Jayo',
    city: 'Wang Yang',
    country: 'China',
    store_total_revenue: 13976.01
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb094'),
    store_name: 'Quinu',
    city: 'Zhiqu',
    country: 'New Zealand',
    store_total_revenue: 13952.88
  },
  {
    _id: ObjectId('69201be2972cebc1b5ccb095'),
    store_name: 'Realcube',
    city: 'Sumenep',
    country: 'China',
    store_total_revenue: 13700.77
  }
]
```

**Распределение продаж по локациям**
```bash
# db.mart_sales_by_store_location.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_sales_by_store_location.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_sales_by_store_location.find().pretty();"
[
  {
    _id: ObjectId('69201be3972cebc1b5ccb097'),
    store_city: 'Slyudyanka',
    store_country: 'Nigeria',
    location_total_revenue: 15751.71,
    location_total_quantity_sold: 317
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb098'),
    store_city: 'Itumbiara',
    store_country: 'China',
    location_total_revenue: 15176.64,
    location_total_quantity_sold: 342
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb099'),
    store_city: 'Wang Yang',
    store_country: 'China',
    location_total_revenue: 13976.01,
    location_total_quantity_sold: 273
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09a'),
    store_city: 'Zhiqu',
    store_country: 'New Zealand',
    location_total_revenue: 13952.88,
    location_total_quantity_sold: 273
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09b'),
    store_city: 'Sumenep',
    store_country: 'China',
    location_total_revenue: 13700.77,
    location_total_quantity_sold: 274
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09c'),
    store_city: 'El Pao',
    store_country: 'Indonesia',
    location_total_revenue: 12995.91,
    location_total_quantity_sold: 256
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09d'),
    store_city: 'Sumenep',
    store_country: 'Brazil',
    location_total_revenue: 12905.71,
    location_total_quantity_sold: 287
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09e'),
    store_city: 'Faruka',
    store_country: 'Mongolia',
    location_total_revenue: 12731.63,
    location_total_quantity_sold: 286
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb09f'),
    store_city: 'Grimstad',
    store_country: 'Russia',
    location_total_revenue: 12068.16,
    location_total_quantity_sold: 260
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a0'),
    store_city: 'Barbacoas',
    store_country: 'China',
    location_total_revenue: 11245.14,
    location_total_quantity_sold: 268
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a1'),
    store_city: 'Huimin',
    store_country: 'Afghanistan',
    location_total_revenue: 11235.31,
    location_total_quantity_sold: 256
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a2'),
    store_city: 'Corail',
    store_country: 'Greece',
    location_total_revenue: 11200.97,
    location_total_quantity_sold: 231
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a3'),
    store_city: 'São Sebastião do Caí',
    store_country: 'Czech Republic',
    location_total_revenue: 11142.46,
    location_total_quantity_sold: 295
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a4'),
    store_city: 'Buenaventura',
    store_country: 'Indonesia',
    location_total_revenue: 11086.34,
    location_total_quantity_sold: 227
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a5'),
    store_city: 'Al Ghāriyah',
    store_country: 'China',
    location_total_revenue: 11074.25,
    location_total_quantity_sold: 228
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a6'),
    store_city: 'Kozmice',
    store_country: 'Indonesia',
    location_total_revenue: 10967.6,
    location_total_quantity_sold: 277
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a7'),
    store_city: 'Jinggongqiao',
    store_country: 'Bosnia and Herzegovina',
    location_total_revenue: 10564.83,
    location_total_quantity_sold: 212
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a8'),
    store_city: 'Ylitornio',
    store_country: 'Russia',
    location_total_revenue: 10167.03,
    location_total_quantity_sold: 225
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0a9'),
    store_city: 'Ust’-Isha',
    store_country: 'Poland',
    location_total_revenue: 10135.9,
    location_total_quantity_sold: 150
  },
  {
    _id: ObjectId('69201be3972cebc1b5ccb0aa'),
    store_city: 'Wolomoni',
    store_country: 'France',
    location_total_revenue: 9941.86,
    location_total_quantity_sold: 218
  }
]
Type "it" for more
```

**Средний чек для каждого магазина**
```bash
# db.mart_avg_store_order_value.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_avg_store_order_value.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_avg_store_order_value.find().pretty();"
[
  {
    _id: ObjectId('69201be4972cebc1b5ccb217'),
    store_name: 'Brightbean',
    avg_transaction_value_per_store: 335.68954545454545
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb218'),
    store_name: 'Eamia',
    avg_transaction_value_per_store: 319.26862068965517
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb219'),
    store_name: 'Youopia',
    avg_transaction_value_per_store: 316.746875
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21a'),
    store_name: 'Ainyx',
    avg_transaction_value_per_store: 313.37888888888887
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21b'),
    store_name: 'Lajo',
    avg_transaction_value_per_store: 311.46838709677417
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21c'),
    store_name: 'Skinte',
    avg_transaction_value_per_store: 309.6824137931034
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21d'),
    store_name: 'Fivespan',
    avg_transaction_value_per_store: 308.13615384615383
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21e'),
    store_name: 'Realmix',
    avg_transaction_value_per_store: 305.1526086956522
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb21f'),
    store_name: 'Flashset',
    avg_transaction_value_per_store: 304.02032258064514
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb220'),
    store_name: 'Mudo',
    avg_transaction_value_per_store: 302.7925
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb221'),
    store_name: 'Riffpath',
    avg_transaction_value_per_store: 302.05642857142857
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb222'),
    store_name: 'Kare',
    avg_transaction_value_per_store: 301.134347826087
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb223'),
    store_name: 'Gigazoom',
    avg_transaction_value_per_store: 298.94586206896554
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb224'),
    store_name: 'Yacero',
    avg_transaction_value_per_store: 298.0529411764706
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb225'),
    store_name: 'Centidel',
    avg_transaction_value_per_store: 296.55034482758623
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb226'),
    store_name: 'Realblab',
    avg_transaction_value_per_store: 296.0703846153846
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb227'),
    store_name: 'Oozz',
    avg_transaction_value_per_store: 296.06041666666664
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb228'),
    store_name: 'Vidoo',
    avg_transaction_value_per_store: 294.25625
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb229'),
    store_name: 'Muxo',
    avg_transaction_value_per_store: 293.2908
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb22a'),
    store_name: 'Twitterbridge',
    avg_transaction_value_per_store: 292.1404
  }
]
Type "it" for more
```

#### MongoDB: 5. Витрина продаж по поставщикам

**Топ-5 поставщиков с наибольшей выручкой**
```bash
# db.mart_top_5_suppliers_by_revenue.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_5_suppliers_by_revenue.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_top_5_suppliers_by_revenue.find().pretty();"
[
  {
    _id: ObjectId('69201be4972cebc1b5ccb397'),
    supplier_name: 'Wikizz',
    supplier_country: 'Portugal',
    supplier_generated_revenue: 17729.73
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb398'),
    supplier_name: 'Livetube',
    supplier_country: 'Indonesia',
    supplier_generated_revenue: 17422.08
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb399'),
    supplier_name: 'Katz',
    supplier_country: 'Indonesia',
    supplier_generated_revenue: 16372.18
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb39a'),
    supplier_name: 'Mynte',
    supplier_country: 'Brazil',
    supplier_generated_revenue: 14784.34
  },
  {
    _id: ObjectId('69201be4972cebc1b5ccb39b'),
    supplier_name: 'Jayo',
    supplier_country: 'Indonesia',
    supplier_generated_revenue: 14409.04
  }
]
```

**Средняя цена товаров от каждого поставщика**
```bash
# db.mart_avg_product_price_by_supplier.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_avg_product_price_by_supplier.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports --eval "db.mart_avg_product_price_by_supplier.find().pretty();"
[
  {
    _id: ObjectId('69201be5972cebc1b5ccb39d'),
    supplier_name: 'Aivee',
    avg_sold_unit_price_from_supplier: 73.1204347826087
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb39e'),
    supplier_name: 'Gabtune',
    avg_sold_unit_price_from_supplier: 68.60214285714285
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb39f'),
    supplier_name: 'Realbridge',
    avg_sold_unit_price_from_supplier: 68.10181818181819
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a0'),
    supplier_name: 'Camimbo',
    avg_sold_unit_price_from_supplier: 67.26842105263158
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a1'),
    supplier_name: 'Topiczoom',
    avg_sold_unit_price_from_supplier: 64.39370370370371
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a2'),
    supplier_name: 'Avavee',
    avg_sold_unit_price_from_supplier: 64.14625
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a3'),
    supplier_name: 'Yodo',
    avg_sold_unit_price_from_supplier: 63.6232
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a4'),
    supplier_name: 'Quamba',
    avg_sold_unit_price_from_supplier: 63.481904761904765
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a5'),
    supplier_name: 'Kamba',
    avg_sold_unit_price_from_supplier: 62.7492
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a6'),
    supplier_name: 'Devify',
    avg_sold_unit_price_from_supplier: 61.545
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a7'),
    supplier_name: 'Gabcube',
    avg_sold_unit_price_from_supplier: 61.31173913043478
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a8'),
    supplier_name: 'Tagcat',
    avg_sold_unit_price_from_supplier: 61.05761904761905
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3a9'),
    supplier_name: 'Bubbletube',
    avg_sold_unit_price_from_supplier: 61.0565
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3aa'),
    supplier_name: 'Brainbox',
    avg_sold_unit_price_from_supplier: 60.97304347826087
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3ab'),
    supplier_name: 'Roodel',
    avg_sold_unit_price_from_supplier: 60.879
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3ac'),
    supplier_name: 'Snaptags',
    avg_sold_unit_price_from_supplier: 60.62347826086957
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3ad'),
    supplier_name: 'Flipopia',
    avg_sold_unit_price_from_supplier: 60.54896551724138
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3ae'),
    supplier_name: 'Tagchat',
    avg_sold_unit_price_from_supplier: 60.12
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3af'),
    supplier_name: 'Realbuzz',
    avg_sold_unit_price_from_supplier: 60.03695652173913
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb3b0'),
    supplier_name: 'Zoonder',
    avg_sold_unit_price_from_supplier: 59.99916666666667
  }
]
Type "it" for more
```

**Распределение продаж по странам поставщиков**
```bash
# db.mart_sales_by_supplier_country.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_sales_by_supplier_country.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_sales_by_supplier_country.find().pretty();"
[
  {
    _id: ObjectId('69201be5972cebc1b5ccb51d'),
    supplier_country: 'China',
    country_total_revenue: 395751.84,
    country_total_quantity_sold: 8742
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb51e'),
    supplier_country: 'Indonesia',
    country_total_revenue: 315434.43,
    country_total_quantity_sold: 6748
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb51f'),
    supplier_country: 'Brazil',
    country_total_revenue: 153864.48,
    country_total_quantity_sold: 3383
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb520'),
    supplier_country: 'France',
    country_total_revenue: 114746.92,
    country_total_quantity_sold: 2501
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb521'),
    supplier_country: 'Poland',
    country_total_revenue: 107507.58,
    country_total_quantity_sold: 2272
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb522'),
    supplier_country: 'Russia',
    country_total_revenue: 105602.14,
    country_total_quantity_sold: 2287
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb523'),
    supplier_country: 'Philippines',
    country_total_revenue: 95778.98,
    country_total_quantity_sold: 2119
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb524'),
    supplier_country: 'Portugal',
    country_total_revenue: 84559.03,
    country_total_quantity_sold: 1800
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb525'),
    supplier_country: 'Sweden',
    country_total_revenue: 63215.75,
    country_total_quantity_sold: 1383
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb526'),
    supplier_country: 'Ukraine',
    country_total_revenue: 49179.9,
    country_total_quantity_sold: 1079
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb527'),
    supplier_country: 'Thailand',
    country_total_revenue: 44530.85,
    country_total_quantity_sold: 853
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb528'),
    supplier_country: 'Japan',
    country_total_revenue: 41134.31,
    country_total_quantity_sold: 928
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb529'),
    supplier_country: 'Mongolia',
    country_total_revenue: 40452.42,
    country_total_quantity_sold: 901
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52a'),
    supplier_country: 'Czech Republic',
    country_total_revenue: 38062.04,
    country_total_quantity_sold: 743
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52b'),
    supplier_country: 'Pakistan',
    country_total_revenue: 36174.63,
    country_total_quantity_sold: 772
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52c'),
    supplier_country: 'United States',
    country_total_revenue: 35073.42,
    country_total_quantity_sold: 733
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52d'),
    supplier_country: 'Colombia',
    country_total_revenue: 32968.46,
    country_total_quantity_sold: 794
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52e'),
    supplier_country: 'Iran',
    country_total_revenue: 30286.66,
    country_total_quantity_sold: 613
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb52f'),
    supplier_country: 'Belarus',
    country_total_revenue: 29866.63,
    country_total_quantity_sold: 528
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb530'),
    supplier_country: 'Finland',
    country_total_revenue: 25987.24,
    country_total_quantity_sold: 552
  }
]
Type "it" for more
```

#### MongoDB: 6. Витрина качества продукции

**Продукты с наивысшим рейтингом**
```bash
# db.mart_highest_rated_products.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_highest_rated_products.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_highest_rated_products.find().pretty();"
[
  {
    _id: ObjectId('69201be5972cebc1b5ccb570'),
    business_product_id: 505,
    product_name: 'Dog Food',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb571'),
    business_product_id: 914,
    product_name: 'Cat Toy',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb572'),
    business_product_id: 524,
    product_name: 'Cat Toy',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb573'),
    business_product_id: 408,
    product_name: 'Dog Food',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb574'),
    business_product_id: 548,
    product_name: 'Dog Food',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb575'),
    business_product_id: 711,
    product_name: 'Dog Food',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb576'),
    business_product_id: 727,
    product_name: 'Cat Toy',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb577'),
    business_product_id: 177,
    product_name: 'Dog Food',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb578'),
    business_product_id: 773,
    product_name: 'Cat Toy',
    rating: 5
  },
  {
    _id: ObjectId('69201be5972cebc1b5ccb579'),
    business_product_id: 684,
    product_name: 'Bird Cage',
    rating: 5
  }
]
```

**Продукты с наименьшим рейтингом**
```bash
# db.mart_lowest_rated_products.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_lowest_rated_products.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_lowest_rated_products.find().pretty();"
[
  {
    _id: ObjectId('69201be6972cebc1b5ccb57b'),
    business_product_id: 137,
    product_name: 'Cat Toy',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb57c'),
    business_product_id: 240,
    product_name: 'Cat Toy',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb57d'),
    business_product_id: 62,
    product_name: 'Dog Food',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb57e'),
    business_product_id: 183,
    product_name: 'Dog Food',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb57f'),
    business_product_id: 227,
    product_name: 'Dog Food',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb580'),
    business_product_id: 471,
    product_name: 'Cat Toy',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb581'),
    business_product_id: 622,
    product_name: 'Bird Cage',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb582'),
    business_product_id: 894,
    product_name: 'Cat Toy',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb583'),
    business_product_id: 902,
    product_name: 'Bird Cage',
    rating: 1
  },
  {
    _id: ObjectId('69201be6972cebc1b5ccb584'),
    business_product_id: 904,
    product_name: 'Cat Toy',
    rating: 1
  }
]
```

**Корреляция между рейтингом и объемом продаж**
```bash
# db.mart_rating_sales_correlation.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_rating_sales_correlation.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_rating_sales_correlation.find().pretty();"
[
  {
    _id: ObjectId('69201be9972cebc1b5ccb586'),
    rating_sales_volume_correlation_coeff: 0.015170265597630222
  }
]
```

**Продукты с наибольшим количеством отзывов**
```bash
# db.mart_top_reviewed_products.find().pretty();

# docker exec -it mongodb_db mongosh reports --eval "db.mart_top_reviewed_products.find().pretty();"
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/rl_lr_2_YuraDudar$ docker exec -it mongodb_db mongosh reports \
  --eval "db.mart_top_reviewed_products.find().pretty();"
[
  {
    _id: ObjectId('69201be9972cebc1b5ccb588'),
    business_product_id: 30,
    product_name: 'Cat Toy',
    number_of_reviews: 1000
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb589'),
    business_product_id: 696,
    product_name: 'Cat Toy',
    number_of_reviews: 1000
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58a'),
    business_product_id: 438,
    product_name: 'Bird Cage',
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58b'),
    business_product_id: 568,
    product_name: 'Dog Food',
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58c'),
    business_product_id: 596,
    product_name: 'Cat Toy',
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58d'),
    business_product_id: 658,
    product_name: 'Cat Toy',
    number_of_reviews: 999
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58e'),
    business_product_id: 246,
    product_name: 'Cat Toy',
    number_of_reviews: 997
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb58f'),
    business_product_id: 573,
    product_name: 'Bird Cage',
    number_of_reviews: 997
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb590'),
    business_product_id: 489,
    product_name: 'Bird Cage',
    number_of_reviews: 996
  },
  {
    _id: ObjectId('69201be9972cebc1b5ccb591'),
    business_product_id: 93,
    product_name: 'Dog Food',
    number_of_reviews: 995
  }
]
```
