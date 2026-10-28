-- sql/03_funnel_staging.sql

-- 1. Create Clean Base Events Table
CREATE OR REPLACE TABLE CLEAN_EVENTS AS
    SELECT
        EVENT_TIME,
        EVENT_TYPE,
        PRODUCT_ID,
        CATEGORY_ID,
        COALESCE(BRAND,
        'Unknown') AS BRAND,
        PRICE,
        USER_ID,
        USER_SESSION
    FROM
        RAW_EVENTS
    WHERE
        USER_SESSION IS NOT NULL
        AND PRICE > 0;

-- 2. Build Session-Level Funnel Aggregation
CREATE OR REPLACE TABLE SESSION_FUNNEL_SUMMARY AS WITH SESSION_EVENTS AS (
    SELECT
        USER_SESSION,
        USER_ID,
        MIN(EVENT_TIME) AS SESSION_START,
        MAX(EVENT_TIME) AS SESSION_END,
        EPOCH(MAX(EVENT_TIME) - MIN(EVENT_TIME)) AS SESSION_DURATION_SECONDS,
        COUNT(*) AS TOTAL_EVENTS,
 
        -- Event count flags
        SUM(
            CASE
                WHEN EVENT_TYPE = 'view' THEN
                    1
                ELSE
                    0
            END) AS VIEW_COUNT,
        SUM(
            CASE
                WHEN EVENT_TYPE = 'cart' THEN
                    1
                ELSE
                    0
            END) AS CART_COUNT,
        SUM(
            CASE
                WHEN EVENT_TYPE = 'remove_from_cart' THEN
                    1
                ELSE
                    0
            END) AS REMOVE_COUNT,
        SUM(
            CASE
                WHEN EVENT_TYPE = 'purchase' THEN
                    1
                ELSE
                    0
            END) AS PURCHASE_COUNT,
 
        -- Monetary metrics
        SUM(
            CASE
                WHEN EVENT_TYPE = 'cart' THEN
                    PRICE
                ELSE
                    0
            END) AS CART_VALUE,
        SUM(
            CASE
                WHEN EVENT_TYPE = 'purchase' THEN
                    PRICE
                ELSE
                    0
            END) AS PURCHASE_VALUE
    FROM
        CLEAN_EVENTS
    GROUP BY
        USER_SESSION,
        USER_ID
)
    SELECT
        USER_SESSION,
        USER_ID,
        SESSION_START,
        SESSION_END,
        SESSION_DURATION_SECONDS,
        TOTAL_EVENTS,
        VIEW_COUNT,
        CART_COUNT,
        REMOVE_COUNT,
        PURCHASE_COUNT,
        CART_VALUE,
        PURCHASE_VALUE,
 
        -- Funnel Stage Booleans (1/0)
        CASE
            WHEN VIEW_COUNT > 0 THEN
                1
            ELSE
                0
        END AS STEP_VIEW,
        CASE
            WHEN CART_COUNT > 0 THEN
                1
            ELSE
                0
        END AS STEP_CART,
        CASE
            WHEN PURCHASE_COUNT > 0 THEN
                1
            ELSE
                0
        END AS STEP_PURCHASE,
 
        -- Cart Abandonment Definition: Added to cart, but ZERO purchases in that session
        CASE
            WHEN CART_COUNT > 0 AND PURCHASE_COUNT = 0 THEN
                1
            ELSE
                0
        END AS IS_CART_ABANDONED,
 
        -- Immediate Bounce: only 1 event in the session and duration is 0
        CASE
            WHEN TOTAL_EVENTS = 1 AND SESSION_DURATION_SECONDS = 0 THEN
                1
            ELSE
                0
        END AS IS_BOUNCE
    FROM
        SESSION_EVENTS;