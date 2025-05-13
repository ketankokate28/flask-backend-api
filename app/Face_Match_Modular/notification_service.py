# notification_service.py

import logging
from datetime import datetime, timezone
from sqlalchemy import asc
import yagmail
from twilio.rest import Client

from config import (
    e_mail_sender, e_mail_password,
    twilio_sid,   twilio_token, twilio_from
)
from db_models import db, User, NotificationRecipient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_user_call_tree(channel: str):
    """Build call‐tree levels from User.notify_* & priority_* flags."""
    if channel == 'EMAIL':
        flag, prio = User.notify_email, User.priority_email
    elif channel == 'SMS':
        flag, prio = User.notify_sms,   User.priority_sms
    else:  # VOICE
        flag, prio = User.notify_call,  User.priority_call

    users = (
        User.query
            .filter(User.is_active==True, flag==True)
            .order_by(asc(prio))
            .all()
    )

    tree, last = [], None
    for u in users:
        lvl = getattr(u, prio.key)
        if lvl != last:
            last = lvl
            tree.append({'level': lvl, 'users': []})
        tree[-1]['users'].append(u)
    return tree


def _record_recipient(notification, user, channel, status):
    """Log one per‐user delivery attempt."""
    nr = NotificationRecipient(
        notification_id = notification.notification_id,
        user_id         = user.id,
        channel         = channel,
        delivery_status = status,
        delivery_time   = datetime.now(timezone.utc)
    )
    db.session.add(nr)


def _send_email(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    subject = f"🚨 Match Alert: {suspect_name}"
    body    = (
        f"{suspect_name} matched in {frame}\n"
        f"Distance: {distance:.3f}\n"
        f"Camera: {cctv_id}\n"
        f"Time: {notification.event_time.isoformat()}"
    )
    try:
        yag = yagmail.SMTP(e_mail_sender, e_mail_password)
        yag.send(user.email, subject, body)
        status = 'SENT'
    except Exception:
        logger.exception(f"Email to {user.email} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'EMAIL', status)


def _send_sms(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    body = (
        f"{suspect_name} matched in {frame}\n"
        f"Distance: {distance:.3f}, Camera: {cctv_id}"
    )
    try:
        client = Client(twilio_sid, twilio_token)
        client.messages.create(body=body, from_=twilio_from, to=user.phoneNumber)
        status = 'SENT'
    except Exception:
        logger.exception(f"SMS to {user.phoneNumber} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'SMS', status)


def _send_call(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    twiml = f"<Response><Say>{suspect_name} matched in {frame}</Say></Response>"
    try:
        client = Client(twilio_sid, twilio_token)
        client.calls.create(twiml=twiml, from_=twilio_from, to=user.phoneNumber)
        status = 'SENT'
    except Exception:
        logger.exception(f"Call to {user.phoneNumber} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'VOICE', status)


def dispatch_notification(
    notification,
    frame, suspect_name, distance, cctv_id, suspect_id, check_ack=None
):
    """
    Given an existing PENDING Notification, walk through EMAIL→SMS→VOICE,
    log per‐user attempts, then mark the Notification itself as SENT.
    """
    # EMAIL
    email_tree = load_user_call_tree('EMAIL')
    for lvl in email_tree:
        for user in lvl['users']:
            _send_email(user, notification, frame, suspect_name, distance, cctv_id, suspect_id)
        # (optional) ACK logic…

    # SMS
    sms_tree = load_user_call_tree('SMS')
    for lvl in sms_tree:
        for user in lvl['users']:
            _send_sms(user, notification, frame, suspect_name, distance, cctv_id, suspect_id)

    # VOICE
    voice_tree = load_user_call_tree('VOICE')
    for lvl in voice_tree:
        for user in lvl['users']:
            _send_call(user, notification, frame, suspect_name, distance, cctv_id, suspect_id)

    # Finalize
    notification.status         = 'SENT'
    notification.last_attempt_at = datetime.now(timezone.utc)
    db.session.commit()
    logger.info(f"Notification {notification.notification_id} dispatched")
