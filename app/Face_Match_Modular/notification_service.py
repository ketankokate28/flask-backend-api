# notification_service.py
import logging
from datetime import datetime, timezone
from sqlalchemy import and_, asc
import yagmail
from twilio.rest import Client

from config import (
    ALERT_THROTTLE_WINDOW,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    TWILIO_SID,
    TWILIO_TOKEN,
    TWILIO_FROM
)
from models import db, User, Notification, NotificationRecipient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _should_send(suspect_id: int) -> bool:
    """
    Return False if a MATCH notification for this suspect
    exists within the throttle window.
    """
    cutoff = datetime.now(timezone.utc) - ALERT_THROTTLE_WINDOW
    recent = Notification.query.filter(
        and_(
            Notification.suspect_id == suspect_id,
            Notification.notification_type == 'MATCH',
            Notification.event_time >= cutoff
        )
    ).first()
    return recent is None


def load_user_call_tree(channel: str):
    """
    Build a call-tree from active Users who have opted into the given channel.
    Groups users by their priority_<channel> value, in ascending order.
    Returns a list of dicts: [{'level': int, 'users': [User,...]}, ...]
    """
    if channel == 'EMAIL':
        flag = User.notify_email
        priority = User.priority_email
    elif channel == 'SMS':
        flag = User.notify_sms
        priority = User.priority_sms
    else:  # 'VOICE'
        flag = User.notify_call
        priority = User.priority_call

    users = User.query \
        .filter(User.is_active == True, flag == True) \
        .order_by(asc(priority)) \
        .all()

    tree = []
    last_level = None
    for u in users:
        lvl = getattr(u, priority.key)
        if lvl != last_level:
            last_level = lvl
            tree.append({'level': lvl, 'users': []})
        tree[-1]['users'].append(u)
    return tree


def _record_recipient(notification, user, channel, status):
    """
    Insert a NotificationRecipient row for the given user + channel.
    """
    nr = NotificationRecipient(
        notification_id=notification.id,
        user_id=user.id,
        channel=channel,
        delivery_status=status,
        delivery_time=datetime.now(timezone.utc)
    )
    db.session.add(nr)


def _send_email(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    """
    Send a single email to one user and record the result.
    """
    subject = f"🚨 Match Alert: {suspect_name}"
    body = (
        f"Suspect {suspect_name} matched in frame {frame}\n"
        f"Distance: {distance:.3f}\n"
        f"Camera ID: {cctv_id}\n"
        f"Time: {notification.event_time.isoformat()}"
    )
    try:
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
        yag.send(user.email, subject, body)
        status = 'SENT'
        logger.info(f"Email sent to {user.email}")
    except Exception:
        logger.exception(f"Email to {user.email} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'EMAIL', status)


def _send_sms(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    """
    Send a single SMS to one user and record the result.
    """
    body = (
        f"{suspect_name} matched in frame {frame}\n"
        f"Distance: {distance:.3f}, Camera ID: {cctv_id}"
    )
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=body, from_=TWILIO_FROM, to=user.phoneNumber)
        status = 'SENT'
        logger.info(f"SMS sent to {user.phoneNumber}")
    except Exception:
        logger.exception(f"SMS to {user.phoneNumber} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'SMS', status)


def _send_call(user, notification, frame, suspect_name, distance, cctv_id, suspect_id):
    """
    Initiate a voice call to one user and record the result.
    """
    twiml = f"<Response><Say>{suspect_name} matched in frame {frame}</Say></Response>"
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.calls.create(twiml=twiml, from_=TWILIO_FROM, to=user.phoneNumber)
        status = 'SENT'
        logger.info(f"Call initiated to {user.phoneNumber}")
    except Exception:
        logger.exception(f"Call to {user.phoneNumber} failed")
        status = 'FAILED'
    _record_recipient(notification, user, 'VOICE', status)


def _walk_tree(tree, send_func, notification, frame, suspect_name, distance, cctv_id, suspect_id, check_ack=None):
    """
    Walk through each level in the call-tree and send alerts.
    check_ack is optional for EMAIL to allow escalation logic.
    """
    for level_block in tree:
        for user in level_block['users']:
            send_func(user, notification, frame, suspect_name, distance, cctv_id, suspect_id)
        # if you want per-level ACK/timeouts, insert that logic here.


def notify_on_match(frame, suspect_name, distance, cctv_id, suspect_id, check_ack=None):
    """
    Master method to:
      1) enforce throttle per suspect
      2) create a Notification record
      3) send EMAIL → SMS → VOICE according to user priorities
      4) record per-user results
      5) mark Notification as SENT
    """
    if not _should_send(suspect_id):
        logger.info(f"Throttled alert for suspect {suspect_id}")
        return

    # 1) Create Notification
    notif = Notification(
        suspect_id=suspect_id,
        event_time=datetime.now(timezone.utc),
        notification_type='MATCH',
        message=f"{suspect_name} matched in frame {frame}",
        status='PENDING'
    )
    db.session.add(notif)
    db.session.flush()  # ensures notif.id is available

    # 2) EMAIL step
    email_tree = load_user_call_tree('EMAIL')
    _walk_tree(email_tree, _send_email, notif, frame, suspect_name, distance, cctv_id, suspect_id, check_ack)

    # 3) SMS step
    sms_tree = load_user_call_tree('SMS')
    _walk_tree(sms_tree, _send_sms, notif, frame, suspect_name, distance, cctv_id, suspect_id)

    # 4) VOICE step
    voice_tree = load_user_call_tree('VOICE')
    _walk_tree(voice_tree, _send_call, notif, frame, suspect_name, distance, cctv_id, suspect_id)

    # 5) Finalize
    notif.status = 'SENT'
    notif.last_attempt = datetime.now(timezone.utc)
    db.session.commit()
    logger.info(f"Notification {notif.id} dispatched successfully")
