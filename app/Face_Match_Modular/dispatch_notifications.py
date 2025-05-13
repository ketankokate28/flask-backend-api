# dispatch_notifications.py
"""
Job B: Send out all pending notifications.
Runs every two minutes.
"""
from datetime import datetime, timezone
from models import db, Notification
from notification_service import notify_on_match


def dispatch():
    """
    Fetch all PENDING notifications, dispatch each via the notification service,
    then mark as SENT or FAILED.
    """
    pending = Notification.query.filter_by(status='PENDING').all()
    for notif in pending:
        try:
            # Dispatch alerts for this notification
            # Assuming notif.message encodes necessary info
            # Here we extract suspect_id, but you can include more fields in Notification
            notify_on_match(
                frame=None,
                suspect_name=f"Suspect {notif.suspect_id}",
                distance=0.0,
                cctv_id=None,
                suspect_id=notif.suspect_id,
                check_ack=None
            )
            notif.status = 'SENT'
        except Exception:
            db.session.rollback()
            notif.status = 'FAILED'
        notif.last_attempt = datetime.now(timezone.utc)
        db.session.commit()

if __name__ == '__main__':
    print("Dispatching pending notifications...")
    dispatch()
    print("Done.")
