# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 15:01:23 2025

@author: KHA
"""

# seed_data.py
import psycopg2
import pyodbc
from faker import Faker
import random

fake = Faker()

# -------------------------
# PostgreSQL connection
# -------------------------
pg_conn = psycopg2.connect(
    dbname="shopdb",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
pg_cur = pg_conn.cursor()

# -------------------------
# SQL Server connection
# -------------------------
driver = "ODBC Driver 17 for SQL Server"  # hoặc "ODBC Driver 18 for SQL Server" tùy máy bạn
sql_conn = pyodbc.connect(
    f"DRIVER={{{driver}}};SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=YourStrong(!)Password;TrustServerCertificate=yes;"
)
sql_cur = sql_conn.cursor()

# -------------------------
# Seed Users
# -------------------------
def seed_users(n=200):
    users = [(i+1, fake.name(), fake.unique.email()) for i in range(n)]
    # Postgres
    pg_cur.executemany("INSERT INTO Users (user_id, name, email) VALUES (%s, %s, %s)", users)
    pg_conn.commit()
    # SQL Server
    sql_cur.executemany("INSERT INTO Users (user_id, name, email) VALUES (?, ?, ?)", users)
    sql_conn.commit()
    print(f"Seeded {n} users")

# -------------------------
# Seed Products
# -------------------------
def seed_products(n=100):
    products = [(i+1, fake.word(), round(random.uniform(5,500),2), random.randint(1,1000)) for i in range(n)]
    # Postgres
    pg_cur.executemany("INSERT INTO Products (product_id, name, price, stock_quantity) VALUES (%s, %s, %s, %s)", products)
    pg_conn.commit()
    # SQL Server
    sql_cur.executemany("INSERT INTO Products (product_id, name, price, stock_quantity) VALUES (?, ?, ?, ?)", products)
    sql_conn.commit()
    print(f"Seeded {n} products")

# -------------------------
# Seed Orders + OrderDetails
# -------------------------
def seed_orders(n=500):
    order_id = 1
    details_pg = []
    details_sql = []
    for i in range(n):
        user_id = random.randint(1,200)
        # Insert order
        pg_cur.execute("INSERT INTO Orders (order_id, user_id) VALUES (%s, %s)", (order_id, user_id))
        sql_cur.execute("INSERT INTO Orders (order_id, user_id) VALUES (?, ?)", (order_id, user_id))
        # Create 1–3 distinct products for this order
        chosen_products = random.sample(range(1,101), random.randint(1,3))
        for pid in chosen_products:
            qty = random.randint(1,5)
            details_pg.append((order_id, pid, qty))
            details_sql.append((order_id, pid, qty))
        order_id += 1
    # Batch insert details
    pg_cur.executemany("INSERT INTO OrderDetails (order_id, product_id, quantity) VALUES (%s, %s, %s)", details_pg)
    pg_conn.commit()
    sql_cur.executemany("INSERT INTO OrderDetails (order_id, product_id, quantity) VALUES (?, ?, ?)", details_sql)
    sql_conn.commit()
    print(f"Seeded {n} orders with details")

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    seed_users(200)      # 200 users
    seed_products(100)   # 100 products
    seed_orders(500)     # 500 orders
    print("✅ Seeding done!")
    pg_cur.close()
    pg_conn.close()
    sql_cur.close()
    sql_conn.close()
