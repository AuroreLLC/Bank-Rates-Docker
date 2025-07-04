# syntax = docker/dockerfile:1.2

# Usar Python 3.12 slim (más compatible)
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements primero para aprovechar el cache de Docker
COPY app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ .

# Copiar variables de entorno usando secrets
RUN --mount=type=secret,id=_env,dst=/etc/secrets/.env \
    if [ -f /etc/secrets/.env ]; then \
        cp /etc/secrets/.env .env; \
    else \
        echo "Warning: No .env secret file found"; \
    fi

# Hacer el script ejecutable si existe
RUN if [ -f start.sh ]; then chmod +x start.sh; fi

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Configurar Streamlit para usar variables de entorno
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
# El puerto será configurado por Render
ENV STREAMLIT_SERVER_PORT=${PORT:-8501}

# Comando para ejecutar la aplicación
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]