# Proyecto de Análisis de Datos de Contaminación del Aire

## Descripción General

Este proyecto se centra en la recolección, transformación y carga de datos de contaminación del aire utilizando un enfoque basado en procesos ETL. Los datos son extraídos desde una API pública, transformados para cumplir con los estándares de análisis y finalmente cargados en una base de datos Amazon Redshift para su posterior estudio. El proyecto está diseñado para operar de manera automatizada mediante Apache Airflow, garantizando la integridad y la disponibilidad continua de los datos.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

- **`air_pollution_etl.py`**: Script principal que orquesta el flujo ETL utilizando Apache Airflow.
- **`functions.py`**: Módulo Python que encapsula las funciones esenciales para la extracción de datos, transformación y carga en Redshift.
- **`docker-compose.yml`**: Archivo de configuración de Docker Compose para iniciar los servicios requeridos, incluidos Airflow y PostgreSQL.
- **`Dockerfile`**: Define la imagen Docker para el entorno de Airflow.
- **`requirements.txt`**: Lista de dependencias de Python necesarias para la ejecución del proyecto.
- **`.env`**: Archivo que contiene las variables de entorno sensibles como API keys y credenciales de la base de datos Redshift.

## Configuración

### Requisitos Previos

Para poner en marcha este proyecto, asegúrese de contar con los siguientes requisitos:

- Docker y Docker Compose instalados
- Python 3.7 o superior
- Instalación de las dependencias especificadas en `requirements.txt`

### Pasos de Instalación

1. **Clonar el Repositorio:**

    Clone el repositorio en su máquina local:
    ```sh
    git clone https://github.com/tu-repo/analisis-datos-contaminacion-aire.git
    cd analisis-datos-contaminacion-aire
    ```

2. **Instalación de Dependencias:**

    Instale las bibliotecas de Python necesarias para el proyecto:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configuración del Entorno:**

    Configure el archivo `.env` con su `API_KEY` y credenciales de Redshift:
    ```env
    api_key=su_api_key
    pwd_redshift=su_contraseña_redshift
    ```

### Ejecución del Proyecto

1. **Iniciar los Servicios:**

    Inicie los servicios de Docker necesarios para ejecutar el entorno de Airflow:
    ```sh
    docker-compose up --build
    ```

2. **Acceso a la Interfaz de Airflow:**

    Una vez que los servicios estén activos, acceda a la interfaz web de Airflow. Desde allí, puede activar el DAG `BC_dag` para ejecutar el flujo de trabajo ETL de manera automatizada.

### Solución de Problemas

Si tiene problemas para iniciar sesión en la interfaz web de Airflow con las credenciales por defecto, puede crear un nuevo usuario administrador ejecutando el siguiente comando en su terminal:

`docker-compose run webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin`

## Mejora Continua

Estamos comprometidos con la mejora continua de este proyecto. Algunas sugerencias para futuros desarrollos incluyen:

1. **Pruebas Unitarias:**

    Desarrollar un conjunto de pruebas unitarias para las funciones en `functions.py`, asegurando la calidad y el funcionamiento esperado del código.

2. **Automatización y Escalabilidad:**

    Considerar la expansión de la automatización, incorporando técnicas de escalabilidad horizontal para manejar volúmenes de datos mayores.

## Ideas para Nuevos Proyectos

Este proyecto puede ser la base para nuevas iniciativas. Algunas ideas incluyen:

1. **Análisis de Correlación Multivariada:**

    Explorar correlaciones entre la calidad del aire y otros factores, como indicadores de salud pública.

2. **Modelos Predictivos:**

    Utilizar machine learning para predecir tendencias en la calidad del aire en función de datos históricos y condiciones meteorológicas.

3. **Integración de Datos de Fuentes Diversas:**

    Combinar estos datos con otros conjuntos de datos ambientales para crear un análisis más comprensivo y holístico.

4. **Desarrollo de Aplicaciones:**

    Crear una aplicación móvil que ofrezca actualizaciones en tiempo real sobre la calidad del aire, personalizadas por ubicación.

## Contribuciones

Las contribuciones son bienvenidas. Si desea colaborar, siga los siguientes pasos:

1. **Fork el Repositorio:**

    Haga un fork del repositorio para trabajar en su copia.

2. **Crear una Nueva Rama:**

    Cree una nueva rama para su funcionalidad o corrección:
    ```sh
    git checkout -b feature-branch
    ```

3. **Realizar Cambios:**

    Realice las modificaciones necesarias y haga commit de los cambios:
    ```sh
    git commit -am 'Agregar nueva característica'
    ```

4. **Enviar Cambios:**

    Empuje la rama a su repositorio:
    ```sh
    git push origin feature-branch
    ```

5. **Crear una Pull Request:**

    Cree una pull request para que sus cambios sean revisados e integrados.

## Agradecimientos

Agradecer a todos los desarrolladores y colaboradores cuyas herramientas y bibliotecas han sido fundamentales para este proyecto. Apreciamos el continuo apoyo de la comunidad y las contribuciones recibidas.
