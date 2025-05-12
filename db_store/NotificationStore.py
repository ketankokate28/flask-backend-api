class NotificationStore:
    @staticmethod
    def create(cctv_id: int,
               suspect_id: int,
               notification_type: str,
               message: str,
               event_time: Optional[datetime] = None) -> Notification:
        notif = Notification(
            cctv_id=cctv_id,
            suspect_id=suspect_id,
            event_time=event_time or datetime.utcnow(),
            notification_type=notification_type,
            message=message
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def get_by_id(notification_id: int) -> Optional[Notification]:
        return Notification.query.get(notification_id)

    @staticmethod
    def list_recent(limit: int = 50) -> List[Notification]:
        return (Notification.query
                .order_by(Notification.created_at.desc())
                .limit(limit)
                .all())
