import requests
import time
import json
import pandas as pd
from datetime import datetime
import psycopg2
import psycopg2.extras as extras

# Función para leer la clave de API desde api_key.txt
def api_key_from_file():
    """
    Lee la clave de API desde el archivo api_key.txt.

    :return: La clave de API como una cadena de texto.
    """
    try:
        with open("api_key.txt", 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print("El archivo api_key.txt no se encuentra. Por favor suba el archivo con la clave de API.")
        return None

def extract_data_from_api(api_key, lat, lon, start_date, end_date):
    """
    Extrae datos de la API de contaminación del aire.

    :param api_key: Clave de API para autenticar la solicitud.
    :param lat: Latitud de la ubicación.
    :param lon: Longitud de la ubicación.
    :param start_date: Fecha de inicio (objeto datetime).
    :param end_date: Fecha de fin (objeto datetime).
    :return: Datos de contaminación del aire en formato JSON.
    """
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
    """
    Transforma los datos crudos de contaminación del aire en un DataFrame de pandas.

    :param raw_data: Datos crudos de contaminación del aire en formato JSON.
    :return: DataFrame de pandas con los datos transformados.
    """
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

# Función para leer la contraseña desde pwd_redshift.txt
def pwd_from_file():
    """
    Lee la contraseña desde el archivo pwd_redshift.txt.

    :return: La contraseña como una cadena de texto.
    """
    try:
        with open("pwd_redshift.txt", 'r') as file:
            password = file.read().strip()
        return password
    except FileNotFoundError:
        print("El archivo pwd_redshift.txt no se encuentra. Por favor suba el archivo con la contraseña.")
        return None

def load_data_to_redshift(df, table_name, redshift_credentials):
    """
    Carga un DataFrame en Amazon Redshift.

    :param df: DataFrame de pandas con los datos a cargar.
    :param table_name: Nombre de la tabla en Redshift.
    :param redshift_credentials: Diccionario con las credenciales de Redshift.
    """
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
        """
        Inserta múltiples filas en una tabla de Redshift.

        :param conn: Conexión a la base de datos.
        :param df: DataFrame de pandas con los datos a insertar.
        :param table: Nombre de la tabla en Redshift.
        """
        tuples = [tuple(x) for x in df.to_numpy()]
        cols = ','.join(list(df.columns))
        query = f"INSERT INTO {table}({cols}) VALUES %s"
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