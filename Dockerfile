# syntax = docker/dockerfile:1.2

# Usar Python 3.12 slim (más compatible)
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema + Chrome headless
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    gnupg \
    unzip \
    # Dependencias mínimas para Chrome headless
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome (headless optimizado)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements primero para aprovechar el cache de Docker
COPY app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Invalidar cache para debug
RUN echo "Build timestamp: $(date)" && echo "Debugging secrets extensively..."

# Buscar secrets en todas las ubicaciones posibles
RUN --mount=type=secret,id=_env,dst=/etc/secrets/.env \
    echo "🔍 EXTENSIVE SECRET DEBUG:"; \
    echo ""; \
    echo "1. Checking /etc/secrets/.env:"; \
    ls -la /etc/secrets/.env 2>/dev/null || echo "❌ /etc/secrets/.env not found"; \
    echo ""; \
    echo "2. Checking /etc/secrets/ directory:"; \
    ls -la /etc/secrets/ 2>/dev/null || echo "❌ /etc/secrets/ directory does not exist"; \
    echo ""; \
    echo "3. Checking all of /etc/:"; \
    ls -la /etc/ | grep -i secret || echo "❌ No secret directories in /etc/"; \
    echo ""; \
    echo "4. Searching for any 'secret' directories:"; \
    find / -type d -name "*secret*" 2>/dev/null | head -10 || echo "❌ No secret directories found"; \
    echo ""; \
    echo "5. Searching for .env files anywhere:"; \
    find / -name ".env" -type f 2>/dev/null | head -10 || echo "❌ No .env files found"; \
    echo ""; \
    echo "6. Searching for _env files anywhere:"; \
    find / -name "_env" -type f 2>/dev/null | head -10 || echo "❌ No _env files found"; \
    echo ""; \
    echo "7. Checking mount points:"; \
    mount | grep -i secret || echo "❌ No secret mounts found"; \
    echo ""; \
    echo "8. Checking environment variables with 'SECRET':"; \
    env | grep -i secret || echo "❌ No SECRET environment variables"; \
    echo ""; \
    echo "9. Creating empty .env file for now..."; \
    touch .env && echo "✅ Empty .env created"

# Copiar el código de la aplicación
COPY app/ .

# Configurar Chrome headless
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_PATH=/usr/bin/google-chrome-stable
ENV DISPLAY=:99

# Crear usuario no-root para seguridad
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome \
    && mkdir -p /home/chrome/Downloads \
    && chown -R chrome:chrome /home/chrome \
    && chown -R chrome:chrome /app

# Hacer el script ejecutable si existe
RUN if [ -f start.sh ]; then chmod +x start.sh; fi

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Configurar Streamlit para usar variables de entorno
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=${PORT:-8501}

# Cambiar a usuario no-root
USER chrome

# Comando para ejecutar la aplicación
CMD ["sh", "-c", "streamlit run main.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]