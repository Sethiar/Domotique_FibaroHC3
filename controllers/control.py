
"""
control.py
Gestion simplifiée des événements IPX800 pour Fibaro HC3.
"""

from typing import Dict
from services.logger_service import logger, log_action
from services.fibaro_service import set_value_to_fibaro

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
    value = 1 if etat in ("on", "1") else 0

    try:
        # Log de l’action
        log_action(device_id, value)

        # Envoi à Fibaro HC3
        result = set_value_to_fibaro(device_id, value)

        if result.get("status") == "success":
            logger.info(f"Valeur'{value}' envoyée avec succès au périphérique {device_id}")
            return {"status": "OK", "device": device_id, "etat": etat}
        else:
            logger.warning(f"Échec de l'envoi de valeur: {result}")
            return {"status": "error", "device": device_id, "etat": etat, "message": "Fibaro HC3 n'a pas accepté la commande"}

    except Exception as e:
        logger.exception(f"Erreur lors du traitement IPX pour device {device_id}: {e}")
        return {"status": "error", "message": "Erreur interne serveur."}