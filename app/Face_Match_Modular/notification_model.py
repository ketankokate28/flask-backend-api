from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

# Initialize SQLAlchemy
# In your Flask app, do:
#   from models import db
#   db.init_app(app)
#   with app.app_context():
#       db.create_all()

db = SQLAlchemy()

class Recipient(db.Model):
    __tablename__ = 'recipients'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(20))
    channels = Column(String(50), nullable=False)  # comma-separated, e.g. 'EMAIL,SMS,VOICE'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    call_tree_entries = relationship(
        'CallTreeEntry', back_populates='recipient', cascade='all, delete-orphan'
    )
    notifications = relationship(
        'NotificationRecipient', back_populates='recipient', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Recipient {self.id} {self.name}>"

class CallTreeEntry(db.Model):
    __tablename__ = 'call_tree'
    __table_args__ = (
        UniqueConstraint('level', 'channel', 'recipient_id', name='uix_call_tree'),
    )

    level = Column(Integer, primary_key=True)
    channel = Column(String(20), primary_key=True)
    recipient_id = Column(
        Integer,
        ForeignKey('recipients.id', ondelete='CASCADE'),
        primary_key=True
    )
    timeout = Column(Integer)  # seconds to wait before escalating

    recipient = relationship('Recipient', back_populates='call_tree_entries')

    def __repr__(self):
        return f"<CallTreeEntry level={self.level} channel={self.channel} recipient_id={self.recipient_id}>"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id                = Column(Integer, primary_key=True)
    cctv_id           = Column(Integer)
    suspect_id        = Column(Integer)
    event_time        = Column(DateTime, default=datetime.utcnow)
    notification_type = Column(String(20))  # e.g. 'MATCH'
    message           = Column(Text)
    created_at        = Column(DateTime, default=datetime.utcnow)

    recipients = relationship(
        'NotificationRecipient', back_populates='notification', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Notification {self.id} type={self.notification_type} at {self.event_time}>"

class NotificationRecipient(db.Model):
    __tablename__ = 'notification_recipients'

    id               = Column(Integer, primary_key=True)
    notification_id  = Column(
        Integer,
        ForeignKey('notifications.id', ondelete='CASCADE'),
        nullable=False
    )
    recipient_id     = Column(Integer, ForeignKey('user.id'), nullable=False)
    channel          = Column(String(20), nullable=False)  # 'EMAIL','SMS','VOICE'
    delivery_status  = Column(String(20))                  # 'SENT','FAILED', etc.
    delivery_time    = Column(DateTime)

    notification = relationship('Notification', back_populates='recipients')
    recipient    = relationship('Recipient', back_populates='notifications')

    def __repr__(self):
        return f"<NotifRecip notif={self.notification_id} recip={self.recipient_id} channel={self.channel}>"
