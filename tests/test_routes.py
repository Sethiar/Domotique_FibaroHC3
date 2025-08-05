# Pour lancer les tests : 
# pytest --maxfail=1 --disable-warnings -q
#


import json
import pytest
from flask import Flask
from routes.fibaro_routes import fibaro_bp

@pytest.fixture
def client():
    # Crée une app Flask pour les tests avec le blueprint fibaro_bp
    app = Flask(__name__)
    app.register_blueprint(fibaro_bp)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_handle_ipx_event_success(client, monkeypatch):
    # Mock process_ipx_event pour simuler un succès
    def mock_process_ipx_event(data):
        return {"status": "OK", "device": data["device_id"], "action": data["action"]}

    monkeypatch.setattr("controllers.control.process_ipx_event", mock_process_ipx_event)

    data = {"device_id": 10, "action": "on"}
    response = client.post('/ipx-event', data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "OK"
    assert json_data["device"] == 10
    assert json_data["action"] == "on"


def test_handle_ipx_event_missing_fields(client):
    # Envoi sans 'device_id'
    data = {"action": "on"}
    response = client.post('/ipx-event', data=json.dumps(data), content_type='application/json')

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert "device_id" in json_data["message"]


def test_handle_ipx_event_invalid_json(client):
    # Envoi d'un JSON invalide
    response = client.post('/ipx-event', data="c'est pas du json", content_type='application/json')

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert "JSON invalide" in json_data["message"]