FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Étape 1 : Crée un sous-dossier "data" à l'intérieur du conteneur
RUN mkdir data

# Copier le code de l'API
COPY affichage/app.py . 

# Copier les données DANS le sous-dossier 'data'
COPY data/restaurants_export.csv data/
COPY data/Population_by_city.csv data/

# Copier les autres scripts si nécessaire (ils sont à la racine)
COPY scraper.py .
COPY city.py .

# ---- Fin de la Correction pour les CSV ----

# Installer les dépendances
RUN pip install flask flask_cors pandas pymysql pymysql 
# Exposer le port par défaut de Flask
EXPOSE 5000

# Commande pour démarrer l'application (l'API RESTful)
CMD ["python", "app.py"]