-- сравнение текущего курса с историческими пиками (макс и мин значения)

CREATE VIEW v_history_peaks AS
SELECT
    date::date AS date,
    usd_byn,
    -- считаем пики для доллара
    MAX(usd_byn) OVER (ORDER BY date::date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS usd_all_time_high,
    MIN(usd_byn) OVER (ORDER BY date::date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS usd_all_time_low,

    eur_byn,
    -- считаем пики для евро
    MAX(eur_byn) OVER (ORDER BY date::date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS eur_all_time_high,
    MIN(eur_byn) OVER (ORDER BY date::date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS eur_all_time_low
FROM exchange_rates
ORDER BY date DESC;