# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Evitar escritura de bytecode y habilitar buffer directo para logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear carpeta de volumen persistente para SQLite
RUN mkdir -p /data && chmod 777 /data
VOLUME ["/data"]

EXPOSE 8000

# Verificación de salud para Traefik y Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de arranque: FastAPI sirviendo Web UI + API REST + MCP SSE
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
