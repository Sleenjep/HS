# Высоконагруженные системы

## Лабораторная работа №4: BigDataTrino

```markdown
Выполнил:
- студент уч. группы М8О-209СВ
- Дрёмов Александр
```

# Отчёт к л.р. №4: BigDataTrino


### Шаг 1: Запуск контейнеров

```bash
docker-compose up -d
```

Потребуется подождать, пока все контейнеры поднимутся.

### Шаг 2: Подключение к Trino (этот шаг можно пропустить)

Для запуска через CLI контейнера:
```bash
docker exec -it mock-data-trino trino
```

### Подключение DBeaver

**PostgreSQL:**

* **Host**: localhost
* **Port**: 5432
* **Database**: mock_data
* **Username**: mock_data
* **Password**: mock_data

**ClickHouse:**

* **Host**: localhost
* **Port**: 8123
* **Database**: mock_data (или default)
* **Username**: default
* **Password**: (пустое)

**Trino:**

* **Host**: localhost
* **Port**: 8080
* **Username**: admin
* **Password**: (пустое)

### Шаг 3: Создание схемы "Звезда" (DDL)

```bash
cat sql/1_create_star_schema.sql | docker exec -i mock-data-trino trino
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ cat sql/1_create_star_schema.sql | docker exec -i mock-data-trino trino
Nov 27, 2025 11:49:48 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
```

### Шаг 4: ETL процесс (наполнение данными)

```bash
cat sql/2_etl_process.sql | docker exec -i mock-data-trino trino
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ cat sql/2_etl_process.sql | docker exec -i mock-data-trino trino
Nov 27, 2025 11:50:07 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
INSERT: 10000 rows
INSERT: 10000 rows
INSERT: 10000 rows
INSERT: 10000 rows
INSERT: 10000 rows
INSERT: 10000 rows
```

### Шаг 5: Генерация отчетов

```bash
cat sql/3_create_reports.sql | docker exec -i mock-data-trino trino
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ cat sql/3_create_reports.sql | docker exec -i mock-data-trino trino
Nov 27, 2025 11:50:17 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
CREATE TABLE: 9 rows
CREATE TABLE: 9999 rows
CREATE TABLE: 12 rows
CREATE TABLE: 10000 rows
CREATE TABLE: 6295 rows
CREATE TABLE: 9595 rows
```

## 4. Аналитические запросы к витринам

### 1. Витрина продаж по продуктам

**Самые продаваемые продукты:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            total_quantity_sold
        FROM clickhouse.mock_data.report_product_sales
        ORDER BY total_quantity_sold DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            total_quantity_sold
        FROM clickhouse.mock_data.report_product_sales
        ORDER BY total_quantity_sold DESC
        LIMIT 5;
    "
Nov 27, 2025 11:54:54 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_name | total_quantity_sold 
--------------+---------------------
 Bird Cage    |               63308 
 Dog Food     |               62934 
 Bird Cage    |               61983 
 Cat Toy      |               60708 
 Cat Toy      |               60281 
(5 rows)
```

**Общая выручка по категориям продуктов:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_category,
            SUM(total_revenue)
        FROM clickhouse.mock_data.report_product_sales
        GROUP BY product_category;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_category,
            SUM(total_revenue)
        FROM clickhouse.mock_data.report_product_sales
        GROUP BY product_category;
    "
Nov 27, 2025 11:55:21 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_category |   _col1    
------------------+------------
 Cage             | 8405504.12 
 Toy              | 8636900.72 
 Food             | 8256116.36 
(3 rows)
```

**Средний рейтинг и количество отзывов:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            avg_rating,
            review_count
        FROM clickhouse.mock_data.report_product_sales
        ORDER BY review_count DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            avg_rating,
            review_count
        FROM clickhouse.mock_data.report_product_sales
        ORDER BY review_count DESC
        LIMIT 5;
    "
Nov 27, 2025 11:55:40 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_name | avg_rating | review_count 
--------------+------------+--------------
 Bird Cage    |        3.0 |         1000 
 Cat Toy      |        3.0 |         1000 
 Cat Toy      |        3.1 |         1000 
 Cat Toy      |        2.9 |         1000 
 Dog Food     |        3.0 |         1000 
(5 rows)
```

### 2. Витрина продаж по клиентам

**Клиенты с наибольшей общей суммой покупок:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            first_name,
            last_name,
            total_spent
        FROM clickhouse.mock_data.report_customer_sales
        ORDER BY total_spent DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            first_name,
            last_name,
            total_spent
        FROM clickhouse.mock_data.report_customer_sales
        ORDER BY total_spent DESC
        LIMIT 5;
    "
Nov 27, 2025 11:56:01 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 first_name | last_name | total_spent 
------------+-----------+-------------
 Kippy      | McCurry   |     5048.25 
 Ford       | Freake    |     4005.98 
 Claudian   | Gleave    |     4005.98 
 Devonna    | Biswell   |     4005.98 
 Randolf    | Rillatt   |     4005.98 
(5 rows)
```

**Распределение клиентов по странам:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            COUNT(*) AS client_count
        FROM clickhouse.mock_data.report_customer_sales
        GROUP BY country
        ORDER BY client_count DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            COUNT(*) AS client_count
        FROM clickhouse.mock_data.report_customer_sales
        GROUP BY country
        ORDER BY client_count DESC
        LIMIT 5;
    "
Nov 27, 2025 11:58:16 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
   country   | client_count 
-------------+--------------
 China       |         1738 
 Indonesia   |         1173 
 Russia      |          628 
 Philippines |          555 
 Brazil      |          385 
(5 rows)
```

**Средний чек для каждого клиента:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            first_name,
            last_name,
            avg_check
        FROM clickhouse.mock_data.report_customer_sales
        ORDER BY avg_check DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            first_name,
            last_name,
            avg_check
        FROM clickhouse.mock_data.report_customer_sales
        ORDER BY avg_check DESC
        LIMIT 5;
    "
Nov 27, 2025 11:58:39 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 first_name | last_name | avg_check 
------------+-----------+-----------
 Manny      | Swannie   |    400.60 
 Randolf    | Rillatt   |    400.60 
 Maryanne   | Bernaldez |    400.60 
 Hannie     | Braddon   |    400.60 
 Mile       | Tuer      |    400.60 
(5 rows)
```

### 3. Витрина продаж по времени

**Месячные и годовые сводки продаж:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            sale_year,
            sale_month,
            total_revenue
        FROM clickhouse.mock_data.report_time_sales
        ORDER BY sale_year, sale_month
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            sale_year,
            sale_month,
            total_revenue
        FROM clickhouse.mock_data.report_time_sales
        ORDER BY sale_year, sale_month
        LIMIT 5;
    "
Nov 27, 2025 11:59:13 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 sale_year | sale_month | total_revenue 
-----------+------------+---------------
      2021 |          1 |     224158.54 
      2021 |          2 |     192348.31 
      2021 |          3 |     207282.20 
      2021 |          4 |     206592.82 
      2021 |          5 |     211764.86 
(5 rows)
```

**Средний размер заказа по месяцам:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            sale_year,
            sale_month,
            avg_order_size
        FROM clickhouse.mock_data.report_time_sales
        ORDER BY sale_year, sale_month
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            sale_year,
            sale_month,
            avg_order_size
        FROM clickhouse.mock_data.report_time_sales
        ORDER BY sale_year, sale_month
        LIMIT 5;
    "
Nov 27, 2025 11:59:48 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 sale_year | sale_month | avg_order_size 
-----------+------------+----------------
      2021 |          1 |         256.47 
      2021 |          2 |         260.28 
      2021 |          3 |         245.89 
      2021 |          4 |         246.83 
      2021 |          5 |         255.75 
(5 rows)
```

### 4. Витрина продаж по магазинам

**Магазины с наибольшей выручкой:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            store_name,
            total_revenue
        FROM clickhouse.mock_data.report_store_sales
        ORDER BY total_revenue DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            store_name,
            total_revenue
        FROM clickhouse.mock_data.report_store_sales
        ORDER BY total_revenue DESC
        LIMIT 5;
    "
Nov 27, 2025 8:41:27 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 store_name | total_revenue 
------------+---------------
 Mynte      |      15751.71 
 Mynte      |      15751.71 
 Mynte      |      15751.71 
 Mynte      |      15751.71 
 Mynte      |      15751.71 
(5 rows)
```

**Распределение продаж по городам и странам:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            city,
            SUM(total_revenue) AS revenue
        FROM clickhouse.mock_data.report_store_sales
        GROUP BY country, city
        ORDER BY revenue DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            city,
            SUM(total_revenue) AS revenue
        FROM clickhouse.mock_data.report_store_sales
        GROUP BY country, city
        ORDER BY revenue DESC
        LIMIT 5;
    "
Nov 27, 2025 12:00:19 PM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 country |    city    | revenue  
---------+------------+----------
 China   | Stockholm  | 48205.53 
 China   | København  | 29798.13 
 China   | Hats’avan  | 25057.70 
 China   | Santa Cruz | 23502.35 
 Brazil  | Qilin      | 23400.64 
(5 rows)
```

**Средний чек для каждого магазина:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            store_name,
            avg_check
        FROM clickhouse.mock_data.report_store_sales
        ORDER BY avg_check DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            store_name,
            avg_check
        FROM clickhouse.mock_data.report_store_sales
        ORDER BY avg_check DESC
        LIMIT 5;
    "
Nov 27, 2025 12:00:37 PM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 store_name | avg_check 
------------+-----------
 Brightbean |    335.69 
 Brightbean |    335.69 
 Brightbean |    335.69 
 Brightbean |    335.69 
 Brightbean |    335.69 
(5 rows)
```

### 5. Витрина продаж по поставщикам

**Поставщики с наибольшей выручкой:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            supplier_name,
            total_revenue
        FROM clickhouse.mock_data.report_supplier_sales
        ORDER BY total_revenue DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            supplier_name,
            total_revenue
        FROM clickhouse.mock_data.report_supplier_sales
        ORDER BY total_revenue DESC
        LIMIT 5;
    "
Nov 27, 2025 8:42:54 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 supplier_name | total_revenue 
---------------+---------------
 Wikizz        |    2482162.20 
 Wikizz        |    2482162.20 
 Katz          |    2455827.00 
 Livetube      |    1916428.80 
 Jayo          |    1584994.40 
(5 rows)
```

**Средняя цена товаров от каждого поставщика:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            supplier_name,
            avg_product_price
        FROM clickhouse.mock_data.report_supplier_sales
        ORDER BY avg_product_price DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            supplier_name,
            avg_product_price
        FROM clickhouse.mock_data.report_supplier_sales
        ORDER BY avg_product_price DESC
        LIMIT 5;
    "
Nov 27, 2025 12:01:18 PM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 supplier_name | avg_product_price 
---------------+-------------------
 Browsecat     |             58.17 
 Browsecat     |             58.17 
 Browsecat     |             58.17 
 Browsecat     |             58.17 
 Browsecat     |             58.17 
(5 rows)
```

**Распределение продаж по странам поставщиков:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            SUM(total_revenue) AS revenue
        FROM clickhouse.mock_data.report_supplier_sales
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            country,
            SUM(total_revenue) AS revenue
        FROM clickhouse.mock_data.report_supplier_sales
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 5;
    "
Nov 27, 2025 12:01:36 PM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
   country   |   revenue    
-------------+--------------
 China       | 137083105.60 
 Indonesia   |  76919212.40 
 Russia      |  40599353.70 
 Philippines |  37871255.70 
 Brazil      |  26626501.00 
(5 rows)
```

### 6. Витрина качества продукции

**Продукты с наивысшим рейтингом:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            rating
        FROM clickhouse.mock_data.report_quality
        ORDER BY rating DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            rating
        FROM clickhouse.mock_data.report_quality
        ORDER BY rating DESC
        LIMIT 5;
    "
Nov 27, 2025 8:44:00 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_name | rating 
--------------+--------
 Cat Toy      |    5.0 
 Dog Food     |    5.0 
 Dog Food     |    5.0 
 Dog Food     |    5.0 
 Cat Toy      |    5.0 
(5 rows)
```

**Продукты с наименьшим рейтингом:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            rating
        FROM clickhouse.mock_data.report_quality
        ORDER BY rating ASC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            rating
        FROM clickhouse.mock_data.report_quality
        ORDER BY rating ASC
        LIMIT 5;
    "
Nov 27, 2025 8:44:17 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_name | rating 
--------------+--------
 Bird Cage    |    1.0 
 Cat Toy      |    1.0 
 Dog Food     |    1.0 
 Dog Food     |    1.0 
 Cat Toy      |    1.0 
(5 rows)
```

**Корреляция между рейтингом и объемом продаж:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            rating,
            AVG(total_sales_volume) AS avg_sales
        FROM clickhouse.mock_data.report_quality
        GROUP BY rating
        ORDER BY rating DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            rating,
            AVG(total_sales_volume) AS avg_sales
        FROM clickhouse.mock_data.report_quality
        GROUP BY rating
        ORDER BY rating DESC
        LIMIT 5;
    "
Nov 27, 2025 12:02:08 PM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 rating |     avg_sales      
--------+--------------------
    5.0 |   54.8796992481203 
    4.9 | 56.902834008097166 
    4.8 |   57.6692607003891 
    4.7 |  57.08365019011407 
    4.6 |  57.75545851528384 
(5 rows)
```

**Продукты с наибольшим количеством отзывов:**
```bash
docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            reviews
        FROM clickhouse.mock_data.report_quality
        ORDER BY reviews DESC
        LIMIT 5;
    "
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_4/BigDataTrino$ docker exec -i mock-data-trino trino \
    --output-format ALIGNED \
    --execute "
        SELECT
            product_name,
            reviews
        FROM clickhouse.mock_data.report_quality
        ORDER BY reviews DESC
        LIMIT 5;
    "
Nov 27, 2025 8:50:29 AM org.jline.utils.Log logr
WARNING: Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
 product_name | reviews 
--------------+---------
 Cat Toy      |    1000 
 Cat Toy      |    1000 
 Dog Food     |    1000 
 Bird Cage    |    1000 
 Bird Cage    |    1000 
(5 rows)
```
