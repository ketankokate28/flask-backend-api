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
            'roles': [u.role] if u.role else []
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
        'roles': [user.role] if user.role else []
    }), 200

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    username = data.get('userName')
    password = data.get('newPassword')
    role     = data.get('role', 'user')

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
        jobTitle=data.get('jobTitle')
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
        'jobTitle': user.jobTitle
    }), 201


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}
    user = User.query.get_or_404(user_id)

    user.username     = data.get('userName', user.username)
    #user.role         = data.get('role', user.role)
    user.email        = data.get('email', user.email)
    user.fullName     = data.get('fullName', user.fullName)
    user.phoneNumber  = data.get('phoneNumber', user.phoneNumber)
    user.jobTitle     = data.get('jobTitle', user.jobTitle)
    role_value = data.get('role')
    if isinstance(role_value, list):
        user.role = role_value[0] if role_value else user.role
    else:
        user.role = role_value or user.role

    if 'newPassword' in data and data['newPassword']:
        user.set_password(data['newPassword'])

    db.session.commit()
    return jsonify(msg='User updated')


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(msg='User deleted')

