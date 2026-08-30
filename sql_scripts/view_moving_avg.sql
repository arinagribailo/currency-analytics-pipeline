-- скользящее среднее за 7 дней и приведение курсов к 1 единице

CREATE VIEW v_bi_exchange_rates AS
SELECT
    date::date AS date,
    usd_byn,
    eur_byn,
    ROUND((rub_byn / 100)::numeric, 4) AS rub_byn_single,
    ROUND((cny_byn / 10)::numeric, 4) AS cny_byn_single,
    ROUND((pln_byn / 10)::numeric, 4) AS pln_byn_single,
    ROUND(
        AVG(usd_byn) OVER (
            ORDER BY date::date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::numeric, 4
    ) AS usd_moving_avg_7
FROM exchange_rates
ORDER BY date DESC;