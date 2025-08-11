import os
import logging

from logging.handlers import RotatingFileHandler


#============================#
#     Paramètres LOGGING     #
#============================#


# Créer le dossier logs/ s'il n'existe pas.
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Chemin du fichier log
LOG_FILE = os.path.join("logs", "action.log")


# Création du logger
logger = logging.getLogger("fibaro_logger")
logger.setLevel(logging.INFO)  

# Format du log
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", 
    datefmt="%d-%m-%Y %H:%M:%S"
)

# Handler console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Handler fichier
file_handler = RotatingFileHandler(
    LOG_FILE,
    # Max : 1 Mo
    maxBytes=1_000_000,  
    # Garde les 5 derniers fichiers
    backupCount=5  
)

file_handler.setFormatter(formatter)

# Ajout du handler au logger
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


#============================#
#    FONCTIONS DE LOGGING    #
#============================#


def log_action(device_id, action):
    """
    Log une action d'un device avec le niveau INFO
    """
    logger.info(f"Device {device_id} => {action.upper()}")
    
