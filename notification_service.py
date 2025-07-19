import base64
from io import BytesIO
import logging
from datetime import datetime

from flask import app
import yagmail
from twilio.rest import Client
from sqlalchemy import asc
from pathlib import Path

from config import (
    email_sender,
    email_password,
    twilio_sid,
    twilio_token,
    twilio_from
)
from models import (
    db,
    User,
    Notification,
    NotificationRecipient,
    Suspect,
    CCTV,
    Matchfacelog,
    Site,
    Subnode,
    Node,
    Tenant
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEMP_FOLDER = Path(__file__).parent / 'temp_email_attachments'
TEMP_FOLDER.mkdir(exist_ok=True)


def load_user_call_tree(channel: str, subnode_id: int):
    """
    Load active users subscribed to the given channel and belonging to the specified subnode,
    ordered by priority and grouped by level.
    """
    if channel == 'EMAIL':
        flag, prio = User.notify_email, User.priority_email
    elif channel == 'SMS':
        flag, prio = User.notify_sms, User.priority_sms
    else:  # 'VOICE'
        flag, prio = User.notify_call, User.priority_call

    users = (
        User.query
            .filter(
                User.is_active == True,
                flag == True,
                User.subnode_id == subnode_id
            )
            .order_by(asc(prio))
            .all()
    )

    tree, last_level = [], None
    for u in users:
        level = getattr(u, prio.key)
        if level != last_level:
            last_level = level
            tree.append({'level': level, 'users': []})
        tree[-1]['users'].append(u)
    return tree


def _record_recipient(notification_id, user_id, channel, status):
    nr = NotificationRecipient(
        notification_id=notification_id,
        recipient_id=user_id,
        channel=channel,
        delivery_status=status,
        delivery_time=datetime.utcnow()
    )
    db.session.add(nr)

def _send_email(user, notification, suspect_name, suspect_descr,
                cctv_name, cctv_descr, site_name,
                subnode_name, subnode_state, subnode_district,
                node_name, tenant_name, frame_path):
    subject = f"🚨 Alert: {suspect_name} spotted on {cctv_name}"
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    html_body = f"""
    <html>
      <body style="font-family:Arial; padding:20px; background:#f0f0f0;">
        <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border-radius:8px;">
          <h2>🚨 Alert: {suspect_name}</h2>
          <p><strong>Camera:</strong> {cctv_name}</p>
          <p><strong>Location:</strong> {cctv_descr}</p>
          <p><strong>Site:</strong> {site_name}</p>
          <p><strong>Subnode:</strong> {subnode_name}</p>
          <p><strong>State:</strong> {subnode_state}</p>
          <p><strong>District:</strong> {subnode_district}</p>
          <p><strong>Node:</strong> {node_name}</p>
          <p><strong>Tenant:</strong> {tenant_name}</p>
          <p><strong>Suspect Details:</strong> {suspect_descr}</p>
          <p><strong>Time:</strong> {timestamp}</p>
        </div>
      </body>
    </html>
    """

    attachment_path = None
    try:
        yag = yagmail.SMTP(email_sender, email_password)

        # Decode base64 and write to temp file
        binary_data = base64.b64decode(frame_path)
        filename = f"{suspect_name.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.jpg"
        attachment_path = TEMP_FOLDER / filename

        with open(attachment_path, 'wb') as f:
            f.write(binary_data)

        # Send email with attachment
        yag.send(
            to=user.email,
            subject=subject,
            contents=[
                html_body,
                str(attachment_path)
            ]
        )

        status = 'SENT'
        logger.info(f"Email sent to {user.email}")
    except Exception:
        logger.exception(f"Failed email to {user.email}")
        status = 'FAILED'
    finally:
        # Always attempt cleanup
        if attachment_path and attachment_path.exists():
            try:
                attachment_path.unlink()
                logger.debug(f"Deleted temp attachment: {attachment_path}")
            except Exception:
                logger.warning(f"Failed to delete temp attachment: {attachment_path}")

    _record_recipient(notification.id, user.id, 'EMAIL', status)


def _send_sms(user, notification, suspect_name, suspect_descr, cctv_name):
    body = f"Alert! {suspect_name} detected on {cctv_name}: {notification.message}"
    try:
        client = Client(twilio_sid, twilio_token)
        client.messages.create(body=body, from_=twilio_from, to=user.phoneNumber)
        status = 'SENT'
        logger.info(f"SMS sent to {user.phoneNumber}")
    except Exception:
        logger.exception(f"Failed SMS to {user.phoneNumber}")
        status = 'FAILED'
    _record_recipient(notification.id, user.id, 'SMS', status)


def _send_call(user, notification, suspect_name, suspect_descr, cctv_name):
    twiml = f"<Response><Say>Alert {suspect_name} detected on {cctv_name}</Say></Response>"
    try:
        client = Client(twilio_sid, twilio_token)
        client.calls.create(twiml=twiml, from_=twilio_from, to=user.phoneNumber)
        status = 'SENT'
        logger.info(f"Call succeeded to {user.phoneNumber}")
    except Exception:
        logger.exception(f"Failed call to {user.phoneNumber}")
        status = 'FAILED'
    _record_recipient(notification.id, user.id, 'VOICE', status)


def dispatch_notification(matchfacelog_id: int, framebase64: any, siteId: int) -> int:
    """
    1) Ensures a Notification exists for the match event.
    2) Gathers related hierarchy: site, subnode, node, tenant.
    3) Dispatches notifications only to users in that subnode, grouped by priority.
    Returns the number of deliveries recorded.
    """
    match = Matchfacelog.query.get(matchfacelog_id)
    if not match:
        raise ValueError(f"MatchFaceLog {matchfacelog_id} not found")

    notif = Notification.query.filter_by(
        cctv_id=match.cctv_id,
        suspect_id=match.suspect_id,
        event_time=match.capture_time
    ).first()
    if not notif:
        notif = Notification(
            cctv_id=match.cctv_id,
            suspect_id=match.suspect_id,
            event_time=match.capture_time,
            notification_type='MATCH',
            message=f"Suspect {match.suspect_id} detected"
        )
        db.session.add(notif)
        db.session.commit()

    cam = CCTV.query.get(match.cctv_id)
    site = Site.query.get(cam.site_id) if cam else None
    subnode = Subnode.query.get(site.subnode_id) if site else None
    node = Node.query.get(subnode.node_id) if subnode else None
    tenant = Tenant.query.get(node.tenant_id) if node else None

    suspect = Suspect.query.get(notif.suspect_id)
    suspect_name = f"{suspect.first_name} {suspect.last_name}" if suspect else ''
    suspect_descr = suspect.description or '' if suspect else ''

    cctv_name = cam.name if cam else ''
    cctv_descr = cam.location or cam.description or '' if cam else ''
    site_name = site.name if site else ''
    subnode_name = subnode.name if subnode else ''
    subnode_state = subnode.state if subnode else ''
    subnode_district = subnode.district if subnode else ''
    node_name = node.name if node else ''
    tenant_name = tenant.name if tenant else ''
    frame_path = framebase64

    deliveries = 0
    if subnode:
        tree = load_user_call_tree('EMAIL', subnode.id)
        for level in tree:
            for user in level['users']:
                _send_email(
                    user, notif, suspect_name, suspect_descr,
                    cctv_name, cctv_descr, site_name,
                    subnode_name, subnode_state, subnode_district,
                    node_name, tenant_name, frame_path
                )
                deliveries += 1
        # SMS
        tree_sms = load_user_call_tree('SMS', subnode.id)
        for level in tree_sms:
            for user in level['users']:
                _send_sms(user, notif, suspect_name, suspect_descr, cctv_name)
                deliveries += 1
        # VOICE
        tree_voice = load_user_call_tree('VOICE', subnode.id)
        for level in tree_voice:
            for user in level['users']:
                _send_call(user, notif, suspect_name, suspect_descr, cctv_name)
                deliveries += 1

    db.session.commit()
    logger.info(f"Notification {notif.id} dispatched to {deliveries} users")
    return deliveries
