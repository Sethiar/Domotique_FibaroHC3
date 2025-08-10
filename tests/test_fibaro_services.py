# tests/test_fibaro_service.py

import pytest
import requests
from unittest.mock import patch
from services.fibaro_service import send_to_fibaro

@patch('serveur_fibaro.services.fibaro_service.requests.post')
def test_send_to_fibaro_success(mock_post):
    # Simulation d'une réponse HTTP avec code 200
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = send_to_fibaro(12, 'turnOn')
    assert result["status"] == "success"
    assert result["code"] == 200

@patch('serveur_fibaro.services.fibaro_service.requests.post')
def test_send_to_fibaro_failure(mock_post):
    # Simulation d'une réponse HTTP avec code 500
    mock_response = requests.Response()
    mock_response.status_code = 500
    mock_response._content = b"Erreur interne"
    mock_post.return_value = mock_response

    result = send_to_fibaro(12, 'turnOff')
    assert result["status"] == "failed"
    assert result["code"] == 500