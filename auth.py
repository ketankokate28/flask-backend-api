# auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required,create_refresh_token
from models import db, User, Role, Permission
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    jobTitle = data.get('jobTitle')
    email = data.get('email')
    fullName = data.get('fullName')
    phoneNumber = data.get('phoneNumber')
    role = data.get('role', 'admin')

    # New fields
    notify_email = data.get('notify_email', True)  # Default to True
    notify_sms = data.get('notify_sms', True)      # Default to True
    notify_call = data.get('notify_call', True)    # Default to True
    priority_email = data.get('priority_email', 0) # Default to 0
    priority_sms = data.get('priority_sms', 0)     # Default to 0
    priority_call = data.get('priority_call', 0)   # Default to 0
    is_active = data.get('is_active', True)         # Default to True

    if not username or not password:
        return jsonify(msg='username & password required'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(msg='User already exists'), 400

    user = User(
        username=username,
        role=role,
        jobTitle=jobTitle,
        email=email,
        fullName=fullName,
        phoneNumber=phoneNumber,
        notify_email=notify_email,
        notify_sms=notify_sms,
        notify_call=notify_call,
        priority_email=priority_email,
        priority_sms=priority_sms,
        priority_call=priority_call,
        is_active=is_active
    )
    
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(
        id=user.id,
        username=user.username,
        role=user.role,
        notify_email=user.notify_email,
        notify_sms=user.notify_sms,
        notify_call=user.notify_call,
        priority_email=user.priority_email,
        priority_sms=user.priority_sms,
        priority_call=user.priority_call,
        is_active=user.is_active
    ), 201


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
    db.session.expire_all()
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify(msg='Bad username or password'), 401

    # Get role and associated permissions
    role = Role.query.filter_by(name=user.role).first()
    permission_values = [p.value for p in role.permissions] if role else []

    # JWT claims
    claims = {
        'role': user.role,
        'permission': permission_values,
        'scope': 'read write',
        'name': user.username,
        'fullname': user.fullName,
        'email': user.email,
        'jobtitle': user.jobTitle,
        'phone_number': user.phoneNumber
    }
    access_token_expires = timedelta(minutes=120)
    id_token_expires = timedelta(hours=2)
    # Create access and ID tokens
    access_token = create_access_token(identity=str(user.id),expires_delta=access_token_expires, additional_claims=claims)
    id_token     = create_access_token(identity=str(user.id),expires_delta=id_token_expires, additional_claims={**claims, 'id_token': True})
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
    