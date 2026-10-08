-- name: setup
CREATE VIEW IF NOT EXISTS daily_returns AS
SELECT
    asset,
    date,
    close,
    close / LAG(close) OVER (PARTITION BY asset ORDER BY date) - 1 AS ret
FROM prices;

-- name: q1_avg_return_by_class
SELECT
    a.asset_class,
    COUNT(*)                         AS observations,
    ROUND(AVG(r.ret) * 100, 4)       AS avg_daily_return_pct
FROM daily_returns r
JOIN assets a ON a.ticker = r.asset
WHERE r.ret IS NOT NULL
GROUP BY a.asset_class
ORDER BY avg_daily_return_pct DESC;

-- name: q2_monthly_returns
WITH month_end AS (
    SELECT asset, substr(date, 1, 7) AS month, MAX(date) AS last_date
    FROM prices
    GROUP BY asset, month
),
monthly AS (
    SELECT m.asset, m.month, p.close
    FROM month_end m
    JOIN prices p ON p.asset = m.asset AND p.date = m.last_date
)
SELECT
    asset,
    month,
    ROUND(close, 2) AS month_end_close,
    ROUND((close / LAG(close) OVER (PARTITION BY asset ORDER BY month) - 1) * 100, 2) AS monthly_return_pct
FROM monthly
ORDER BY asset, month;

-- name: q3_best_worst_days
WITH ranked AS (
    SELECT
        asset, date, ret,
        ROW_NUMBER() OVER (PARTITION BY asset ORDER BY ret DESC) AS best_rank,
        ROW_NUMBER() OVER (PARTITION BY asset ORDER BY ret ASC)  AS worst_rank
    FROM daily_returns
    WHERE ret IS NOT NULL
)
SELECT asset, date, ROUND(ret * 100, 2) AS return_pct, 'best' AS kind
FROM ranked WHERE best_rank <= 5
UNION ALL
SELECT asset, date, ROUND(ret * 100, 2), 'worst'
FROM ranked WHERE worst_rank <= 5
ORDER BY asset, kind, return_pct DESC;

-- name: q4_rolling_vol_30d
WITH w AS (
    SELECT
        asset, date,
        COUNT(*)           OVER win AS n,
        AVG(ret)           OVER win AS mean_r,
        AVG(ret * ret)     OVER win AS mean_sq
    FROM daily_returns
    WHERE ret IS NOT NULL
    WINDOW win AS (PARTITION BY asset ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
)
SELECT
    asset, date,
    ROUND(SQRT(mean_sq - mean_r * mean_r) * SQRT(252) * 100, 2) AS vol_30d_annualized_pct
FROM w
WHERE n = 30
ORDER BY asset, date;

-- name: q5_roe_vs_leverage
-- name: q5_roe_vs_leverage
SELECT
    a.name,
    ROUND(f.roe * 100, 1)           AS roe_pct,
    ROUND(f.debt_to_equity, 2)      AS debt_to_equity,
    ROUND(f.equity_multiplier, 1)   AS equity_multiplier,
    f.is_bank,
    RANK() OVER (ORDER BY f.roe DESC) AS roe_rank,
    CASE WHEN f.is_bank = 0
         THEN RANK() OVER (PARTITION BY f.is_bank ORDER BY f.debt_to_equity ASC)
    END AS leverage_rank_nonbanks
FROM fundamentals f
JOIN assets a ON a.ticker = f.asset
ORDER BY roe_rank;