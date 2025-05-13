from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import db, Matchfacelog
import base64
import os
from flask import jsonify, send_file, current_app
from config import Config

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
            Matchfacelog.suspect
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
    logs = (
        Matchfacelog.query
        .filter_by(suspect_id=suspect_id)
        .order_by(Matchfacelog.capture_time.desc())
        .all()
    )

    # Fetch suspect once using the relationship from the first log
    suspect_blob = None
    if logs and logs[0].suspect_ref:
        suspect_blob = logs[0].suspect_ref.file_blob

    result_logs = []
    for log in logs:
        image_path = os.path.join(
            Config.matched_dir,
            str(log.suspect_id),
            log.frame
        )


        image_base64 = None
        if os.path.isfile(image_path):
            try:
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                current_app.logger.error(f"Failed to read image {image_path}: {e}")

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
            'image_path': image_path
        })

    return jsonify({
        'suspectPhoto': suspect_blob,
        'logs': result_logs
    })
