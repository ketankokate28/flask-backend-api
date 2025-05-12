from flask import Blueprint, jsonify
from models import db, Permission

permission_bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')

@permission_bp.route('/', methods=['GET'])
def get_permissions():
    permissions = Permission.query.all()

    grouped = {}
    for perm in permissions:
        group = perm.group_name
        if group not in grouped:
            grouped[group] = {
                'groupName': group,
                'permissions': []
            }
        grouped[group]['permissions'].append({
            'name': perm.name,
            'value': perm.value,
            'description': perm.description
        })

    return jsonify(list(grouped.values()))
