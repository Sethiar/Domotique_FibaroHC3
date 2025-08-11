from flask import Blueprint, request, jsonify
from services.logger_service import logger
from controllers.control import process_ipx_event
import xml.etree.ElementTree as ET


# Routes/fibaro_routes.py
fibaro_bp = Blueprint('fibaro', __name__)


# Fonction qui va recevoir les événements de l'IPx800.
@fibaro_bp.route('/ipx-event', methods=['POST'])
def handle_ipx_event():
    """
    Point d'entrée API pour recevoir les événements de l'IPX800.

    Cette route attend une requête HTTP POST provenant de l'IPX800,
    contenant les informations d'événement d'un périphérique, soit via :
      - paramètres URL (query string),
      - données de formulaire (form-data),
      - ou corps JSON.

    Les données requises sont :
        - device_id (identifiant du périphérique),
        - action (commande, typiquement 'on' ou 'off').

    Le traitement consiste à :
        - logger les détails de la requête pour faciliter le debugging,
        - extraire les données selon différents formats possibles,
        - valider la présence des données essentielles,
        - appeler la fonction métier `process_ipx_event` pour traitement,
        - retourner une réponse JSON avec le statut de la requête.

    Returns:
        Response JSON avec :
          - status 200 et résultat de la commande en cas de succès,
          - status 400 et message d'erreur si données manquantes ou invalides,
          - status 500 en cas d'erreur interne serveur.
    """
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
            logger.warning("Erreur lors de la récupération des données JSON.", {e})   
    
    # Texte brut clé=valeur (ex: "device_id=123&action=on")    
    if not device_id or not action:
        try:
            raw = request.data.decode(errors='ignore').strip()
            if raw  and '=' in raw:
                params = dict(pair.split('=') for pair in raw.split('&') if '=' in pair)
                device_id = device_id or params.get('device_id')
                action = action or params.get('action')
        except Exception as e:
            logger.warning("Erreur lors de la récupération des données brutes.", {e})
            
    if not device_id or not action:        
        return jsonify({"status": "error", "message": "device_id et action requis."}), 400    
    
    
    # Log des données extraites
    logger.info(f"ID du périphérique : {device_id}, Action : {action}")
    data = {'device_id': device_id, 'action': action}
    response = process_ipx_event(data)
    return jsonify(response), 200
