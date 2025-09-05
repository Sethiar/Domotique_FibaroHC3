
import smtplib
from email.message import EmailMessage
import time
import config

from services.logger_service import logger

LAST_ALERT = {}


def send_sms_alert(device, force=False):
    now = time.time()
    
    # Anti-flood sauf si force=True(test)
    if not force and LAST_ALERT.get(device, 0) + config.ALERT_COOLDOWN > now:
        logger.info(f"Alerte récente pour {device}, sms non envoyé.")
        return
    
    
    LAST_ALERT[device] = now
    
    
    msg = EmailMessage()
    msg.set_content(f"Alerte : {device} hors tension !!!")
    msg['Subject'] = f"IPX Alarme {device}"
    msg['From'] = config.SMTP_USER
    # Email to SMS orange
    msg['To'] = config.SMS_TO
    
    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASS)
            server.send_message(msg)
        logger.info(f"SMS envoyé pour {device}")
    except Exception as e:
        logger.exception(f"Erreur envoi SMS pour {device} : {e}")
                