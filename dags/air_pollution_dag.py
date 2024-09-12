from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functions import extract_data_from_api, transform_data, load_data_to_redshift

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables de entorno
api_key = os.getenv('api_key')
pwd_redshift = os.getenv('pwd_redshift')
email_user = os.getenv('email_user')  # Remitente del correo
email_code = os.getenv('email_code')
email_to = os.getenv('email_to')  # Destinatario del correo

# Función para enviar correos


def enviar_correo(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_code)
        text = msg.as_string()
        server.sendmail(email_user, email_to, text)
        server.quit()
    except Exception as e:
        logging.error(f"Error al enviar el correo: {str(e)}")

# Función personalizada para enviar correo en caso de error


def notify_failure(context):
    task_instance = context.get('task_instance')
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    log_url = task_instance.log_url

    # Enviar correo al detectar un fallo
    subject = f"Tarea fallida en el DAG: {dag_id}"
    body = f"La tarea '{task_id}' ha fallado. Revisa los logs en el siguiente enlace: {log_url}"
    enviar_correo(subject, body)


# Definir argumentos por defecto para el DAG
default_args = {
    'owner': 'rincybarra_coderhouse',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email_on_failure': False,  # Usar callback personalizado
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': notify_failure,  # Notificación en caso de fallo
}

# Definir el DAG principal
dag = DAG(
    'Air_Pollution_DAG',
    default_args=default_args,
    description='DAG para ETL de datos de contaminación del aire',
    schedule_interval=timedelta(days=1),
    catchup=True,
)

# Funciones ETL con envío de correos


def extraer_datos(**kwargs):
    lat = "-37.2075"
    lon = "-73.2368"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=36*30)

    raw_data = extract_data_from_api(api_key, lat, lon, start_date, end_date)
    kwargs['ti'].xcom_push(key='raw_data', value=raw_data)

    # Enviar correo al finalizar la tarea
    enviar_correo('Extracción completada',
                  'La tarea de extracción se completó exitosamente.')


def transformar_datos(**kwargs):
    raw_data = kwargs['ti'].xcom_pull(key='raw_data', task_ids='extraer_datos')
    df = transform_data(raw_data)
    kwargs['ti'].xcom_push(key='transformed_data', value=df)

    # Enviar correo al finalizar la tarea
    enviar_correo('Transformación completada',
                  'La tarea de transformación se completó exitosamente.')


def conexion_redshift(**kwargs):
    redshift_credentials = {
        'host': 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com',
        'port': '5439',
        'user': 'rincybarra_coderhouse',
        'password': pwd_redshift,
        'dbname': 'data-engineer-database'
    }
    df = kwargs['ti'].xcom_pull(
        key='transformed_data', task_ids='transformar_datos')
    load_data_to_redshift(df, 'air_pollution', redshift_credentials)

    # Enviar correo al finalizar la tarea
    enviar_correo('Carga a Redshift completada',
                  'La tarea de carga a Redshift se completó exitosamente.')

# Función final para enviar correo de éxito al final del ETL


def enviar_correo_final():
    enviar_correo('Proceso ETL finalizado',
                  'El proceso ETL completo ha finalizado correctamente.')


# Definir tareas principales en el DAG
task_1 = PythonOperator(
    task_id='extraer_datos',
    python_callable=extraer_datos,
    dag=dag,
)

task_2 = PythonOperator(
    task_id='transformar_datos',
    python_callable=transformar_datos,
    dag=dag,
)

task_3 = PythonOperator(
    task_id='conexion_redshift',
    python_callable=conexion_redshift,
    dag=dag,
)

# Tarea final para enviar el correo del éxito del ETL
task_4 = PythonOperator(
    task_id='correo_final',
    python_callable=enviar_correo_final,
    dag=dag,
)

# Dependencias: Sincronizar las tareas principales y el correo final
task_1 >> task_2 >> task_3 >> task_4
