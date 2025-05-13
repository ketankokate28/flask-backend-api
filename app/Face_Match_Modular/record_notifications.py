# record_notifications.py
"""
Job A: Scan recent match logs and insert pending notifications for each suspect.
Runs every minute.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import distinct
from db_models import db, MatchFaceLog, Notification
from config import ALERT_THROTTLE_WINDOW
from app_scheduler import create_app


def record_new():
    """
    Insert one PENDING Notification per suspect who matched in the last throttle window.
    """
    cutoff = datetime.now() - ALERT_THROTTLE_WINDOW
    # Fetch distinct suspect_ids from match logs in the window
    rows = (
        db.session.query(distinct(MatchFaceLog.suspect_id))
        .filter(MatchFaceLog.capture_time >= cutoff)
        .all()
    )
    suspect_ids = [r[0] for r in rows]

    for sid in suspect_ids:
        # Skip if a PENDING notification already exists
        exists = (
            Notification.query
            .filter_by(suspect_id=sid, status='PENDING')
            .first()
        )
        if exists:
            continue

        # Create new notification
        notif = Notification(
            suspect_id=sid,
            event_time=datetime.now(timezone.utc),
            notification_type='MATCH',
            message=f"Suspect {sid} matched recently",
            status='PENDING'
        )
        db.session.add(notif)

    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        record_new()