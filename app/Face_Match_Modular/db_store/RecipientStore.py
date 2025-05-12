class RecipientStore:

    
    @staticmethod
    def get_all(active_only: bool = True) -> List[Recipient]:
        query = Recipient.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_by_id(recipient_id: int) -> Optional[Recipient]:
        return Recipient.query.get(recipient_id)

    @staticmethod
    def create(name: str,
               email: Optional[str],
               phone_number: Optional[str],
               channels: List[str],
               is_active: bool = True) -> Recipient:
        channels_str = ",".join(channels)
        rec = Recipient(
            name=name,
            email=email,
            phone_number=phone_number,
            channels=channels_str,
            is_active=is_active,
            created_at=datetime.utcnow()
        )
        db.session.add(rec)
        db.session.commit()
        return rec

    @staticmethod
    def update(recipient_id: int,
               name: Optional[str] = None,
               email: Optional[str] = None,
               phone_number: Optional[str] = None,
               channels: Optional[List[str]] = None,
               is_active: Optional[bool] = None) -> Optional[Recipient]:
        rec = Recipient.query.get(recipient_id)
        if not rec:
            return None
        if name is not None:
            rec.name = name
        if email is not None:
            rec.email = email
        if phone_number is not None:
            rec.phone_number = phone_number
        if channels is not None:
            rec.channels = ",".join(channels)
        if is_active is not None:
            rec.is_active = is_active
        db.session.commit()
        return rec

    @staticmethod
    def delete(recipient_id: int) -> bool:
        rec = Recipient.query.get(recipient_id)
        if not rec:
            return False
        db.session.delete(rec)
        db.session.commit()
        return True