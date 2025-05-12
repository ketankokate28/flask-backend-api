# alert_utils.py
import logging
from datetime import datetime
import sqlite3
import yagmail
from twilio.rest import Client
from config import (
    e_mail_sender,
    e_mail_password,
    e_mail_receiver,
    twilio_sid,
    twilio_token,
    twilio_from,
    twilio_to,
    db_path  # path to your SQLite database
)

logger = logging.getLogger(__name__)


def insert_notification(cctv_id: int,
                        suspect_id: int | None,
                        event_time: datetime,
                        notification_type: str,
                        message: str,
                        channel: str,
                        delivery_status: str,
                        delivery_time: datetime | None):
    """
    Inserts a notification record into the Notifications table.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Notifications (
                cctv_id,
                suspect_id,
                event_time,
                notification_type,
                message,
                channel,
                delivery_status,
                delivery_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cctv_id,
                suspect_id,
                event_time.isoformat(),
                notification_type,
                message,
                channel,
                delivery_status,
                delivery_time.isoformat() if delivery_time else None
            )
        )
        conn.commit()
        cursor.close()
    except Exception:
        logger.exception("Failed to insert notification into DB")
    finally:
        conn.close()


def send_email_alert(frame: str,
                     suspect: str,
                     distance: float,
                     cctv_id: int,
                     suspect_id: int | None):
    """
    Sends an email alert and logs the notification to the database.
    """
    event_time = datetime.now()
    body = (
        f"Match in {frame}\n"
        f"Suspect: {suspect}\n"
        f"Distance: {distance:.3f}\n"
        f"Time: {event_time.isoformat()}"
    )
    try:
        yag = yagmail.SMTP(e_mail_sender, e_mail_password)
        subject = f"🚨 Face Match: {suspect}"
        yag.send(e_mail_receiver, subject, body)
        logger.info("Email alert sent")
        delivery_status = 'SENT'
        delivery_time = datetime.now()
    except Exception:
        logger.exception("Failed to send email alert")
        delivery_status = 'FAILED'
        delivery_time = None

    insert_notification(
        cctv_id=cctv_id,
        suspect_id=suspect_id,
        event_time=event_time,
        notification_type='MATCH',
        message=body,
        channel='EMAIL',
        delivery_status=delivery_status,
        delivery_time=delivery_time
    )


def send_sms_alert(frame: str,
                   suspect: str,
                   cctv_id: int,
                   suspect_id: int | None):
    """
    Sends an SMS alert and logs the notification to the database.
    """
    event_time = datetime.now()
    body = f"Face match: {suspect} in {frame} at {event_time.isoformat()}"
    try:
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(
            body=body,
            from_=twilio_from,
            to=twilio_to
        )
        logger.info(f"SMS sent: SID {msg.sid}")
        delivery_status = 'SENT'
        delivery_time = datetime.now()
    except Exception:
        logger.exception("Failed to send SMS alert")
        delivery_status = 'FAILED'
        delivery_time = None

    insert_notification(
        cctv_id=cctv_id,
        suspect_id=suspect_id,
        event_time=event_time,
        notification_type='MATCH',
        message=body,
        channel='SMS',
        delivery_status=delivery_status,
        delivery_time=delivery_time
    )


def send_call_alert(frame: str,
                    suspect: str,
                    cctv_id: int,
                    suspect_id: int | None):
    """
    Sends a voice call alert and logs the notification to the database.
    """
    event_time = datetime.now()
    body = f"Face match: {suspect} in {frame} at {event_time.isoformat()}"
    try:
        client = Client(twilio_sid, twilio_token)
        call = client.calls.create(
            twiml=f'<Response><Say>{body}</Say></Response>',
            from_=twilio_from,
            to=twilio_to
        )
        logger.info(f"Voice call initiated: SID {call.sid}")
        delivery_status = 'SENT'
        delivery_time = datetime.now()
    except Exception:
        logger.exception("Failed to send voice alert")
        delivery_status = 'FAILED'
        delivery_time = None

    insert_notification(
        cctv_id=cctv_id,
        suspect_id=suspect_id,
        event_time=event_time,
        notification_type='MATCH',
        message=body,
        channel='VOICE',
        delivery_status=delivery_status,
        delivery_time=delivery_time
    )
