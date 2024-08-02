import requests
import time
import json
import pandas as pd
from datetime import datetime
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine

def extract_data_from_api(api_key, lat, lon, start_date, end_date):
    """Extract data from the air pollution API."""
    start_unix = int(start_date.timestamp())
    end_unix = int(end_date.timestamp())
    
    base_url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        'lat': lat,
        'lon': lon,
        'start': start_unix,
        'end': end_unix,
        'appid': api_key
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        response.raise_for_status()

def transform_data(raw_data):
    for item in raw_data['list']:
        item['dt'] = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')

    df = pd.json_normalize(raw_data, 'list', ['coord'])
    df_agrupado = df.drop('coord', axis=1).groupby('dt', as_index=False).mean()

    df_agrupado.rename(columns={
        'dt': 'date',
        'main.aqi': 'aqi',
        'components.co': 'co',
        'components.no': 'no',
        'components.no2': 'no2',
        'components.o3': 'o3',
        'components.so2': 'so2',
        'components.pm2_5': 'pm_2_5',
        'components.pm10': 'pm_10',
        'components.nh3': 'nh3'
    }, inplace=True)

    return df_agrupado

def load_data_to_redshift(df, table_name, redshift_credentials):
    """Load DataFrame into Amazon Redshift."""
    conn = psycopg2.connect(
        host=redshift_credentials['host'],
        dbname=redshift_credentials['dbname'],
        user=redshift_credentials['user'],
        password=redshift_credentials['password'],
        port=redshift_credentials['port']
    )
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                date VARCHAR,
                aqi FLOAT,
                co FLOAT,
                no FLOAT,
                no2 FLOAT,
                o3 FLOAT,
                so2 FLOAT,
                pm_2_5 FLOAT,
                pm_10 FLOAT,
                nh3 FLOAT,
                ingestion_time TIMESTAMP DEFAULT GETDATE()
            )
        """)
        conn.commit()

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name}")
        conn.commit()

    def execute_values(conn, df, table):
        tuples = [tuple(x) for x in df.to_numpy()]
        cols = ','.join(list(df.columns))
        query  = f"INSERT INTO {table}({cols}) VALUES %s"
        cursor = conn.cursor()
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("La inserción fue exitosa")
        cursor.close()

    execute_values(conn, df, table_name)

    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        results = cur.fetchall()
        for row in results:
            print(row)
        cur.close()

    conn.close()
