from app import app  # make sure your Flask app is exposed in app.py
from models import db, Notification

with app.app_context():
    # Create sample notifications
    notifications = [
        Notification(
            channel='email',
            cctv_id=1,
            match_id=None,
            payload='{"message": "Suspicious activity detected"}',
            recipient='user@example.com',
            status='pending'
        ),
        Notification(
            channel='sms',
            cctv_id=2,
            match_id=None,
            payload='{"message": "Unauthorized entry"}',
            recipient='+1234567890',
            status='sent'
        ),
        Notification(
            channel='push',
            cctv_id=None,
            match_id=None,
            payload='{"alert": "Camera offline"}',
            recipient='user_device_token',
            status='failed',
            last_error='Device unreachable'
        )
    ]

    # Add and commit
    db.session.add_all(notifications)
    db.session.commit()
    print("✅ Sample notifications inserted successfully.")
