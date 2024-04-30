# FROM python:3.10.12-alpine
FROM python:3.12-alpine3.19

# Configura la zona horaria a Bogotá
ENV TZ=America/Bogota

RUN apk update && \
    apk add --no-cache nano bash && \
    rm -rf /var/cache/apk/*

# Copia los archivos de la aplicación al contenedor
COPY ./app /app

# Automatizar la hora de ejecucion del contenedor
RUN (crontab -l ; echo "* * * * * python3 /app/app.py") | crontab -
       
# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala los paquetes requeridos
RUN pip3 install --no-cache-dir -r requirements.txt

# Iniciar cron al ejecutar el contenedor
CMD crond -l 2 -f