class NotificationRecipientStore:
    @staticmethod
    def add(notification_id: int,
            recipient_id: int,
            channel: str,
            delivery_status: str,
            delivery_time: Optional[datetime]) -> NotificationRecipient:
        nr = NotificationRecipient(
            notification_id=notification_id,
            recipient_id=recipient_id,
            channel=channel,
            delivery_status=delivery_status,
            delivery_time=delivery_time
        )
        db.session.add(nr)
        db.session.commit()
        return nr

    @staticmethod
    def list_for_notification(notification_id: int) -> List[NotificationRecipient]:
        return (NotificationRecipient.query
                .filter_by(notification_id=notification_id)
                .all())

    @staticmethod
    def delete_for_notification(notification_id: int) -> int:
        rows = NotificationRecipient.query.filter_by(notification_id=notification_id).delete()
        db.session.commit()
        return rows
