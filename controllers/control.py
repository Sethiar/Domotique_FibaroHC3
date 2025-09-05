"""
control.py
Gestion simplifiée des événements IPX800 pour Fibaro HC3.
"""

from typing import Dict
from services.logger_service import logger, log_action
from services.fibaro_service import turn_off_fibaro, turn_on_fibaro
from services.device_mapping import get_fibaro_id


def process_ipx_event(data: Dict[str, str]) -> Dict[str, str]:
    """
    Traite un événement venant de l'IPX800 et envoie la commande ON/OFF à la Fibaro.

    Le périphérique IPX est identifié par son nom (ex: 'ipx_congelateur'), qui est
    mappé vers l'ID Fibaro correspondant via le fichier device_mapping.json.
    """
    ipx_name = data.get("device_id")
    etat = data.get("etat")

    # Validation de base
    if not ipx_name or not etat:
        logger.error(f"Données invalides reçues: {data}")
        return {"status": "error", "message": "device_id et etat requis."}

    # Récupération de l'ID Fibaro via le mapping
    device_id = get_fibaro_id(ipx_name)
    if device_id is None:
        logger.error(f"Aucun mapping trouvé pour le périphérique IPX '{ipx_name}'")
        return {"status": "error", "message": f"Aucun mapping trouvé pour {ipx_name}"}

    try:
        # Log de l’action
        log_action(device_id)
        
        # Normalisation de l'état
        etat = etat.strip().lower()
        
        # Déterminer l'action à exécuter
        if etat in ('1', 'on', 'true', 'turnon'):
            result = turn_on_fibaro(device_id)
        elif etat in ('0', 'off', 'false', 'turnoff'):
            result = turn_off_fibaro(device_id)
        else:
            logger.error(f"Etat invalide reçu : {etat}")
            return {"status": "error", "message": "Etat doit être 0/1/on/off/true/false/turnOn/turnOff."}

        # Retour et logging du résultat
        if result.get("status") == "success":
            logger.info(f"Action '{etat}' envoyée avec succès au périphérique {device_id} ({ipx_name})")
            return {"status": "OK", "device": device_id, "ipx_name": ipx_name, "etat": etat}
        else:
            logger.warning(f"Échec de l'envoi de valeur: {result}")
            return {
                "status": "error",
                "device": device_id,
                "ipx_name": ipx_name,
                "etat": etat,
                "message": "Fibaro HC3 n'a pas accepté la commande"
            }

    except Exception as e:
        logger.exception(f"Erreur lors du traitement IPX pour device {device_id} ({ipx_name}): {e}")
        return {"status": "error", "message": "Erreur interne serveur."}