"""
src/export_bi_layers.py
Aggregates and exports clean dimensional tables from DuckDB into data/processed/
for rapid ingestion into Power BI or Tableau.
"""

import duckdb
import os
import time

DB_PATH = "database/analytics.duckdb"
EXPORT_DIR = "data/processed"

def export_bi_tables():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)
    print(f"Connected to {DB_PATH}. Exporting BI data marts to {EXPORT_DIR}/...")
    start = time.time()

    # 1. Fact Table: Daily Funnel Metrics Time-Series
    print("1. Exporting fact_daily_funnel...")
    con.execute(f"""
        COPY (
            SELECT
                session_start::DATE AS event_date,
                visitor_segment,
                COUNT(*) AS total_sessions,
                SUM(step_view) AS views,
                SUM(step_cart) AS carts,
                SUM(step_purchase) AS purchases,
                SUM(is_cart_abandoned) AS cart_abandonments,
                ROUND(SUM(cart_value), 2) AS total_cart_value,
                ROUND(SUM(purchase_value), 2) AS total_revenue,
                ROUND(SUM(CASE WHEN is_cart_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS abandoned_cart_value
            FROM session_segmented
            GROUP BY 1, 2
            ORDER BY 1, 2
        ) TO '{EXPORT_DIR}/fact_daily_funnel.csv' (HEADER, DELIMITER ',');
    """)

    # 2. Dimension / Mart Table: Category & Brand Funnel Leakage
    print("2. Exporting mart_brand_funnel...")
    con.execute(f"""
        COPY (
            SELECT
                brand,
                COUNT(*) AS total_interactions,
                SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS brand_views,
                SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS brand_carts,
                SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS brand_purchases,
                ROUND(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 2) AS brand_revenue,
                ROUND(SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) * 100.0 / 
                      NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0), 2) AS view_to_cart_pct,
                ROUND(SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) * 100.0 / 
                      NULLIF(SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END), 0), 2) AS cart_to_purchase_pct
            FROM clean_events
            GROUP BY brand
            HAVING brand_views >= 500  -- Filter long-tail noise
            ORDER BY brand_revenue DESC
        ) TO '{EXPORT_DIR}/mart_brand_funnel.csv' (HEADER, DELIMITER ',');
    """)

    # 3. Dimension Table: Session Duration & Loyalty Breakdown
    print("3. Exporting dim_duration_loyalty...")
    con.execute(f"""
        COPY (
            SELECT
                visitor_segment,
                duration_bracket,
                COUNT(*) AS total_sessions,
                SUM(step_cart) AS carts,
                SUM(step_purchase) AS purchases,
                SUM(is_cart_abandoned) AS abandoned_carts,
                ROUND(SUM(step_purchase) * 100.0 / COUNT(*), 2) AS session_cvr_pct,
                ROUND(SUM(is_cart_abandoned) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_abandonment_pct,
                ROUND(AVG(session_duration_seconds), 1) AS avg_duration_sec
            FROM session_segmented
            GROUP BY visitor_segment, duration_bracket
            ORDER BY visitor_segment, duration_bracket
        ) TO '{EXPORT_DIR}/dim_duration_loyalty.csv' (HEADER, DELIMITER ',');
    """)

    duration = time.time() - start
    print(f"\n[✓] All 3 BI tables exported successfully in {duration:.2f} seconds.")

    # Print file sizes
    print("\nGenerated files in data/processed/:")
    for f in os.listdir(EXPORT_DIR):
        fpath = os.path.join(EXPORT_DIR, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f" - {f} ({size_kb:.1f} KB)")

    con.close()

if __name__ == "__main__":
    export_bi_tables()