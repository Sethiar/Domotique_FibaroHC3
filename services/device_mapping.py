"""
device_mapping.py

Mapping des périphériques IPX800 vers les IDs Fibaro HC3.

Ce module centralise la correspondance entre les noms logiques des périphériques IPX
et leurs identifiants réels sur Fibaro. Cela permet de modifier les IDs Fibaro sans
changer le code métier ou les routes.

Fonctions :
- get_fibaro_id(ipx_name: str) -> int | None : retourne l'ID Fibaro correspondant
  au nom du périphérique IPX, ou None si non trouvé.

Auteur : Arnaud Lefetey (SethiarWorks)
Date : 2025-09-05
"""

import json
import os
from services.logger_service import logger

# Chemin par défaut vers le fichier de mapping
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "device_mapping.json")

# Chargement du mapping
try:
    with open(MAPPING_FILE, "r") as f:
        DEVICE_MAP = json.load(f)
except FileNotFoundError:
    DEVICE_MAP = {}
    print(f"[WARNING] Fichier de mapping non trouvé : {MAPPING_FILE}")
except json.JSONDecodeError as e:
    DEVICE_MAP = {}
    print(f"[ERROR] Erreur parsing JSON mapping : {e}")


# Fonntion récupèrant l'id fibaro correpondant au périphérique IPX.
def get_fibaro_id(ipx_name: str) -> int:
    """
    Récupère l'ID Fibaro associé à un périphérique IPX.
    
    Args:
        ipx_name (str): Nom du périphérique côté IPX (ex. "ipx_congelateur").
    
    Returns:
        int: ID Fibaro correspondant, ou None si non trouvé.
    """
    return DEVICE_MAP.get(ipx_name)


# --- Exemple rapide d'utilisation ---
if __name__ == "__main__":
    for name in DEVICE_MAP:
        print(f"{name} -> Fibaro ID {get_fibaro_id(name)}")