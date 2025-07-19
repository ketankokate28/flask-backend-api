from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required
from models import db, CCTV, Site

camera_config_bp = Blueprint("camera_config", __name__)

@camera_config_bp.route("/cameras", methods=["GET"])
# @jwt_required()
def list_cameras():
    """
    GET /api/config/cameras?site_ids=1,2,5
    Returns JSON array of active cameras, optionally filtered by site_ids.
    """
    site_ids = request.args.get("site_ids", "")
    session = db.session
    q = (
        session.query(CCTV, Site)
               .join(Site, CCTV.site_id == Site.id)
               .filter(CCTV.status == "Active")
               .filter(Site.is_active == "true")
               .filter(CCTV.stream_url.isnot(None))
               .filter(CCTV.stream_url != "")
    )
    if site_ids:
        ids = [int(s) for s in site_ids.split(",") if s.strip().isdigit()]
        q = q.filter(Site.id.in_(ids))
    rows = q.all()
    cameras = []
    for cam, site in rows:
        cameras.append({
            'camera_id':   cam.id,
            'camera_name': cam.name,
            'rtsp_url':    cam.stream_url,
            'site_id':     site.id,
            'site_name':   site.name,
            'site_desc':   site.description,
        })
    return jsonify(cameras)

@camera_config_bp.route("/cameras/<int:camera_id>", methods=["GET"])
@jwt_required()
def get_camera(camera_id):
    """
    GET /api/config/cameras/<camera_id>
    Returns one camera or 404 if not found.
    """
    session = db.session
    result = (
        session.query(CCTV, Site)
               .join(Site, CCTV.site_id == Site.id)
               .filter(CCTV.id == camera_id)
               .filter(CCTV.status == "Active")
               .first()
    )
    if not result:
        abort(404, 'Camera not found')
    cam, site = result
    return jsonify({
        'camera_id':   cam.id,
        'camera_name': cam.name,
        'rtsp_url':    cam.stream_url,
        'site_id':     site.id,
        'site_name':   site.name,
        'site_desc':   site.description,
    })

# inside your Blueprint registration block

@camera_config_bp.route("/cameras/<int:camera_id>/status", methods=["PATCH"])
@jwt_required()
def update_camera_status(camera_id):
    """
    PATCH /api/config/cameras/<camera_id>/status
    Body JSON: { "is_active": true|false }
    """
    data = request.get_json(silent=True) or {}
    if 'is_active' not in data:
        return jsonify({"msg": "`is_active` boolean field is required"}), 400

    is_active = data['is_active']
    cam = db.session.get(CCTV, camera_id)
    if not cam:
        return jsonify({"msg": "Camera not found"}), 404

    cam.status = "Active" if is_active else "Inactive"
    db.session.commit()

    return jsonify({
        "camera_id": camera_id,
        "new_status": cam.status
    }), 200