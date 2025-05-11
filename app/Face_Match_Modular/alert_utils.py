# alert_utils.py
import logging
from datetime import datetime
import yagmail
from twilio.rest import Client
from config import (
    e_mail_sender, e_mail_password, e_mail_receiver,
    twilio_sid, twilio_token, twilio_from, twilio_to
)

logger = logging.getLogger(__name__)

def send_email_alert(frame, suspect, distance):
    try:
        yag = yagmail.SMTP(e_mail_sender, e_mail_password)
        subject = f"🚨 Face Match: {suspect}"
        body = (
            f"Match in {frame}\n"
            f"Suspect: {suspect}\n"
            f"Distance: {distance:.3f}\n"
            f"Time: {datetime.now()}"
        )
        yag.send(e_mail_receiver, subject, body)
        logger.info("Email alert sent")
    except Exception:
        logger.exception("Failed to send email alert")


def send_sms_alert(frame, suspect):
    try:
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(
            body=f"Face match: {suspect} in {frame}",
            from_=twilio_from,
            to=twilio_to
        )
        logger.info(f"SMS sent: SID {msg.sid}")
    except Exception:
        logger.exception("Failed to send SMS alert")
