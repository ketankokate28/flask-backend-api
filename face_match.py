from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import os
#import face_recognition
import numpy as np

face_match_bp = Blueprint('face_match', __name__)

# Preload suspects from the suspects/ folder
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SUSPECTS_DIR = os.path.join(BASE_DIR, 'suspects')

suspects = []
if os.path.isdir(SUSPECTS_DIR):
    for fn in os.listdir(SUSPECTS_DIR):
        if fn.lower().endswith(('jpg','jpeg','png')):
            path = os.path.join(SUSPECTS_DIR, fn)
            encs = face_recognition.face_encodings(
                face_recognition.load_image_file(path)
            )
            if encs:
                suspects.append((os.path.splitext(fn)[0], encs[0]))
else:
    print(f"[⚠️] Suspects directory not found: {SUSPECTS_DIR}")

@face_match_bp.route('/', methods=['POST'])
@jwt_required()
def face_match():
    if 'frame' not in request.files:
        return jsonify(msg='No file part'), 400
    file = request.files['frame']
    save_dir = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(save_dir, exist_ok=True)
    frame_path = os.path.join(save_dir, file.filename)
    file.save(frame_path)

    image = face_recognition.load_image_file(frame_path)
    locs  = face_recognition.face_locations(image)
    encs  = face_recognition.face_encodings(image, locs)

    matches = []
    for fe in encs:
        dists = face_recognition.face_distance([s[1] for s in suspects], fe)
        idx   = int(np.argmin(dists))
        dist  = float(dists[idx])
        if dist < 0.45:
            matches.append({'suspect': suspects[idx][0], 'distance': dist})

    return jsonify(matches=matches)
    