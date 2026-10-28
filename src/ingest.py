"""
src/ingest.py
Initializes the DuckDB database, materializes the raw clickstream events,
and prints data profile diagnostics.
"""

import duckdb
import os
import time

DB_PATH = "database/analytics.duckdb"
SOURCE_CSV = "data/raw/2019-Oct.csv"

def get_connection():
    os.makedirs("database", exist_ok=True)
    con = duckdb.connect(DB_PATH)
    # Hardware resource allocation
    con.execute("PRAGMA threads=4;")
    con.execute("PRAGMA memory_limit='6GB';")
    return con

def ingest_october_data(con):
    print(f"Connecting to database at: {DB_PATH}")
    print(f"Ingesting raw source: {SOURCE_CSV}")
    start = time.time()
    
    # Let DuckDB auto-detect, then enforce clean column types
    query = f"""
    CREATE OR REPLACE TABLE raw_events AS 
    SELECT 
        event_time::TIMESTAMPTZ AS event_time,
        event_type::VARCHAR AS event_type,
        product_id::BIGINT AS product_id,
        category_id::BIGINT AS category_id,
        category_code::VARCHAR AS category_code,
        brand::VARCHAR AS brand,
        ROUND(price::DECIMAL(10, 2), 2) AS price,
        user_id::BIGINT AS user_id,
        user_session::VARCHAR AS user_session
    FROM read_csv('{SOURCE_CSV}', header=True);
    """
    
    print("Executing ingestion and schema enforcement...")
    con.execute(query)
    duration = time.time() - start
    
    row_count = con.execute("SELECT COUNT(*) FROM raw_events;").fetchone()[0]
    print(f"[✓] Successfully ingested {row_count:,} rows in {duration:.2f} seconds.")

def profile_raw_data(con):
    print("\n" + "="*50)
    print("DATA QUALITY PROFILE & HEALTH CHECKS")
    print("="*50)

    # 1. High-level aggregates
    print("\n[1] Volume & Time Range:")
    volume_df = con.execute("""
        SELECT 
            COUNT(*) AS total_records,
            COUNT(DISTINCT user_id) AS unique_users,
            COUNT(DISTINCT user_session) AS unique_sessions,
            MIN(event_time) AS start_time,
            MAX(event_time) AS end_time
        FROM raw_events;
    """).df()
    print(volume_df.to_string(index=False))

    # 2. Event Distribution Breakdown
    print("\n[2] Event Type Breakdown:")
    event_df = con.execute("""
        SELECT 
            event_type,
            COUNT(*) AS total_events,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
        FROM raw_events
        GROUP BY event_type
        ORDER BY total_events DESC;
    """).df()
    print(event_df.to_string(index=False))

    # 3. Missing Value Audit (Null checks)
    print("\n[3] Missing / Null Value Audit:")
    nulls_df = con.execute("""
        SELECT 
            ROUND(SUM(CASE WHEN category_code IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS category_code_null_pct,
            ROUND(SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS brand_null_pct,
            ROUND(SUM(CASE WHEN user_session IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS session_null_pct,
            ROUND(SUM(CASE WHEN price <= 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS zero_or_negative_price_pct
        FROM raw_events;
    """).df()
    print(nulls_df.to_string(index=False))

if __name__ == "__main__":
    con = get_connection()
    ingest_october_data(con)
    profile_raw_data(con)
    con.close()
    print("\n[✓] Ingestion and profiling complete. Connection closed.")