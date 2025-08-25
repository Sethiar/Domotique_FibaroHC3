
"""
control.py
Gestion simplifiée des événements IPX800 pour Fibaro HC3.
"""

from typing import Dict
from services.logger_service import logger, log_action
from services.fibaro_service import send_to_fibaro  # envoie turnOn/turnOff

def process_ipx_event(data: Dict[str, str]) -> Dict[str, str]:
    """
    Traite un événement venant de l'IPX800 et envoie la commande ON/OFF à la Fibaro.
    """
    device_id = data.get("device_id")
    etat = data.get("etat")

    # Validation
    if not device_id or etat not in ("on", "off", "1", "0"):
        logger.error(f"Données invalides reçues: {data}")
        return {"status": "error", "message": "Données invalides ou etat inconnu."}

    try:
        device_id = int(device_id)
    except (ValueError, TypeError):
        logger.error(f"device_id invalide : {device_id}")
        return {"status": "error", "message": "device_id doit être un entier."}

    # Normalisation de l'état
    action = "on" if etat in ("on", "1") else "off"
    fibaro_command = "turnOn" if action == "on" else "turnOff"

    try:
        # Log de l’action
        log_action(device_id, action)

        # Envoi à Fibaro HC3
        result = send_to_fibaro(device_id, fibaro_command)

        if result.get("status") == "success":
            logger.info(f"Commande '{fibaro_command}' envoyée avec succès pour {device_id}")
            return {"status": "OK", "device": device_id, "etat": action}
        else:
            logger.warning(f"Échec de l'envoi de commande: {result}")
            return {"status": "error", "device": device_id, "etat": action, "message": "Fibaro HC3 n'a pas accepté la commande"}

    except Exception as e:
        logger.exception(f"Erreur lors du traitement IPX pour device {device_id}: {e}")
        return {"status": "error", "message": "Erreur interne serveur."}