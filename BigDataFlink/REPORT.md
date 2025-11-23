# Высоконагруженные системы


## Лабораторная работа №2: BigDataSpark

```markdown
Выполнил:
- студент уч. группы М8О-209СВ
- Дрёмов Александр
```

# Отчёт к л.р. №3: BigDataFlink

## Инструкция по запуску:

```bash
docker-compose up -d --build
```

Сервисы запускаются около 30-60 секунд.

### 4. Запуск Flink Job

Отправление задачи на выполнение в кластер Flink:

```bash
# docker exec -it jobmanager ./bin/flink run -py /opt/flink/usrlib/job.py

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3/BigDataFlink$ docker exec -it jobmanager ./bin/flink run -py /opt/flink/usrlib/job.py
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by org.apache.flink.api.java.ClosureCleaner (file:/opt/flink/lib/flink-dist-1.17.1.jar) to field java.lang.String.value
WARNING: Please consider reporting this to the maintainers of org.apache.flink.api.java.ClosureCleaner
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
Job has been submitted with JobID 196625efc181eecdc13a18c2888982fc
```

### 5. Проверка работы системы

#### А. Проверка отправки данных (Producer)

Можно посмотреть логи продюсера, чтобы убедиться, что данные отправляются в Kafka:

```bash
# docker logs -f producer

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3/BigDataFlink$ docker logs -f producer
Connected to Kafka
Processing /data/MOCK_DATA (1).csv
Finished /data/MOCK_DATA (1).csv
Processing /data/MOCK_DATA (2).csv
Finished /data/MOCK_DATA (2).csv
Processing /data/MOCK_DATA (3).csv
Finished /data/MOCK_DATA (3).csv
Processing /data/MOCK_DATA (4).csv
Finished /data/MOCK_DATA (4).csv
Processing /data/MOCK_DATA (5).csv
Finished /data/MOCK_DATA (5).csv
Processing /data/MOCK_DATA (6).csv
Finished /data/MOCK_DATA (6).csv
Processing /data/MOCK_DATA (7).csv
Finished /data/MOCK_DATA (7).csv
Processing /data/MOCK_DATA (8).csv
Finished /data/MOCK_DATA (8).csv
Processing /data/MOCK_DATA (9).csv
Finished /data/MOCK_DATA (9).csv
Processing /data/MOCK_DATA.csv
Finished /data/MOCK_DATA.csv
All data sent.
```

#### Б. Мониторинг Flink

Можно открыть Flink Dashboard в браузере: <http://localhost:8081>

#### В. Проверка данных в PostgreSQL

1. **Проверка количества записей в таблице фактов:**

```bash
# docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "SELECT COUNT(*) FROM fact_sales;"

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "SELECT COUNT(*) FROM fact_sales;"
 count 
-------
 10000
(1 row)
```

2. **Проверка заполнения всех таблиц:**

```bash
# docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
# SELECT 'dim_customer' as table, COUNT(*) FROM dim_customer UNION ALL 
# SELECT 'dim_product', COUNT(*) FROM dim_product UNION ALL 
# SELECT 'dim_seller', COUNT(*) FROM dim_seller UNION ALL 
# SELECT 'dim_store', COUNT(*) FROM dim_store UNION ALL 
# SELECT 'fact_sales', COUNT(*) FROM fact_sales;"

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c " 
SELECT 'dim_customer' as table, COUNT(*) FROM dim_customer UNION ALL 
SELECT 'dim_product', COUNT(*) FROM dim_product UNION ALL 
SELECT 'dim_seller', COUNT(*) FROM dim_seller UNION ALL 
SELECT 'dim_store', COUNT(*) FROM dim_store UNION ALL 
SELECT 'fact_sales', COUNT(*) FROM fact_sales;"
    table     | count 
--------------+-------
 dim_customer |  1000
 dim_product  |  1000
 dim_seller   |  1000
 dim_store    |   383
 fact_sales   | 10000
(5 rows)

```

3. **Просмотр примеров данных:**

```bash
# docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "SELECT * FROM fact_sales LIMIT 5;"

alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3/BigDataFlink$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "SELECT * FROM fact_sales LIMIT 5;"
 sale_id | customer_id | seller_id | product_id | store_name | quantity | total_amount | sale_date  
---------+-------------+-----------+------------+------------+----------+--------------+------------
     474 |         401 |       401 |        401 | Livetube   |        2 |       476.05 | 2021-06-10
     475 |         402 |       402 |        402 | Kayveo     |        8 |       206.58 | 2021-02-18
     476 |         403 |       403 |        403 | Bluezoom   |        2 |       482.73 | 2021-09-14
     477 |         404 |       404 |        404 | Oyoyo      |        4 |       214.38 | 2021-07-18
     478 |         405 |       405 |        405 | Meetz      |        2 |       429.89 | 2021-10-22
(5 rows)
```

Также можно подключиться через DBeaver к postges:

- **Host**: localhost
- **Port**: 5432
- **Database**: spark_db
- **User**: spark_user_name
- **Password**: spark_my_secret_password

### Примеры аналитических запросов к полученным данным

По заданию запросы не требовались, но я сделал несколько.

**1. Топ-5 категорий продуктов по общей выручке:**

```sql
SELECT 
    p.category, 
    SUM(f.total_amount) as total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 5;
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3/BigDataFlink$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
SELECT 
    p.category, 
    SUM(f.total_amount) as total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 5;"
 category | total_revenue 
----------+---------------
 Cage     |     845521.98
 Food     |     843109.67
 Toy      |     841220.47
(3 rows)
```

**2. Топ-5 магазинов по количеству продаж:**

```sql
SELECT 
    s.store_name, 
    COUNT(*) as sales_count
FROM fact_sales f
JOIN dim_store s ON f.store_name = s.store_name
GROUP BY s.store_name
ORDER BY sales_count DESC
LIMIT 5;
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3/BigDataFlink$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
SELECT 
    s.store_name, 
    COUNT(*) as sales_count
FROM fact_sales f
JOIN dim_store s ON f.store_name = s.store_name
GROUP BY s.store_name
ORDER BY sales_count DESC
LIMIT 5;"
 store_name | sales_count 
------------+-------------
 Quatz      |          58
 Mynte      |          56
 Skimia     |          54
 Livetube   |          53
 Realcube   |          51
(5 rows)
```

**3. Распределение выручки по странам продавцов:**

```sql
SELECT 
    s.country, 
    SUM(f.total_amount) as total_revenue
FROM fact_sales f
JOIN dim_seller s ON f.seller_id = s.seller_id
GROUP BY s.country
ORDER BY total_revenue DESC;
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
SELECT 
    s.country, 
    SUM(f.total_amount) as total_revenue
FROM fact_sales f
JOIN dim_seller s ON f.seller_id = s.seller_id
GROUP BY s.country
ORDER BY total_revenue DESC
LIMIT 15"
    country     | total_revenue 
----------------+---------------
 China          |     455470.89
 Indonesia      |     252294.38
 Russia         |     207103.92
 Philippines    |     138219.78
 Poland         |      87782.71
 Brazil         |      85664.92
 Portugal       |      81572.71
 France         |      73807.21
 Sweden         |      60583.10
 Czech Republic |      60345.26
 United States  |      47047.92
 Peru           |      43894.52
 Argentina      |      42533.85
 Thailand       |      40543.26
 Japan          |      39088.97
(15 rows)
```

**4. Топ-5 самых активных покупателей (по потраченной сумме):**

```sql
SELECT 
    c.first_name, 
    c.last_name, 
    SUM(f.total_amount) as total_spent
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 5;
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
SELECT 
    c.first_name, 
    c.last_name, 
    SUM(f.total_amount) as total_spent
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 5;"
 first_name | last_name | total_spent 
------------+-----------+-------------
 Mile       | Tuer      |     4005.98
 Lewiss     | Pinshon   |     3784.44
 Alexis     | Quinton   |     3751.09
 Benita     | Godding   |     3682.52
 Elvira     | Faircliff |     3645.94
(5 rows)
```

**5. Динамика продаж по дням:**

```sql
SELECT 
    sale_date, 
    SUM(total_amount) as daily_revenue,
    COUNT(*) as transactions_count
FROM fact_sales
GROUP BY sale_date
ORDER BY sale_date DESC
LIMIT 10;
```

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS_NENAHOV/hs_lr_3$ docker exec -it postgres_db psql -U spark_user_name -d spark_db -c "
SELECT 
    sale_date, 
    SUM(total_amount) as daily_revenue,
    COUNT(*) as transactions_count
FROM fact_sales
GROUP BY sale_date
ORDER BY sale_date DESC
LIMIT 10;"
 sale_date  | daily_revenue | transactions_count 
------------+---------------+--------------------
 2021-12-30 |       6784.13 |                 28
 2021-12-29 |       6752.50 |                 24
 2021-12-28 |       8144.54 |                 30
 2021-12-27 |       8047.03 |                 34
 2021-12-26 |       6087.64 |                 29
 2021-12-25 |       2857.68 |                 17
 2021-12-24 |       8456.67 |                 29
 2021-12-23 |       5101.05 |                 18
 2021-12-22 |       6066.08 |                 26
 2021-12-21 |       6657.42 |                 23
(10 rows)
```
