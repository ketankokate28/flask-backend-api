from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, CCTV
from datetime import datetime

cctv_bp = Blueprint('cctv', __name__)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None

@cctv_bp.route('/', methods=['GET'])
@jwt_required()
def get_cctvs():
    all_ctvs = CCTV.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'location': c.location,
        'description': c.description,
        'ipAddress': c.ip_address,
        'latitude': c.latitude,
        'longitude': c.longitude,
        'altitude': c.altitude,
        'cameraType': c.camera_type,
        'cameraAngle': c.camera_angle,
        'resolution': c.resolution,
        'recordingStatus': c.recording_status,
        'storageDurationDays': c.storage_duration_days,
'installationDate': c.installation_date.strftime('%Y-%m-%d') if c.installation_date else None,
'lastMaintenanceDate': c.last_maintenance_date.strftime('%Y-%m-%d') if c.last_maintenance_date else None,
        'status': c.status,
'lastActiveTimestamp': c.last_active_timestamp.strftime('%Y-%m-%d %H:%M:%S') if c.last_active_timestamp else None,
        'errorCount': c.error_count,
        'autoRestart': c.auto_restart,
        'isCritical': c.is_critical,
        'faceCropEnabled': c.face_crop_enabled,
        'frameMatchInterval': c.frame_match_interval,
        'alertGroupId': c.alert_group_id,
        'siteId': c.site_id,
        'zone': c.zone,
        'assignedGuard': c.assigned_guard,
        'cameraModel': c.camera_model,
        'videoDownloadLocation': c.video_download_location,
        'streamUrl': c.stream_url
    } for c in all_ctvs])

@cctv_bp.route('/', methods=['POST'])
@jwt_required()
def create_cctv():
    data = request.get_json() or {}
    c = CCTV(
        name=data.get('name'),
        location=data.get('location'),
        description=data.get('description'),
        ip_address=data.get('ipAddress'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        altitude=data.get('altitude'),
        camera_type=data.get('cameraType'),
        camera_angle=data.get('cameraAngle'),
        resolution=data.get('resolution'),
        recording_status=data.get('recordingStatus'),
        storage_duration_days=data.get('storageDurationDays'),
       # installation_date=datetime.strptime(data.get('installationDate'), '%Y-%m-%d').date(),
       # last_maintenance_date=datetime.strptime(data.get('lastMaintenanceDate'), '%Y-%m-%d').date(),
        installation_date=parse_date(data.get('installationDate')),
        last_maintenance_date=parse_date(data.get('lastMaintenanceDate')),
        status=data.get('status'),
        last_active_timestamp=datetime.utcnow(),
        error_count=data.get('errorCount'),
        auto_restart=data.get('autoRestart'),
        is_critical=data.get('isCritical'),
        face_crop_enabled=data.get('faceCropEnabled'),
        frame_match_interval=data.get('frameMatchInterval'),
        alert_group_id=data.get('alertGroupId'),
        site_id=data.get('siteId'),
        zone=data.get('zone'),
        assigned_guard=data.get('assignedGuard'),
        camera_model=data.get('cameraModel'),
        video_download_location=data.get('videoDownloadLocation'),
        stream_url=data.get('streamUrl')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(id=c.id, name=c.name, streamUrl=c.stream_url), 201

@cctv_bp.route('/<int:cctv_id>', methods=['PUT'])
@jwt_required()
def update_cctv(cctv_id):
    data = request.get_json() or {}
    c = CCTV.query.get_or_404(cctv_id)
    c.name = data.get('name', c.name)
    c.location = data.get('location', c.location)
    c.description = data.get('description', c.description)
    c.ip_address = data.get('ipAddress', c.ip_address)
    c.latitude = data.get('latitude', c.latitude)
    c.longitude = data.get('longitude', c.longitude)
    c.altitude = data.get('altitude', c.altitude)
    c.camera_type = data.get('cameraType', c.camera_type)
    c.camera_angle = data.get('cameraAngle', c.camera_angle)
    c.resolution = data.get('resolution', c.resolution)
    c.recording_status = data.get('recordingStatus', c.recording_status)
    c.storage_duration_days = data.get('storageDurationDays', c.storage_duration_days)

    new_installation_date = parse_date(data.get('installationDate'))
    new_maintenance_date = parse_date(data.get('lastMaintenanceDate'))
    c.installation_date = new_installation_date if new_installation_date is not None else c.installation_date
    c.last_maintenance_date = new_maintenance_date if new_maintenance_date is not None else c.last_maintenance_date

    c.status = data.get('status', c.status)
    c.last_active_timestamp = datetime.utcnow()
    c.error_count = data.get('errorCount', c.error_count)
    c.auto_restart = data.get('autoRestart', c.auto_restart)
    c.is_critical = data.get('isCritical', c.is_critical)
    c.face_crop_enabled = data.get('faceCropEnabled', c.face_crop_enabled)
    c.frame_match_interval = data.get('frameMatchInterval', c.frame_match_interval)
    c.alert_group_id = data.get('alertGroupId', c.alert_group_id)
    c.site_id = data.get('siteId', c.site_id)
    c.zone = data.get('zone', c.zone)
    c.assigned_guard = data.get('assignedGuard', c.assigned_guard)
    c.camera_model = data.get('cameraModel', c.camera_model)
    c.video_download_location = data.get('videoDownloadLocation', c.video_download_location)
    c.stream_url = data.get('streamUrl', c.stream_url)

    db.session.commit()
    return jsonify(msg='Updated')

@cctv_bp.route('/<int:cctv_id>', methods=['DELETE'])
@jwt_required()
def delete_cctv(cctv_id):
    c = CCTV.query.get_or_404(cctv_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify(msg='Deleted')
