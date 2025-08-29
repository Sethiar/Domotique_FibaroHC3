"""
fibaro_service.py

Ce module contient la logique pour envoyer des commandes de l'IPX800 vers la Fibaro HC3 
via des requêtes HTTP sécurisées. 

Il permet de changer l'état des appareils (ex. allumer/éteindre une lumière) en fonction des événements reçus.

Auteur : Arnaud Lefetey (SethiarWorks)
Date : 2025-08-05
"""

# Importation pour faire des appels HTTP vers la box FIbaro HC3.
import requests
# Permet de lire les variables d'environnement définies dans le fichier .env.
import os
# Module pour la gestion des données JSON.
import json

# Importation afin de pouvoir faire des logging de suivi.
from services.logger_service import logger

# Permet de gérer l'authentification HTTP Basic(nom d'utilisateur et password en entête)
from requests.auth import HTTPBasicAuth

# Chargment des variables définies dans .env.
from dotenv import load_dotenv
load_dotenv()


# Adresse IP de la box Fibaro HC3
FIBARO_IP = "192.168.1.33"
# Port d'écoute de l'API (80 par défaut)
FIBARO_PORT = "80"
# utilisateur de la Fibaro HC3
FIBARO_USER = "Rv2"
# Mot de passe de la Fibaro HC3
FIBARO_PASSWORD = "+1958Rv1005+"
# Construction dynamique de l'url.
USE_SIMULATOR = os.getenv("USE_SIMULATOR", "false").lower() == "true"


# Fonction qui va envoyer la valeur d'état du bouton à la Fibaro.
def set_value_to_fibaro(device_id: int, value: int) -> dict:
    """
    Met à jour la valeur d'un périphérique Fibaro HC3 via l'API setValue.
    
    Args:
        device_id (int): Identifiant du périphérique cible.
        value (int): Nouvelle valeur (O ou 1).
    
    Returns:
        dict: Résultat de l'opération.    
    """
    auth = HTTPBasicAuth(FIBARO_USER, FIBARO_PASSWORD)
    
    base_url = f"http://{FIBARO_IP}" if FIBARO_PORT =="80" else f"http://{FIBARO_IP}:{FIBARO_PORT}"
    url = f"{base_url}/api/devices/{device_id}/action/setValue"
    
    payload = {"args": value}
    headers = {"Content-Type": "application/json"}
    
    try:
        logger.debug(f"Envoi à Fibaro: URL={url}, payload={payload}")
        response = requests.post(url, auth=auth, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "success", "code": response.status_code}   
        else: 
            logger.warning(f"Erreur setValue Fibaro ({response.status_code}): {response.text}")
            return {"status": "failed", "code": response.status_code, "message": response.text}
        
    except Exception as e:
        logger.exception(f"Erreur lors de l'envoi setValue à {device_id}")
        return {"status": "error", "message": str(e)}
        