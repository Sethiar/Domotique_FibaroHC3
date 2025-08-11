"""
config.py

Ce fichier contient les variables de configuration de l'application serveur_fibaro.
Les valeurs sont lues depuis un fichier `.env` pour plus de sécurité et de flexibilité.

Auteurs : Arnaud Lefetey (SethiarWorks)
Version : 1.0
Date : 2025-08-05
"""

import os
from dotenv import load_dotenv



# Chargement des variables d'environnement à partir du fichier .env
load_dotenv()


#==========================================#
#     Paramètres de l'application Flask    #
#==========================================#


# Activation ou non du mode debug (True = verbose, False = silencieux)
DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

# Port d'écoute du serveur Flask
PORT = int(os.getenv("FLASK_PORT", 5000))

# Adresse IP du serveur (0.0.0.0 pour écouter toutes les interfaces)
HOST = os.getenv("FLASK_HOST", "0.0.0.0")

# Clé secrète Flask (sessions sécurisées, CSRF, etc.)
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "sethiarworks-secretkey")


#===========================#
#     Paramètres Fibaro     #
#===========================#

# Adresse IP de la box Fibaro
FIBARO_IP = os.getenv("FIBARO_IP", "192.168.1.33")

# Identifiants API Fibaro
FIBARO_USER = os.getenv("FIBARO_USER", "Rv2")
FIBARO_PASSWORD = os.getenv("FIBARO_PASSWORD", "+1958Rv1005+")

# Port de l'API Fibaro (souvent 80 ou 443)
FIBARO_PORT = int(os.getenv("FIBARO_PORT", 80))

# URL de base construite automatiquement à partir des paramètres
FIBARO_BASE_URL = f"http://{FIBARO_USER}:{FIBARO_PASSWORD}@{FIBARO_IP}:{FIBARO_PORT}/api"

# === Répertoires et fichiers ===

# Chemin du fichier de log (relatif au dossier du projet)
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/actions.log")

# Niveau de verbosité pour les logs (INFO, DEBUG, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

