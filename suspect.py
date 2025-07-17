import os
import base64
import random
import shutil
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import and_, or_
from werkzeug.utils import secure_filename
from models import Node, Site, Subnode, db, Suspect
from datetime import datetime, timezone
from dateutil.parser import parse
from storage import get_storage  # ✅ import storage abstraction
from sqlalchemy import text
from dateutil.tz import tzlocal

suspect_bp = Blueprint('suspect', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None

logging.basicConfig(level=logging.DEBUG)

# CREATE Suspect
# CREATE Suspect
@suspect_bp.route('/', methods=['POST'])
@jwt_required()
def create_suspect():
    db.session.expire_all()
    data = request.form
    image = request.files.get('image')

    date_of_birth = parse_date(data.get('date_of_birth'))
    if not date_of_birth:
        return jsonify({'msg': 'Invalid or missing date_of_birth. Expected format: YYYY-MM-DD'}), 400

    subnode_id = data.get('subnode_id')
    if subnode_id and str(subnode_id).isdigit():
        subnode_id = int(subnode_id)
    else:
        subnode_id = None

    suspect = Suspect(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        date_of_birth=date_of_birth,
        gender=data.get('gender'),
        nationality=data.get('nationality'),
        subnode_id=subnode_id,
        height_cm=data.get('height_cm'),
        weight_kg=data.get('weight_kg'),
        shoulder_width_cm=data.get('shoulder_width_cm'),
        torso_height_cm=data.get('torso_height_cm'),
        leg_length_cm=data.get('leg_length_cm'),
        distribution_to=data.get('distribution_to') or 'P',
        hair_color=data.get('hair_color'),
        eye_color=data.get('eye_color'),
        face_embedding=data.get('face_embedding'),
        fingerprint_template=data.get('fingerprint_template'),
        iris_code=data.get('iris_code'),
        gait_signature=data.get('gait_signature'),
        aliases=data.get('aliases'),
        created_by=data.get('created_by'),
        modified_by=data.get('created_by'),
        description=data.get('description'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        db.session.add(suspect)
        db.session.flush()  # flush to get suspect_id for path

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            relative_path = f"suspects/{suspect.suspect_id}/{filename}"

            image_data = image.read()
            get_storage().save(relative_path, image_data)

            # update suspect with path and blob
            suspect.file_path = relative_path
            #suspect.file_blob = base64.b64encode(image_data).decode('utf-8')

        db.session.commit()
    except Exception as e:
        print(">>> ERROR inserting suspect:", str(e))
        db.session.rollback()
        return jsonify({'msg': 'Database error occurred'}), 500

    return jsonify({"id": suspect.suspect_id, "msg": "Suspect created"}), 201

# GET All or Single Suspect
@suspect_bp.route('/', methods=['GET'])
@jwt_required()
def get_suspects():
    db.session.expire_all()
    suspect_id = request.args.get('id')
    subnode_id = request.args.get('subnode_id', type=int)

    if suspect_id:
        s = Suspect.query.get(suspect_id)
        if not s:
            return jsonify({"msg": "Suspect not found"}), 404
        return jsonify(s.serialize(include_blob=False)), 200

    query = Suspect.query

    if subnode_id and subnode_id > 0:
        query = query.filter_by(subnode_id=subnode_id)

    suspects = query.all()

    return jsonify([s.serialize(include_blob=False) for s in suspects]), 200

# UPDATE Suspect
@suspect_bp.route('/<int:suspect_id>', methods=['PUT'])
@jwt_required()
def update_suspect(suspect_id):
    suspect = Suspect.query.get(suspect_id)
    if not suspect:
        return jsonify({'msg': 'Suspect not found'}), 404

    data = request.form
    image = request.files.get('image')

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        relative_path = f"suspects/{suspect_id}/{filename}"

        image_data = image.read()
        #suspect.file_blob = base64.b64encode(image_data).decode('utf-8')
        image.stream.seek(0)

        get_storage().save(relative_path, image_data)

        suspect.file_path = relative_path

    for field in [
        'first_name', 'last_name', 'gender', 'nationality',
        'height_cm', 'weight_kg', 'shoulder_width_cm', 'torso_height_cm',
        'leg_length_cm', 'distribution_to', 'hair_color', 'eye_color', 'aliases',
        'face_embedding', 'fingerprint_template', 'iris_code', 'gait_signature',
        'modified_by', 'description'
    ]:
        if field in data:
            setattr(suspect, field, data.get(field))

    dob = parse_date(data.get('date_of_birth'))
    if dob:
        suspect.date_of_birth = dob

    subnode_id = data.get('subnode_id')
    if subnode_id and str(subnode_id).isdigit():
        suspect.subnode_id = int(subnode_id)

    suspect.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Suspect updated"}), 200

# DELETE Suspect
@suspect_bp.route('/<int:suspect_id>', methods=['DELETE'])
@jwt_required()
def delete_suspect(suspect_id):
    suspect = Suspect.query.get(suspect_id)
    if not suspect:
        return jsonify({'msg': 'Suspect not found'}), 404

    if suspect.file_path:
        try:
            get_storage().delete(suspect.file_path)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete file {suspect.file_path}: {e}")

    db.session.delete(suspect)
    db.session.commit()
    return jsonify({"msg": "Suspect deleted"}), 200

# GET Single Suspect by ID
@suspect_bp.route('/<int:suspect_id>', methods=['GET'])
@jwt_required()
def get_suspect_by_id(suspect_id):
    db.session.expire_all()
    suspect = Suspect.query.get(suspect_id)
    if not suspect:
        return jsonify({"msg": "Suspect not found"}), 404
    return jsonify(suspect.serialize(include_blob=True)), 200

@suspect_bp.route('/<int:suspect_id>/upload-images', methods=['POST'])
@jwt_required()
def upload_suspect_images(suspect_id):
    suspect = Suspect.query.get(suspect_id)
    if not suspect:
        return jsonify({'msg': 'Suspect not found'}), 404

    updated = False
    for i in range(1, 6):
        image_field = f'image{i}'
        image = request.files.get(image_field)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            random_number = random.randint(100000, 999999) 
            relative_path = f"{suspect_id}\image{i}_{random_number}_{filename}"

            image_data = image.read()
            #file_blob = base64.b64encode(image_data).decode('utf-8')

            setattr(suspect, f'file_path{i}', relative_path)
            #setattr(suspect, f'file_blob{i}', file_blob)

            get_storage().save(relative_path, image_data)

            updated = True

    if updated:
        suspect.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'msg': 'Images uploaded/updated successfully'}), 200
    else:
        return jsonify({'msg': 'No valid images provided'}), 400

@suspect_bp.route('/by-site/<int:site_id>', methods=['GET'])
@jwt_required()
def get_suspects_by_site(site_id):
    db.session.expire_all()

    site = Site.query.get(site_id)
    if not site:
        return jsonify({"msg": "Site not found"}), 404

    site_subnode_id = site.subnode_id
    site_subnode = Subnode.query.get(site_subnode_id)
    if not site_subnode:
        return jsonify({"msg": "Subnode for site not found"}), 404

    district_node_id = site_subnode.node_id
    district_node = Node.query.get(district_node_id)
    if not district_node:
        return jsonify({"msg": "District node for subnode not found"}), 404

    tenant_id = district_node.tenant_id

    district_subnode_ids = [id for (id,) in Subnode.query.with_entities(Subnode.id).filter_by(node_id=district_node_id).all()]
    tenant_node_ids = [id for (id,) in Node.query.with_entities(Node.id).filter_by(tenant_id=tenant_id).all()]
    tenant_subnode_ids = [id for (id,) in Subnode.query.with_entities(Subnode.id).filter(Subnode.node_id.in_(tenant_node_ids)).all()]

    last_sync_str = request.args.get('lastSync')
    last_sync = None
    if last_sync_str:
        try:
            last_sync = datetime.fromisoformat(last_sync_str)
        except ValueError:
            return jsonify({"msg": "Invalid lastSync format. Use ISO8601"}), 400

    filters = or_(
        and_(Suspect.subnode_id == site_subnode_id, Suspect.distribution_to == 'P'),
        and_(Suspect.subnode_id.in_(district_subnode_ids), Suspect.distribution_to == 'D'),
        and_(Suspect.subnode_id.in_(tenant_subnode_ids), Suspect.distribution_to == 'S'),
    )

    query = Suspect.query.filter(filters)
    if last_sync:
        query = query.filter(Suspect.updated_at > last_sync)

    suspects = query.all()
    return jsonify([s.serialize(include_blob=True) for s in suspects]), 200

@suspect_bp.route('/metadata', methods=['GET'])
def get_suspects_metadata():
    db.session.expire_all()

    # Current server UTC timestamp
    server_now_utc = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc).isoformat()

    last_sync_str = request.args.get('lastSync')
    current_app.logger.info(f"last_sync_str: {last_sync_str}")
    last_sync = None

    if last_sync_str:
        try:
            last_sync_str = last_sync_str.strip().replace(" ", "+")
            last_sync = parse(last_sync_str)

            if last_sync.tzinfo is None:
                last_sync = last_sync.replace(tzinfo=timezone.utc)
            else:
                last_sync = last_sync.astimezone(timezone.utc)

            last_sync = last_sync.replace(microsecond=0)
            current_app.logger.info(f"last_sync UTC: {last_sync}")

        except Exception as e:
            current_app.logger.error(f"Failed to parse lastSync: {e}")
            return jsonify({"msg": "Invalid lastSync format. Use ISO8601"}), 400

    query = Suspect.query
    if last_sync:
        query = query.filter(Suspect.updated_at >= last_sync)

    suspects = query.all()
    result = []
    for s in suspects:
        image_urls = []
        for i in range(6):
            path = getattr(s, f'file_path{i}' if i > 0 else 'file_path')
            if path:
                image_urls.append(path)

        result.append({
            "Id": s.suspect_id,
            "Name": f"{s.first_name} {s.last_name}".strip(),
            "UpdatedAt": s.updated_at.replace(tzinfo=timezone.utc).isoformat(),
            "ImageUrls": image_urls
        })

    return jsonify({
        "last_sync_time": server_now_utc,
        "suspects": result
    }), 200

@suspect_bp.route('/images', methods=['POST'])
def download_suspect_images():
    data = request.get_json()
    if not data or 'suspect_id' not in data:
        return jsonify({"msg": "Missing 'suspect_id' in body"}), 400

    suspect_id = data['suspect_id']
    suspect = Suspect.query.get(suspect_id)

    if not suspect:
        return jsonify({"msg": f"Suspect {suspect_id} not found"}), 404

    images = []

    for i in range(6):
        image_path = getattr(suspect, f'file_path{i}' if i > 0 else 'file_path')
        if not image_path:
            continue

        try:
            current_app.logger.info(f"[download_suspect_images] Requesting image: {image_path}")
            image_bytes = get_storage().load(image_path)
            encoded_str = base64.b64encode(image_bytes).decode('utf-8')
            current_app.logger.info(f"[download_suspect_images] Successfully read {image_path} ({len(image_bytes)} bytes)")
            images.append({
                "image_path": image_path,
                "base64": encoded_str
            })
        except Exception as e:
            current_app.logger.warning(f"[download_suspect_images] Failed to read {image_path}: {e}")
            images.append({
                "image_path": image_path,
                "base64": None
            })

    return jsonify({"images": images}), 200
