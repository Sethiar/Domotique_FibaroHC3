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

# Importation afin de pouvoir faire des logging de suivi.
from services.logger_service import logger

# Permet de gérer l'authentification HTTP Basic(nom d'utilisateur et password en entête)
from requests.auth import HTTPBasicAuth
# Chargment des variables définies dans .env.
from dotenv import load_dotenv
load_dotenv()


# Adresse IP de la box Fibaro HC3
FIBARO_IP = os.getenv("FIBARO_IP")
# Port d'écoute de l'API (80 par défaut)
FIBARO_PORT = int(os.getenv("FIBARO_PORT", 80))

# Fonction qui permet d'envoyer une commande à la fibaro HC3.
def send_to_fibaro(device_id: int, command: str) -> dict:
    """
    Envoie une commande à un périphérique Fibaro HC3.
    
    Args:
        device_id (int): Identifiant du périphérique cible.
        command (str): Commande à exécuter (ex turnOn ou turnOff).
        
    Returns:
        dict: Résultat de l'opération.   
    """
    # Récupération du login et mdp depuis .env, puis transmis à l'objet auth à la requête HTTP.
    auth = HTTPBasicAuth(os.getenv("FIBARO_USER"), os.getenv("FIBARO_PASSWORD"))
    
    # Construction dynamique de l'url.
    url = f"http://{FIBARO_IP}:{FIBARO_PORT}/api/devices/{device_id}/action/{command}"
    
    # Envoi de la requête POST vers la Fibaro HC3
    try:
        response = requests.post(url, auth=auth)
        
        # Si commande réussie, réponse 200.
        if response.status_code == 200:
            logger.info(f"Commande envoyée '{command}' à {device_id}: {response.status_code}")
            # Retour explicite en cas de succès.
            return {"status": "success", "code": response.status_code}
        
        # Si erreur d'authentification erreur 401.
        elif response.status_code == 401:
            logger.error("Authentification échouée à la Fibaro HC3.")
            return {"status": "unauthorized", "code": response.status_code}
        
        # Si appareil introuvable erreur 404.
        elif response.status_code == 404:
            logger.error(f"Appareil {device_id} introuvable.")    
            return {"status": "not_found", "code": response.status_code}
            
        else:
            logger.warning(f"Réponse inattendue de la Fibaro HC3 ({response.status_code}): {response.text}")
            return {"status": "failed", "code": response.status_code, "message": response.text}
        
    # Gestion des erreurs.
    except Exception as e:
        # Affichage console utile pour debug local.
        logger.exception(f"Erreur lors de l'envoi de la commande à {device_id}")
        # Retour explicite en cas d'échec.
        return {"status": "error", "message": str(e)}
    