import logging
from datetime import datetime
import sqlite3
import yagmail
from twilio.rest import Client
from config import (
    e_mail_sender, e_mail_password, e_mail_receiver,
    twilio_sid, twilio_token, twilio_from, twilio_to,
    db_path  
)

logger = logging.getLogger(__name__)

class NotificationDB:
    """Handles database interactions for notifications."""
    
    def __init__(self, db_path):
        self.db_path = db_path

    def insert_notification(self, cctv_id, suspect_id, event_time, notification_type, message, channel, delivery_status, delivery_time):
        """Inserts a notification record into the Notifications table."""
        query = """
            INSERT INTO Notifications (
                cctv_id, suspect_id, event_time, notification_type, 
                message, channel, delivery_status, delivery_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            cctv_id, suspect_id, event_time.isoformat(), notification_type,
            message, channel, delivery_status,
            delivery_time.isoformat() if delivery_time else None
        )
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('PRAGMA journal_mode=WAL;')
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
        except Exception:
            logger.exception("Failed to insert notification into DB")

db_handler = NotificationDB(db_path)

def send_email_alert(frame, suspect, distance, cctv_id, suspect_id):
    """Sends an email alert and logs the notification to the database."""
    event_time = datetime.now()
    body = f"Match in {frame}\nSuspect: {suspect}\nDistance: {distance:.3f}\nTime: {event_time.isoformat()}"

    try:
        yag = yagmail.SMTP(e_mail_sender, e_mail_password)
        yag.send(e_mail_receiver, f"🚨 Face Match: {suspect}", body)
        logger.info("Email alert sent")
        delivery_status, delivery_time = 'SENT', datetime.now()
    except Exception:
        logger.exception("Failed to send email alert")
        delivery_status, delivery_time = 'FAILED', None

    db_handler.insert_notification(
        cctv_id, suspect_id, event_time, 'MATCH', body, 'EMAIL', delivery_status, delivery_time
    )

def send_sms_alert(frame, suspect, cctv_id, suspect_id):
    """Sends an SMS alert and logs the notification to the database."""
    event_time = datetime.now()
    body = f"Face match: {suspect} in {frame} at {event_time.isoformat()}"

    try:
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(body=body, from_=twilio_from, to=twilio_to)
        logger.info(f"SMS sent: SID {msg.sid}")
        delivery_status, delivery_time = 'SENT', datetime.now()
    except Exception:
        logger.exception("Failed to send SMS alert")
        delivery_status, delivery_time = 'FAILED', None

    db_handler.insert_notification(
        cctv_id, suspect_id, event_time, 'MATCH', body, 'SMS', delivery_status, delivery_time
    )

def send_call_alert(frame, suspect, cctv_id, suspect_id):
    """Sends a voice call alert and logs the notification to the database."""
    event_time = datetime.now()
    body = f"Face match: {suspect} in {frame} at {event_time.isoformat()}"

    try:
        client = Client(twilio_sid, twilio_token)
        call = client.calls.create(twiml=f'<Response><Say>{body}</Say></Response>', from_=twilio_from, to=twilio_to)
        logger.info(f"Voice call initiated: SID {call.sid}")
        delivery_status, delivery_time = 'SENT', datetime.now()
    except Exception:
        logger.exception("Failed to send voice alert")
        delivery_status, delivery_time = 'FAILED', None

    db_handler.insert_notification(
        cctv_id, suspect_id, event_time, 'MATCH', body, 'VOICE', delivery_status, delivery_time
    )