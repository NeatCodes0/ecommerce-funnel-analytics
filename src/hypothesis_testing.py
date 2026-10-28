"""
src/hypothesis_testing.py
Creates visitor loyalty and session engagement segments directly in DuckDB,
then runs two-proportion Z-tests and Chi-Square tests of independence.
"""

import duckdb
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import chi2_contingency

DB_PATH = "database/analytics.duckdb"

def run_segmentation_and_stats():
    print(f"Connecting to DuckDB: {DB_PATH}")
    con = duckdb.connect(DB_PATH)

    # Step 1: Create session_segmented table
    print("1. Building session_segmented table...")
    con.execute("""
        CREATE OR REPLACE TABLE session_segmented AS
        WITH visitor_ranked AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY session_start) AS user_session_seq
            FROM session_funnel_summary
        )
        SELECT
            *,
            CASE 
                WHEN user_session_seq = 1 THEN 'New Visitor'
                ELSE 'Returning Visitor'
            END AS visitor_segment,
            CASE 
                WHEN session_duration_seconds < 60 THEN '< 1 min (Bounce/Skim)'
                WHEN session_duration_seconds BETWEEN 60 AND 300 THEN '1 - 5 mins (Quick Browse)'
                WHEN session_duration_seconds BETWEEN 301 AND 900 THEN '5 - 15 mins (Engaged)'
                ELSE '> 15 mins (Deep Dive)'
            END AS duration_bracket
        FROM visitor_ranked;
    """)

    # Step 2: Create segment_loyalty_summary table
    print("2. Building segment_loyalty_summary table...")
    con.execute("""
        CREATE OR REPLACE TABLE segment_loyalty_summary AS
        SELECT
            visitor_segment,
            COUNT(*) AS total_sessions,
            SUM(step_view) AS views,
            SUM(step_cart) AS carts,
            SUM(step_purchase) AS purchases,
            SUM(is_cart_abandoned) AS cart_abandonments,
            ROUND(SUM(step_cart) * 100.0 / NULLIF(SUM(step_view), 0), 2) AS view_to_cart_pct,
            ROUND(SUM(step_purchase) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_to_purchase_pct,
            ROUND(SUM(step_purchase) * 100.0 / COUNT(*), 2) AS session_cvr_pct,
            ROUND(SUM(is_cart_abandoned) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_abandonment_pct,
            ROUND(AVG(cart_value), 2) AS avg_cart_value,
            ROUND(SUM(CASE WHEN is_cart_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS total_lost_cart_value
        FROM session_segmented
        GROUP BY visitor_segment;
    """)

    # Step 3: Create segment_duration_summary table
    print("3. Building segment_duration_summary table...")
    con.execute("""
        CREATE OR REPLACE TABLE segment_duration_summary AS
        SELECT
            duration_bracket,
            COUNT(*) AS total_sessions,
            SUM(step_purchase) AS purchases,
            ROUND(SUM(step_purchase) * 100.0 / COUNT(*), 2) AS session_cvr_pct,
            ROUND(SUM(is_cart_abandoned) * 100.0 / NULLIF(SUM(step_cart), 0), 2) AS cart_abandonment_pct
        FROM session_segmented
        GROUP BY duration_bracket
        ORDER BY session_cvr_pct DESC;
    """)

    # Fetch tables
    loyalty_df = con.execute("SELECT * FROM segment_loyalty_summary;").df()
    print("\n" + "="*70)
    print("VISITOR LOYALTY SEGMENTATION SUMMARY")
    print("="*70)
    print(loyalty_df.to_string(index=False))

    duration_df = con.execute("SELECT * FROM segment_duration_summary;").df()
    print("\n" + "="*70)
    print("SESSION DURATION BRACKET SUMMARY")
    print("="*70)
    print(duration_df.to_string(index=False))

    # --- STATISTICAL HYPOTHESIS TESTING ---
    print("\n" + "="*70)
    print("HYPOTHESIS TEST 1: TWO-PROPORTION Z-TEST (NEW VS. RETURNING)")
    print("="*70)

    # Safe extraction
    new_data = loyalty_df[loyalty_df['visitor_segment'] == 'New Visitor'].iloc[0]
    ret_data = loyalty_df[loyalty_df['visitor_segment'] == 'Returning Visitor'].iloc[0]

    purchases = np.array([int(ret_data['purchases']), int(new_data['purchases'])])
    carts = np.array([int(ret_data['carts']), int(new_data['carts'])])

    z_stat, p_val = proportions_ztest(purchases, carts)

    print(f"Returning Visitor Cart CVR : {ret_data['cart_to_purchase_pct']}% ({ret_data['purchases']:,} / {ret_data['carts']:,})")
    print(f"New Visitor Cart CVR       : {new_data['cart_to_purchase_pct']}% ({new_data['purchases']:,} / {new_data['carts']:,})")
    print(f"Z-Statistic                : {z_stat:.4f}")
    print(f"p-value                    : {p_val:.4e}")

    if p_val < 0.05:
        print("[✓] REJECT H0: Difference between New and Returning conversion is statistically significant.")
    else:
        print("[!] FAIL TO REJECT H0: Difference is not statistically significant.")

    print("\n" + "="*70)
    print("HYPOTHESIS TEST 2: CHI-SQUARE TEST (DURATION VS. PURCHASE)")
    print("="*70)

    duration_matrix = con.execute("""
        SELECT 
            duration_bracket,
            SUM(step_purchase) AS purchased,
            COUNT(*) - SUM(step_purchase) AS not_purchased
        FROM session_segmented
        GROUP BY duration_bracket
        ORDER BY duration_bracket;
    """).df()

    contingency_table = duration_matrix[['purchased', 'not_purchased']].values
    chi2, p_chi2, dof, _ = chi2_contingency(contingency_table)

    print(f"Chi-Square Statistic       : {chi2:.4f}")
    print(f"Degrees of Freedom         : {dof}")
    print(f"p-value                    : {p_chi2:.4e}")

    if p_chi2 < 0.05:
        print("[✓] REJECT H0: Session engagement duration significantly impacts purchase likelihood.")

    con.close()
    print("\n[✓] Statistical tests completed successfully.")

if __name__ == "__main__":
    run_segmentation_and_stats()