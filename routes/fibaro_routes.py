from flask import Blueprint, request, jsonify
from services.logger_service import logger
from controllers.control import process_ipx_event


# Routes/fibaro_routes.py
fibaro_bp = Blueprint('fibaro', __name__)


# Fonction qui va recevoir les événements de l'IPx800.
@fibaro_bp.route('/ipx-event', methods=['POST'])
def handle_ipx_event():
    """
    Point d'entrée API pour recevoir les événements de l'IPX800.

    Cette route attend une requête HTTP POST provenant de l'IPX800,
    contenant les informations d'événement d'un périphérique, pouvant
    être transmises via :

      - paramètres URL (query string),
      - données de formulaire (form-data),
      - corps JSON,
      - ou données brutes au format clé=valeur (ex: device_id=123&action=on).

    Données requises :

      - device_id (identifiant du périphérique),
      - action (commande, typiquement 'on' ou 'off').

    Processus :

      1. Log des détails de la requête (headers, query, form, raw data).
      2. Extraction des données dans l'ordre : query string → form → JSON → texte brut.
      3. Validation de la présence des champs `device_id` et `action`.
      4. Appel de la fonction métier `process_ipx_event` pour traitement.
      5. Retour d'une réponse JSON avec le statut et message.

    Returns:
      - 200 : succès avec résultat du traitement.
      - 400 : données manquantes ou invalides.
      - 500 : erreur serveur (non gérée ici explicitement mais possible).
    """
    try:
        # Logs pour debugging et suivi
        logger.info(f"Headers de la requête : {dict(request.headers)}")
        logger.info(f"Query string de la requête : {request.query_string.decode()}")
        logger.info(f"Form data : {request.form.to_dict()}")
        logger.info(f"Raw data : {request.data.decode(errors='ignore')}")
    
        # Paramètres URL.
        device_id = request.args.get('device_id')
        action = request.args.get('action')
    
        # Form data (si non trouvé dans les paramètres URL).
        if not device_id or not action:
            device_id = device_id or request.form.get('device_id')
            action = action or request.form.get('action') 
        
        # Si pas trouvé, essayer de parser le raw data si possible (ex: JSON brut)
        if not device_id or not action:
            try:
                # Récupère et force la conversion en JSON, lève une erreur si invalide
                json_data = request.get_json(silent=True)
                
                if json_data:
                    device_id = device_id or json_data.get('device_id')
                    action = action or json_data.get('action')
            
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des données JSON.", {e})   
        
        # Texte brut clé=valeur (ex: "device_id=123&action=on")    
        if not device_id or not action:
            try:
                raw = request.data.decode(errors='ignore').strip()
                if raw  and '=' in raw:
                    params = dict(pair.split('=') for pair in raw.split('&') if '=' in pair)
                    device_id = device_id or params.get('device_id')
                    action = action or params.get('action')
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des données brutes.", {e})
            
        if not device_id or not action:        
            logger.error("device_id ou action manquants après parsing complet.")
            return jsonify({"status": "error", "message": "device_id et action requis."}), 400    
    
        # Normalisation de l'action (ex: 'on' ou 'off').
        action = action.lower()
       
        # Log des données extraites
        logger.info(f"ID du périphérique : {device_id}, Action : {action}")
        data = {'device_id': device_id, 'action': action}
        response = process_ipx_event(data)
        return jsonify(response), 200
    
    except Exception as e:
        logger.exception(f"Erreur lors du traitement de l'événement IPX800 : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500