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
    auth = HTTPBasicAuth('Rv2', '+1958Rv1005+')
    
    # Construction dynamique de l'url.
    print(f"[DEBUG] USE_SIMULATOR brut = {os.getenv('USE_SIMULATOR')}")
    if USE_SIMULATOR:
        base_url = "http://127.0.0.1:5001"
    else:
        # Intègre le port dans l'URL si ce n'est pas le port par défaut 80
        if FIBARO_PORT == 80:
            base_url = f"http://{FIBARO_IP}"
        else:
            base_url = f"http://{FIBARO_IP}:{FIBARO_PORT}"
            

    # Construction de l'URL dynamique (avec action on/off)
    url = f"{base_url}/api/devices/{device_id}/action/{command}"
    
    # Définition de la valeur en fonction de la commande.
    payload = {"args":""}
    headers = {"Content-Type": "application/json"}
    
    
    # Envoi de la requête POST vers la Fibaro HC3
    try:
        logger.debug(f"Envoi à Fibaro: URL={url}, payload={json.dumps(payload)}")
        response = requests.post(url, auth=auth, json=payload, headers=headers, timeout=15)
        
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

def set_icon(device_id: int, icon_id: int) -> dict:
    """
    Change l'icône d'un périphérique Fibaro HC3.
    
    Args:
        device_id (int): Identifiant du périphérique cible.
        icon (int): Identifiant de l'icône à (ON ou OFF)
        
    Returns:
        dict: Résultat de l'opération.   
    """
    # Récupération du login et mdp depuis .env, puis transmis à l'objet auth à la requête HTTP.
    auth = HTTPBasicAuth(FIBARO_USER, FIBARO_PASSWORD)
    
    # Construction dynamique de l'url.
    if USE_SIMULATOR:
        base_url = "http://127.0.1:5001"
    else:
        # Intègre le port dans l'URL si ce n'est pas le port par défaut 80
        if FIBARO_PORT == 80:
            base_url = f"http://{FIBARO_IP}"
        else:
            base_url = f"http://{FIBARO_IP}:{FIBARO_PORT}"
    
    url = f"{base_url}/api/devices/{device_id}/action/setIcon"
    payload = {"iconId": icon_id}
    headers = {"Content-Type": "application/json"}
    
    try:
        logger.debug(f"Changement d'icône pour {device_id}: URL={url}, payload={json.dumps(payload)}")
        response = requests.post(url, auth=auth, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            logger.info(f"Icône changée pour {device_id} avec succès.")
            return {"status": "success", "code": response.status_code}
        elif response.status_code == 401:
            logger.error("Authentification échouée à la Fibaro HC3.")
            return {"status": "unauthorized", "code": response.status_code}
        elif response.status_code == 404:
            logger.error(f"Appareil {device_id} introuvable.")    
            return {"status": "not_found", "code": response.status_code}  
        else:
            logger.warning(f"Réponse inattendue de la Fibaro HC3 ({response.status_code}): {response.text}")
            return {"status": "failed", "code": response.status_code, "message": response.text}
    except Exception as e:
        logger.exception(f"Erreur lors du changement d'icône pour {device_id}")
        return {"status": "error", "message": str(e)}
    
             