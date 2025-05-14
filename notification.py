from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Notification, NotificationRecipient, User, Suspect

notification_bp = Blueprint('notification', __name__)

# API 1: Summary List for Dashboard (First Grid)
@notification_bp.route('/summary', methods=['GET'])
@jwt_required()
def notification_summary():
    try:
        results = db.session.query(
            Notification.id.label('notification_id'),
            Notification.message,
            User.id.label('recipient_id'),
            User.fullName.label('recipient_name'),
            Suspect.first_name,
            Suspect.last_name
        ).join(NotificationRecipient, Notification.id == NotificationRecipient.notification_id
        ).join(User, NotificationRecipient.recipient_id == User.id
        ).outerjoin(Suspect, Notification.suspect_id == Suspect.suspect_id
        ).distinct().all()

        data = []
        for r in results:
            data.append({
                'notification_id': r.notification_id,
                'message': r.message,
                'recipient_id': r.recipient_id,
                'recipient_name': r.recipient_name,
                'suspect_name': f"{r.first_name} {r.last_name}" if r.first_name else None
            })
        return jsonify(data), 200

    except Exception as e:
        print(f">>> Error in /summary: {str(e)}")
        return jsonify({'msg': 'Server error'}), 500


# API 2: Detailed Channels Sent to One Recipient for a Notification (Second Grid)
@notification_bp.route('/details', methods=['GET'])
@jwt_required()
def notification_details():
    notification_id = request.args.get('notification_id', type=int)
    recipient_id = request.args.get('recipient_id', type=int)

    if not notification_id or not recipient_id:
        return jsonify({'msg': 'Missing notification_id or recipient_id'}), 400

    try:
        results = db.session.query(
            NotificationRecipient.channel,
            NotificationRecipient.delivery_status,
            NotificationRecipient.delivery_time,
            User.fullName.label('recipient_name'),
            User.email,
            User.phoneNumber.label('phone')
        ).join(User, NotificationRecipient.recipient_id == User.id
        ).filter(
            NotificationRecipient.notification_id == notification_id,
            NotificationRecipient.recipient_id == recipient_id
        ).all()

        data = []
        for r in results:
            data.append({
                'channel': r.channel,
                'delivery_status': r.delivery_status,
                'delivery_time': r.delivery_time.isoformat() if r.delivery_time else None,
                'recipient_name': r.recipient_name,
                'email': r.email,
                'phone': r.phone
            })

        return jsonify(data), 200

    except Exception as e:
        print(f">>> Error in /details: {str(e)}")
        return jsonify({'msg': 'Server error'}), 500
