from datetime import datetime,timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from uuid import uuid4

db = SQLAlchemy(session_options={"expire_on_commit": True})
    
class MatchFaceLog(db.Model):
    __tablename__ = 'Matchfacelogs'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    capture_time  = db.Column(db.DateTime, nullable=False)
    frame         = db.Column(db.String(255), nullable=False)
    cctv_id       = db.Column(db.Integer, db.ForeignKey('cctv.id'), nullable=True)
    suspect_id    = db.Column(db.Integer, nullable=True)
    suspect       = db.Column(db.String(100), nullable=True)
    distance      = db.Column(db.Float, nullable=False)
    created_date  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<MatchFaceLog id={self.id} "
            f"suspect_id={self.suspect_id} distance={self.distance:.3f} "
            f"time={self.capture_time.isoformat()}>"
        )
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    password_hash= db.Column(db.String(128), nullable=False)
    role         = db.Column(db.String(20), nullable=False)
    jobTitle         = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    fullName= db.Column(db.String(50), nullable=True)
    phoneNumber= db.Column(db.String(20), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Recipient(db.Model):
    __tablename__ = 'recipients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    channels = db.Column(db.String(50), nullable=False)  # comma-separated, e.g. 'EMAIL,SMS,VOICE'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    call_tree_entries = db.relationship(
        'CallTreeEntry', back_populates='recipient', cascade='all, delete-orphan'
    )
    notifications = db.relationship(
        'NotificationRecipient', back_populates='recipient', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Recipient id={self.id} name={self.name!r}>"

class CallTreeEntry(db.Model):
    __tablename__ = 'call_tree'
    __table_args__ = (
        db.UniqueConstraint('level', 'channel', 'recipient_id', name='uix_call_tree'),
    )

    level = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(20), primary_key=True)
    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey('recipients.id', ondelete='CASCADE'),
        primary_key=True
    )
    timeout = db.Column(db.Integer)  # seconds to wait before escalating

    recipient = db.relationship('Recipient', back_populates='call_tree_entries')

    def __repr__(self):
        return f"<CallTreeEntry level={self.level} channel={self.channel} recipient_id={self.recipient_id}>"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    cctv_id = db.Column(db.Integer, nullable=True)
    suspect_id = db.Column(db.Integer, nullable=True)
    event_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notification_type = db.Column(db.String(20), nullable=True)  # e.g. 'MATCH'
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(10), default='PENDING', nullable=False)  # PENDING / SENT / FAILED
    recipients = db.relationship(
        'NotificationRecipient', back_populates='notification', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Notification id={self.id} type={self.notification_type} at {self.event_time}>"

class NotificationRecipient(db.Model):
    __tablename__ = 'notification_recipients'

    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(
        db.Integer,
        db.ForeignKey('notifications.id', ondelete='CASCADE'),
        nullable=False
    )
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # 'EMAIL','SMS','VOICE'
    delivery_status = db.Column(db.String(20), nullable=True)  # 'SENT','FAILED', etc.
    delivery_time = db.Column(db.DateTime, nullable=True)

    notification = db.relationship('Notification', back_populates='recipients')
    recipient = db.relationship('Recipient', back_populates='notifications')

    def __repr__(self):
        return f"<NotificationRecipient notif_id={self.notification_id} recipient_id={self.recipient_id} channel={self.channel}>"
