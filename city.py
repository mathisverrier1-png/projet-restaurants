import requests
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import os


# Fonction pour supprimer les accents d'un texte
def remove_accents(input_str):
    if input_str is None:
        return None
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


url = "https://www.donneesmondiales.com/capitales.php"

# Liste des villes à récupérer (sans accents pour comparaison)
villes_cible = [
    "Paris",
    "Rome",
    "Stockholm",
    "Oslo",
    "Ottawa",
    "Helsinki",
    "Berlin",
    "Tokyo",
    "Londres",
    "Pekin",
    "Santiago",
    "Canberra",
    "Tirana",
]

# Effectuer une requête GET
response = requests.get(url)
response.raise_for_status()  # Vérifie si la requête a réussi

# Parse le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Trouver tous les tableaux sur la page
tables = soup.find_all("table")

# Initialiser une liste pour toutes les données combinées
all_data = []

# Parcourir chaque tableau trouvé
for table in tables:
    # Extraire les lignes du tableau
    rows = table.find_all("tr")

    # Parcourir les lignes du tableau
    for row in rows[1:]:
        cols = row.find_all("td")
        # Supprime les espaces et accents des colonnes
        cols = [remove_accents(col.text.strip()) for col in cols]

        # Vérifie si la ville est dans la liste cible (sans accents)
        if cols and cols[1] in villes_cible:
            pays = cols[0]
            capitale = cols[1]
            population_ville = cols[2]
            population_urbaine = (
                cols[3] if len(cols) > 3 and cols[3] else population_ville
            )
            all_data.append(
                {
                    "Pays": pays,
                    "Capitale": capitale,
                    "Population ville": population_ville,
                    "Population et périphérie": population_urbaine,
                }
            )

# Créer un DataFrame avec toutes les données
df = pd.DataFrame(
    all_data,
    columns=["Pays", "Capitale", "Population ville", "Population et périphérie"],
)


output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Sauvegarder toutes les données dans un seul fichier CSV
file_name = os.path.join(output_dir, "Population_by_city.csv")
df.to_csv(file_name, index=False, encoding="utf-8")
print(f"Toutes les données filtrées ont été sauvegardées dans '{file_name}'")