-- sql/04_funnel_segmentation.sql

-- 1. Create User Loyalty / Visit Sequence Table
CREATE OR REPLACE TABLE SESSION_SEGMENTED AS WITH VISITOR_RANKED AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY USER_ID ORDER BY SESSION_START) AS USER_SESSION_SEQ
    FROM
        SESSION_FUNNEL_SUMMARY
)
    SELECT
        *,
        CASE
            WHEN USER_SESSION_SEQ = 1 THEN
                'New Visitor'
            ELSE
                'Returning Visitor'
        END AS VISITOR_SEGMENT,
        CASE
            WHEN SESSION_DURATION_SECONDS < 60 THEN
                '< 1 min (Bounce/Skim)'
            WHEN SESSION_DURATION_SECONDS BETWEEN 60 AND 300 THEN
                '1 - 5 mins (Quick Browse)'
            WHEN SESSION_DURATION_SECONDS BETWEEN 301 AND 900 THEN
                '5 - 15 mins (Engaged)'
            ELSE
                '> 15 mins (Deep Dive)'
        END AS DURATION_BRACKET
    FROM
        VISITOR_RANKED;

-- 2. Aggregate Comparison: New vs. Returning
CREATE OR REPLACE TABLE SEGMENT_LOYALTY_SUMMARY AS
    SELECT
        VISITOR_SEGMENT,
        COUNT(*) AS TOTAL_SESSIONS,
        SUM(STEP_VIEW) AS VIEWS,
        SUM(STEP_CART) AS CARTS,
        SUM(STEP_PURCHASE) AS PURCHASES,
        SUM(IS_CART_ABANDONED) AS CART_ABANDONMENTS,
        ROUND(SUM(STEP_CART) * 100.0 / NULLIF(SUM(STEP_VIEW),
        0),
        2) AS VIEW_TO_CART_PCT,
        ROUND(SUM(STEP_PURCHASE) * 100.0 / NULLIF(SUM(STEP_CART),
        0),
        2) AS CART_TO_PURCHASE_PCT,
        ROUND(SUM(STEP_PURCHASE) * 100.0 / COUNT(*),
        2) AS SESSION_CVR_PCT,
        ROUND(SUM(IS_CART_ABANDONED) * 100.0 / NULLIF(SUM(STEP_CART),
        0),
        2) AS CART_ABANDONMENT_PCT,
        ROUND(AVG(CART_VALUE),
        2) AS AVG_CART_VALUE,
        ROUND(SUM(
            CASE
                WHEN IS_CART_ABANDONED = 1 THEN
                    CART_VALUE
                ELSE
                    0
            END),
        2) AS TOTAL_LOST_CART_VALUE
    FROM
        SESSION_SEGMENTED
    GROUP BY
        VISITOR_SEGMENT;

-- 3. Aggregate Comparison: Session Duration Brackets
CREATE OR REPLACE TABLE SEGMENT_DURATION_SUMMARY AS
    SELECT
        DURATION_BRACKET,
        COUNT(*) AS TOTAL_SESSIONS,
        SUM(STEP_PURCHASE) AS PURCHASES,
        ROUND(SUM(STEP_PURCHASE) * 100.0 / COUNT(*),
        2) AS SESSION_CVR_PCT,
        ROUND(SUM(IS_CART_ABANDONED) * 100.0 / NULLIF(SUM(STEP_CART),
        0),
        2) AS CART_ABANDONMENT_PCT
    FROM
        SESSION_SEGMENTED
    GROUP BY
        DURATION_BRACKET
    ORDER BY
        SESSION_CVR_PCT DESC;