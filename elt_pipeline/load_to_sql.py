import pandas as pd
from sqlalchemy import create_engine


def upload_to_postgres():
    df = pd.read_csv("nbrb_currency_history_3.csv")


    db_user = 'postgres'
    db_password = 'PASSWORD'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'currency_analytics'

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)

    df.to_sql("exchange_rates", engine, if_exists="replace", index=False)


if __name__ == "__main__":
    upload_to_postgres()