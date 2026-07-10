FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza a que los logs salgan directo a la consola
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero (aprovecha la caché de Docker y hace que construya más rápido)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear un usuario sin privilegios de administrador llamado "appuser"
RUN adduser --disabled-password --gecos "" appuser

# Copiar el código y darle permisos a ese usuario
COPY --chown=appuser:appuser . .

# Cambiar del usuario Root al usuario seguro
USER appuser

EXPOSE 8501

# --server.fileWatcherType=poll fuerza a Streamlit a detectar cambios mediante polling
# en lugar de inotify. Necesario para que el hot-reload funcione con volúmenes
# montados desde Windows a través de WSL2.
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=poll"]