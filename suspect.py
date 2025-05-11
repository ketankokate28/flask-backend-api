import os
import base64
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from models import db, Suspect
from datetime import datetime

suspect_bp = Blueprint('suspect', __name__)

UPLOAD_FOLDER = 'suspects'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None

# CREATE Suspect
@suspect_bp.route('/', methods=['POST'])
@jwt_required()
def create_suspect():
    print(">>> DEBUG: create_suspect called")
    print(">>> Form Data:", request.form.to_dict())
    print(">>> Files:", request.files)

    data = request.form
    image = request.files.get('image')

    file_path = None
    file_blob = None

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Read the image content BEFORE saving
        image_data = image.read()

        # Convert to base64
        file_blob = base64.b64encode(image_data).decode('utf-8')
        print(">>> file_blob:", file_blob)

        # Reset stream and save the file
        image.stream.seek(0)
        image.save(file_path)
    else:
        return jsonify({'msg': 'Valid image file is required'}), 400

    date_of_birth = parse_date(data.get('date_of_birth'))
    if not date_of_birth:
        return jsonify({'msg': 'Invalid or missing date_of_birth. Expected format: YYYY-MM-DD'}), 400

    suspect = Suspect(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        date_of_birth=date_of_birth,
        gender=data.get('gender'),
        nationality=data.get('nationality'),
        height_cm=data.get('height_cm'),
        weight_kg=data.get('weight_kg'),
        shoulder_width_cm=data.get('shoulder_width_cm'),
        torso_height_cm=data.get('torso_height_cm'),
        leg_length_cm=data.get('leg_length_cm'),
        shoe_size=data.get('shoe_size'),
        hair_color=data.get('hair_color'),
        eye_color=data.get('eye_color'),
        face_embedding=data.get('face_embedding'),
        fingerprint_template=data.get('fingerprint_template'),
        iris_code=data.get('iris_code'),
        gait_signature=data.get('gait_signature'),
        aliases=data.get('aliases'),
        created_by=data.get('created_by'),
        modified_by=data.get('created_by'),
        file_path=file_path,
        file_blob=file_blob,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        db.session.add(suspect)
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
    if suspect_id:
        s = Suspect.query.get(suspect_id)
        if not s:
            return jsonify({"msg": "Suspect not found"}), 404
        return jsonify(s.serialize(include_blob=True)), 200
    else:
        suspects = Suspect.query.all()
        return jsonify([s.serialize(include_blob=True) for s in suspects]), 200

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
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Read first, then save
        image_data = image.read()
        suspect.file_blob = base64.b64encode(image_data).decode('utf-8')
        image.stream.seek(0)
        image.save(file_path)

        suspect.file_path = file_path
    for field in [
        'first_name', 'last_name', 'gender', 'nationality',
        'height_cm', 'weight_kg', 'shoulder_width_cm', 'torso_height_cm',
        'leg_length_cm', 'shoe_size', 'hair_color', 'eye_color', 'aliases',
        'face_embedding', 'fingerprint_template', 'iris_code', 'gait_signature',
        'modified_by'
    ]:
        if field in data:
            setattr(suspect, field, data.get(field))

    # Parse and update date_of_birth
    dob = parse_date(data.get('date_of_birth'))
    if dob:
        suspect.date_of_birth = dob

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

    if suspect.file_path and os.path.exists(suspect.file_path):
        os.remove(suspect.file_path)

    db.session.delete(suspect)
    db.session.commit()
    return jsonify({"msg": "Suspect deleted"}), 200
