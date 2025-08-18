from flask import Blueprint, request, jsonify
from services.logger_service import logger
from controllers.control import process_ipx_event


# Routes/fibaro_routes.py
fibaro_bp = Blueprint('fibaro', __name__)


# Fonction tests qui reçoit tout de l'ipx800
@fibaro_bp.route('/ipx-tests', methods=['GET', 'POST'])
def ipx_tests():
    try:
        logger.info("---- NOUVELLE REQUÊTE IPX ----")
        logger.info(f"Méthode : {request.method}")
        logger.info(f"Headers : {dict(request.headers)}")
        logger.info(f"Query String : {request.query_string.decode(errors='ignore')}")
        logger.info(f"Form data : {request.form.to_dict()}")
        logger.info(f"Raw data : {request.data.decode(errors='ignore')}")
        logger.info(f"JSON : {request.get_json(silent=True)}")
        logger.info("---------------------------------")
        return "OK", 200
    except Exception as e:
        logger.exception(f"Erreur dans ipx-tests : {e}")
        return "Erreur serveur", 500
  
  
# Fonction qui va recevoir les événements de l'IPx800.
@fibaro_bp.route('/ipx-event', methods=['GET', 'POST'])
def handle_ipx_event():
    """
    Point d'entrée API pour recevoir les événements de l'IPX800.

    Cette route attend une requête HTTP POST provenant de l'IPX800,
    contenant les informations d'événement d'un périphérique, pouvant
    être transmises via :

      - paramètres URL (query string),
      - données de formulaire (form-data),
      - corps JSON,
      - ou données brutes au format clé=valeur (ex: device_id=123&etat=on).

    Données requises :

      - device_id (identifiant du périphérique),
      - etat (commande, typiquement '1/on' ou '0/off').

    Processus :

      1. Log des détails de la requête (headers, query, form, raw data).
      2. Extraction des données dans l'ordre : query string → form → JSON → texte brut.
      3. Validation de la présence des champs `device_id` et `etat`.
      4. Appel de la fonction métier `process_ipx_event` pour traitement.
      5. Retour d'une réponse JSON avec le statut et message.

    Returns:
      - 200 : succès avec résultat du traitement.
      - 400 : données manquantes ou invalides.
      - 500 : erreur serveur (non gérée ici explicitement mais possible).
    """
    try:
        # Logs pour debug
        logger.info(f"---- NOUVELLE REQUÊTE IPX ----")
        logger.info(f"Méthode : {request.method}")
        logger.info(f"Headers : {dict(request.headers)}")
        logger.info(f"Query string : {request.query_string.decode(errors='ignore')}")
        logger.info(f"Form data : {request.form.to_dict()}")
        logger.info(f"Raw data : {request.data.decode(errors='ignore')}")
        logger.info(f"JSON : {request.get_json(silent=True)}")
        logger.info("---------------------------------")

        # Récupération des paramètres
        device_id = request.args.get('relais') or request.form.get('relais')
        etat = request.args.get('etat') or request.form.get('etat')

        # Tentative JSON si non trouvé
        if not device_id or not etat:
            json_data = request.get_json(silent=True)
            if json_data:
                device_id = device_id or json_data.get('device_id') or json_data.get('relais')
                etat = etat or json_data.get('etat')

        # Tentative raw data clé=valeur
        if not device_id or not etat:
            raw = request.data.decode(errors='ignore').strip()
            if raw and '=' in raw:
                params = dict(pair.split('=', 1) for pair in raw.split('&') if '=' in pair)
                device_id = device_id or params.get('device_id') or params.get('relais')
                etat = etat or params.get('etat')

        # Vérification
        if not device_id or not etat:
            logger.error("device_id ou etat manquants après parsing complet.")
            return jsonify({"status": "error", "message": "device_id et etat requis."}), 400

        # Normalisation de l'état
        etat = etat.strip().lower()
        if etat in ('1', 'on'):
            etat = 'on'
        elif etat in ('0', 'off'):
            etat = 'off'
        else:
            logger.error(f"Etat invalide reçu : {etat}")
            return jsonify({"status": "error", "message": "Etat doit être 0/1 ou on/off."}), 400

        # Log final
        logger.info(f"ID du périphérique : {device_id}, Etat : {etat}")
        data = {'device_id': device_id, 'etat': etat}

        # Appel de la fonction métier
        response = process_ipx_event(data)
        return jsonify(response), 200

    except Exception as e:
        logger.exception(f"Erreur lors du traitement de l'événement IPX800 : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

# Route pour envoyer des commandes à l'IPX800
@fibaro_bp.route('/ipx-tests2', methods=['GET'])
def receive_ipx_data():
    data = request.args if request.method == "GET" else request.form
    print("Données reçues :", data.to_dict())
    return "OK", 200

