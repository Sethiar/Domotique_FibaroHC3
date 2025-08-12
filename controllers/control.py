from typing import Dict

from services.logger_service import log_action, logger

from services.fibaro_service import send_to_fibaro


def process_ipx_event(data: Dict[str, str]) -> Dict[str, str]:
    """
    Traite un événement IPx800, envoie la commande appropriée à Fibaro HC3 et log action.
    
    Args:
        data (dict): Données JSON ontenant 'device_id' et 'action' ('on' ou 'off').
        
    Returns:
        dict: Résultat avec status et détails ou message d'erreur.    
    """
    # Identifiant du périphérique.
    device_id = data.get("device_id")
    # 'on' ou 'off'
    action = data.get("action")
    
    # Validation simple des données.
    if not device_id or action not in ("on", "off"):
        logger.error(f"Données invalides reçues: {data}")
        return {"status": "error", "message": "Données invalides ou action inconnue."}
    
    try:
        # Assurer que device_id est un entier
        device_id = int(device_id)
    except (ValueError, TypeError):
        logger.error(f"device_id invalide (non entier) : {device_id}")
        return {"status": "error", "message": "device_id doit être un entier."}
    
    fibaro_command = "turnOn" if action == "on" else "turnOff"
    
    try:
        # Log l'action reçue.
        log_action(device_id, action)
        
        # Envoi commande à Fibaro.
        result = send_to_fibaro(device_id, fibaro_command)
        
        # Log résultant de l'envoi.
        if result.get("status") == "success":
            logger.info(f"Commande '{fibaro_command}' envoyée avec succès pour device {device_id}")
        
        else:
            logger.warning(f"Échec de l'envoi de commande: {result}")

        return {"status": "OK", "device": device_id, "action": action}
    
    except Exception as e:
        logger.exception(f"Erreur lors du traitement de l'événement IPX pour device {device_id}: {e}")
        return {"status": "error", "message": "Erreur interne serveur."}
