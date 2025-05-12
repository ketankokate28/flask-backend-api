from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from db_store.suspect_store import SuspectStore

suspect_bp = Blueprint('suspect', __name__)

# CREATE
@suspect_bp.route('/', methods=['POST'])  # noqa: F821
@jwt_required()
def create_suspect():
    try:
        suspect = SuspectStore.create(request.form, request.files.get('image'))
        return jsonify({'id': suspect.suspect_id, 'msg': 'Suspect created'}), 201
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400
    except Exception:
        current_app.logger.exception('Error creating suspect')
        return jsonify({'msg': 'Server error'}), 5
        00

# READ
@suspect_bp.route('/', methods=['GET'])  # noqa: F821
@jwt_required()
def get_suspects():
    sid = request.args.get('id')
    if sid:
        s = SuspectStore.get_by_id(int(sid))
        if not s:
            return jsonify({'msg': 'Not found'}), 404
        return jsonify(s.serialize(include_blob=True)), 200
    all_s = SuspectStore.get_all()
    return jsonify([s.serialize(include_blob=True) for s in all_s]), 200

# UPDATE
@suspect_bp.route('/<int:sid>', methods=['PUT'])  # noqa: F821
@jwt_required()
def update_suspect(sid):
    updated = SuspectStore.update(sid, request.form, request.files.get('image'))
    if not updated:
        return jsonify({'msg': 'Not found'}), 404
    return jsonify({'msg': 'Suspect updated'}), 200

# DELETE
@suspect_bp.route('/<int:sid>', methods=['DELETE'])  # noqa: F821
@jwt_required()
def delete_suspect(sid):
    if not SuspectStore.delete(sid):
        return jsonify({'msg': 'Not found'}), 404
    return jsonify({'msg': 'Suspect deleted'}), 200
