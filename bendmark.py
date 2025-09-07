import time, random, csv
import psycopg2, pyodbc
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

# ---------------------------
# Database connections
# ---------------------------
def get_pg_conn():
    return psycopg2.connect(
        dbname="shopdb", user="postgres", password="postgres", host="localhost", port=5432
    )

def get_sql_conn():
    driver = "ODBC Driver 17 for SQL Server"
    return pyodbc.connect(
        f"DRIVER={{{driver}}};SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=YourStrong(!)Password;TrustServerCertificate=yes;"
    )

# ---------------------------
# Scenario 1: Read-heavy
# ---------------------------
def test_read(pg=True, runs=50):
    if pg:
        conn = get_pg_conn()
        cur = conn.cursor()
        query = """
        SELECT p.product_id, p.name, SUM(od.quantity) AS total_sold
        FROM orderdetails od
        JOIN orders o ON od.order_id = o.order_id
        JOIN products p ON p.product_id = od.product_id
        WHERE o.order_date >= (CURRENT_DATE - INTERVAL '30 days')
        GROUP BY p.product_id, p.name
        ORDER BY total_sold DESC
        LIMIT 10;
        """
    else:
        conn = get_sql_conn()
        cur = conn.cursor()
        query = """
        SELECT TOP 10 p.product_id, p.name, SUM(od.quantity) AS total_sold
        FROM OrderDetails od
        JOIN Orders o ON od.order_id = o.order_id
        JOIN Products p ON p.product_id = od.product_id
        WHERE o.order_date >= DATEADD(DAY, -30, GETDATE())
        GROUP BY p.product_id, p.name
        ORDER BY total_sold DESC;
        """

    times = []
    for _ in range(runs):
        t0 = time.time()
        cur.execute(query)
        cur.fetchall()
        t1 = time.time()
        times.append((t1 - t0) * 1000)  # ms
    cur.close()
    conn.close()
    return times

# ---------------------------
# Scenario 2: Write-heavy
# ---------------------------
def worker_place_order(pg=True):
    uid = random.randint(1, 200)
    prods = random.sample(range(1, 100), random.randint(1, 3))
    if pg:
        conn = get_pg_conn()
        cur = conn.cursor()
        try:
            cur.execute("BEGIN;")
            oid = random.randint(10000, 20000)
            cur.execute("INSERT INTO Orders (order_id, user_id, order_date) VALUES (%s, %s, NOW())", (oid, uid))
            for pid in prods:
                qty = random.randint(1, 5)
                cur.execute("INSERT INTO OrderDetails (order_id, product_id, quantity) VALUES (%s, %s, %s)", (oid, pid, qty))
            conn.commit()
        except:
            conn.rollback()
        finally:
            cur.close(); conn.close()
    else:
        conn = get_sql_conn()
        cur = conn.cursor()
        try:
            cur.execute("BEGIN TRAN;")
            oid = random.randint(10000, 20000)
            cur.execute("INSERT INTO Orders (order_id, user_id, order_date) VALUES (?, ?, GETDATE())", (oid, uid))
            for pid in prods:
                qty = random.randint(1, 5)
                cur.execute("INSERT INTO OrderDetails (order_id, product_id, quantity) VALUES (?, ?, ?)", (oid, pid, qty))
            conn.commit()
        except:
            conn.rollback()
        finally:
            cur.close(); conn.close()

def test_write(pg=True, clients=50):
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=clients) as ex:
        futures = [ex.submit(worker_place_order, pg) for _ in range(clients)]
        for f in futures: f.result()
    t1 = time.time()
    elapsed = t1 - t0
    tps = clients / elapsed
    return elapsed, tps

# ---------------------------
# Main benchmarking
# ---------------------------
if __name__ == "__main__":
    results = []

    print("Running Read-heavy test...")
    pg_times = test_read(pg=True, runs=50)
    sql_times = test_read(pg=False, runs=50)
    results.append(["PostgreSQL", "Read-heavy", sum(pg_times)/len(pg_times), None])
    results.append(["SQL Server", "Read-heavy", sum(sql_times)/len(sql_times), None])

    print("Running Write-heavy test...")
    elapsed_pg, tps_pg = test_write(pg=True, clients=50)
    elapsed_sql, tps_sql = test_write(pg=False, clients=50)
    results.append(["PostgreSQL", "Write-heavy", None, tps_pg])
    results.append(["SQL Server", "Write-heavy", None, tps_sql])

    # Save to CSV
    with open("benchmark_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["DB", "Scenario", "AvgTime(ms)", "TPS"])
        writer.writerows(results)

    print("\n✅ Results saved to benchmark_results.csv")

    # Plot chart
    labels = ["Read-heavy (ms)", "Write-heavy (TPS)"]
    pg_values = [results[0][2], results[2][3]]
    sql_values = [results[1][2], results[3][3]]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], pg_values, width, label="PostgreSQL")
    ax.bar([i + width/2 for i in x], sql_values, width, label="SQL Server")

    ax.set_ylabel("Performance")
    ax.set_title("PostgreSQL vs SQL Server Performance")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.savefig("benchmark_chart.png")
    plt.show()
    print("📊 Chart saved to benchmark_chart.png")
