# notifications/routes.py

from flask import Blueprint, jsonify, current_app as app
from models import Matchfacelog
from notification_service import dispatch_notification

notificationregister_bp = Blueprint('notificationregister', __name__)

@notificationregister_bp.route(
    '/<int:matchfacelog_id>/notify',
    methods=['POST']
)
def notify_for_matchfacelog(matchfacelog_id):
    """
    Trigger notification dispatch for the given MatchFaceLog.

    1) Verifies the MatchFaceLog exists.
    2) Calls dispatch_notification(matchfacelog_id) which handles creating
       the Notification if needed and sending alerts.
    """
    # 1) Fetch the match entry
    match = Matchfacelog.query.get(matchfacelog_id)
    if not match:
        return jsonify({'status': 'error',
                        'message': f'MatchFaceLog {matchfacelog_id} not found'}), 404

    # 2) Dispatch via service (handles Notification creation internally)
    try:
        dispatched_count = dispatch_notification(matchfacelog_id, null)
        return jsonify({'status': 'success', 'dispatched': dispatched_count}), 200
    except Exception as e:
        app.logger.exception(
            "Error dispatching notification for MatchFaceLog %s: %s",
            matchfacelog_id, e
        )
        return jsonify({'status': 'error', 'message': str(e)}), 500
