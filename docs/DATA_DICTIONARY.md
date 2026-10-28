# Data Dictionary & Cleaning Rules

## Raw Table: `raw_events`
- Source: October 2019 Cosmetics Shop Event Logs (4,102,283 rows)
- Time Range: 2019-10-01 to 2019-10-31 UTC

| Column          | Type          | Null %      | Integrity Rule / Action Required                                |
| :-------------- | :------------ | :---------- | :-------------------------------------------------------------- |
| `event_time`    | TIMESTAMPTZ   | 0.00%       | Valid timestamp. Used for session windowing.                    |
| `event_type`    | VARCHAR       | 0.00%       | Values: `view`, `cart`, `remove_from_cart`, `purchase`.         |
| `product_id`    | BIGINT        | 0.00%       | Primary product identifier.                                     |
| `category_id`   | BIGINT        | 0.00%       | Primary category taxonomy key (use instead of `category_code`). |
| `category_code` | VARCHAR       | 98.36%      | High null rate. Flagged as unreliable for primary grouping.     |
| `brand`         | VARCHAR       | 40.45%      | Replace NULLs with `'Unknown'`.                                 |
| `price`         | DECIMAL(10,2) | 0.15% (<=0) | Exclude `<= 0` when calculating gross merchandise value (GMV).  |
| `user_id`       | BIGINT        | 0.00%       | Persistent user account identifier.                             |
| `user_session`  | VARCHAR       | 0.02%       | Must filter `WHERE user_session IS NOT NULL` for funnel paths.  |