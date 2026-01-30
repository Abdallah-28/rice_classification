FROM python:3.11-slim

WORKDIR /app

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Dépendances système
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Installation des libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#Copie du projet
COPY . .

#Exposer le port
EXPOSE 5000

#Commande de démarrage FORCÉE sur 0.0.0.0
CMD ["python", "-m", "flask", "--app", "api/api.py", "run", "--host=0.0.0.0", "--port=5000"]