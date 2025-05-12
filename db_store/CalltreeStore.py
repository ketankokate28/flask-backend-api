class CallTreeStore:
    @staticmethod
    def get_tree(channel: str) -> List[CallTreeEntry]:
        return (CallTreeEntry.query
                .filter_by(channel=channel)
                .order_by(CallTreeEntry.level)
                .all())

    @staticmethod
    def add_entry(level: int, channel: str, recipient_id: int, timeout: Optional[int]) -> CallTreeEntry:
        entry = CallTreeEntry(
            level=level,
            channel=channel,
            recipient_id=recipient_id,
            timeout=timeout
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def delete_entry(level: int, channel: str, recipient_id: int) -> bool:
        entry = CallTreeEntry.query.get((level, channel, recipient_id))
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True