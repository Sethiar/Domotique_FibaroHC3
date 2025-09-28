"""
fibaro_service.py

Module pour envoyer des commandes de l'IPX800 vers la Fibaro HC3 via HTTP POST JSON.

Il permet de changer l'état des appareils (ex. allumer/éteindre une lumière) en fonction des événements reçus.

Auteur : Arnaud Lefetey (SethiarWorks)
Date : 2025-08-05
"""

# Importation pour faire des appels HTTP vers la box FIbaro HC3.
import requests
# Module pour la gestion des données JSON.
import json
# Importation de config
import config

# Importation afin de pouvoir faire des logging de suivi.
from services.logger_service import logger

# Permet de gérer l'authentification HTTP Basic(nom d'utilisateur et password en entête)
from requests.auth import HTTPBasicAuth

# Chargment des variables définies dans .env.
from dotenv import load_dotenv

load_dotenv()


# Fonction qui va envoyer la valeur d'état du bouton à la Fibaro.
def _call_action(device_id: int, action: str) -> dict:
    """
    Met à jour la valeur d'un périphérique Fibaro HC3 via l'API setValue.
    
    Args:
        device_id (int): Identifiant du périphérique cible.
        action (str) : Action (turnOn et turnOff) sur un périphérique.
    
    Returns:
        dict: Résultat de l'opération.    
    """
    auth = HTTPBasicAuth(config.FIBARO_USER, config.FIBARO_PASSWORD)
    
    base_url = f"http://{config.FIBARO_IP}" if config.FIBARO_PORT == 80 else f"http://{config.FIBARO_IP}:{config.FIBARO_PORT}"
    url = f"{base_url}/api/callAction"
 
    # Paramètres GET
    payload = {
        "deviceID": device_id,
        "name": action
    }
    
    try:
        logger.debug(f"Envoi à Fibaro: URL={url}, payload={payload}")
        response = requests.get(url, auth=auth, json=payload, timeout=5)
        logger.debug(f"Réponse Fibaro: {response.text}")
        
        try:
            resp_json = response.json()
        except ValueError:
            resp_json = {}

        if response.status_code == 200:
            return {"status": "success", "code": response.status_code, "response": resp_json}   
        else:
            logger.warning(f"Erreur callAction Fibaro ({response.status_code}): {response.text}")
            return {"status": "failed", "code": response.status_code, "response": resp_json, "message": response.text}
        
    except Exception as e:
        logger.exception(f"Erreur lors de l'appel de l'action {action} sur {device_id}")
        return {"status": "error", "message": str(e)}
    


# Fonction qui retourne l'action turnOn.
def turn_on_fibaro(device_id:int) -> dict:
    """
    Allume un périphérique Fibaro.
    """
    return _call_action(device_id, "turnOn")


# Fonction qui retourne l'action turnOff.
def turn_off_fibaro(device_id:int) -> dict:
    """
    Éteint un périphérique Fibaro.
    """
    return _call_action(device_id, "turnOff")


# Fonction allumant / éteignant le périphérique.
def set_fibaro(device_id: int, etat) -> dict:
    """
    Allume ou éteint un périphérique selon la valeur reçue (0/1, False/True, "0"/"1").

    Args:
        device_id (int): ID du périphérique.
        etat (int/str/bool): Valeur de l'état.

    Returns:
        dict: Résultat de l'opération.
    """
    if etat in [0, "0", False, "off"]:
        return turn_off_fibaro(device_id)
    elif etat in [1, "1", True, "on"]:
        return turn_on_fibaro(device_id)
    else:
        logger.warning(f"Etat invalide pour le périphérique {device_id}: {etat}")
        return {"status": "error", "message": f"Etat invalide: {etat}"}