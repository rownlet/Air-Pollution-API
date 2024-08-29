# Usar la imagen oficial de Python como base
FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt ./

# Instalar los paquetes necesarios desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar una versión específica de werkzeug compatible con flask-wtf
RUN pip install werkzeug==3.0.3

# Instalar una versión específica de pendulum compatible con Airflow
RUN pip install pendulum==2.1.2

# Instalar Apache Airflow
RUN pip install apache-airflow

# Copiar los scripts y el archivo .env a la carpeta de trabajo
COPY air_pollution_etl.py /app/air_pollution_etl.py
COPY .env /app/.env

# Copiar los DAGs a la carpeta de dags de Airflow
COPY dags/ /opt/airflow/dags/

# Exponer el puerto 8080 para Airflow webserver
EXPOSE 8080

# Comando para iniciar Airflow webserver
CMD ["airflow", "webserver"]