from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from uuid import uuid4

db = SQLAlchemy(session_options={"expire_on_commit": True})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    jobTitle = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    fullName = db.Column(db.String(50), nullable=True)
    phoneNumber = db.Column(db.String(20), nullable=True)
    notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=True)
    notify_call = db.Column(db.Boolean, default=True)
    priority_email = db.Column(db.Integer, default=0)
    priority_sms = db.Column(db.Integer, default=0)
    priority_call = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=True)
    notifications = db.relationship('NotificationRecipient', back_populates='recipient')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CCTV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    camera_type = db.Column(db.String(20), nullable=True)
    camera_angle = db.Column(db.String(10), nullable=True)
    resolution = db.Column(db.String(10), nullable=True)
    recording_status = db.Column(db.String(10), nullable=True)
    storage_duration_days = db.Column(db.Integer, nullable=True)
    installation_date = db.Column(db.DateTime, nullable=True)
    last_maintenance_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    last_active_timestamp = db.Column(db.DateTime, nullable=True)
    error_count = db.Column(db.Integer, nullable=True)
    auto_restart = db.Column(db.Boolean, nullable=True)
    is_critical = db.Column(db.Boolean, nullable=True)
    face_crop_enabled = db.Column(db.Boolean, nullable=True)
    frame_match_interval = db.Column(db.Integer, nullable=True)
    alert_group_id = db.Column(db.Integer, nullable=True)
    site_id = db.Column(db.Integer, nullable=True)
    zone = db.Column(db.String(50), nullable=True)
    assigned_guard = db.Column(db.Integer, nullable=True)
    camera_model = db.Column(db.String(100), nullable=True)
    video_download_location = db.Column(db.String(255), nullable=True)
    stream_url = db.Column(db.String(500), nullable=True)

class Suspect(db.Model):
    __tablename__ = 'suspects'

    suspect_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)  # 'M', 'F', 'O', 'U'
    nationality = db.Column(db.String(100))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    shoulder_width_cm = db.Column(db.Float)
    torso_height_cm = db.Column(db.Float)
    leg_length_cm = db.Column(db.Float)
    shoe_size = db.Column(db.Float)
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    face_embedding = db.Column(db.LargeBinary)
    fingerprint_template = db.Column(db.LargeBinary)
    iris_code = db.Column(db.LargeBinary)
    gait_signature = db.Column(db.LargeBinary)
    aliases = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
    file_path = db.Column(db.String(200))
    description = db.Column(db.String(2000))
    file_blob = db.Column(db.String)  # Changed to store Base64-encoded image data
    file_path1 = db.Column(db.String(200))
    file_blob1 = db.Column(db.String)
    file_path2 = db.Column(db.String(200))
    file_blob2 = db.Column(db.String)
    file_path3 = db.Column(db.String(200))
    file_blob3 = db.Column(db.String)
    file_path4 = db.Column(db.String(200))
    file_blob4 = db.Column(db.String)
    file_path5 = db.Column(db.String(200))
    file_blob5 = db.Column(db.String)

    def serialize(self, include_blob=False):
        data = {
            'suspect_id': self.suspect_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'nationality': self.nationality,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'shoulder_width_cm': self.shoulder_width_cm,
            'torso_height_cm': self.torso_height_cm,
            'leg_length_cm': self.leg_length_cm,
            'shoe_size': self.shoe_size,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
            'aliases': self.aliases,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'file_path1': self.file_path1,
            'file_path2': self.file_path2,
            'file_path3': self.file_path3,
            'file_path4': self.file_path4,
            'file_path5': self.file_path5,
            'description': self.description
        }


        if include_blob:
            try:
                if self.face_embedding:
                    data['face_embedding'] = base64.b64encode(self.face_embedding).decode('utf-8')
                if self.fingerprint_template:
                    data['fingerprint_template'] = base64.b64encode(self.fingerprint_template).decode('utf-8')
                if self.iris_code:
                    data['iris_code'] = base64.b64encode(self.iris_code).decode('utf-8')
                if self.gait_signature:
                    data['gait_signature'] = base64.b64encode(self.gait_signature).decode('utf-8')
            except Exception as e:
                print(f"[ERROR] Binary encoding failed: {e}")

            for i in range(1, 6):
                blob_attr = f'file_blob{i if i > 0 else ""}'
                if getattr(self, blob_attr):
                    data[f'file_blob{i}_base64'] = getattr(self, blob_attr)
                else:
                    data[f'file_blob{i}_base64'] = None

        return data

class Matchfacelog(db.Model):
    __tablename__ = 'Matchfacelogs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    capture_time = db.Column(db.DateTime, nullable=False)
    frame = db.Column(db.Text, nullable=False)
    cctv_id = db.Column(db.Integer, db.ForeignKey('cctv.id'), nullable=False)
    suspect_id = db.Column(db.Integer, db.ForeignKey('suspects.suspect_id'), nullable=True)
    suspect = db.Column(db.Text, nullable=True)
    distance = db.Column(db.Float, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)

    cctv = db.relationship('CCTV', backref=db.backref('match_logs', lazy=True))
    suspect_ref = db.relationship('Suspect', backref=db.backref('match_logs', lazy=True), foreign_keys=[suspect_id])

    def serialize(self):
        return {
            'id': self.id,
            'capture_time': self.capture_time,
            'frame': self.frame,
            'cctv_id': self.cctv_id,
            'suspect_id': self.suspect_id,
            'suspect': self.suspect,
            'distance': self.distance,
            'created_date': self.created_date
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    cctv_id = db.Column(db.Integer)
    suspect_id = db.Column(db.Integer)
    event_time = db.Column(db.DateTime, default=datetime.now)
    notification_type = db.Column(db.String(20))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    recipients = db.relationship('NotificationRecipient', back_populates='notification', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'cctv_id': self.cctv_id,
            'suspect_id': self.suspect_id,
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'notification_type': self.notification_type,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'recipients': [r.serialize() for r in self.recipients]
        }

class NotificationRecipient(db.Model):
    __tablename__ = 'notification_recipients'
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    delivery_status = db.Column(db.String(20))
    delivery_time = db.Column(db.DateTime)

    notification = db.relationship('Notification', back_populates='recipients')
    recipient = db.relationship('User', back_populates='notifications')

    def serialize(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'recipient_id': self.recipient_id,
            'channel': self.channel,
            'delivery_status': self.delivery_status,
            'delivery_time': self.delivery_time.isoformat() if self.delivery_time else None
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    value = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), primary_key=True)
    permission_value = db.Column(db.String(50), db.ForeignKey('permissions.value'), primary_key=True)

class PoliceStation(db.Model):
    __tablename__ = 'police_stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), default="India")
    state = db.Column(db.String(50), nullable=False)
    taluka = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=False)
    full_address = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    station_house_officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    station_house_officer = db.relationship('User', foreign_keys=[station_house_officer_id])
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
