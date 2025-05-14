from datetime import datetime
from app import create_app
from models import db, User, Suspect, CCTV, Notification, NotificationRecipient

# Initialize the app
app = create_app()

def seed_data():
    # Fetch existing User, Suspect, and CCTV records
    user = db.session.query(User).filter_by(id=1).first()
    suspect = db.session.query(Suspect).filter_by(suspect_id=1).first()
    cctv = db.session.query(CCTV).filter_by(id=1).first()

    if not user or not suspect or not cctv:
        print("Required records (User, Suspect, CCTV) not found. Please ensure they exist.")
        return

    # Create a Notification record
    notification = Notification(
        cctv_id=cctv.id, 
        suspect_id=suspect.suspect_id, 
        event_time=datetime.utcnow(),
        notification_type="MATCH", 
        message=f"Match detected for suspect {suspect.first_name} {suspect.last_name}"
    )
    db.session.add(notification)
    db.session.commit()

    # Create NotificationRecipients for the Notification
    recipient1 = NotificationRecipient(
        notification_id=notification.id, 
        recipient_id=user.id, 
        channel="EMAIL", 
        delivery_status="SENT", 
        delivery_time=datetime.utcnow()
    )

    recipient2 = NotificationRecipient(
        notification_id=notification.id, 
        recipient_id=user.id, 
        channel="SMS", 
        delivery_status="FAILED", 
        delivery_time=datetime.utcnow()
    )
    
    db.session.add(recipient1)
    db.session.add(recipient2)
    db.session.commit()

    print("Notification and NotificationRecipient data seeded successfully!")

if __name__ == '__main__':
    with app.app_context():
        seed_data()
