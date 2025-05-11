from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    all_users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in all_users])

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role     = data.get('role', 'user')

    if User.query.filter_by(username=username).first():
        return jsonify(msg='User exists'), 400

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id, username=user.username, role=user.role), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}
    user = User.query.get_or_404(user_id)
    user.username = data.get('username', user.username)
    user.role     = data.get('role', user.role)
    db.session.commit()
    return jsonify(msg='Updated')

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(msg='Deleted')
