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
    installation_date = db.Column(db.Date, nullable=True)
    last_maintenance_date = db.Column(db.Date, nullable=True)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
    file_path = db.Column(db.String(200))
    file_blob = db.Column(db.String)  # Changed to store Base64-encoded image data

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
            'file_path': self.file_path
        }

        if include_blob:
            print(f">>> DEBUG: Serializing blob for suspect {self.suspect_id}")
            if self.file_blob:
                data['file_blob_base64'] = self.file_blob  # Already base64 string in DB
                print(f">>> Base64 present for suspect {self.suspect_id}")
            else:
                print(f">>> No blob for suspect {self.suspect_id}")

        return data


class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    channel = db.Column(db.String(10), nullable=False)  # 'email', 'sms', 'call', 'push'
    cctv_id = db.Column(db.Integer, db.ForeignKey('cctv.id'), nullable=True)
    match_id = db.Column(db.Integer, nullable=True)  # You can set up ForeignKey if MatchLog exists
    payload = db.Column(db.Text, nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_attempt_at = db.Column(db.DateTime, nullable=True)
    attempt_count = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(10), default='pending', nullable=False)  # 'pending', 'sent', 'failed'
    last_error = db.Column(db.Text)

    def serialize(self):
        return {
            'notification_id': self.notification_id,
            'channel': self.channel,
            'cctv_id': self.cctv_id,
            'match_id': self.match_id,
            'payload': self.payload,
            'recipient': self.recipient,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            'attempt_count': self.attempt_count,
            'status': self.status,
            'last_error': self.last_error
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    value = db.Column(db.String(50), primary_key=True)  # e.g., "users.view"
    name = db.Column(db.String(100), nullable=False)    # e.g., "View Users"
    group_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    permissions = db.relationship(
        'Permission',
        secondary='role_permissions',
        backref='roles'
    )

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), primary_key=True)
    permission_value = db.Column(db.String(50), db.ForeignKey('permissions.value'), primary_key=True)

class Members(db.Model):
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    update_at= db.Column(db.DateTime, default=datetime.utcnow)
    def serialize(self):
        return {
            'member_id': self.member_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'update_at': self.update_at.isoformat() if self.update_at else None,
        }