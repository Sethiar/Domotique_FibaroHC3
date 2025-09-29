"""
app.py

Fichier principal de lancement de l'application Flask.
Ce script initialise l'application web qui permet la communication entre l'IPX800
et la box domotique Fibaro HC3.

Fonctionnalités :
- Chargement des variables d'environnement depuis un fichier .env
- Création et configuration de l'application Flask
- Enregistrement des routes via Blueprint
- Lancement du serveur Flask avec gestion dynamique du port, host et mode debug

Auteur : SethiarWorks
Date : [Date de livraison]
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Importation des routes définies dans un Blueprint
from routes.fibaro_routes import fibaro_bp
from routes.ipx_routes import ipx_bp
from routes.fibaro_test import fibaro_test_bp


def create_app() -> Flask:
    """
    Crée et configure une instance de l'application Flask.

    Returns:
        Flask: Instance configurée de l'application Flask.
    """
    app = Flask("Herve Fibaro")
    app.register_blueprint(fibaro_bp)
    app.register_blueprint(ipx_bp)
    app.register_blueprint(fibaro_test_bp)
    
    return app


if __name__ == "__main__":
    app = create_app()

    # Lecture des paramètres de configuration depuis les variables d'environnement
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))

    try:
        # Lancement de l'application Flask
        app.run(debug=debug, host=host, port=port)
    except Exception as e:
        # Gestion des erreurs lors du lancement
        print(f"[ERREUR] Le serveur Flask n'a pas pu démarrer : {e}")
    