# record_notifications.py
"""
Job A: Scan recent match logs and insert pending notifications for each suspect.
Runs every minute.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import distinct
from models import db, MatchFaceLogs, Notification
from config import ALERT_THROTTLE_WINDOW


def record_new():
    """
    Insert one PENDING Notification per suspect who matched in the last throttle window.
    """
    cutoff = datetime.now(timezone.utc) - ALERT_THROTTLE_WINDOW
    # Fetch distinct suspect_ids from match logs in the window
    rows = (
        db.session.query(distinct(MatchFaceLogs.suspect_id))
        .filter(MatchFaceLogs.capture_time >= cutoff)
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
    print("Recording new notifications...")
    record_new()
    print("Done.")