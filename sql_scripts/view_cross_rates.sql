-- расчет кросс-курсов валют (отношение доллара к другим валютам)

CREATE OR REPLACE VIEW v_cross_rates AS
SELECT
    date::date AS date,
    ROUND((usd_byn / (rub_byn / 100))::numeric, 2) AS usd_to_rub, -- сколько RUB за 1 USD
    ROUND((eur_byn / usd_byn)::numeric, 4) AS eur_to_usd,         -- курс EUR/USD через белорусский рубль
    ROUND((usd_byn / (cny_byn / 10))::numeric, 2) AS usd_to_cny   -- сколько CNY за 1 USD
FROM exchange_rates
ORDER BY date DESC;