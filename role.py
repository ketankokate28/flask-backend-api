from flask import Blueprint, request, jsonify
from models import db, Role, Permission
from uuid import uuid4

role_bp = Blueprint('roles', __name__, url_prefix='/api/roles')

@role_bp.route('/', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify([serialize_role(role) for role in roles])

@role_bp.route('/<role_id>', methods=['GET'])
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify(serialize_role(role))

@role_bp.route('/', methods=['POST'])
def create_role():
    data = request.json
    role = Role(name=data['name'], description=data.get('description'))

    # Flatten nested permission values
    permission_values = [
        perm['value']
        for group in data['permissions']
        for perm in group.get('permissions', [])
    ]
    role.permissions = Permission.query.filter(Permission.value.in_(permission_values)).all()

    db.session.add(role)
    db.session.commit()
    return jsonify(serialize_role(role)), 201

@role_bp.route('/<role_id>', methods=['PUT'])
def update_role(role_id):
    data = request.json
    role = Role.query.get_or_404(role_id)
    role.name = data['name']
    role.description = data.get('description')

    # Flatten nested permission values just like in POST
    permission_values = [
        perm['value']
        for group in data['permissions']
        for perm in group.get('permissions', [])
    ]
    role.permissions = Permission.query.filter(Permission.value.in_(permission_values)).all()

    db.session.commit()
    return jsonify(serialize_role(role))


@role_bp.route('/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    return '', 204

def serialize_role(role):
    return {
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permissions': [{
            'name': p.name,
            'value': p.value,
            'groupName': p.group_name,
            'description': p.description
        } for p in role.permissions],
        'usersCount': 0  # You can implement this later if needed
    }

# Register this blueprint in your Flask app
# app.register_blueprint(role_bp)
