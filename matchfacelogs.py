import threading
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, Matchfacelog
import base64
import os
from flask import jsonify, send_file, current_app
from config import Config
from notification_service import dispatch_notification

matchfacelogs_bp = Blueprint('matchfacelogs', __name__)

@matchfacelogs_bp.route('/', methods=['GET'])
@jwt_required()
def get_matchfacelogs():
    db.session.expire_all()
    logs = Matchfacelog.query.order_by(Matchfacelog.capture_time.desc()).all()

    return jsonify([
        {
            'id': log.id,
            'captureTime': log.capture_time,
            'frame': log.frame,
            'cctvId': log.cctv_id,
            'suspectId': log.suspect_id,
            'suspect': log.suspect,
            'distance': log.distance,
            'createdDate': log.created_date
        }
        for log in logs
    ])

@matchfacelogs_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_suspect_summary():
    from sqlalchemy import func

    # Group by suspect_id and get latest capture_time + count
    results = (
        db.session.query(
            Matchfacelog.suspect_id,
            func.max(Matchfacelog.capture_time).label("latest_capture"),
            func.count(Matchfacelog.id).label("match_count"),
            #Matchfacelog.suspect
            func.max(Matchfacelog.suspect).label("suspect")
        )
        .filter(Matchfacelog.suspect_id.isnot(None))
        .group_by(Matchfacelog.suspect_id)
        .all()
    )

    return jsonify([
        {
            "suspectId": r.suspect_id,
            "latestCapture": r.latest_capture,
            "matchCount": r.match_count,
            "suspectName": r.suspect
        }
        for r in results
    ])
@matchfacelogs_bp.route('/suspect/<int:suspect_id>', methods=['GET'])
@jwt_required()
def get_logs_by_suspect(suspect_id):
    from storage import get_storage

    logs = (
        Matchfacelog.query
        .filter_by(suspect_id=suspect_id)
        .order_by(Matchfacelog.capture_time.desc())
        .all()
    )

    suspect_blob = None
    storage = get_storage()

    # Fetch suspect and try to load first available image
    if logs and logs[0].suspect_ref:
        suspect = logs[0].suspect_ref
        for i in range(6):
            path_attr = f'file_path{i}' if i > 0 else 'file_path'
            rel_path = getattr(suspect, path_attr)
            if not rel_path:
                continue

            try:
                binary_data = storage.load(rel_path)
                suspect_blob = base64.b64encode(binary_data).decode('utf-8')
                break  # use the first valid file
            except Exception as e:
                current_app.logger.warning(f"Failed to load suspect image {rel_path}: {e}")

    result_logs = []
    for log in logs:
        rel_path = os.path.join(str(log.suspect_id), log.frame)

        image_base64 = None
        try:
            binary_data = storage.load(rel_path)
            image_base64 = base64.b64encode(binary_data).decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"Failed to load frame image for log {log.id}: {rel_path}: {e}")

        result_logs.append({
            'id': log.id,
            'captureTime': log.capture_time,
            'frame': log.frame,
            'cctvId': log.cctv_id,
            'cctvName': log.cctv.name if log.cctv else None,
            'cctvLocation': log.cctv.location if log.cctv else None,
            'suspectId': log.suspect_id,
            'suspect': log.suspect,
            'distance': log.distance,
            'createdDate': log.created_date,
            'frameBase64': image_base64,
            'image_path': rel_path
        })

    return jsonify({
        'suspectPhoto': suspect_blob,
        'logs': result_logs
    })

@matchfacelogs_bp.route('/log/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log_by_id(log_id):
    log = Matchfacelog.query.get(log_id)
    if not log:
        return jsonify({"message": f"Log ID {log_id} not found"}), 404

    rel_path = os.path.join(str(log.suspect_id), log.frame)
    image_path = rel_path  # to include in response

    frame_base64 = None

    found_in_storage = False
    try:
        if Config.STORAGE_BACKEND == 'blob':
            from azure.storage.blob import BlobServiceClient
            blob_client = BlobServiceClient.from_connection_string(
                Config.BLOB_SETTINGS['connection_string']
            ).get_blob_client(
                container=Config.BLOB_SETTINGS['matchedContainer'],
                blob=rel_path
            )
            # check if blob exists
            if blob_client.exists():
                binary_data = blob_client.download_blob().readall()
                frame_base64 = base64.b64encode(binary_data).decode('utf-8')
                found_in_storage = True
        else:
            abs_path = os.path.join(Config.matched_dir, rel_path)
            if os.path.isfile(abs_path):
                with open(abs_path, 'rb') as f:
                    binary_data = f.read()
                frame_base64 = base64.b64encode(binary_data).decode('utf-8')
                found_in_storage = True

    except Exception as e:
        current_app.logger.error(f"Error checking storage for image {rel_path}: {e}")

    # If not found in storage, fallback to DB
    if not found_in_storage:
        frame_base64 = log.framebase64

    return jsonify({
        "id": log.id,
        "frame": log.frame,
        "frameBase64": frame_base64,
        "imagePath": image_path,
        "captureTime": log.capture_time.isoformat(),
        "suspectId": log.suspect_id,
        "suspect": log.suspect,
        "cctvId": log.cctv_id,
        "createdDate": log.created_date.isoformat(),
    })

    
@matchfacelogs_bp.route('/addmatchfacelogs', methods=['POST'])
def create_matchfacelog():
    data = request.json

    try:
        # Persist the DB record
        log = Matchfacelog(
            capture_time=data['captureTime'],
            frame=data['frame'],  # frame file name
            cctv_id=data['cctvId'],
            suspect_id=data.get('suspectId'),
            suspect=data.get('suspect'),
            distance=data['distance'],
            created_date=data.get('createdDate'),
            framebase64=f"{data.get('suspectId')}/{data['frame']}",
            site_id=data.get('siteId')
        )
        db.session.add(log)
        db.session.commit()
        db.session.flush()  # ensure log.id is available

        # Save the frame image
        frame_base64 = data.get('frameBase64')

        if frame_base64:
            binary_data = base64.b64decode(frame_base64)

            # Relative path is <suspectId>/<frame filename>
            suspect_id_str = str(data.get('suspectId') or 'unknown')
            rel_path = os.path.join(suspect_id_str, data['frame'])

            if Config.STORAGE_BACKEND == 'blob':
                from azure.storage.blob import BlobServiceClient
                blob_client = BlobServiceClient.from_connection_string(
                    Config.BLOB_SETTINGS['connection_string']
                ).get_blob_client(
                    container=Config.BLOB_SETTINGS['matchedContainer'],
                    blob=rel_path
                )
                blob_client.upload_blob(binary_data, overwrite=True)
                current_app.logger.info(f"Saved frame to blob storage: {rel_path}")
            else:
                # Default local
                abs_path = os.path.join(Config.matched_dir, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, 'wb') as f:
                    f.write(binary_data)
                current_app.logger.info(f"Saved frame to local storage: {abs_path}")

        # Dispatch notifications asynchronously
        def async_notification(matchfacelog_id, framebase64, siteId):
            try:
                dispatched_count = dispatch_notification(matchfacelog_id, framebase64, siteId)
                current_app.logger.info(f"Notifications dispatched: {dispatched_count}")
            except Exception as e:
                current_app.logger.error(f"Notification dispatch failed: {e}")

        threading.Thread(
            target=async_notification,
            args=(log.id, frame_base64, data.get('siteId'))
        ).start()

        db.session.commit()
        return jsonify({"message": "MatchFaceLog created", "id": log.id}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create MatchFaceLog: {e}")
        return jsonify({"error": str(e)}), 400
