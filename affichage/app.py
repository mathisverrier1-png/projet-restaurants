from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Connexion à la base de données MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="scraping_tripadvisor"
    )


# Route pour récupérer tous les restaurants
@app.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurant ORDER BY ville")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour récupérer les KPIs des restaurants
@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Requête pour obtenir les KPIs
        query = """
        SELECT 
            ville,
            COUNT(*) AS nombre_restaurants,
            ROUND(AVG(note), 1) AS moyenne_note,
            SUM(nb_avis) AS total_avis,
            MAX(note) AS meilleure_note,
            MIN(note) AS pire_note
        FROM restaurant
        GROUP BY ville;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour le graphique à bulles
@app.route("/api/bubble-chart", methods=["GET"])
def get_bubble_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Données nécessaires : note moyenne (x), total des avis (y), taille (nombre de restaurants)
        query = """
        SELECT 
            ville,
            ROUND(AVG(note), 1) AS moyenne_note,
            SUM(nb_avis) AS total_avis,
            COUNT(*) AS nombre_restaurants
        FROM restaurant
        GROUP BY ville;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour le graphique à secteurs
@app.route("/api/pie-chart", methods=["GET"])
def get_pie_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Données nécessaires : répartition des restaurants par ville
        query = """
        SELECT 
            ville,
            COUNT(*) AS nombre_restaurants
        FROM restaurant
        GROUP BY ville;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour le graphique en courbes
@app.route("/api/line-chart", methods=["GET"])
def get_line_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Données nécessaires : note moyenne triée par ville
        query = """
        SELECT 
            ville,
            ROUND(AVG(note), 1) AS moyenne_note
        FROM restaurant
        GROUP BY ville
        ORDER BY ville;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)