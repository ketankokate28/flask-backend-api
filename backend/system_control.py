from flask_jwt_extended import jwt_required

@system_control_bp.route('/status', methods=['GET'])
@jwt_required()     # require any logged-in user
def status_system():
    alive = False
    if _workers:
        alive = all(p.is_alive() for p in _workers.values())
    return jsonify(running=alive), 200
