# Usar Python 3.12 Alpine (más segura y liviana)
FROM python:3.12-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para Alpine
RUN apk update && apk add --no-cache \
    build-base \
    curl \
    git \
    gcc \
    musl-dev \
    linux-headers

# Copiar archivos de requirements primero para aprovechar el cache de Docker
COPY app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ .

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Configurar Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]