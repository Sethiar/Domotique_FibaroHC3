"""
    ipx_list.py
   
    Ce fichier permet de récupérer la liste des relais de l'IPX800 et de les afficher.
    Il est utilisé pour la gestion des périphériques Fibaro HC3.
    
    Auteur : Arnaud Lefetey (SethiarWorks)
    Date : 2025-08-05 
"""

import requests

# Importation afin de pouvoir faire des logging de suivi.
from services.logger_service import logger

# Adresse IP de l'IPX800
IPX_IP = "http://192.168.1.28"
# Clé API de l'IPX800
IPX_API_KEY = "0667"
FLASK_SERVER = "http://192.168.1.10"
ENDPOINT = "ipx-list"

# Récupération des relais depuis l'IPX800
try:
    response = requests.get(f"{IPX_IP}/api/xdevices.json?key={IPX_API_KEY}", timeout=10)
    response.raise_for_status()  # Vérifie si la requête a réussi
    ipx_data = response.json()
    logger.info(f"{len(ipx_data)} relais récupérés depuis l'IPX800.")
except Exception as e:
    logger.info(f"Erreur lors de la récupération des relais depuis l'IPX800 : {e}")
    ipx_data = []
    
# Parcours de tous les relais connus.
for device in ipx_data:
    relais_id = device.get("id")  # ou la clé correspondant à l'ID
    name = device.get("name", "Inconnu")
    
    if not relais_id:
            logger.warning(f"ID de périphérique manquant pour le relais {name}.")
            continue
    
    etat = device.get("value")  # '1' ou '0' selon l'IPX800
    if etat not in ("0", "1"):
        logger.warning(f"Etat inconnu pour le relais {name}, on skip.")
        continue

    payload = {
        "device_id": relais_id,
        "etat": "on" if etat == "1" else "off"
    }
    
    logger.info(f"Envoi des données à Flask pour le relais {name} : {payload['etat']}")
    
    # Envoi des données à Flask.
    try:
        logger.debug(f"Payload complet envoyé : {payload}")
        post_response = requests.post(f"{FLASK_SERVER}/{ENDPOINT}", json=payload, timeout=10)
        post_response.raise_for_status()
        logger.info(f"Réponse de Flask pour {relais_id} ({name}) : {post_response.status_code}")
        logger.info(f"Données envoyées avec succès à Flask pour {relais_id} ({name}) : {post_response.text}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi à Flask pour le relais {relais_id} ({name}) : {e}")