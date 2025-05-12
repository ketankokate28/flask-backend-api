import os
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import current_app
from models import db, Suspect

# Configuration (could also live in config.py)
UPLOAD_FOLDER = 'suspects'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None


class SuspectStore:
    @staticmethod
    def create(form_data, image_file) -> Suspect:
        # Handle image
        if not image_file or not _allowed_file(image_file.filename):
            raise ValueError('Valid image file is required')
        filename = secure_filename(image_file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        data = image_file.read()
        blob = base64.b64encode(data).decode('utf-8')
        image_file.stream.seek(0)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_file.save(path)
        # Parse DOB
        dob = _parse_date(form_data.get('date_of_birth'))
        if not dob:
            raise ValueError('Invalid or missing date_of_birth. Expected YYYY-MM-DD')
        # Build model
        suspect = Suspect(
            first_name=form_data.get('first_name'),
            last_name=form_data.get('last_name'),
            date_of_birth=dob,
            gender=form_data.get('gender'),
            nationality=form_data.get('nationality'),
            height_cm=form_data.get('height_cm'),
            weight_kg=form_data.get('weight_kg'),
            shoulder_width_cm=form_data.get('shoulder_width_cm'),
            torso_height_cm=form_data.get('torso_height_cm'),
            leg_length_cm=form_data.get('leg_length_cm'),
            shoe_size=form_data.get('shoe_size'),
            hair_color=form_data.get('hair_color'),
            eye_color=form_data.get('eye_color'),
            face_embedding=form_data.get('face_embedding'),
            fingerprint_template=form_data.get('fingerprint_template'),
            iris_code=form_data.get('iris_code'),
            gait_signature=form_data.get('gait_signature'),
            aliases=form_data.get('aliases'),
            created_by=form_data.get('created_by'),
            modified_by=form_data.get('created_by'),
            file_path=path,
            file_blob=blob,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(suspect)
        db.session.commit()
        return suspect

    @staticmethod
    def get_all() -> list:
        db.session.expire_all()
        return Suspect.query.all()

    @staticmethod
    def get_by_id(suspect_id: int) -> Suspect:
        return Suspect.query.get(suspect_id)

    @staticmethod
    def update(suspect_id: int, form_data, image_file) -> Suspect:
        suspect = Suspect.query.get(suspect_id)
        if not suspect:
            return None
        # Image update
        if image_file and _allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            data = image_file.read()
            suspect.file_blob = base64.b64encode(data).decode('utf-8')
            image_file.stream.seek(0)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_file.save(path)
            suspect.file_path = path
        # Update fields
        for field in ['first_name','last_name','gender','nationality',
                      'height_cm','weight_kg','shoulder_width_cm',
                      'torso_height_cm','leg_length_cm','shoe_size',
                      'hair_color','eye_color','aliases',
                      'face_embedding','fingerprint_template',
                      'iris_code','gait_signature','modified_by']:
            if field in form_data:
                setattr(suspect, field, form_data.get(field))
        dob = _parse_date(form_data.get('date_of_birth'))
        if dob:
            suspect.date_of_birth = dob
        suspect.updated_at = datetime.utcnow()
        db.session.commit()
        return suspect

    @staticmethod
    def delete(suspect_id: int) -> bool:
        suspect = Suspect.query.get(suspect_id)
        if not suspect:
            return False
        if suspect.file_path and os.path.exists(suspect.file_path):
            os.remove(suspect.file_path)
        db.session.delete(suspect)
        db.session.commit()
        return True
