# Utilisation de l'image Python comme base
FROM python:3.9

# Définition du répertoire de travail
WORKDIR /app

# Copier les fichiers du projet dans l'image Docker
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par FastAPI
EXPOSE 7860

# Lancer l'application avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]


ENV C:\Program Files\Docker\Docker