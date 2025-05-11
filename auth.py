# auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required,create_refresh_token
from models import db, User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role     = data.get('role', 'admin')

    if not username or not password:
        return jsonify(msg='username & password required'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(msg='User already exists'), 400

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(id=user.id, username=user.username, role=user.role), 201

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json() or {}
#     username = data.get('username')
#     password = data.get('password')

#     user = User.query.filter_by(username=username).first()
#     if not user or not user.check_password(password):
#         return jsonify(msg='Bad username or password'), 401

#     # Create token with string identity and include role in additional_claims
#     token = create_access_token(
#         identity=str(user.id),
#         additional_claims={'role': user.role}
#     )
#     return jsonify(token=token), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify(msg='Bad username or password'), 401

    # Create access and ID tokens
    access_token_expires = timedelta(minutes=120)
    id_token_expires = timedelta(hours=2)

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=access_token_expires,
        additional_claims={'role': user.role, 'scope': 'read write', 'name':user.username}
    )

    id_token = create_access_token(
        identity=str(user.id),
        expires_delta=id_token_expires,
        additional_claims={'role': user.role, 'scope': 'read write', 'id_token': True,'name':user.username}
    )

    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": int(id_token_expires.total_seconds()),  # seconds
        "token_type": "Bearer",
        "scope": "read write"
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    # Retrieve and convert identity claim back to int
    user_id = int(get_jwt_identity())
    role    = get_jwt().get('role')
    return jsonify(id=user_id, role=role)
    