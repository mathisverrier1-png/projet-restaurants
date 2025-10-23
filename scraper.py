import requests
import time
import mysql.connector
import pandas as pd
import re

# Clé d'API depuis RapidAPI
api_url_restaurant = (
    "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
)
headers = {
    "X-RapidAPI-Key": "8dfbeaf8bfmsh1eed75490e0bedep151605jsnc9afdbbffbda",
    "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
}

# Connexion à la base de données MySQL
db = mysql.connector.connect(
    host="localhost",  # Hôte de la base de données
    user="root",  # Nom d'utilisateur MySQL (à adapter)
    password="",  # Mot de passe MySQL (à adapter)
    database="scraping_tripadvisor",  # Nom de ta base de données
)

cursor = db.cursor()


# Fonction pour formater le nom du restaurant et générer une clé unique
def generate_unique_id(nom, ville):
    # Nettoyer le nom et la ville : retirer caractères spéciaux et espaces -> _
    formatted_name = re.sub(r"[^a-zA-Z0-9]", "_", nom).lower()
    formatted_city = re.sub(r"[^a-zA-Z0-9]", "_", ville).lower()
    # Combiner nom et ville pour générer un ID unique
    id_unique = f"{formatted_name}_{formatted_city}"
    return id_unique


# Fonction pour insérer un restaurant dans la base de données
def insert_restaurant(nom, note, nb_avis, ville, pays, pop_city, all_pop_city):
    try:
        # Si pays est None, définir une valeur par défaut
        if pays is None:
            pays = "Inconnu"
        if pop_city is None:
            pop_city = 0  # Valeur par défaut pour la population de la ville
        if all_pop_city is None:
            all_pop_city = 0  # Valeur par défaut pour la population totale de la ville et périphérie

        # Générer un identifiant unique
        id_unique = generate_unique_id(nom, ville)

        query = """
                    INSERT INTO restaurant (id_unique, nom, note, nb_avis, ville, pays, pop_city, all_pop_city)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nom = VALUES(nom),
                        note = VALUES(note),
                        nb_avis = VALUES(nb_avis),
                        ville = VALUES(ville),
                        pays = VALUES(pays),
                        pop_city = VALUES(pop_city),
                        all_pop_city = VALUES(all_pop_city);
                """
        values = (id_unique, nom, note, nb_avis, ville, pays, pop_city, all_pop_city)
        cursor.execute(query, values)
        db.commit()
    except mysql.connector.Error as err:
        print(f"Erreur MySQL : {err}")


# Fonction pour récupérer les restaurants par locationId
def fetch_restaurants(location_id):
    querystring = {
        "locationId": location_id,
        "limit": "50",
    }

    response = requests.get(api_url_restaurant, headers=headers, params=querystring)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Trop de requêtes, attente de 20 secondes...")
        time.sleep(20)
        return fetch_restaurants(location_id)
    else:
        print(
            f"Erreur lors de l'appel à l'API des restaurants : {response.status_code} - {response.text}"
        )
        return None


# Charger les données de population des villes depuis le CSV
city_data = pd.read_csv("data/Population_by_city.csv", encoding="utf-8")

# Créer un dictionnaire pour accéder rapidement aux données des villes
city_pop_info = {
    row["Capitale"]: {
        "pays": row["Pays"],
        "pop_city": row["Population ville"],
        "all_pop_city": row["Population et périphérie"],
    }
    for _, row in city_data.iterrows()
}

# Liste des cityIds pour les villes cibles
city_ids = {
    "Paris": 187147,
    "Rome": 187791,
    "Ottawa": 155004,
    "Helsinki": 189934,
    "Berlin": 187323,
    "Tokyo": 298184,
    "Londres": 186338,
    "Pekin": 294212,
    "Canberra": 255057,
    "Tirana": 294446,
}

# Recherche et insertion des restaurants pour chaque ville
for city, location_id in city_ids.items():
    # Envoi de la requête et récupération des données
    data = fetch_restaurants(location_id)

    if data:
        if isinstance(data, dict) and "data" in data and "data" in data["data"]:
            for restaurant in data["data"]["data"]:
                try:
                    # Vérifie si les informations sont présentes dans l'objet
                    name = restaurant.get("name")
                    rating = restaurant.get("averageRating")  # Note
                    reviews = restaurant.get("userReviewCount")  # Nombre d'avis

                    # Si la ville est présente dans le dictionnaire city_pop_info, récupère les infos de population
                    if city in city_pop_info:
                        pop_info = city_pop_info[city]
                        pays = pop_info["pays"]
                        pop_city = pop_info["pop_city"]
                        all_pop_city = pop_info["all_pop_city"]
                    else:
                        pays = pop_city = all_pop_city = (
                            None  # Si la ville n'est pas dans le CSV, met des valeurs par défaut
                        )

                    if name and rating is not None and reviews is not None:
                        if isinstance(rating, (int, float)) and 1 <= rating <= 5:
                            # Insère les données dans la base de données
                            insert_restaurant(
                                name,
                                rating,
                                reviews,
                                city,
                                pays,
                                pop_city,
                                all_pop_city,
                            )
                            print(f"Inséré : {name}, ville : {city}, pays : {pays}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction des données pour {city}: {e}")

# Exporter les données de la base de données dans un CSV
try:
    query = (
        "SELECT nom, note, nb_avis, ville, pays, pop_city, all_pop_city FROM restaurant"
    )
    cursor.execute(query)
    restaurants = cursor.fetchall()

    # Création du DataFrame pandas à partir des résultats
    columns = [
        "Nom",
        "Note",
        "Avis",
        "Ville",
        "Pays",
        "Population ville",
        "Population et périphérie",
    ]
    df = pd.DataFrame(restaurants, columns=columns)

    # Sauvegarde dans un fichier CSV
    df.to_csv("data/restaurants_export.csv", index=False, encoding="utf-8")
    print("Export des données vers restaurants_export.csv terminé !")
except mysql.connector.Error as err:
    print(f"Erreur MySQL lors de l'exportation des données : {err}")


# Fermer la connexion à la base de données
cursor.close()
db.close()

print("Extraction et insertion dans la base de données terminées !")