import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine, text

DB_USER = 'postgres'
DB_PASSWORD = 'PASSWORD'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'currency_analytics'

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)


def get_last_date_from_db():
    # проверяем последнюю дату в бд
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(date) FROM exchange_rates"))
            last_date = result.scalar()
            if last_date:
                return pd.to_datetime(last_date).date()
    except Exception:
        pass
    return (datetime.now() - timedelta(days=3 * 365)).date()


def update_currency_pipeline():

    start_date = get_last_date_from_db()
    today = datetime.now().date()

    # если данные есть, останавливаем
    if start_date >= today:
        print(f" Все данные уже актуальны по {start_date} .")
        return

    # если есть недостающие данные, скачиваем со следующего дня
    start_date_fetch = start_date + timedelta(days=1)
    print(f"База обновлена по {start_date}. Докачиваю данные с {start_date_fetch} по {today}...")

    currencies = {'431': 'usd_byn', '451': 'eur_byn', '456': 'rub_byn', '462': 'cny_byn', '440': 'pln_byn'}
    final_df = pd.DataFrame()

    start_str = start_date_fetch.strftime('%Y-%m-%d')
    end_str = today.strftime('%Y-%m-%d')

    for cur_id, col_name in currencies.items():
        url = f"https://www.nbrb.by/api/exrates/rates/dynamics/{cur_id}?startDate={start_str}&endDate={end_str}"

        for attempt in range(1, 4):
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df_period = pd.DataFrame(data)
                        df_period = df_period[['Date', 'Cur_OfficialRate']].copy()
                        df_period.rename(columns={'Cur_OfficialRate': col_name}, inplace=True)
                        df_period['Date'] = pd.to_datetime(df_period['Date']).dt.date

                        if final_df.empty:
                            final_df = df_period
                        else:
                            final_df = pd.merge(final_df, df_period, on='Date', how='outer')
                    break
                time.sleep(1)
            except Exception:
                time.sleep(3)

    if not final_df.empty:
        final_df.sort_values(by='Date', inplace=True)
        final_df.rename(columns={'Date': 'date'}, inplace=True)

        # добавляем данные в конец таблицы
        final_df.to_sql("exchange_rates", engine, if_exists="append", index=False)
        print(f"Успешно добавлено новых строк в Postgres: {len(final_df)}")
    else:
        print(" Новых курсов валют на сайте банка пока не появилось.")


if __name__ == "__main__":
    update_currency_pipeline()