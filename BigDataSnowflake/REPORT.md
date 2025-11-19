# Высоконагруженные системы

## Лабораторная работа №1: BigDataSnowflake

```markdown
Выполнил:
- студент уч. группы М8О-209СВ
- Дрёмов Александр
```

# Отчёт к л.р. №1: BigDataSnowflake

## Инструкция по запуску:

Запуск docker-compose:

```bash
docker-compose up -d
```

Скриншот shonflake из dbeaver:
- pg_db_lab_1 - public.png.

Параметры для dbeaver:

```markdown
Host: localhost
Port: 5438
Database: pg_db_lab_1
Username: admin
Password: qwerty
```

Проверка состояния сервиса:

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS/hs_lr_1/BigDataSnowflake$ docker ps --filter name=snowflake-postgres
docker exec snowflake-postgres psql -U admin -d pg_db_lab_1 -c "\\dt"
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS          PORTS                                         NAMES
38cbab30d39d   postgres:16   "docker-entrypoint.s…"   24 minutes ago   Up 24 minutes   0.0.0.0:5438->5432/tcp, [::]:5438->5432/tcp   snowflake-postgres
           List of relations
 Schema |     Name     | Type  | Owner 
--------+--------------+-------+-------
 public | dim_customer | table | admin
 public | dim_product  | table | admin
 public | dim_seller   | table | admin
 public | dim_store    | table | admin
 public | dim_supplier | table | admin
 public | fact_sales   | table | admin
 public | pet_sales    | table | admin
(7 rows)
```

## Аналитические запросы

### 1. Выручка по категориям товаров

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS/hs_lr_1/BigDataSnowflake$ docker exec snowflake-postgres psql -U admin -d pg_db_lab_1 -F $'\t' -A -c "SELECT dp.product_category, ROUND(SUM(fs.sale_total_price)::NUMERIC,2) AS total_revenue, SUM(fs.sale_quantity) AS total_units, ROUND(AVG(fs.product_price)::NUMERIC,2) AS avg_price FROM fact_sales fs JOIN dim_product dp ON dp.product_id = fs.product_id GROUP BY dp.product_category ORDER BY total_revenue DESC LIMIT 5;"
product_category        total_revenue   total_units     avg_price
Toy                     1184629.31      25330           50.25
Food                    1106423.11      23903           50.24
Cage                    1103709.98      23915           51.88
(3 rows)
```

### 2. Топ-10 покупателей по выручке

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS/hs_lr_1/BigDataSnowflake$ docker exec snowflake-postgres psql -U admin -d pg_db_lab_1 -F $'\t' -A -c "SELECT dc.customer_first_name || ' ' || dc.customer_last_name AS customer_name, dc.customer_country, ROUND(SUM(fs.sale_total_price)::NUMERIC,2) AS total_spent, SUM(fs.sale_quantity) AS total_items FROM fact_sales fs JOIN dim_customer dc ON dc.customer_id = fs.customer_id GROUP BY customer_name, dc.customer_country ORDER BY total_spent DESC LIMIT 10;"
customer_name           customer_country        total_spent     total_items
Mayor Bottomley         Sweden                  2468.82         12
Hilario Edmons          Russia                  2307.15         40
Freeman Itzcak          Philippines             2246.15         20
Judon Linnock           China                   1993.88         16
Torry Gruszczak         China                   1985.04         20
Riccardo Coytes         Azerbaijan              1984.60         28
Ally Bagger             Portugal                1983.96         28
Bancroft Wethered       South Africa            1983.08         12
Nicoline Fellgate       Vietnam                 1929.00         20
Celine Dobing           Brazil                  1732.72         8
(10 rows)
``` 

### 3. Динамика продаж по месяцам

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS/hs_lr_1/BigDataSnowflake$ docker exec snowflake-postgres psql -U admin -d pg_db_lab_1 -F $'\t' -A -c "SELECT TO_CHAR(date_trunc('month', sale_date), 'YYYY-MM') AS month, ROUND(SUM(sale_total_price)::NUMERIC,2) AS total_revenue, SUM(sale_quantity) AS total_units FROM fact_sales GROUP BY month ORDER BY month;"
month   total_revenue   total_units
2021-01 300017.95       6449
2021-02 262511.50       5550
2021-03 280028.33       6272
2021-04 272494.40       6075
2021-05 275567.98       5819
2021-06 288567.74       5946
2021-07 302031.96       6455
2021-08 294288.98       6320
2021-09 280225.53       5916
2021-10 306352.13       6700
2021-11 277258.52       5917
2021-12 255417.38       5729
(12 rows)
```

### 4. Вклад стран-поставщиков

```bash
alex@alex-Aspire-A715-75G:~/Ubuntu GDrive/VUZ/HS/hs_lr_1/BigDataSnowflake$ docker exec snowflake-postgres psql -U admin -d pg_db_lab_1 -F $'\t' -A -c "SELECT dsu.supplier_country, COUNT(DISTINCT dsu.supplier_id) AS suppliers, ROUND(SUM(fs.sale_total_price)::NUMERIC,2) AS revenue_share FROM fact_sales fs JOIN dim_supplier dsu ON dsu.supplier_id = fs.supplier_id GROUP BY dsu.supplier_country ORDER BY revenue_share DESC LIMIT 5;"
supplier_country        suppliers       revenue_share
China                   1921            668720.22
Indonesia               1079            352909.21
Russia                  582             206092.04
Philippines             536             184974.48
Brazil                  376             129265.87
(5 rows)
```
