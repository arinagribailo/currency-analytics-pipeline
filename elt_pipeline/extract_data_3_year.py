import requests
import pandas as pd
from datetime import datetime, timedelta
import time


def get_nbrb_data():
    # справочник валют НБРБ
    currencies = {
        '431': 'usd_byn',
        '451': 'eur_byn',
        '456': 'rub_byn',
        '462': 'cny_byn',
        '440': 'pln_byn'
    }

    # период на 3 отрезка по 1 году.
    # список пар (дата_начала, дата_конца)
    today = datetime.now()
    periods = [
        (today - timedelta(days=365), today),  # последний год
        (today - timedelta(days=2 * 365), today - timedelta(days=366)),  # предпоследний год
        (today - timedelta(days=3 * 365), today - timedelta(days=2 * 366))  # три года назад
    ]

    final_df = pd.DataFrame()

    # перебираем валюты по очереди
    for cur_id, col_name in currencies.items():
        currency_all_years = pd.DataFrame()

        # для каждой валюты делаем 3 отдельных запроса в базу банка
        for start_date, end_date in periods:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f"https://www.nbrb.by/api/exrates/rates/dynamics/{cur_id}?startDate={start_str}&endDate={end_str}"

            # логика повторных попыток при таймауте
            success = False
            for attempt in range(1, 4):
                try:
                    response = requests.get(url, timeout=20)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            df_period = pd.DataFrame(data)
                            # UNION ALL
                            currency_all_years = pd.concat([currency_all_years, df_period], ignore_index=True)
                        success = True
                        break
                    else:
                        print(f" Попытка {attempt} неуспешна (Статус {response.status_code})")

                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    time.sleep(3)

            if not success:
                print(f" Ошибка на периоде {start_str} - {end_str}")

            time.sleep(0.5)

        # если данные по валюте собрались за все года, обрабатываем их
        if not currency_all_years.empty:
            currency_all_years = currency_all_years[['Date', 'Cur_OfficialRate']].copy()
            currency_all_years.rename(columns={'Cur_OfficialRate': col_name}, inplace=True)
            currency_all_years['Date'] = pd.to_datetime(currency_all_years['Date']).dt.date

            # удаляем дубликаты дат, если они появились
            currency_all_years.drop_duplicates(subset=['Date'], inplace=True)

            # склеиваем столбцы по дате
            if final_df.empty:
                final_df = currency_all_years
            else:
                final_df = pd.merge(final_df, currency_all_years, on='Date', how='outer')

    if not final_df.empty:
        final_df.sort_values(by='Date', inplace=True)
        final_df.rename(columns={'Date': 'date'}, inplace=True)
        print(f"Данные собраны, итого строк за 3 года: {len(final_df)}")

    return final_df


if __name__ == "__main__":
    df = get_nbrb_data()
    if not df.empty:
        print("\nПервые 5 строк:")
        print(df.head())
        print("\nПоследние 5 строк:")
        print(df.tail())

        df.to_csv("nbrb_currency_history_3.csv", index=False)
        print("\n файл сохранен")