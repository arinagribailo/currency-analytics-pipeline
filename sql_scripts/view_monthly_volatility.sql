-- средний курс и волатильность (размах колебаний) по месяцам

CREATE VIEW v_monthly_volatility AS
SELECT
    EXTRACT(YEAR FROM date::date) AS year,
    EXTRACT(MONTH FROM date::date) AS month,
    -- аналитика для USD
    ROUND(AVG(usd_byn)::numeric, 4) AS avg_usd,
    ROUND((MAX(usd_byn) - MIN(usd_byn))::numeric, 4) AS max_usd_drop,
    -- аналитика для EUR
    ROUND(AVG(eur_byn)::numeric, 4) AS avg_eur,
    ROUND((MAX(eur_byn) - MIN(eur_byn))::numeric, 4) AS max_eur_drop
FROM exchange_rates
GROUP BY EXTRACT(YEAR FROM date::date), EXTRACT(MONTH FROM date::date)
ORDER BY year DESC, month DESC;