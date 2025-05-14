from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    all_users = User.query.all()
    return jsonify([
        {
            'id': u.id,
            'userName': u.username,
            'email': u.email,
            'fullName': u.fullName,
            'phoneNumber': u.phoneNumber,
            'jobTitle': u.jobTitle,
            'roles': [u.role] if u.role else [],
            'notify_email': u.notify_email,
            'notify_sms': u.notify_sms,
            'notify_call': u.notify_call,
            'priority_email': u.priority_email,
            'priority_sms': u.priority_sms,
            'priority_call': u.priority_call,
            'is_active': u.is_active,
            'created_at': u.created_at
        }
        for u in all_users
    ])

@users_bp.route('/<int:user_id>', methods=['GET']) 
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'userName': user.username,
        'email': user.email,
        'fullName': user.fullName,
        'phoneNumber': user.phoneNumber,
        'jobTitle': user.jobTitle,
        'roles': [user.role] if user.role else [],
        'notify_email': user.notify_email,
        'notify_sms': user.notify_sms,
        'notify_call': user.notify_call,
        'priority_email': user.priority_email,
        'priority_sms': user.priority_sms,
        'priority_call': user.priority_call,
        'is_active': user.is_active,
        'created_at': user.created_at
    }), 200

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    username = data.get('userName')
    password = data.get('newPassword')
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify(msg='Username and password are required'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(msg='User already exists'), 400

    user = User(
        username=username,
        role=role,
        email=data.get('email'),
        fullName=data.get('fullName'),
        phoneNumber=data.get('phoneNumber'),
        jobTitle=data.get('jobTitle'),
        notify_email=data.get('notify_email', True),  # Default to True
        notify_sms=data.get('notify_sms', True),      # Default to True
        notify_call=data.get('notify_call', True),    # Default to True
        priority_email=data.get('priority_email', 0), # Default to 0
        priority_sms=data.get('priority_sms', 0),     # Default to 0
        priority_call=data.get('priority_call', 0),   # Default to 0
        is_active=data.get('is_active', True)          # Default to True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'userName': user.username,
        'roles': [user.role] if user.role else [],
        'email': user.email,
        'fullName': user.fullName,
        'phoneNumber': user.phoneNumber,
        'jobTitle': user.jobTitle,
        'notify_email': user.notify_email,
        'notify_sms': user.notify_sms,
        'notify_call': user.notify_call,
        'priority_email': user.priority_email,
        'priority_sms': user.priority_sms,
        'priority_call': user.priority_call,
        'is_active': user.is_active,
        'created_at': user.created_at
    }), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}
    user = User.query.get_or_404(user_id)

    user.username = data.get('userName', user.username)
    user.email = data.get('email', user.email)
    user.fullName = data.get('fullName', user.fullName)
    user.phoneNumber = data.get('phoneNumber', user.phoneNumber)
    user.jobTitle = data.get('jobTitle', user.jobTitle)
    
    # Update roles
    role_value = data.get('role')
    if isinstance(role_value, list):
        user.role = role_value[0] if role_value else user.role
    else:
        user.role = role_value or user.role

    # Update new fields
    user.notify_email = data.get('notify_email', user.notify_email)
    user.notify_sms = data.get('notify_sms', user.notify_sms)
    user.notify_call = data.get('notify_call', user.notify_call)
    user.priority_email = data.get('priority_email', user.priority_email)
    user.priority_sms = data.get('priority_sms', user.priority_sms)
    user.priority_call = data.get('priority_call', user.priority_call)
    user.is_active = data.get('is_active', user.is_active)
    
    # Update password if provided
    if 'newPassword' in data and data['newPassword']:
        user.set_password(data['newPassword'])

    db.session.commit()

    return jsonify({
        'id': user.id,
        'userName': user.username,
        'roles': [user.role] if user.role else [],
        'email': user.email,
        'fullName': user.fullName,
        'phoneNumber': user.phoneNumber,
        'jobTitle': user.jobTitle,
        'notify_email': user.notify_email,
        'notify_sms': user.notify_sms,
        'notify_call': user.notify_call,
        'priority_email': user.priority_email,
        'priority_sms': user.priority_sms,
        'priority_call': user.priority_call,
        'is_active': user.is_active,
        'created_at': user.created_at
    }), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(msg='User deleted')
