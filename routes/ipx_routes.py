from flask import Blueprint, request, jsonify
from services.logger_service import logger
from services.device_mapping import get_fibaro_id
from avertissements.ipx_alarms import send_sms_alert


# Routes/ipx_routes.py"
ipx_bp = Blueprint('ipx', __name__)


# Fonction tests SMS
@ipx_bp.route('/test-sms', methods=['GET'])
def test_sms():
    logger.info("Test SMS déclenché manuellement")
    send_sms_alert("TEST", force=True)
    return jsonify({'status': "sms test envoyé"})


# Fonction qui reçoit la valeur de la sortie du congèlateur.
@ipx_bp.route('/ipx-alarms', methods=['POST'])
def ipx_alarms():
    data = request.json
    # ON ou OFF
    state = data.get('state')
    # Périphérique
    ipx_name = data.get('device')
    
    logger.info(f"Reçu alerte IPX -- device={ipx_name}, state={state}")
    
    if not ipx_name or not state:
        logger.warning(f"Données invalides reçues : {data}")
        return jsonify({'status': 'error', 'message': 'invalid payload'}), 400
    
    # Mapping IPX → Fibaro déclenchement des actions Fibaro.
    device_id = get_fibaro_id(ipx_name)
    if device_id is None:
        logger.warning(f"Aucun mapping trouvé pour {ipx_name}")
    
    if state.upper() == 'OFF':
        logger.warning(f"{ipx_name} est hors tension -> Envoi SMS")
        send_sms_alert(ipx_name)
    else:
        logger.info(f"{ipx_name} est en état normal ({state})")
            
    return jsonify({'statut': 'OK'})
    