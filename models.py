from datetime import datetime
import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from uuid import uuid4
from storage import get_storage
db = SQLAlchemy(session_options={"expire_on_commit": True})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
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
    subnode_id = db.Column(db.Integer, db.ForeignKey('subnodes.id', ondelete='SET NULL'), nullable=True)
    notifications = db.relationship('NotificationRecipient', back_populates='recipient')
    subnode = db.relationship('Subnode', backref='users', foreign_keys=[subnode_id])

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
    ##site_id = db.Column(db.Integer, nullable=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    zone = db.Column(db.String(50), nullable=True)
    assigned_guard = db.Column(db.Integer, nullable=True)
    camera_model = db.Column(db.String(100), nullable=True)
    video_download_location = db.Column(db.String(255), nullable=True)
    stream_url = db.Column(db.String(500), nullable=True)

    site = db.relationship('Site', back_populates='cctvs')

class Suspect(db.Model):
    __tablename__ = 'suspects'

    suspect_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subnode_id = db.Column(db.Integer, db.ForeignKey('subnodes.id'), nullable=True)
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
    distribution_to = db.Column(db.String(1), nullable=True, default='P') # 'C', 'S', 'D', 'P'
    #shoe_size = db.Column(db.Float)
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
    subnode = db.relationship('Subnode', backref='suspects')

    def serialize(self, include_blob=False):
        data = {
            'suspect_id': self.suspect_id,
            'subnode_id': self.subnode_id,
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
            'distribution_to': self.distribution_to,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
            'aliases': self.aliases,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'description': self.description,
        }

    # add all file_path fields
        for i in range(6):
            path_attr = f'file_path{i}' if i > 0 else 'file_path'
            data[path_attr] = getattr(self, path_attr)

        if include_blob:
        # encode binary fields
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
                current_app.logger.error(f"[ERROR] Binary encoding failed: {e}")

            storage = get_storage()

        # encode image files
            for i in range(6):
                path_attr = f'file_path{i}' if i > 0 else 'file_path'
                blob_attr = f'file_blob{i}' if i > 0 else 'file_blob'

                file_path = getattr(self, path_attr)
                data[blob_attr] = None

                if file_path:
                    try:
                        binary_data = storage.load(file_path)  # ⬅️ Use storage strategy
                        b64_str = base64.b64encode(binary_data).decode('utf-8')
                        data[blob_attr] = b64_str
                        current_app.logger.debug(f"[SERIALIZE] Loaded and encoded {file_path} ({len(binary_data)} bytes)")
                    except Exception as e:
                        current_app.logger.warning(f"[SERIALIZE] Could not load image {file_path}: {e}")

        else:
            # if blobs not included, explicitly set blob fields to None
            for i in range(6):
                blob_attr = f'file_blob{i}' if i > 0 else 'file_blob'
                data[blob_attr] = None

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
    framebase64 = db.Column(db.Text, nullable=True) 

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
            'created_date': self.created_date,
            'framebase64': self.framebase64,
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

class Tenant(db.Model):
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    nodes = db.relationship('Node', backref='tenant', lazy=True)


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    parent_node_id = db.Column(db.Integer, db.ForeignKey('nodes.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    parent_node = db.relationship('Node', remote_side=[id], backref='child_nodes')
    subnodes = db.relationship('Subnode', backref='node', lazy=True)


class Subnode(db.Model):
    __tablename__ = 'subnodes'

    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), default="India")
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=True)
    taluka = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    full_address = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    station_house_officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    station_house_officer = db.relationship('User', foreign_keys=[station_house_officer_id])
    sites = db.relationship('Site', backref='subnode', lazy=True)

class Site(db.Model):
    __tablename__ = 'sites'

    id = db.Column(db.Integer, primary_key=True)
    subnode_id = db.Column(
        db.Integer, db.ForeignKey('subnodes.id', ondelete='CASCADE'), nullable=False
    )

    # DVR / Site metadata
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # DVR location
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(255), nullable=True)

    # DVR connection details
    dvr_ip = db.Column(db.String(45), nullable=True)  # IPv4/IPv6
    dvr_port = db.Column(db.Integer, default=554)      # Default RTSP port
    dvr_username = db.Column(db.String(100), nullable=True)
    dvr_password = db.Column(db.String(100), nullable=True)
    dvr_rtsp_url = db.Column(db.String(500), nullable=True)  # Full RTSP template if needed

    # DVR model/info
    dvr_model = db.Column(db.String(100), nullable=True)
    dvr_vendor = db.Column(db.String(100), nullable=True)
    dvr_firmware_version = db.Column(db.String(100), nullable=True)

    # Maintenance & status
    last_maintenance_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    cctvs = db.relationship('CCTV', back_populates='site', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "subnode_id": self.subnode_id,
            "name": self.name,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "address": self.address,
            "dvr_ip": self.dvr_ip,
            "dvr_port": self.dvr_port,
            "dvr_username": self.dvr_username,
            "dvr_password": self.dvr_password,
            "dvr_rtsp_url": self.dvr_rtsp_url,
            "dvr_model": self.dvr_model,
            "dvr_vendor": self.dvr_vendor,
            "dvr_firmware_version": self.dvr_firmware_version,
            "last_maintenance_date": str(self.last_maintenance_date) if self.last_maintenance_date else None,
            "is_active": self.is_active
        }