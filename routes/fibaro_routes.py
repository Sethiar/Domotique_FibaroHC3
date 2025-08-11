from flask import Blueprint, request, jsonify
from services.logger_service import logger
from controllers.control import process_ipx_event

fibaro_bp = Blueprint('fibaro', __name__)


# Fonction qui va recevoir les événements de l'IPx800.
@fibaro_bp.route('/ipx-event', methods=['POST'])
def handle_ipx_event():
    """
    Point d'entrée API pour recevoir les événements de l'IPX800.
    Cette route attend un JSON POST contenant 'device_id' et 'action' (on/off).
    
    Processus :
        - Validation du JSON reçu.
        - Vérification des champs obligatoires.
        - Appel à la logique métier pour traitement.
        - Retour d'une réponse JSON avec un code HTTP adapté.
    192.128.192.168.1.28
    Returns:
        Response JSON avec le statut de la requête et code HTTP :
            - 200 si succès,
            - 400 si erreur de validation ou données invalides,
            - 500 en cas d'erreur serveur.
    """
    try:
        # Récupère et force la conversion en JSON, lève une erreur si invalide
        data = request.get_json(force=True)
        if not data:
            logger.warning("Requête JSON vide reçue.")
            return jsonify({"status": "ignored"}), 200
    except Exception as e:
        logger.error(f"Erreur parsing JSON : {e}")
        return jsonify({"status": "error", }), 200
    
    # Vérifie que les champs nécessaires sont présents
    if not data or "device_id" not in data or "action" not in data:
        logger.warning(f"Données manquantes dans la requête : {data}")
        return jsonify({"status": "error", "message": "device_id et action requis."}), 400
    
    # Appel de la fonction métier pour traitement de l'événement
    response = process_ipx_event(data)

    # Retourne une réponse HTTP adaptée selon le résultat de la fonction métier
    if response.get("status") == "OK":
        return jsonify(response), 200
    elif response.get("status") == "error":
        return jsonify(response), 400
    else:
        # Cas non prévu, probablement une erreur interne
        logger.error(f"Erreur interne lors du traitement: {response}")
        return jsonify({"status": "error", "message": "Erreur interne serveur."}), 500
