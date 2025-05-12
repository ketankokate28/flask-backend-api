from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Notification

notification_bp = Blueprint('notification', __name__)

# GET all or single notification
@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    #db.session.expire_all()
    notification_id = request.args.get('id')

    if notification_id:
        notification = Notification.query.get(notification_id)
        if not notification:
            print(f">>> Notification with ID {notification_id} not found.")
            return jsonify({'msg': 'Notification not found'}), 404
        print(f">>> Fetched notification ID {notification_id}: {notification.serialize()}")
        return jsonify(notification.serialize()), 200

    notifications = Notification.query.all()
    print(f">>> Total notifications found: {len(notifications)}")
    for n in notifications:
        print(f">>> Notification ID {n.notification_id}: {n.serialize()}")

    return jsonify([n.serialize() for n in notifications]), 200
