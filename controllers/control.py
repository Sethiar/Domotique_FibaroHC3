
"""
control.py

Module de gestion des événements IPX800 pour intégration avec Fibaro HC3.

Ce module permet :
- de recevoir les données envoyées par l'IPX800 (ex : état d’un relais),
- de normaliser et valider les données,
- d’envoyer les commandes correspondantes à la Fibaro HC3 (allumer/éteindre),
- de mettre à jour dynamiquement l’icône du périphérique dans l’interface Fibaro,
- et de journaliser toutes les actions pour suivi et debugging.

Auteur : Arnaud Lefetey (SethiarWorks)
Date : 2025-08-05
"""

from typing import Dict

from services.logger_service import log_action, logger
from services.fibaro_service import send_to_fibaro, set_icon


# Constantes : identifiants des icônes "ON" et "OFF" dans Fibaro.
ICON_ON = 776
ICON_OFF = 782



def process_ipx_event(data: Dict[str, str]) -> Dict[str, str]:
    """
    Traite un événement provenant de l'IPX800 et synchronise l’état avec la Fibaro HC3.

    Étapes principales :
    1. Vérifie et normalise les données reçues (`etat` peut être '1', '0', 'on', 'off').
    2. Détermine la commande Fibaro correspondante (turnOn/turnOff).
    3. Met à jour l’icône associée au périphérique sur la Fibaro.
    4. Log toutes les actions effectuées (succès ou erreurs).

    Args:
        data (dict):
            Données JSON attendues, au format :
            {
                "device_id": "<id du périphérique Fibaro (int ou str convertible en int)>",
                "etat": "1" | "0" | "on" | "off"
            }

    Returns:
        dict: Résultat de l’opération, par exemple :
            {
                "status": "OK",
                "device": 27,
                "etat": "on"
            }
        ou en cas d’erreur :
            {
                "status": "error",
                "message": "Données invalides ou erreur interne"
            }

    Raises:
        Exception: Capture et log toute erreur interne (ne remonte pas brute).
    """
    # Identifiant du périphérique.
    device_id = data.get("device_id")
    # 'on', 'off', '1' ou '0'
    etat = data.get("etat")

    # Validation des données
    if not device_id or etat not in ("on", "off", "1", "0"):
        logger.error(f"Données invalides reçues: {data}")
        return {"status": "error", "message": "Données invalides ou etat inconnu."}

    try:
        # Assurer que device_id est un entier
        device_id = int(device_id)
    except (ValueError, TypeError):
        logger.error(f"device_id invalide (non entier) : {device_id}")
        return {"status": "error", "message": "device_id doit être un entier."}

    # Normalisation de l'état
    if etat == "1":
        action = "on"
        set_icon(device_id, ICON_ON)
    elif etat == "0":
        action = "off"
        set_icon(device_id, ICON_OFF)
    else:
        action = etat  # déjà 'on' ou 'off'

    fibaro_command = "turnOn" if action == "on" else "turnOff"

    try:
        # Log l’état reçu
        log_action(device_id, action)

        # Envoi de la commande à Fibaro
        result = send_to_fibaro(device_id, fibaro_command)

        # Tentative de mise à jour de l’icône
        try:
            icon_id = ICON_ON if action == "on" else ICON_OFF
            update_icon_result = send_to_fibaro(device_id, {"iconId": icon_id})

            if update_icon_result.get("status") == "success":
                logger.info(f"Mise à jour de l'icône réussie pour {device_id}: {action}")
            else:
                logger.error(f"Échec mise à jour icône pour {device_id}: {update_icon_result}")

        except Exception as e:
            logger.error(f"Erreur mise à jour icône pour {device_id}: {e}")

        # Log résultat de la commande principale
        if result.get("status") == "success":
            logger.info(f"Commande '{fibaro_command}' envoyée avec succès pour {device_id}")
        else:
            logger.warning(f"Échec de l'envoi de commande: {result}")

        return {"status": "OK", "device": device_id, "etat": action}

    except Exception as e:
        logger.exception(f"Erreur lors du traitement IPX pour device {device_id}: {e}")
        return {"status": "error", "message": "Erreur interne serveur."}
