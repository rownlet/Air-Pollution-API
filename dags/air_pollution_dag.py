from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from functions import extract_data_from_api, transform_data, load_data_to_redshift

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables de entorno
api_key = os.getenv('api_key')
pwd_redshift = os.getenv('pwd_redshift')

# Debugging: Verificar que las variables se han cargado correctamente
print(f"API Key Loaded: {api_key}")
print(f"Redshift Password Loaded: {pwd_redshift}")

if not api_key or not pwd_redshift:
    raise ValueError("Las variables de entorno no se han cargado correctamente.")

# Definir argumentos por defecto para el DAG
default_args = {
    'owner': 'rincybarra_coderhouse',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
dag = DAG(
    'Air_Pollution_DAG',
    default_args=default_args,
    description='DAG para ETL de datos de contaminación del aire',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Funciones ETL para Airflow
def extraer_datos(**kwargs):
    lat = "-37.2075"
    lon = "-73.2368"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=36*30)
    
    raw_data = extract_data_from_api(api_key, lat, lon, start_date, end_date)
    kwargs['ti'].xcom_push(key='raw_data', value=raw_data)

def transformar_datos(**kwargs):
    raw_data = kwargs['ti'].xcom_pull(key='raw_data', task_ids='extraer_datos')
    df = transform_data(raw_data)
    kwargs['ti'].xcom_push(key='transformed_data', value=df)

def conexion_redshift(**kwargs):
    redshift_credentials = {
        'host': 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com',
        'port': '5439',
        'user': 'rincybarra_coderhouse',
        'password': pwd_redshift,
        'dbname': 'data-engineer-database'
    }
    df = kwargs['ti'].xcom_pull(key='transformed_data', task_ids='transformar_datos')
    load_data_to_redshift(df, 'air_pollution', redshift_credentials)

# Definir tareas en el DAG

# 1. Extracción
task_1 = PythonOperator(
    task_id='extraer_datos',
    python_callable=extraer_datos,
    provide_context=True,
    dag=dag,
)

# 2. Transformación
task_2 = PythonOperator(
    task_id='transformar_datos',
    python_callable=transformar_datos,
    provide_context=True,
    dag=dag,
)

# 3. Envío de data a Redshift
task_3 = PythonOperator(
    task_id='conexion_redshift',
    python_callable=conexion_redshift,
    provide_context=True,
    dag=dag,
)

# Establecer dependencias entre las tareas
task_1 >> task_2 >> task_3
