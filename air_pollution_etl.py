#!/usr/bin/env python
# coding: utf-8

# # API de OpenWeatherMap para data histórica de contaminación del aire

# ## Parámetros de la API:

# * `lat`: Latitud de la ciudad.
# 
# * `lon`: Longitud de la ciudad.
# 
# * `start`: Fecha de inicio en tiempo Unix (zona horaria UTC).
# 
# * `end`: Fecha de fin en tiempo Unix (zona horaria UTC).
# 
# * `appid`: Clave única, que puedes encontrar en la página de tu cuenta denominada `API key`.


get_ipython().run_line_magic('pip', 'install python-dotenv')


# Importar librerias
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import create_engine


# Importar las funciones desde functions.py
from functions import api_key_from_file, extract_data_from_api, transform_data, pwd_from_file, load_data_to_redshift


# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# Accedemos a las variables de entorno
api_key = os.getenv('api_key')
pwd_redshift = os.getenv('pwd_redshift')

# Verificamos que las variables se han cargado correctamente
if api_key and pwd_redshift:
    print("Las variables de entorno se han cargado correctamente.")
else:
    print("Error al cargar las variables de entorno.")


# Definir los parámetros necesarios
api_key = api_key
lat = "-37.2075"
lon = "-73.2368"
end_date = datetime.now()
start_date = end_date - timedelta(days=36*30)


# ## Campos en la respuesta de la API:
# 
# * `coord`: Coordenadas de la ubicación especificada (latitud, longitud).
# 
# * `dt`: Fecha y hora en formato Unix (UTC).
# 
# * `main.aqi`: Índice de Calidad del Aire (Air Quality Index). Valores posibles:
#   - 1 = Bueno
#   - 2 = Aceptable
#   - 3 = Moderado
#   - 4 = Malo
#   - 5 = Muy malo
# 
# * `components.co`: Concentración de CO (Monóxido de Carbono), μg/m³.
# * `components.no`: Concentración de NO (Monóxido de Nitrógeno), μg/m³.
# * `components.no2`: Concentración de NO2 (Dióxido de Nitrógeno), μg/m³.
# * `components.o3`: Concentración de O3 (Ozono), μg/m³.
# * `components.so2`: Concentración de SO2 (Dióxido de Azufre), μg/m³.
# * `components.pm2_5`: Concentración de PM2.5 (Partículas Finas), μg/m³.
# * `components.pm10`: Concentración de PM10 (Partículas Gruesas), μg/m³.
# * `components.nh3`: Concentración de NH3 (Amoníaco), μg/m³.

# ## Extracción de los datos 


# Extraer datos de la API
raw_data = extract_data_from_api(api_key, lat, lon, start_date, end_date)

# Verifica el número de registros o las claves del diccionario
print(f"Número de registros extraídos: {len(raw_data)}")
print(f"Claves disponibles: {list(raw_data.keys())}")


# ## Transformación de los Datos


# Transformar los datos
df = transform_data(raw_data)

df


# ## Checkeo preliminar de valores duplicados y nulos


# Si existen duplicados, eliminarlos
if duplicados > 0:
    df = df.drop_duplicates()
    print(f"Duplicados eliminados. Número de filas restantes: {len(df)}")
else:
    print("No se encontraron duplicados.")


# Si existen datos nulos, eliminar las filas con nulos
if total_nulos > 0:
    df = df.dropna()
    print("Datos nulos eliminados. Número de filas restantes:", len(df))
else:
    print("No se encontraron datos nulos.")


# ## Carga de Datos en Amazon Redshift


#  Definir las credenciales de Redshift
redshift_credentials = {
    'host': 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com',
    'port': '5439',
    'user': 'rincybarra_coderhouse',
    'password': pwd_redshift,
    'dbname': 'data-engineer-database'
}


# Definir el nombre de la tabla en Redshift
table_name = 'air_pollution'

# Cargar los datos en Redshift
load_data_to_redshift(df, table_name, redshift_credentials)


# Mostrar el DataFrame resultante
df


# Verificar tipos de datos
df.info()


# Aplicar funcion de agregación por fecha
df_filtered = df.groupby('date').mean().reset_index()

df_filtered


import matplotlib.pyplot as plt
import seaborn as sns

# Asegurar que la columna 'date' sea tipo datetime
df['date'] = pd.to_datetime(df['date'])

# Extraer el mes y el año de la columna 'date'
df['month'] = df['date'].dt.to_period('M')

# Agrupar por mes y calcular la media de 'pm_2_5'
df_monthly = df.groupby('month').mean().reset_index()

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.plot(df_monthly['month'].astype(str), df_monthly['pm_2_5'], marker='o', linestyle='-', color='darkblue')

# Personalizar el gráfico
plt.title('Evolución de MP 2.5 por Mes')
plt.xlabel('Mes')
plt.ylabel('PM 2.5')
plt.grid(False)
plt.xticks(rotation=90)  # Rotar las etiquetas del eje x para mejor visualización

# Mostrar el gráfico
plt.show()