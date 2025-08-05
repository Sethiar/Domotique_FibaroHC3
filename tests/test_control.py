# Dans terminal dans dossier sorce : 
# pytest --maxfail=1 --disable-warnings -q


import pytest
from unittest.mock import patch

from controllers.control import process_ipx_event


@patch("controllers.control.send_to_fibaro")
@patch("controllers.control.log_action")
def test_process_ipx_event_success(mock_log, mock_send):
    # Mock la réponse de send_to_fibaro pour simuler succès
    mock_send.return_value = {"status": "success", "code": 200}
    
    data = {"device_id": 12, "action": "on"}
    result = process_ipx_event(data)
    
    assert result["status"] == "OK"
    assert result["device"] == 12
    assert result["action"] == "on"
    
    # Vérifie que log_action a été appelé
    mock_log.assert_called_once_with(12, "on")
    
    # Vérifie que send_to_fibaro a été appelé avec le bon état Fibaro
    mock_send.assert_called_once_with(12, "turnOn")


@patch("controllers.control.send_to_fibaro")
@patch("controllers.control.log_action")
def test_process_ipx_event_invalid_data(mock_log, mock_send):
    # Cas données invalides : device_id manquant
    data = {"action": "on"}
    result = process_ipx_event(data)
    assert result["status"] == "error"
    
    # Cas données invalides : action inconnue
    data = {"device_id": 1, "action": "invalid_action"}
    result = process_ipx_event(data)
    assert result["status"] == "error"
    
    # log_action et send_to_fibaro ne doivent pas être appelés
    mock_log.assert_not_called()
    mock_send.assert_not_called()


@patch("controllers.control.send_to_fibaro")
@patch("controllers.control.log_action")
def test_process_ipx_event_send_failure(mock_log, mock_send):
    # Simule échec de send_to_fibaro
    mock_send.return_value = {"status": "failed", "code": 500, "message": "Erreur"}
    
    data = {"device_id": 20, "action": "off"}
    result = process_ipx_event(data)
    
    assert result["status"] == "OK"  # Ton code renvoie quand même "OK"
    mock_log.assert_called_once_with(20, "off")
    mock_send.assert_called_once_with(20, "turnOff")