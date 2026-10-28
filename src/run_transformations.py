"""
src/run_transformations.py
Executes the staging and funnel modeling SQL against analytics.duckdb.
"""

import duckdb
import time

DB_PATH = "database/analytics.duckdb"
SQL_FILE = "sql/03_funnel_staging.sql"

def run_transformations():
    print(f"Connecting to DuckDB: {DB_PATH}")
    con = duckdb.connect(DB_PATH)
    
    print(f"Reading SQL transformation logic from {SQL_FILE}...")
    with open(SQL_FILE, "r") as f:
        sql_script = f.read()

    start = time.time()
    # DuckDB execute multiple statements
    con.execute(sql_script)
    duration = time.time() - start
    print(f"[✓] Staging tables materialized in {duration:.2f} seconds.")

    # Verification Query: Macro Funnel Conversion Rates
    print("\n" + "="*50)
    print("SESSION-LEVEL CONVERSION FUNNEL METRICS")
    print("="*50)
    
    funnel_metrics = con.execute("""
        SELECT
            COUNT(*) AS total_sessions,
            SUM(step_view) AS sessions_with_view,
            SUM(step_cart) AS sessions_with_cart,
            SUM(step_purchase) AS sessions_with_purchase,
            SUM(is_cart_abandoned) AS abandoned_cart_sessions,
            -- Conversion Rates
            ROUND(SUM(step_cart) * 100.0 / NULLIF(SUM(step_view), 0), 2) AS view_to_cart_cvr_pct,
            ROUND(SUM(step_purchase) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_to_purchase_cvr_pct,
            ROUND(SUM(step_purchase) * 100.0 / COUNT(*), 2) AS overall_session_cvr_pct,
            -- Cart Abandonment Rate
            ROUND(SUM(is_cart_abandoned) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_abandonment_rate_pct,
            -- Abandoned Revenue
            ROUND(SUM(CASE WHEN is_cart_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS lost_cart_value_dollars
        FROM session_funnel_summary;
    """).df()
    
    print(funnel_metrics.T.to_string(header=False))
    con.close()

if __name__ == "__main__":
    run_transformations()